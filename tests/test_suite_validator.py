"""Suite validation rejects malformed schemas and checks real fixture paths."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

from benchmarks import suite_validator as validator


def suite(files=None, skill_name="fruit", prompt="Transform the supplied fruit list."):
    return {
        "skill_name": skill_name,
        "evals": [
            {
                "id": 1,
                "prompt": prompt,
                "expected_output": "A complete transformed fruit list.",
                "files": files or [],
                "assertions": [{"check": "contains 'apple'", "type": "deterministic"}],
            }
        ],
    }


@pytest.mark.parametrize(
    "data",
    [
        None,
        7,
        {"skill_name": "fruit", "evals": [None]},
        [{"query": "apple", "should_trigger": "true"}],
        suite() | {"evals": "bad"},
    ],
)
def test_schema_errors_are_pass_l_findings(tmp_path, data):
    path = tmp_path / "suite.json"
    path.write_text(json.dumps(data))
    result = validator.validate_suite(str(path))
    assert any(item["pass"] == "Pass L" for item in result["findings"])


@pytest.mark.parametrize("fixture", ["missing.txt", "directory"])
def test_missing_and_directory_fixtures_are_findings(tmp_path, fixture):
    (tmp_path / "directory").mkdir()
    path = tmp_path / "suite.json"
    path.write_text(json.dumps(suite([fixture])))
    result = validator.validate_suite(str(path))
    assert any(item["pass"] == "Pass G" for item in result["findings"])


def test_fixture_paths_are_relative_to_suite(tmp_path, monkeypatch):
    fixture_dir = tmp_path / "inputs"
    fixture_dir.mkdir()
    (fixture_dir / "fruit.txt").write_text("apple")
    path = tmp_path / "suite.json"
    path.write_text(json.dumps(suite(["inputs/fruit.txt"])))
    monkeypatch.chdir(tmp_path.parent)
    result = validator.validate_suite(str(path))
    assert not any(item["pass"] == "Pass G" for item in result["findings"])


def test_leakage_detection_is_case_insensitive(tmp_path):
    path = tmp_path / "suite.json"
    path.write_text(
        json.dumps(
            suite(skill_name="Fruit-Skill", prompt="Please run the fruit-skill on this list.")
        )
    )
    result = validator.validate_suite(str(path))
    assert any(
        item["pass"] == "Pass F" and item["severity"] == "High" for item in result["findings"]
    )


def test_malformed_json_is_reported_without_traceback(tmp_path):
    path = tmp_path / "suite.json"
    path.write_text("{broken")
    result = validator.validate_suite(str(path))
    assert result["high_findings"] >= 1
    assert all(finding["pass"] == "Pass L" for finding in result["findings"])


def test_validator_reports_implemented_coverage(tmp_path):
    path = tmp_path / "suite.json"
    path.write_text(json.dumps(suite()))
    result = validator.validate_suite(str(path))
    assert set(result["unimplemented_passes"]) == {"Pass B", "Pass E", "Pass J", "Pass K"}


def test_cli_returns_failure_for_analytical_findings(tmp_path):
    path = tmp_path / "suite.json"
    path.write_text(json.dumps(suite()))
    result = subprocess.run(
        [sys.executable, str(Path(validator.__file__)), str(path)], text=True, capture_output=True
    )
    assert result.returncode == 1
    assert "findings" in result.stdout


def test_cli_returns_failure_for_missing_file(tmp_path):
    result = subprocess.run(
        [sys.executable, str(Path(validator.__file__)), str(tmp_path / "missing.json")],
        text=True,
        capture_output=True,
    )
    assert result.returncode == 1
    assert "Traceback" not in result.stderr


def test_one_repeated_token_is_detected_as_low_entropy(tmp_path):
    path = tmp_path / "suite.json"
    path.write_text(json.dumps(suite(prompt="apple " * 20)))
    result = validator.validate_suite(str(path))
    assert any(
        item["pass"] == "Pass F" and "Low token entropy" in item["finding"]
        for item in result["findings"]
    )


def test_deeply_nested_suite_json_is_a_clean_file_addressed_error(tmp_path):
    path = tmp_path / "deep-suite.json"
    path.write_text("[" * 2000 + '"private-marker"' + "]" * 2000)
    result = validator.validate_suite(str(path))
    assert result["file"] == str(path)
    assert result["high_findings"] >= 1
    assert all(finding["pass"] == "Pass L" for finding in result["findings"])
    process = subprocess.run(
        [sys.executable, str(Path(validator.__file__)), str(path)],
        text=True,
        capture_output=True,
    )
    assert process.returncode == 1
    assert "deep-suite.json" in process.stdout
    assert "private-marker" not in process.stdout + process.stderr
    assert "Traceback" not in process.stderr
