"""Aggregation preserves provenance, validates counters, and renders safe reports."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

from benchmarks import aggregate


def record(**changes):
    return {
        "skill_name": "fruit",
        "total_evals": 1,
        "total_assertions": 2,
        "passed_assertions": 2,
        "pass_rate_percent": 100.0,
        "duration_seconds": 0.5,
        "mode": "replay",
        "output_source": "provided-output",
    } | changes


def write_record(root, filename, data):
    path = root / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data))
    return path


def test_rates_are_derived_from_counts(tmp_path):
    write_record(
        tmp_path, "fruit-benchmark.json", record(passed_assertions=0, pass_rate_percent=100.0)
    )
    result = aggregate.aggregate_results(str(tmp_path))
    assert result["groups"]["replay"]["pass_rate_percent"] == 0.0
    assert "0.0%" in result["markdown"]
    assert "✅ PASS" not in result["markdown"]


def test_identical_exports_deduplicate_but_distinct_runs_remain(tmp_path):
    data = record()
    write_record(tmp_path, "a-benchmark.json", data)
    write_record(tmp_path, "copies/a-benchmark.json", dict(reversed(list(data.items()))))
    write_record(tmp_path, "another-benchmark.json", record(duration_seconds=2.0))
    result = aggregate.aggregate_results(str(tmp_path))
    assert result["files_discovered"] == 3
    assert result["duplicates_skipped"] == 1
    assert result["unique_records"] == 2
    assert result["unique_skills"] == 1
    assert result["groups"]["replay"]["total_assertions"] == 4


def test_provenance_groups_do_not_mix_measured_totals(tmp_path):
    write_record(tmp_path, "replay-benchmark.json", record())
    write_record(tmp_path, "dry-benchmark.json", record(mode="dry-run", passed_assertions=0))
    legacy = record(skill_name="legacy", passed_assertions=0)
    legacy.pop("mode")
    legacy.pop("output_source")
    write_record(tmp_path, "legacy-benchmark.json", legacy)
    result = aggregate.aggregate_results(str(tmp_path))
    assert result["groups"]["replay"]["total_assertions"] == 2
    assert result["groups"]["replay"]["pass_rate_percent"] == 100.0
    assert result["groups"]["dry-run"]["total_assertions"] == 2
    assert result["groups"]["legacy"]["total_assertions"] == 2
    assert "provenance unknown" in result["markdown"].lower()


@pytest.mark.parametrize(
    "changes",
    [
        {"total_evals": True},
        {"total_assertions": -1},
        {"total_assertions": 1.5},
        {"passed_assertions": 3},
        {"duration_seconds": float("inf")},
        {"total_assertions": "2"},
        {"duration_seconds": -0.1},
    ],
)
def test_invalid_numeric_records_fail_clearly(tmp_path, changes):
    write_record(tmp_path, "bad-benchmark.json", record(**changes))
    with pytest.raises(ValueError, match="bad-benchmark.json"):
        aggregate.aggregate_results(str(tmp_path))


def test_invalid_record_shape_fails_clearly(tmp_path):
    write_record(tmp_path, "bad-benchmark.json", [])
    with pytest.raises(ValueError, match="bad-benchmark.json"):
        aggregate.aggregate_results(str(tmp_path))


def test_markdown_name_is_escaped_and_order_is_stable(tmp_path):
    write_record(tmp_path, "z-benchmark.json", record(skill_name="zeta"))
    write_record(tmp_path, "a-benchmark.json", record(skill_name="bad` | forged\n# heading"))
    first = aggregate.aggregate_results(str(tmp_path))["markdown"]
    second = aggregate.aggregate_results(str(tmp_path))["markdown"]
    assert first == second
    assert "\n# heading" not in first
    assert "\\| forged" in first
    assert first.index("bad") < first.index("zeta")


def test_nested_output_directories_are_created(tmp_path):
    write_record(tmp_path, "fruit-benchmark.json", record())
    output = tmp_path / "reports" / "summary.md"
    result = aggregate.aggregate_results(str(tmp_path), str(output))
    assert output.read_text() == result["markdown"]


def test_cli_reports_invalid_record_without_traceback(tmp_path):
    write_record(tmp_path, "bad-benchmark.json", [])
    result = subprocess.run(
        [sys.executable, str(Path(aggregate.__file__)), str(tmp_path)],
        text=True,
        capture_output=True,
    )
    assert result.returncode == 1
    assert "bad-benchmark.json" in result.stderr
    assert "Traceback" not in result.stderr


def test_oversized_duration_has_a_file_addressed_validation_error(tmp_path):
    write_record(tmp_path, "bad-benchmark.json", record(duration_seconds=10**400))
    with pytest.raises(ValueError, match="bad-benchmark.json"):
        aggregate.aggregate_results(str(tmp_path))


def test_nonfinite_nested_values_have_a_file_addressed_validation_error(tmp_path):
    write_record(tmp_path, "bad-benchmark.json", record(eval_results=[float("nan")]))
    with pytest.raises(ValueError, match="bad-benchmark.json"):
        aggregate.aggregate_results(str(tmp_path))


@pytest.mark.parametrize("alias_kind", ["direct", "symlink", "hardlink"])
def test_report_destination_cannot_alias_a_source_export(tmp_path, alias_kind):
    source = write_record(tmp_path, "fruit-benchmark.json", record())
    before = source.read_bytes()
    if alias_kind == "direct":
        output = source
    else:
        output = tmp_path / "report.md"
        if alias_kind == "symlink":
            output.symlink_to(source)
        else:
            output.hardlink_to(source)
    with pytest.raises(ValueError, match="[Oo]utput"):
        aggregate.aggregate_results(str(tmp_path), str(output))
    assert source.read_bytes() == before


def test_report_destination_cannot_poison_future_export_discovery(tmp_path):
    source = write_record(tmp_path, "fruit-benchmark.json", record())
    before = source.read_bytes()
    output = tmp_path / "reports" / "new-benchmark.json"
    with pytest.raises(ValueError, match="[Oo]utput"):
        aggregate.aggregate_results(str(tmp_path), str(output))
    assert not output.exists()
    assert source.read_bytes() == before


def test_deeply_nested_benchmark_json_has_a_clean_file_addressed_error(tmp_path):
    path = tmp_path / "deep-benchmark.json"
    path.write_text("[" * 2000 + '"private-marker"' + "]" * 2000)
    with pytest.raises(ValueError, match="deep-benchmark.json"):
        aggregate.aggregate_results(str(tmp_path))
    result = subprocess.run(
        [sys.executable, str(Path(aggregate.__file__)), str(tmp_path)],
        text=True,
        capture_output=True,
    )
    assert result.returncode == 1
    assert "deep-benchmark.json" in result.stderr
    assert "private-marker" not in result.stderr
    assert "Traceback" not in result.stderr
