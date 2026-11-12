#!/usr/bin/env python3
"""
Audit JSON suite inputs and a documented subset of Deep Eval Optimizer checks.

Implemented checks cover A, C, D, F, G, H, I, and L. The results explicitly
identify B, E, J, and K as unimplemented rather than claiming those checks passed.
"""

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any, Dict

if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from runner.config import (
    ENTROPY_MIN_TOKENS,
    ENTROPY_RATIO_MIN,
    EXPECTED_OUTPUT_MIN_WORDS,
    FIXTURE_SIZE_LIMIT_BYTES,
    FUNCTIONAL_MIN_CASES,
    TRIGGER_HIGH_SEVERITY_BELOW,
    TRIGGER_MIN_EXAMPLES_PER_CLASS,
)
from runner.validation import validate_functional_suite, validate_trigger_suite

PASSES = {
    "Pass A": "Prompt Realism & Ecological Validity",
    "Pass B": "Discriminative Power & Baseline Contrast",
    "Pass C": "Assertion Objectivity & Verifiability",
    "Pass D": "Near-Miss & False-Positive Coverage",
    "Pass E": "Flakiness & Determinism Hygiene",
    "Pass F": "Leakage & Tautology (Answer Contamination)",
    "Pass G": "Input Fixture Integrity & Isolation",
    "Pass H": "Coverage & Boundary Distribution",
    "Pass I": "Expected Output Precision & Completeness",
    "Pass J": "Cost, Latency & Token Efficiency",
    "Pass K": "Anti-Overfitting & Train/Val Split",
    "Pass L": "Format & Schema Compliance",
}

IMPLEMENTED_PASSES = (
    "Pass A",
    "Pass C",
    "Pass D",
    "Pass F",
    "Pass G",
    "Pass H",
    "Pass I",
    "Pass L",
)


def _report(path: Path, findings: list[dict], error: str | None = None) -> dict:
    result = {
        "file": str(path),
        "total_findings": len(findings),
        "high_findings": sum(1 for finding in findings if finding["severity"] == "High"),
        "medium_findings": sum(1 for finding in findings if finding["severity"] == "Medium"),
        "low_findings": sum(1 for finding in findings if finding["severity"] == "Low"),
        "findings": findings,
        "implemented_passes": list(IMPLEMENTED_PASSES),
        "unimplemented_passes": [name for name in PASSES if name not in IMPLEMENTED_PASSES],
    }
    if error is not None:
        result["error"] = error
    return result


def _schema_finding(message: str) -> dict:
    return {
        "pass": "Pass L",
        "severity": "High",
        "finding": message,
        "recommendation": "Correct the input shape before running analytical checks.",
    }


def validate_suite(eval_file: str) -> Dict[str, Any]:
    path = Path(eval_file).resolve()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError, RecursionError):
        message = "Suite must be an existing, readable UTF-8 JSON file"
        return _report(path, [_schema_finding(message)], error=message)

    schema_errors = (
        validate_trigger_suite(data) if isinstance(data, list) else validate_functional_suite(data)
    )
    if schema_errors:
        return _report(path, [_schema_finding(error) for error in schema_errors])

    findings = []

    # Check if trigger-eval list or functional-eval dict
    is_trigger_eval = isinstance(data, list)

    if is_trigger_eval:
        # Validate trigger-evals
        positives = [q for q in data if q.get("should_trigger") is True]
        negatives = [q for q in data if q.get("should_trigger") is False]

        # Pass D: Near-miss & false-positive coverage (Trigger Calibration)
        if len(negatives) < TRIGGER_MIN_EXAMPLES_PER_CLASS:
            findings.append(
                {
                    "pass": "Pass D",
                    "severity": "High"
                    if len(negatives) < TRIGGER_HIGH_SEVERITY_BELOW
                    else "Medium",
                    "finding": f"Insufficient negative near-miss queries ({len(negatives)} found, min {TRIGGER_MIN_EXAMPLES_PER_CLASS} required for trigger calibration)",
                    "recommendation": "Add realistic near-miss queries with contrasting intent (Verb_competing + Noun_shared).",
                }
            )

        if len(positives) < TRIGGER_MIN_EXAMPLES_PER_CLASS:
            findings.append(
                {
                    "pass": "Pass H",
                    "severity": "High"
                    if len(positives) < TRIGGER_HIGH_SEVERITY_BELOW
                    else "Medium",
                    "finding": f"Insufficient positive queries ({len(positives)} found, min {TRIGGER_MIN_EXAMPLES_PER_CLASS} required)",
                    "recommendation": "Expand positive queries to cover direct, symptom, terse, and context-rich intents.",
                }
            )

        # Pass A: Realism
        robotic = [
            q["query"]
            for q in data
            if any(
                k in q.get("query", "").lower()
                for k in [
                    "please run the skill",
                    "test query",
                    "execute skill",
                    "using standard parameters",
                ]
            )
        ]
        if robotic:
            findings.append(
                {
                    "pass": "Pass A",
                    "severity": "Medium",
                    "finding": f"Robotic or synthetic prompt phrasing in {len(robotic)} queries",
                    "recommendation": "Rewrite prompts to reflect authentic, natural user phrasing and pain points.",
                }
            )

    else:
        # Validate functional evals
        skill_name = data.get("skill_name")
        evals = data.get("evals", [])

        # Pass L: Schema
        if not skill_name:
            findings.append(
                {
                    "pass": "Pass L",
                    "severity": "High",
                    "finding": "Missing top-level 'skill_name' in eval suite",
                    "recommendation": "Specify canonical skill name.",
                }
            )

        if len(evals) < FUNCTIONAL_MIN_CASES:
            findings.append(
                {
                    "pass": "Pass H",
                    "severity": "Medium",
                    "finding": f"Eval suite has only {len(evals)} test case(s); minimum {FUNCTIONAL_MIN_CASES} required",
                    "recommendation": "Add diverse test cases covering happy path, edge cases, and file transformation.",
                }
            )

        for ev in evals:
            eid = ev.get("id")
            name = ev.get("name", f"eval-{eid}")
            prompt = ev.get("prompt", "")
            expected = ev.get("expected_output", "")
            assertions = ev.get("assertions", [])

            # Pass C: Assertion objectivity & Negative Tripwires
            if not assertions:
                findings.append(
                    {
                        "pass": "Pass C",
                        "severity": "High",
                        "finding": f"Eval #{eid} '{name}' has no assertions",
                        "recommendation": "Add at least 2 objectively verifiable assertions (Structural, Schema, Deterministic, Negative Bounds).",
                    }
                )
            else:
                for a in assertions:
                    txt = a if isinstance(a, str) else a.get("check", "")
                    if any(
                        vibe in txt.lower()
                        for vibe in ["looks good", "well written", "nice", "appropriate"]
                    ):
                        findings.append(
                            {
                                "pass": "Pass C",
                                "severity": "Medium",
                                "finding": f"Subjective/vague assertion '{txt}' in eval #{eid}",
                                "recommendation": "Replace with concrete structural, schema, or negative bounds checks.",
                            }
                        )

            # Pass F: Answer leakage, N-gram priming & Saliency Entropy
            if skill_name.lower() in prompt.lower():
                findings.append(
                    {
                        "pass": "Pass F",
                        "severity": "High"
                        if "run the " + skill_name.lower() in prompt.lower()
                        else "Medium",
                        "finding": f"Prompt in eval #{eid} directly leaks skill name '{skill_name}'",
                        "recommendation": "Apply Natural User Persona Transform: describe user symptoms without naming the skill.",
                    }
                )

            # Tier-3 Saliency Entropy Audit
            words = prompt.split()
            if len(words) >= ENTROPY_MIN_TOKENS:
                import collections

                counts = collections.Counter(words)
                total = len(words)
                entropy = -sum((c / total) * math.log(c / total) for c in counts.values())
                max_entropy = math.log(len(counts))
                if max_entropy == 0 or (entropy / max_entropy) < ENTROPY_RATIO_MIN:
                    findings.append(
                        {
                            "pass": "Pass F",
                            "severity": "Medium",
                            "finding": f"Low token entropy in eval #{eid} prompt ({entropy:.2f}/{max_entropy:.2f}), suggesting high token concentration or copy-pasted syntax",
                            "recommendation": "Rewrite prompt with realistic natural user phrasing to ensure high token dispersion.",
                        }
                    )

            # Pass G: Fixture size and isolation
            files = ev.get("files", [])
            for fpath in files:
                fp = Path(fpath)
                if not fp.is_absolute():
                    fp = path.parent / fpath
                if not fp.is_file():
                    findings.append(
                        {
                            "pass": "Pass G",
                            "severity": "Medium",
                            "finding": f"Fixture '{fpath}' in eval #{eid} is missing or is not a regular file",
                            "recommendation": "Supply a readable fixture file, relative to the suite directory or with an absolute path.",
                        }
                    )
                    continue
                try:
                    fixture_size = fp.stat().st_size
                except OSError:
                    findings.append(
                        {
                            "pass": "Pass G",
                            "severity": "Medium",
                            "finding": f"Fixture '{fpath}' in eval #{eid} is inaccessible",
                            "recommendation": "Check fixture access before running the suite.",
                        }
                    )
                    continue
                if fixture_size > FIXTURE_SIZE_LIMIT_BYTES:
                    findings.append(
                        {
                            "pass": "Pass G",
                            "severity": "Medium",
                            "finding": f"Fixture '{fpath}' in eval #{eid} exceeds {FIXTURE_SIZE_LIMIT_BYTES} bytes ({fixture_size} bytes)",
                            "recommendation": "Minify fixture dataset to a minimal reproducible representation below the configured size limit.",
                        }
                    )

            # Pass I: Expected output precision
            if not expected or len(expected.split()) < EXPECTED_OUTPUT_MIN_WORDS:
                findings.append(
                    {
                        "pass": "Pass I",
                        "severity": "Medium",
                        "finding": f"Underspecified expected output in eval #{eid}",
                        "recommendation": "Detail the exact required artifact sections, shapes, or behavior.",
                    }
                )

    return _report(path, findings)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("eval_file", help="Path to a functional or trigger JSON suite")
    args = parser.parse_args()
    res = validate_suite(args.eval_file)
    print(json.dumps(res, indent=2))
    return 1 if res.get("error") or res["total_findings"] else 0


if __name__ == "__main__":
    sys.exit(main())
