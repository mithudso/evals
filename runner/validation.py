"""Pure validation shared by evaluation runners and suite auditing.

Each function returns field-addressed errors without reading files, executing
checks, mutating its argument, or including input contents in error messages.
"""

import re
from collections.abc import Mapping
from typing import Any

SUPPORTED_ASSERTION_TYPES = frozenset(
    {
        "heuristic",
        "content",
        "behavioral",
        "negative",
        "structural",
        "deterministic",
        "schema",
    }
)
_SAFE_SKILL_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]*\Z")


def is_safe_skill_name(value: Any) -> bool:
    """Return whether a value can safely form one benchmark filename component."""
    return isinstance(value, str) and _SAFE_SKILL_NAME.fullmatch(value) is not None


def _nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _assertion_errors(assertion: Any, location: str) -> list[str]:
    if isinstance(assertion, str):
        return [] if assertion.strip() else [f"{location}: must be a nonempty check string"]
    if not isinstance(assertion, Mapping):
        return [f"{location}: must be a check string or object"]
    errors = []
    if not _nonempty_string(assertion.get("check")):
        errors.append(f"{location}.check: must be a nonempty string")
    kind = assertion.get("type", "heuristic")
    if not isinstance(kind, str) or kind.strip().lower() not in SUPPORTED_ASSERTION_TYPES:
        errors.append(f"{location}.type: must name a supported assertion type")
    if "name" in assertion and not isinstance(assertion["name"], str):
        errors.append(f"{location}.name: must be a string")
    return errors


def validate_functional_suite(data: Any) -> list[str]:
    """Validate functional case shapes, safe skill names and unambiguous IDs.

    Numeric IDs and their equivalent string IDs share an output-map key. Reject
    duplicates across those representations so replay never selects ambiguously.
    Supported assertion types describe dispatch; schema assertions still require
    an evaluator and do not become executable merely by passing validation.
    """
    if not isinstance(data, Mapping):
        return ["suite: must be an object"]
    errors = []
    if not is_safe_skill_name(data.get("skill_name")):
        errors.append(
            "skill_name: must be a safe ASCII filename slug (letters, digits, underscore or hyphen)"
        )
    evals = data.get("evals")
    if not isinstance(evals, list) or not evals:
        errors.append("evals: must be a nonempty list")
        return errors
    seen_ids = set()
    for index, item in enumerate(evals):
        location = f"evals[{index}]"
        if not isinstance(item, Mapping):
            errors.append(f"{location}: must be an object")
            continue
        case_id = item.get("id")
        valid_id = type(case_id) is int or _nonempty_string(case_id)
        if not valid_id:
            errors.append(f"{location}.id: must be an integer or nonempty string (not boolean)")
        elif str(case_id) in seen_ids:
            errors.append(f"{location}.id: duplicates an earlier output-map key")
        else:
            seen_ids.add(str(case_id))
        if not _nonempty_string(item.get("prompt")):
            errors.append(f"{location}.prompt: must be a nonempty string")
        for field in ("expected_output", "actual_output", "name"):
            if field in item and not isinstance(item[field], str):
                errors.append(f"{location}.{field}: must be a string")
        files = item.get("files", [])
        if not isinstance(files, list):
            errors.append(f"{location}.files: must be a list of path strings")
        else:
            for file_index, file_path in enumerate(files):
                if not _nonempty_string(file_path):
                    errors.append(f"{location}.files[{file_index}]: must be a nonempty path string")
        assertions = item.get("assertions")
        if not isinstance(assertions, list) or not assertions:
            errors.append(f"{location}.assertions: must be a nonempty list")
        else:
            for assertion_index, assertion in enumerate(assertions):
                errors.extend(
                    _assertion_errors(assertion, f"{location}.assertions[{assertion_index}]")
                )
    return errors


def validate_trigger_suite(data: Any) -> list[str]:
    """Validate trigger rows and require both positive and negative queries."""
    if not isinstance(data, list) or not data:
        return ["suite: must be a nonempty list of trigger objects"]
    errors = []
    classes = set()
    for index, item in enumerate(data):
        location = f"[{index}]"
        if not isinstance(item, Mapping):
            errors.append(f"{location}: must be a trigger object")
            continue
        if not _nonempty_string(item.get("query")):
            errors.append(f"{location}.query: must be a nonempty string")
        label = item.get("should_trigger")
        if type(label) is not bool:
            errors.append(f"{location}.should_trigger: must be a boolean")
        else:
            classes.add(label)
    if True not in classes:
        errors.append("suite: must include a positive should_trigger=true query")
    if False not in classes:
        errors.append("suite: must include a negative should_trigger=false query")
    return errors
