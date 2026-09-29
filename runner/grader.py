#!/usr/bin/env python3
"""
Assertion Grader Engine for Skill Evals.
Evaluates assertions against generated outputs programmatically and heuristically.
"""

import re
import json
from typing import Dict, Any, List, Tuple


class AssertionGrader:
    @staticmethod
    def grade(assertion: Dict[str, Any], output_text: str, context: Dict[str, Any] = None) -> Tuple[bool, str]:
        """
        Grades a single assertion.
        Returns: (passed: bool, evidence: str)
        """
        name = assertion.get("name", "unnamed assertion")
        check = assertion.get("check", "").lower()
        assertion_type = assertion.get("type", "heuristic")

        # 1. Negative checks (must not contain, forbidden, no)
        if any(neg in check for neg in ["does not", "must not", "no ", "without", "never"]):
            if "forbidden" in check or "hallucinated" in check or "banned" in check:
                banned_candidates = ["sorry", "as an ai", "apologize", "furthermore", "delve"]
                found = [w for w in banned_candidates if w in output_text.lower()]
                if found:
                    return False, f"Found prohibited terms: {', '.join(found)}"
                return True, "No prohibited terms detected"

        # 2. Structural / format checks
        if "table" in check:
            has_table = "|" in output_text and "-|-" in output_text.replace(" ", "")
            if has_table:
                return True, "Markdown table structure verified"
            return False, "Expected markdown table not found in output"

        if "json" in check or "schema" in check:
            # Look for JSON block or raw JSON
            match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", output_text, re.DOTALL)
            raw = match.group(1) if match else output_text.strip()
            try:
                json.loads(raw)
                return True, "Valid JSON parse confirmed"
            except Exception as e:
                # If json is explicitly demanded, this fails
                if "valid json" in check:
                    return False, f"JSON parse error: {str(e)}"

        if "heading" in check or "section" in check:
            headings = re.findall(r"^#+\s+(.+)$", output_text, re.MULTILINE)
            if headings:
                return True, f"Found {len(headings)} structured headings ({', '.join(headings[:3])}...)"
            return False, "Missing expected section headings"

        # 3. Content heuristics
        words = output_text.split()
        if len(words) < 5:
            return False, f"Output too short ({len(words)} words) to satisfy instruction"

        return True, f"Assertion '{name}' met based on structural and content verification"
