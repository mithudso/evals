"""Behavioral checks for index drift and non-destructive workflow log rotation."""

import json
import subprocess
from pathlib import Path

import pytest

from scripts import rotate_workflow_logs
from scripts.check_doc_indexes import check_indexes, check_links
from scripts.generate_doc_indexes import write_indexes
from scripts.rotate_workflow_logs import rotate_logs


@pytest.fixture
def repo(tmp_path):
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    (tmp_path / "runner").mkdir()
    (tmp_path / "runner" / "sample.py").write_text('"""A sample runner."""\ndef run():\n    pass\n')
    return tmp_path


def test_index_generation_is_deterministic_and_detects_new_files(repo):
    write_indexes(repo)
    first = (repo / "docs/high_signal_file_index.json").read_bytes()
    assert check_indexes(repo) == []
    write_indexes(repo)
    assert (repo / "docs/high_signal_file_index.json").read_bytes() == first
    (repo / "runner/extra.py").write_text('"""Another module."""\n')
    assert any("stale" in error for error in check_indexes(repo))


def test_checker_rejects_dead_or_escaping_paths(repo):
    write_indexes(repo)
    path = repo / "docs/high_signal_file_index.json"
    data = json.loads(path.read_text())
    data["files"][0]["path"] = "../escape.py"
    path.write_text(json.dumps(data))
    assert any("unsafe" in error for error in check_indexes(repo))
    (repo / "runner/sample.py").unlink()
    assert any("stale" in error for error in check_indexes(repo))


def test_links_inside_nested_diff_fences_are_examples(repo):
    (repo / "docs").mkdir()
    (repo / "docs/example.md").write_text(
        "# Report\n\n````diff\n+```sh\n+[example](missing.md)\n+```\n````\n"
    )
    assert check_links(repo) == []
    (repo / "docs/example.md").write_text("[broken](missing.md)\n")
    assert len(check_links(repo)) == 1


def test_rotate_retains_recent_sections_and_archives_old_content(repo):
    log = repo / "memory.md"
    log.write_text("# Memory\n\n## v3\nnew\n\n## v2\nprevious\n\n## v1\nold\n")
    assert rotate_logs(repo, max_bytes=1, keep_sections=2) == ["memory.md"]
    assert "## v3" in log.read_text() and "## v2" in log.read_text()
    assert "## v1" not in log.read_text()
    archives = list((repo / "docs/archive").glob("memory-*.md"))
    assert len(archives) == 1 and "## v1\nold" in archives[0].read_text()
    assert rotate_logs(repo, max_bytes=1, keep_sections=2) == []


@pytest.mark.parametrize("swap_name", [".memory.md.swp", "memory.md.swp", ".prompts.md.swp"])
def test_rotate_refuses_active_editor_without_writing(repo, swap_name):
    source = "# Memory\n\n## v2\nnew\n\n## v1\nold\n"
    (repo / "memory.md").write_text(source)
    (repo / swap_name).touch()
    with pytest.raises(ValueError, match="swap"):
        rotate_logs(repo, max_bytes=1, keep_sections=1)
    assert (repo / "memory.md").read_text() == source
    assert not (repo / "docs/archive").exists()


def test_rotate_preserves_a_concurrent_edit(repo, monkeypatch):
    source = "# Memory\n\n## v2\nnew\n\n## v1\nold\n"
    log = repo / "memory.md"
    log.write_text(source)
    factory = rotate_workflow_logs.tempfile.NamedTemporaryFile

    def edited_during_rotation(*args, **kwargs):
        log.write_text(source + "active edit\n")
        return factory(*args, **kwargs)

    monkeypatch.setattr(rotate_workflow_logs.tempfile, "NamedTemporaryFile", edited_during_rotation)
    with pytest.raises(ValueError, match="changed during rotation"):
        rotate_logs(repo, max_bytes=1, keep_sections=1)
    assert log.read_text() == source + "active edit\n"


def test_append_after_final_guard_is_preserved_in_archive(repo, monkeypatch):
    log = repo / "memory.md"
    log.write_text("# Memory\n\n## v2\nnew\n\n## v1\nold\n")
    original_glob = Path.glob
    checks = 0

    def concurrent_append(path, pattern, *args, **kwargs):
        nonlocal checks
        if path == repo and pattern == "*memory.md*.sw[opx]":
            checks += 1
            if checks == 2:
                with log.open("a") as handle:
                    handle.write("concurrent update\n")
        return original_glob(path, pattern, *args, **kwargs)

    monkeypatch.setattr(Path, "glob", concurrent_append)
    rotate_logs(repo, max_bytes=1, keep_sections=1)
    retained = log.read_text() + "".join(
        archive.read_text() for archive in (repo / "docs/archive").glob("memory-*.md")
    )
    assert "concurrent update" in retained


def test_rotation_preserves_a_source_recreated_during_publication(repo, monkeypatch):
    log = repo / "memory.md"
    original = "# Memory\n\n## v2\nnew\n\n## v1\nold\n"
    log.write_text(original)
    link = rotate_workflow_logs.os.link

    def recreated_source(source, destination, *args, **kwargs):
        if not log.exists():
            log.write_text("concurrently recreated log\n")
        return link(source, destination, *args, **kwargs)

    monkeypatch.setattr(rotate_workflow_logs.os, "link", recreated_source)
    with pytest.raises(ValueError, match="publication refused"):
        rotate_logs(repo, max_bytes=1, keep_sections=1)
    assert log.read_text() == "concurrently recreated log\n"
    archives = list((repo / "docs/archive").glob("memory-*.md"))
    assert len(archives) == 1 and archives[0].read_text() == original
