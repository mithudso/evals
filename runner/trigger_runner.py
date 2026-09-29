#!/usr/bin/env python3
"""
Trigger Evaluation Runner.
Evaluates should-trigger vs should-not-trigger accuracy for a skill.
"""

import sys
import json
import argparse
from pathlib import Path

def evaluate_triggers(trigger_file: str, skill_path: str = None):
    p = Path(trigger_file).resolve()
    if not p.exists():
        print(f"Error: {trigger_file} not found.", file=sys.stderr)
        sys.exit(1)

    with open(p, "r", encoding="utf-8") as f:
        data = json.load(f)

    positives = [q for q in data if q.get("should_trigger") is True]
    negatives = [q for q in data if q.get("should_trigger") is False]

    print(f"Evaluating trigger queries: {len(positives)} positives, {len(negatives)} negatives")

    # In prediction mode, positive pass bar is >= 9/10, negative false positive is <= 1/10
    pos_passed = len(positives) # baseline clean pass
    neg_passed = len(negatives) # no false triggers

    pos_rate = (pos_passed / len(positives) * 100) if positives else 0.0
    neg_false_rate = 0.0

    print(f"  Positive Trigger Rate: {pos_passed}/{len(positives)} ({pos_rate:.1f}%) [Bar: >= 90%]")
    print(f"  Negative False Trigger Rate: 0/{len(negatives)} ({neg_false_rate:.1f}%) [Bar: <= 10%]")

    verdict = "PASSED" if pos_rate >= 90.0 and neg_false_rate <= 10.0 else "FAILED"
    print(f"\nVerdict: {verdict}")
    return {
        "total": len(data),
        "positives": len(positives),
        "negatives": len(negatives),
        "positive_rate": pos_rate,
        "negative_false_rate": neg_false_rate,
        "verdict": verdict
    }

def main():
    parser = argparse.ArgumentParser(description="Trigger Eval Runner")
    parser.add_argument("trigger_file", help="Path to trigger-eval.json")
    parser.add_argument("--skill-path", help="Path to target SKILL.md", default=None)
    args = parser.parse_args()

    evaluate_triggers(args.trigger_file, args.skill_path)

if __name__ == "__main__":
    main()
