#!/usr/bin/env python3
"""Grade supplied functional responses or explicitly check expectations.

Replay accepts observed responses from each case's ``actual_output`` or an
ID-to-response mapping. Dry runs grade expectations only. No live adapter is
implemented, and neither mode manufactures a response or proves model execution.
"""

import argparse
import json
import logging
import sys
import tempfile
import time
from collections.abc import Mapping
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from runner.grader import AssertionGrader
from runner.validation import validate_functional_suite

logger = logging.getLogger(__name__)


def _json_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON object key")
        result[key] = value
    return result


def _invalid(message: str, code: str = "invalid_eval_input") -> None:
    logger.error("Functional evaluation rejected", extra={"error_code": code})
    raise ValueError(message)


def _load_json(path: Path, label: str):
    try:
        with path.open(encoding="utf-8") as handle:
            return json.load(handle, object_pairs_hook=_json_object)
    except (OSError, UnicodeError, ValueError, RecursionError) as error:
        logger.error(
            "Evaluation input could not be loaded", extra={"error_code": "eval_input_read_failed"}
        )
        raise ValueError(f"Unable to read {label} as UTF-8 JSON") from error


def _prepare_outputs(evals: list, dry_run: bool, outputs: Mapping | None) -> list[str]:
    if dry_run and outputs is not None:
        _invalid("dry-run cannot be combined with an outputs mapping")
    if outputs is not None and not isinstance(outputs, Mapping):
        _invalid("outputs must be an ID-to-response object")
    normalized = {}
    for key, value in (outputs or {}).items():
        if not (type(key) is int or isinstance(key, str)) or isinstance(key, bool):
            _invalid("outputs keys must be case IDs")
        if str(key) in normalized:
            _invalid("outputs contains duplicate case ID keys")
        if not isinstance(value, str):
            _invalid("outputs values must be response strings")
        normalized[str(key)] = value
    if set(normalized) - {str(item["id"]) for item in evals}:
        _invalid("outputs contains an unknown case ID")

    prepared = []
    for index, item in enumerate(evals):
        if dry_run:
            if "expected_output" not in item:
                _invalid(f"evals[{index}].expected_output: required for dry-run")
            response = item["expected_output"]
        elif str(item["id"]) in normalized:
            response = normalized[str(item["id"])]
        elif "actual_output" in item:
            response = item["actual_output"]
        else:
            _invalid(f"evals[{index}].actual_output: provide an observed output or outputs mapping")
        prepared.append(response)
    return prepared


def _summary_path(output_dir: str | None, skill_name: str) -> Path | None:
    if output_dir is None:
        return None
    directory = Path(output_dir).resolve()
    destination = directory / f"{skill_name}-benchmark.json"
    if destination.is_symlink() or destination.resolve().parent != directory:
        _invalid("Unsafe output benchmark path", "unsafe_output_path")
    if directory.exists() and not directory.is_dir():
        _invalid("output directory must be a directory")
    return destination


def _preserve_input_paths(destination: Path | None, inputs: tuple[Path, ...]) -> None:
    if destination is None:
        return
    for source in inputs:
        resolved_source = source.resolve()
        if destination.resolve() == resolved_source or (
            destination.exists()
            and resolved_source.exists()
            and destination.samefile(resolved_source)
        ):
            _invalid("Unsafe output benchmark path: aliases an input file", "unsafe_output_path")


def run_suite(
    eval_file: str,
    output_dir: str | None = None,
    dry_run: bool = False,
    execute_live: bool = False,
    outputs: Mapping | None = None,
    *,
    _protected_inputs: tuple[Path, ...] = (),
):
    """Grade cases and return a provenance-labelled benchmark summary.

    The first four parameters retain the previous positional API. Invalid input
    raises ``ValueError`` before any output directory or benchmark is written.
    Failed assertions remain in the returned summary and cause CLI failure.
    """
    if execute_live:
        _invalid(
            "Live execution is not implemented; provide observed outputs for replay",
            "live_unsupported",
        )
    eval_path = Path(eval_file).resolve()
    data = _load_json(eval_path, "evaluation suite")
    errors = validate_functional_suite(data)
    if errors:
        _invalid("Invalid evaluation suite: " + "; ".join(errors))
    skill_name = data["skill_name"]
    evals = data["evals"]
    responses = _prepare_outputs(evals, dry_run, outputs)
    destination = _summary_path(output_dir, skill_name)
    _preserve_input_paths(destination, (eval_path, *_protected_inputs))
    mode = "dry-run" if dry_run else "replay"
    print(f"Grading {mode} for: {skill_name} ({len(evals)} cases; no live execution)")
    logger.info("Functional evaluation started", extra={"mode": mode, "case_count": len(evals)})

    start_all = time.perf_counter()
    results = []
    total_passed = 0
    total_assertions = 0
    for item, response in zip(evals, responses):
        start_case = time.perf_counter()
        assertion_results = []
        for assertion in item["assertions"]:
            if isinstance(assertion, str):
                assertion = {"name": assertion, "check": assertion}
            passed, evidence = AssertionGrader.grade(assertion, response)
            total_assertions += 1
            total_passed += int(passed)
            assertion_results.append(
                {
                    "name": assertion.get("name", "unnamed assertion"),
                    "passed": passed,
                    "evidence": evidence,
                }
            )
        duration = round(time.perf_counter() - start_case, 3)
        passed = all(result["passed"] for result in assertion_results)
        results.append(
            {
                "id": item["id"],
                "name": item.get("name", f"eval-{item['id']}"),
                "passed": passed,
                "duration_s": duration,
                "assertions": assertion_results,
            }
        )
        print(
            f"  [{'PASS' if passed else 'FAIL'}] Eval #{item['id']}: {len(assertion_results)} checks ({duration}s)"
        )
        for index, assertion_result in enumerate(assertion_results, 1):
            if not assertion_result["passed"]:
                print(f"    Assertion {index}: {assertion_result['evidence']}")

    total_duration = round(time.perf_counter() - start_all, 3)
    pass_rate = round(total_passed / total_assertions * 100, 1)
    summary = {
        "skill_name": skill_name,
        "mode": mode,
        "output_source": "expected_output" if dry_run else "provided-output",
        "total_evals": len(evals),
        "total_assertions": total_assertions,
        "passed_assertions": total_passed,
        "pass_rate_percent": pass_rate,
        "duration_seconds": total_duration,
        "eval_results": results,
    }
    if destination is not None:
        temporary = None
        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=destination.parent,
                prefix=".benchmark-",
                delete=False,
            ) as handle:
                temporary = Path(handle.name)
                json.dump(summary, handle, indent=2)
                handle.write("\n")
            temporary.replace(destination)
        except OSError:
            logger.error(
                "Benchmark output write failed", extra={"error_code": "benchmark_write_failed"}
            )
            raise
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
        print(f"Wrote benchmark summary to: {destination}")
    logger.info(
        "Functional evaluation completed", extra={"mode": mode, "assertion_count": total_assertions}
    )
    print(
        f"Final: {total_passed}/{total_assertions} assertions passed ({pass_rate}%) in {total_duration}s"
    )
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Grade supplied skill responses; no live execution"
    )
    parser.add_argument("eval_file", help="Path to a functional suite JSON file")
    parser.add_argument(
        "--output-dir", "-o", default=None, help="Directory for the benchmark summary"
    )
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument(
        "--dry-run", action="store_true", help="Grade expected_output only; not execution"
    )
    modes.add_argument(
        "--live", action="store_true", help="Unsupported: a live adapter is not implemented"
    )
    parser.add_argument(
        "--outputs", help="UTF-8 JSON object mapping case IDs to observed response strings"
    )
    args = parser.parse_args(argv)
    try:
        outputs = _load_json(Path(args.outputs), "outputs mapping") if args.outputs else None
        if args.outputs and not isinstance(outputs, Mapping):
            _invalid("outputs must be an ID-to-response object")
        result = run_suite(
            args.eval_file,
            args.output_dir,
            args.dry_run,
            args.live,
            outputs,
            _protected_inputs=(Path(args.outputs),) if args.outputs else (),
        )
    except (OSError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2
    return 0 if result["passed_assertions"] == result["total_assertions"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
