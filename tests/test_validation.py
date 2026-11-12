"""Pure suite validation protects callers before any execution or output write."""

from copy import deepcopy

import pytest

from runner.validation import (
    is_safe_skill_name,
    validate_functional_suite,
    validate_trigger_suite,
)


def functional():
    return {
        "skill_name": "test-skill",
        "evals": [
            {
                "id": 1,
                "prompt": "A realistic user request",
                "expected_output": "A clear response",
                "assertions": [{"check": "contains `response`", "type": "deterministic"}],
            }
        ],
    }


def test_valid_suite_is_not_mutated():
    data = functional()
    original = deepcopy(data)
    assert validate_functional_suite(data) == []
    assert data == original


@pytest.mark.parametrize(
    "value", ["../escape", "/absolute", ".", "", "a/b", "a\\b", "two words", "name.json"]
)
def test_skill_name_rejects_unsafe_filename_components(value):
    assert is_safe_skill_name(value) is False
    data = functional()
    data["skill_name"] = value
    assert any("skill_name" in error for error in validate_functional_suite(data))


@pytest.mark.parametrize(
    "data",
    [None, [], 1, {"skill_name": "valid", "evals": None}, {"skill_name": "valid", "evals": []}],
)
def test_invalid_root_and_empty_cases_return_errors(data):
    assert validate_functional_suite(data)


def test_nested_errors_report_field_locations():
    data = functional()
    data["evals"][0].update(
        {
            "id": True,
            "prompt": " ",
            "expected_output": None,
            "files": [None],
            "assertions": [{"check": "", "type": "typo"}],
        }
    )
    errors = validate_functional_suite(data)
    for field in [
        "id",
        "prompt",
        "expected_output",
        "files[0]",
        "assertions[0].check",
        "assertions[0].type",
    ]:
        assert any(f"evals[0].{field}" in error for error in errors)


def test_duplicate_ids_include_numeric_string_output_key_collision():
    data = functional()
    data["evals"].append({**deepcopy(data["evals"][0]), "id": "1"})
    assert any("evals[1].id" in error for error in validate_functional_suite(data))


@pytest.mark.parametrize("assertions", [[], [None], [""], [{}]])
def test_vacuous_or_malformed_assertions_are_invalid(assertions):
    data = functional()
    data["evals"][0]["assertions"] = assertions
    assert validate_functional_suite(data)


def test_trigger_validates_types_query_and_both_classes():
    assert (
        validate_trigger_suite(
            [
                {"query": "primary request", "should_trigger": True},
                {"query": "adjacent request", "should_trigger": False},
            ]
        )
        == []
    )
    errors = validate_trigger_suite([{"query": None, "should_trigger": "false"}])
    assert any("[0].query" in error for error in errors)
    assert any("[0].should_trigger" in error for error in errors)
    assert validate_trigger_suite([{"query": "one class", "should_trigger": True}])
    assert validate_trigger_suite([])
