"""Replay evaluates observed responses; dry-run only checks supplied expectations."""

import json
import logging
import subprocess
import sys
from pathlib import Path

import pytest

from runner import eval_runner


def write_suite(tmp_path, **updates):
    data = {
        "skill_name": "sample",
        "evals": [
            {
                "id": 1,
                "prompt": "prompt_marker",
                "expected_output": "expected_marker",
                "actual_output": "observed_marker",
                "assertions": [{"check": "contains `observed_marker`", "type": "deterministic"}],
            }
        ],
    }
    data.update(updates)
    path = tmp_path / "suite.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path, data


def test_replay_uses_observed_response_without_prompt_or_expected_leakage(tmp_path):
    path, data = write_suite(tmp_path)
    result = eval_runner.run_suite(str(path))
    assert result["mode"] == "replay"
    assert result["output_source"] == "provided-output"
    assert result["passed_assertions"] == 1
    data["evals"][0]["assertions"][0]["check"] = "contains `expected_marker`"
    path.write_text(json.dumps(data), encoding="utf-8")
    assert eval_runner.run_suite(str(path))["passed_assertions"] == 0


def test_dry_run_grades_expectation_verbatim_without_synthetic_structure(tmp_path):
    path, data = write_suite(tmp_path)
    data["evals"][0]["assertions"] = [{"check": "has heading", "type": "structural"}]
    path.write_text(json.dumps(data), encoding="utf-8")
    result = eval_runner.run_suite(str(path), dry_run=True)
    assert result["mode"] == "dry-run"
    assert result["output_source"] == "expected_output"
    assert result["passed_assertions"] == 0


def test_outputs_mapping_can_supply_observed_response(tmp_path):
    path, data = write_suite(tmp_path)
    del data["evals"][0]["actual_output"]
    path.write_text(json.dumps(data), encoding="utf-8")
    result = eval_runner.run_suite(str(path), outputs={"1": "observed_marker"})
    assert result["passed_assertions"] == 1


def test_missing_observed_output_is_error_before_output_directory_write(tmp_path):
    path, data = write_suite(tmp_path)
    del data["evals"][0]["actual_output"]
    path.write_text(json.dumps(data), encoding="utf-8")
    destination = tmp_path / "no-write"
    with pytest.raises(ValueError, match="output"):
        eval_runner.run_suite(str(path), str(destination))
    assert not destination.exists()


def test_live_execution_is_rejected_before_output_write(tmp_path):
    path, _ = write_suite(tmp_path)
    destination = tmp_path / "no-write"
    with pytest.raises(ValueError, match="[Ll]ive"):
        eval_runner.run_suite(str(path), str(destination), execute_live=True)
    assert not destination.exists()


def test_unsafe_skill_filename_and_existing_output_symlink_are_rejected(tmp_path):
    path, _ = write_suite(tmp_path, skill_name="../escape")
    destination = tmp_path / "no-write"
    with pytest.raises(ValueError, match="skill_name"):
        eval_runner.run_suite(str(path), str(destination))
    assert not destination.exists()
    path, _ = write_suite(tmp_path)
    destination.mkdir()
    victim = tmp_path / "victim.json"
    victim.write_text("preserve", encoding="utf-8")
    (destination / "sample-benchmark.json").symlink_to(victim)
    with pytest.raises(ValueError, match="output"):
        eval_runner.run_suite(str(path), str(destination))
    assert victim.read_text(encoding="utf-8") == "preserve"


def test_case_timing_includes_grading(tmp_path, monkeypatch):
    path, _ = write_suite(tmp_path)
    clock = iter([100.0, 101.0, 103.0, 104.0])
    monkeypatch.setattr(eval_runner.time, "perf_counter", lambda: next(clock))
    result = eval_runner.run_suite(str(path))
    assert result["eval_results"][0]["duration_s"] == 2.0
    assert result["duration_seconds"] == 4.0


def test_operational_errors_log_without_response_or_prompt_content(tmp_path, caplog):
    path, data = write_suite(tmp_path)
    del data["evals"][0]["actual_output"]
    path.write_text(json.dumps(data), encoding="utf-8")
    with caplog.at_level(logging.ERROR), pytest.raises(ValueError):
        eval_runner.run_suite(str(path))
    assert caplog.records
    assert "prompt_marker" not in caplog.text
    assert "expected_marker" not in caplog.text


def test_cli_reports_failed_assertions_and_accepts_outputs_file(tmp_path):
    path, _ = write_suite(tmp_path)
    script = Path(eval_runner.__file__)
    failed = subprocess.run(
        [sys.executable, str(script), str(path), "--dry-run"], capture_output=True, text=True
    )
    assert failed.returncode != 0
    outputs = tmp_path / "outputs.json"
    outputs.write_text('{"1": "observed_marker"}', encoding="utf-8")
    passed = subprocess.run(
        [sys.executable, str(script), str(path), "--outputs", str(outputs)],
        capture_output=True,
        text=True,
    )
    assert passed.returncode == 0, passed.stderr


@pytest.mark.parametrize("raw", ["null", '{"1":"first", "1":"second"}'])
def test_cli_rejects_ambiguous_or_non_object_outputs_file(tmp_path, raw):
    path, _ = write_suite(tmp_path)
    outputs = tmp_path / "outputs.json"
    outputs.write_text(raw, encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(Path(eval_runner.__file__)), str(path), "--outputs", str(outputs)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2
    assert "Traceback" not in result.stderr


def test_outputs_mapping_rejects_unknown_id_and_non_string_response(tmp_path):
    path, _ = write_suite(tmp_path)
    with pytest.raises(ValueError, match="unknown case ID"):
        eval_runner.run_suite(str(path), outputs={"typo": "a response"})
    with pytest.raises(ValueError, match="response strings"):
        eval_runner.run_suite(str(path), outputs={"1": None})


@pytest.mark.parametrize("as_outputs", [False, True])
def test_cli_rejects_deeply_nested_json_without_a_traceback(tmp_path, as_outputs):
    path, _ = write_suite(tmp_path)
    nested = tmp_path / "nested.json"
    nested.write_text("[" * 2000 + "0" + "]" * 2000, encoding="utf-8")
    args = [str(path), "--outputs", str(nested)] if as_outputs else [str(nested)]
    result = subprocess.run(
        [sys.executable, str(Path(eval_runner.__file__)), *args],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2
    assert "Traceback" not in result.stderr
    assert "RecursionError" not in result.stderr


@pytest.mark.parametrize("alias", ["direct", "symlink", "hardlink"])
def test_benchmark_destination_cannot_overwrite_input_suite(tmp_path, alias):
    path, _ = write_suite(tmp_path)
    destination = tmp_path / "sample-benchmark.json"
    if alias == "direct":
        path = path.rename(destination)
    elif alias == "symlink":
        destination.symlink_to(path)
    else:
        destination.hardlink_to(path)
    original = path.read_bytes()
    with pytest.raises(ValueError, match="output"):
        eval_runner.run_suite(str(path), str(tmp_path))
    assert path.read_bytes() == original


@pytest.mark.parametrize("alias", ["direct", "symlink", "hardlink"])
def test_cli_benchmark_destination_cannot_overwrite_outputs_input(tmp_path, alias):
    path, _ = write_suite(tmp_path)
    outputs = tmp_path / "outputs.json"
    outputs.write_text('{"1": "observed_marker"}', encoding="utf-8")
    destination = tmp_path / "sample-benchmark.json"
    if alias == "direct":
        outputs = outputs.rename(destination)
    elif alias == "symlink":
        destination.symlink_to(outputs)
    else:
        destination.hardlink_to(outputs)
    original = outputs.read_bytes()
    result = subprocess.run(
        [
            sys.executable,
            str(Path(eval_runner.__file__)),
            str(path),
            "--outputs",
            str(outputs),
            "--output-dir",
            str(tmp_path),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2
    assert "Traceback" not in result.stderr
    assert outputs.read_bytes() == original
