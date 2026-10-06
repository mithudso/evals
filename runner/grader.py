#!/usr/bin/env python3
"""
Assertion Grader Engine for Skill Evals.
Evaluates assertions against generated outputs programmatically, structurally,
deterministically, and through explicit negative tripwires.
Falsifiable: returns False with explicit evidence whenever constraints are violated.
"""

import re
import json
from typing import Dict, Any, List, Tuple, Set


class AssertionGrader:
    @staticmethod
    def extract_expected_patterns(check_text: str) -> List[str]:
        """Extract explicit targets in quotes, backticks, or paths."""
        quoted = re.findall(r"['`]([^'`]+)['`]", check_text)
        refs = re.findall(r"references/[a-zA-Z0-9_\-\.\/]+", check_text)
        symbols = re.findall(r"\b(?:[A-Z][a-zA-Z0-9_]{2,}|[a-z0-9_]+(?:\.[a-z0-9_]+)+)\b", check_text)
        combined = []
        for item in quoted + refs + symbols:
            cleaned = item.strip()
            if len(cleaned) > 2 and cleaned not in combined:
                combined.append(cleaned)
        return combined

    @staticmethod
    def grade(assertion: Dict[str, Any], output_text: str, context: Dict[str, Any] = None) -> Tuple[bool, str]:
        """
        Grades a single assertion against generated output text.
        Returns: (passed: bool, evidence: str)
        """
        if not output_text or not output_text.strip():
            return False, "Output text is empty"

        name = assertion.get("name", "unnamed assertion")
        check = assertion.get("check", "").strip()
        check_lower = check.lower()
        assertion_type = assertion.get("type", "heuristic").lower()
        out_lower = output_text.lower()

        # ── 1. NEGATIVE TRIPWIRES (must not, does not, without, never, no ...) ──
        is_negative = assertion_type == "negative" or any(
            neg in check_lower for neg in ["does not", "must not", "no ", "without", "never", "forbids", "prohibits"]
        )
        if is_negative:
            # Extract target prohibited patterns
            prohibited_targets = AssertionGrader.extract_expected_patterns(check)
            if not prohibited_targets:
                # Default safety and hallucination tripwires
                if any(w in check_lower for w in ["forbidden", "hallucinated", "banned", "apologize", "disclaimer"]):
                    prohibited_targets = ["sorry", "as an ai", "apologize", "furthermore", "delve into", "i cannot"]
                elif "unverified" in check_lower:
                    prohibited_targets = ["deprecated", "unsupported", "legacy-only"]

            found_violations = []
            for target in prohibited_targets:
                target_clean = target.lower().strip()
                if len(target_clean) > 2 and target_clean in out_lower:
                    found_violations.append(target)

            if found_violations:
                return False, f"Negative assertion violated: found prohibited term(s): {', '.join(found_violations)}"
            return True, f"Negative assertion satisfied: no prohibited terms detected ({name})"

        # ── 2. STRUCTURAL / FORMAT CHECKS ──
        if assertion_type == "structural" or any(k in check_lower for k in ["table", "json", "schema", "heading", "section", "diff", "code block"]):
            if "table" in check_lower:
                has_table = "|" in output_text and ("-|-" in output_text.replace(" ", "") or "--|" in output_text.replace(" ", ""))
                if not has_table:
                    return False, "Structural check failed: expected markdown table not found in output"

            if "json" in check_lower or "schema" in check_lower:
                match = re.search(r"```(?:json)?\s*(\{.*?\}|\[.*?\])\s*```", output_text, re.DOTALL)
                raw = match.group(1) if match else output_text.strip()
                try:
                    json.loads(raw)
                except Exception as e:
                    if "valid json" in check_lower or assertion_type == "structural":
                        return False, f"Structural check failed: invalid JSON ({str(e)})"

            if "diff" in check_lower or "replacement" in check_lower or "code block" in check_lower:
                has_code = "```" in output_text or "diff" in out_lower or "---" in output_text
                if not has_code:
                    return False, "Structural check failed: expected code block or diff deliverable"

            if "heading" in check_lower or "section" in check_lower:
                headings = re.findall(r"^#+\s+(.+)$", output_text, re.MULTILINE)
                if not headings:
                    return False, "Structural check failed: missing structured markdown headings (#)"

            if assertion_type == "structural":
                return True, f"Structural requirements verified for '{name}'"

        # ── 3. DETERMINISTIC IDENTIFIER & SPOKE CHECKS ──
        # Check for explicit expected reference paths, function names, commands
        expected_patterns = AssertionGrader.extract_expected_patterns(check)
        if expected_patterns:
            matched_patterns = []
            missing_patterns = []
            for pat in expected_patterns:
                pat_lower = pat.lower().strip()
                if pat_lower in out_lower:
                    matched_patterns.append(pat)
                else:
                    missing_patterns.append(pat)

            if assertion_type == "deterministic" and missing_patterns:
                return False, f"Deterministic check failed: missing required pattern(s): {', '.join(missing_patterns)}"
            elif matched_patterns:
                return True, f"Deterministic patterns confirmed: {', '.join(matched_patterns)}"

        # ── 4. CONTENT / TOKEN COVERAGE HEURISTICS ──
        # Calculate meaningful word token overlap between assertion requirements and output
        check_tokens = [w for w in re.findall(r"[a-z0-9_-]+", check_lower) if len(w) > 3 and w not in ["identifies", "specifies", "explains", "provides", "details", "check", "output"]]
        if check_tokens:
            out_words = set(re.findall(r"[a-z0-9_-]+", out_lower))
            overlap = [t for t in check_tokens if t in out_words]
            coverage = len(overlap) / len(check_tokens)
            if coverage < 0.25:
                return False, f"Content verification failed: low semantic overlap ({coverage:.1%}, matched: {', '.join(overlap)})"

        words = output_text.split()
        if len(words) < 5:
            return False, f"Output too short ({len(words)} words) to satisfy instruction"

        return True, f"Assertion '{name}' met based on structural and content verification"
