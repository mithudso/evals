#!/usr/bin/env python3
"""Aggregate benchmark exports without mixing their output provenance.

Identical JSON records count once. Distinct records remain separate runs even
when they name the same skill. Replay rates describe supplied responses; they do
not authenticate how those responses were produced.
"""

import argparse
import json
import math
import os
import sys
from pathlib import Path

if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from runner.config import BENCHMARK_PASS_RATE_MIN, BENCHMARK_WARNING_RATE_MIN

GROUP_LABELS = {
    "replay": "Replay of provided responses",
    "dry-run": "Dry runs: expectations only, no skill execution",
    "legacy": "Legacy records: provenance unknown",
}


def _validated_record(data, path: Path) -> dict:
    """Validate one export and derive its rate from assertion counters."""
    if not isinstance(data, dict):
        raise ValueError(f"{path.name}: benchmark record must be an object")
    name = data.get("skill_name", path.stem.removesuffix("-benchmark"))
    if not isinstance(name, str) or not name.strip():
        raise ValueError(f"{path.name}: skill_name must be a nonempty string")
    record = dict(data, skill_name=name)
    for field in ("total_evals", "total_assertions", "passed_assertions"):
        value = record.get(field)
        if type(value) is not int or value < 0:
            raise ValueError(f"{path.name}: {field} must be a nonnegative integer")
    if record["passed_assertions"] > record["total_assertions"]:
        raise ValueError(f"{path.name}: passed_assertions exceeds total_assertions")
    duration = record.get("duration_seconds", 0.0)
    try:
        valid_duration = (
            isinstance(duration, (int, float))
            and not isinstance(duration, bool)
            and math.isfinite(duration)
            and duration >= 0
        )
    except OverflowError:
        valid_duration = False
    if not valid_duration:
        raise ValueError(f"{path.name}: duration_seconds must be finite and nonnegative")
    record["duration_seconds"] = duration
    record["pass_rate_percent"] = (
        100 * record["passed_assertions"] / record["total_assertions"]
        if record["total_assertions"]
        else 0.0
    )
    return record


def _provenance(record: dict) -> str:
    if record.get("mode") == "replay" and record.get("output_source") == "provided-output":
        return "replay"
    if record.get("mode") == "dry-run":
        return "dry-run"
    return "legacy"


def _markdown_cell(value: str) -> str:
    """Keep untrusted names inside one Markdown table cell."""
    value = " ".join(value.splitlines())
    value = value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    for delimiter in ("\\", "|", "`", "[", "]", "(", ")"):
        value = value.replace(delimiter, "\\" + delimiter)
    return value


def _group_summary(records: list[dict]) -> dict:
    total = sum(record["total_assertions"] for record in records)
    passed = sum(record["passed_assertions"] for record in records)
    return {
        "records": len(records),
        "unique_skills": len({record["skill_name"] for record in records}),
        "total_evals": sum(record["total_evals"] for record in records),
        "total_assertions": total,
        "passed_assertions": passed,
        "pass_rate_percent": 100 * passed / total if total else 0.0,
    }


def _report_destination(directory: Path, sources: list[Path], output_md: str | None) -> Path | None:
    """Reject output paths that could overwrite or become an input export."""
    if not output_md:
        return None
    requested = Path(os.path.abspath(output_md))
    resolved = requested.resolve()
    for candidate in (requested, resolved):
        if candidate.is_relative_to(directory) and candidate.name.endswith("-benchmark.json"):
            raise ValueError("Output report must not use a benchmark export filename in results")
    for source in sources:
        if resolved == source.resolve() or (resolved.exists() and resolved.samefile(source)):
            raise ValueError("Output report must not overwrite or alias a source benchmark export")
    return resolved


def aggregate_results(results_dir: str, output_md: str | None = None) -> dict:
    """Print and optionally save deterministic Markdown; return report metadata.

    Raises ValueError for malformed exports and OSError for inaccessible paths.
    Historical exports are never modified.
    """
    directory = Path(results_dir).resolve()
    if not directory.is_dir():
        raise ValueError(f"{results_dir}: results directory does not exist")
    files = sorted(directory.rglob("*-benchmark.json"))
    output = _report_destination(directory, files, output_md)
    grouped = {name: [] for name in GROUP_LABELS}
    seen = set()
    unique_names = set()
    for path in files:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (ValueError, UnicodeError, RecursionError):
            raise ValueError(f"{path.name}: benchmark file is not valid UTF-8 JSON") from None
        record = _validated_record(data, path)
        try:
            identity = json.dumps(record, sort_keys=True, ensure_ascii=True, allow_nan=False)
        except (ValueError, RecursionError):
            raise ValueError(
                f"{path.name}: benchmark record contains invalid JSON values"
            ) from None
        if identity in seen:
            continue
        seen.add(identity)
        unique_names.add(record["skill_name"])
        grouped[_provenance(record)].append(record)

    groups = {name: _group_summary(records) for name, records in grouped.items()}
    markdown = [
        "# Skill Corpus Benchmark Exports",
        "",
        f"**Files discovered:** {len(files)} | **Distinct records:** {len(seen)} | "
        f"**Unique skill names:** {len(unique_names)} | **Duplicate exports skipped:** {len(files) - len(seen)}",
        "",
        "Replay rates grade provided responses; their model-execution origin is not authenticated. "
        "Dry-run and legacy records are excluded from replay totals.",
    ]
    for name, records in grouped.items():
        totals = groups[name]
        markdown.extend(
            [
                "",
                f"## {GROUP_LABELS[name]}",
                "",
                f"Records: {totals['records']} | Evals: {totals['total_evals']} | "
                f"Assertions: {totals['passed_assertions']}/{totals['total_assertions']} | "
                f"Pass rate: {totals['pass_rate_percent']:.1f}%",
                "",
            ]
        )
        if not records:
            markdown.append("No records in this group.")
            continue
        markdown.extend(
            [
                "| Skill Name | Evals | Assertions Passed | Pass Rate | Duration | Status |",
                "|---|---|---|---|---|---|",
            ]
        )
        for record in records:
            rate = record["pass_rate_percent"]
            if not record["total_assertions"]:
                status = "UNSCORED"
            elif name == "legacy":
                status = "UNVERIFIED"
            elif name == "dry-run":
                status = "EXPECTATION CHECK"
            else:
                status = (
                    "✅ PASS"
                    if rate >= BENCHMARK_PASS_RATE_MIN
                    else "⚠️ WARN"
                    if rate >= BENCHMARK_WARNING_RATE_MIN
                    else "❌ FAIL"
                )
            markdown.append(
                f"| {_markdown_cell(record['skill_name'])} | {record['total_evals']} | "
                f"{record['passed_assertions']}/{record['total_assertions']} | {rate:.1f}% | "
                f"{record['duration_seconds']:g}s | {status} |"
            )
    content = "\n".join(markdown) + "\n"
    print(content, end="")
    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(content, encoding="utf-8")
    return {
        "markdown": content,
        "files_discovered": len(files),
        "unique_records": len(seen),
        "duplicates_skipped": len(files) - len(seen),
        "unique_skills": len(unique_names),
        "groups": groups,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results_dir", nargs="?", default="results")
    parser.add_argument("output_md", nargs="?", help="Optional report path; omitted to print only")
    args = parser.parse_args()
    try:
        aggregate_results(args.results_dir, args.output_md)
    except (OSError, ValueError, UnicodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
