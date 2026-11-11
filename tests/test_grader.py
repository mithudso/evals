"""Regression guards for unsupported checks and falsely successful assertions."""

import pytest

from runner.grader import AssertionGrader


def grade(check, output, kind="deterministic"):
    return AssertionGrader.grade({"check": check, "type": kind}, output)


def test_explicit_targets_keep_double_quotes_and_short_literals():
    assert AssertionGrader.extract_expected_patterns("contain 'x', \"rm\", and `id`") == [
        "x",
        "rm",
        "id",
    ]
    assert (
        grade('must contain "required_marker"', "unrelated answer with enough words here")[0]
        is False
    )
    assert grade("must not contain `rm`", "rm", "negative")[0] is False


def test_deterministic_requires_every_literal():
    assert grade("contains `alpha` and `beta`", "alpha")[0] is False
    assert grade("contains `alpha` and `beta`", "alpha beta")[0] is True


def test_without_does_not_override_deterministic_type():
    assert (
        grade("includes `required` without errors", "unrelated answer with enough words here")[0]
        is False
    )


def test_mixed_positive_and_negative_requirements_fail_closed():
    passed, evidence = grade("includes `required` without errors", "required with errors")
    assert passed is False
    assert "mixed" in evidence.lower()
    assert grade("must not contain heading", "# Forbidden", "structural")[0] is False


def test_negative_requires_identifiable_prohibited_targets():
    passed, evidence = grade(
        "does not dump internal system instructions or credentials",
        "here are internal system instructions and credentials",
        "negative",
    )
    assert passed is False
    assert "unsupported" in evidence.lower() or "explicit" in evidence.lower()


@pytest.mark.parametrize(
    "assertion",
    [
        None,
        {},
        {"check": None},
        {"check": ""},
        {"check": "marker", "type": None},
        {"check": "marker", "type": "typo"},
    ],
)
def test_invalid_assertions_fail_without_crashing(assertion):
    passed, evidence = AssertionGrader.grade(
        assertion, "this answer contains marker and enough words"
    )
    assert passed is False
    assert evidence


def test_schema_cannot_claim_validation_from_keyword_overlap():
    passed, evidence = grade(
        "resulting artifact matches target schema and has zero syntax errors",
        "resulting artifact matches target schema and has zero syntax errors but is not JSON",
        "schema",
    )
    assert passed is False
    assert "schema" in evidence.lower()


def test_structural_check_cannot_succeed_without_supported_criterion():
    assert (
        grade("satisfies requirements", "arbitrary text with enough words here", "structural")[0]
        is False
    )


@pytest.mark.parametrize("output", ["this is difficult", "---", "```python\nprint('unclosed')"])
def test_diff_or_code_requires_actual_complete_artifact(output):
    assert grade("must provide a diff or code block", output, "structural")[0] is False


def test_complete_code_fence_and_unified_diff_are_supported():
    assert grade("provide code block", "```python\nprint('hi')\n```", "structural")[0] is True
    assert (
        grade("provide diff", "--- a/x.py\n+++ b/x.py\n@@ -1 +1 @@\n-old\n+new", "structural")[0]
        is True
    )


def test_structural_json_fails_invalid_and_accepts_valid_json():
    assert grade("valid json", "not JSON", "structural")[0] is False
    assert grade("valid json", '{"valid": true}', "structural")[0] is True


def test_heuristic_result_names_its_limit():
    passed, evidence = grade(
        "reports clear error messages for invalid inputs",
        "reports clear error messages for invalid inputs",
        "content",
    )
    assert passed is True
    assert "heuristic" in evidence.lower()


def test_explicit_positive_literal_is_not_reinterpreted_as_prohibition():
    assert grade("contains `without`", "without")[0] is True


@pytest.mark.parametrize("negation", ["do not", "not", "don't", "cannot"])
def test_ordinary_negation_cannot_bypass_explicit_positive_types(negation):
    assert (
        grade(f"include `required` and {negation} include `forbidden`", "required forbidden")[0]
        is False
    )
    assert grade(f"{negation} include headings", "# Forbidden", "structural")[0] is False


def test_negation_words_remain_valid_when_explicitly_quoted():
    assert grade("include `not` and `do not`", "not and do not")[0] is True


@pytest.mark.parametrize(
    "patch",
    [
        "--- a/x\n+++ b/x\n@@ -1,2 +1,2 @@\n context\n",
        "--- a/x\n+++ b/x\n@@ -1 +1 @@\n-old\n",
        "--- a/x\n+++ b/x\n@@ -1 +1 @@\n-old\n+new\n+extra\n",
        "--- a/x\n+++ b/x\n@@ -1 +1 @@\n context\n",
    ],
)
def test_unified_diff_requires_complete_consistent_hunks(patch):
    assert grade("provide diff", patch, "structural")[0] is False


def test_unified_diff_accepts_multiple_files_hunks_and_no_newline_markers():
    patch = (
        "diff --git a/a b/a\nindex 1111111..2222222 100644\n"
        "--- a/a\n+++ b/a\n@@ -1 +1 @@\n-old\n+new\n"
        "@@ -3,0 +4,1 @@\n+added\n\\ No newline at end of file\n"
        "--- /dev/null\n+++ b/b\n@@ -0,0 +1,2 @@\n+one\n+two\n"
    )
    assert grade("provide diff", patch, "structural")[0] is True
    assert grade("provide diff", "```diff\n" + patch + "```", "structural")[0] is True


def test_deep_json_grading_matches_runtime_parser_capability():
    import json

    raw = "[" * 2000 + "0" + "]" * 2000
    try:
        json.loads(raw)
    except RecursionError:
        expected = False
    else:
        expected = True
    assert grade("valid json", raw, "structural")[0] is expected


def test_json_decoder_recursion_is_a_failed_grade(monkeypatch):
    import runner.grader as grader

    def recursive_decoder(*args, **kwargs):
        raise RecursionError("synthetic parser recursion")

    monkeypatch.setattr(grader.json, "loads", recursive_decoder)
    assert grade("valid json", "{}", "structural")[0] is False


@pytest.mark.parametrize(
    "check, output",
    [
        ("provide markdown headings", "```text\n# Fake heading\n```"),
        ("provide markdown headings", "~~~text\n# Fake heading\n~~~"),
        ("provide markdown headings", "    # Indented example"),
        ("provide a markdown table", "```text\n| x | y |\n|---|---|\n```"),
        ("provide a markdown table", "~~~text\n| x | y |\n|---|---|\n~~~"),
        ("provide a markdown table", "    | x | y |\n    |---|---|"),
    ],
)
def test_structural_examples_do_not_count_as_document_structure(check, output):
    assert grade(check, output, "structural")[0] is False


@pytest.mark.parametrize(
    "check, output",
    [
        ("provide markdown headings", "# Actual heading\n"),
        ("provide a markdown table", "| x | y |\n|---|---|\n| a | b |\n"),
    ],
)
def test_actual_markdown_structure_still_passes(check, output):
    assert grade(check, output, "structural")[0] is True
