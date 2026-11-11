#!/usr/bin/env python3
"""Grade literal and structural checks; label token overlap as a heuristic.

This module never executes code or validates an unspecified JSON Schema. An
unsupported check fails with evidence instead of being treated as successful.
"""

import json
import re
from collections.abc import Mapping
from typing import Any

from markdown_it import MarkdownIt

from runner.config import CONTENT_OVERLAP_MIN, MIN_OUTPUT_WORDS
from runner.validation import SUPPORTED_ASSERTION_TYPES

_QUOTED = re.compile(r"(`[^`\n]+`|'[^'\n]+'|\"[^\"\n]+\")")
_REFERENCE = re.compile(r"(?:references/[A-Za-z0-9_./-]+|\b[A-Za-z0-9_]+(?:\.[A-Za-z0-9_]+)+\b)")
_NEGATIVE = re.compile(
    r"\b(?:not|never|without|forbids|prohibits|no|cannot|can['’]t|don['’]t|doesn['’]t|mustn['’]t)\b"
)
_CODE_FENCE = re.compile(r"^```([^`\n]*)\n(.*?)^```[ \t]*$", re.MULTILINE | re.DOTALL)
_MARKDOWN = MarkdownIt("commonmark").enable("table")
_HUNK_HEADER = re.compile(r"@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@(?: .*)?")
_DIFF_METADATA = (
    "diff --git ",
    "index ",
    "new file mode ",
    "deleted file mode ",
    "old mode ",
    "new mode ",
    "similarity index ",
    "dissimilarity index ",
    "rename from ",
    "rename to ",
    "copy from ",
    "copy to ",
)


def _targets(check: str) -> list[str]:
    quoted = [match.group()[1:-1].strip() for match in _QUOTED.finditer(check)]
    # Explicit literals take precedence over guessed filenames. This prevents a
    # filename inside a literal from becoming a second, contradictory requirement.
    values = quoted if quoted else _REFERENCE.findall(check)
    return list(dict.fromkeys(value for value in values if value))


def _reject_json_constant(value: str) -> None:
    raise ValueError("non-finite JSON constant")


def _complete_unified_diff(text: str) -> bool:
    """Check text-file hunk headers and exact old/new line counts without execution.

    This accepts optional Git metadata and multiple files or hunks. It does not
    prove that a patch applies to a particular checkout, or support binary diffs.
    """
    lines = text.strip("\n").splitlines()
    index = 0
    files = 0
    any_change = False
    while index < len(lines):
        while index < len(lines) and lines[index].startswith(_DIFF_METADATA):
            index += 1
        if index + 1 >= len(lines) or not lines[index].startswith("--- "):
            return False
        if not lines[index][4:].strip() or not lines[index + 1].startswith("+++ "):
            return False
        if not lines[index + 1][4:].strip():
            return False
        index += 2
        hunks = 0
        while index < len(lines) and (header := _HUNK_HEADER.fullmatch(lines[index])):
            try:
                old_start = int(header[1])
                old_expected = int(header[2]) if header[2] is not None else 1
                new_start = int(header[3])
                new_expected = int(header[4]) if header[4] is not None else 1
            except ValueError:
                return False
            if (old_expected and old_start == 0) or (new_expected and new_start == 0):
                return False
            if old_expected == new_expected == 0:
                return False
            index += 1
            old_seen = new_seen = 0
            hunk_changed = False
            previous_was_content = False
            while old_seen < old_expected or new_seen < new_expected:
                if index >= len(lines):
                    return False
                line = lines[index]
                if line == "\\ No newline at end of file":
                    if not previous_was_content:
                        return False
                    previous_was_content = False
                    index += 1
                    continue
                if not line or line[0] not in " +-":
                    return False
                if line[0] in " -":
                    old_seen += 1
                if line[0] in " +":
                    new_seen += 1
                hunk_changed |= line[0] in "+-"
                if old_seen > old_expected or new_seen > new_expected:
                    return False
                previous_was_content = True
                index += 1
            if index < len(lines) and lines[index] == "\\ No newline at end of file":
                if not previous_was_content:
                    return False
                index += 1
            if not hunk_changed:
                return False
            any_change = True
            hunks += 1
        if hunks == 0:
            return False
        files += 1
    return files > 0 and any_change


def _structural(check: str, output: str) -> tuple[bool, str]:
    if _NEGATIVE.search(_QUOTED.sub("", check)):
        return (
            False,
            "Unsupported mixed structural check: separate positive and negative requirements",
        )
    recognized = False
    fences = list(_CODE_FENCE.finditer(output))
    markdown_types = (
        {token.type for token in _MARKDOWN.parse(output)}
        if re.search(r"\b(?:table|headings?|sections?)\b", check)
        else set()
    )
    if re.search(r"\b(?:json|schema)\b", check):
        recognized = True
        if re.search(r"\bschema\b", check):
            return False, "Unsupported schema check: JSON parsing does not validate a JSON Schema"
        json_blocks = [m.group(2) for m in fences if m.group(1).strip().lower() in {"", "json"}]
        raw = json_blocks[0] if json_blocks else output.strip()
        try:
            json.loads(raw, parse_constant=_reject_json_constant)
        except (ValueError, TypeError, RecursionError):
            return False, "Structural check failed: invalid JSON"
    if re.search(r"\btable\b", check):
        recognized = True
        if "table_open" not in markdown_types:
            return False, "Structural check failed: expected markdown table"
    if re.search(r"\b(?:diff|replacement|code block)\b", check):
        recognized = True
        wants_code = re.search(r"\b(?:replacement|code block)\b", check)
        wants_diff = re.search(r"\bdiff\b", check)
        has_code = any(m.group(2).strip() for m in fences)
        has_diff = _complete_unified_diff(output) or any(
            m.group(1).strip().lower() == "diff" and _complete_unified_diff(m.group(2))
            for m in fences
        )
        if wants_code and wants_diff and re.search(r"\bor\b", check):
            valid = has_code or has_diff
        else:
            valid = (not wants_code or has_code) and (not wants_diff or has_diff)
        if not valid:
            return False, "Structural check failed: expected a complete code block or unified diff"
    if re.search(r"\b(?:headings?|sections?)\b", check):
        recognized = True
        if "heading_open" not in markdown_types:
            return False, "Structural check failed: expected markdown headings"
    if not recognized:
        return False, "Unsupported structural check: no recognized criterion"
    return (
        True,
        "Structural criteria satisfied; this does not prove execution or semantic correctness",
    )


class AssertionGrader:
    @staticmethod
    def extract_expected_patterns(check_text: str) -> list[str]:
        """Return ordered explicit literals, or unquoted reference paths/symbols.

        Single quotes, double quotes and backticks preserve short nonempty
        literals. General English capitalized words are not inferred targets.
        """
        return _targets(check_text) if isinstance(check_text, str) else []

    @staticmethod
    def grade(
        assertion: Any, output_text: str, context: Mapping[str, Any] | None = None
    ) -> tuple[bool, str]:
        """Return ``(passed, evidence)`` without executing an assertion or output.

        ``context`` is reserved for callers; it does not authorize execution.
        ``content``, ``behavioral`` and ``heuristic`` use token overlap only.
        """
        if not isinstance(assertion, Mapping):
            return False, "Invalid assertion: expected an object"
        check = assertion.get("check")
        kind = assertion.get("type", "heuristic")
        if not isinstance(check, str) or not check.strip():
            return False, "Invalid assertion: check must be a nonempty string"
        if not isinstance(kind, str) or kind.strip().lower() not in SUPPORTED_ASSERTION_TYPES:
            return False, "Invalid assertion: unsupported type"
        if not isinstance(output_text, str) or not output_text.strip():
            return False, "Output text is empty or is not a string"

        kind = kind.strip().lower()
        check = check.strip()
        check_lower = check.lower()
        unquoted_check = _QUOTED.sub("", check_lower)
        output_lower = output_text.lower()
        targets = _targets(check)
        if kind == "schema":
            return False, "Unsupported schema check: no JSON Schema evaluator is configured"
        if kind == "negative":
            if not targets:
                return False, "Unsupported negative check: provide explicit prohibited literals"
            violations = [target for target in targets if target.lower() in output_lower]
            if violations:
                return False, "Negative check failed: prohibited literal(s): " + ", ".join(
                    violations
                )
            return True, "Negative literal check satisfied"
        if kind == "deterministic":
            if not targets:
                return False, "Unsupported deterministic check: provide explicit required literals"
            if _NEGATIVE.search(unquoted_check):
                return False, "Unsupported mixed check: separate required and prohibited literals"
            missing = [target for target in targets if target.lower() not in output_lower]
            if missing:
                return (
                    False,
                    "Deterministic check failed: missing required literal(s): "
                    + ", ".join(missing),
                )
            return True, "Deterministic literal check satisfied"
        if kind == "structural":
            return _structural(check_lower, output_text)

        # Legacy heuristic assertions may infer a structural or negative check,
        # but explicit assertion types above always control their own dispatch.
        if kind == "heuristic" and _NEGATIVE.search(unquoted_check):
            return AssertionGrader.grade({"check": check, "type": "negative"}, output_text)
        if kind == "heuristic" and re.search(
            r"\b(?:table|json|schema|headings?|sections?|diff|code block)\b", unquoted_check
        ):
            passed, evidence = _structural(check_lower, output_text)
            return passed, "Heuristic dispatch: " + evidence

        check_tokens = [
            word
            for word in re.findall(r"[a-z0-9_-]+", check_lower)
            if len(word) > 3
            and word
            not in {"identifies", "specifies", "explains", "provides", "details", "check", "output"}
        ]
        if not check_tokens:
            return False, "Unsupported heuristic check: no meaningful tokens"
        output_words = set(re.findall(r"[a-z0-9_-]+", output_lower))
        coverage = sum(token in output_words for token in check_tokens) / len(check_tokens)
        if coverage < CONTENT_OVERLAP_MIN:
            return False, f"Heuristic token overlap below threshold ({coverage:.1%})"
        if len(output_text.split()) < MIN_OUTPUT_WORDS:
            return False, "Heuristic check failed: output is too short"
        return (
            True,
            f"Heuristic token overlap satisfied ({coverage:.1%}); no semantic or execution proof",
        )
