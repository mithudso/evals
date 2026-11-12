#!/usr/bin/env python3
"""
Trigger Evaluation Runner.
Evaluates should-trigger vs should-not-trigger accuracy for a skill
using optional hybrid scoring:
1. Cosine similarity (via Ollama embeddings) + plain token overlap.
2. Explicit boundary checks: checks match against TRIGGER clauses and penalty for SKIP clauses.
"""

import argparse
import json
import logging
import math
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ollama_client import OllamaClient, OllamaPool, cosine

from runner.config import (
    EMBEDDING_MODEL,
    EMBEDDING_RETRIES,
    EMBEDDING_TIMEOUT_SECONDS,
    EXACT_TRIGGER_BONUS,
    FALSE_POSITIVE_RATE_MAX,
    HYBRID_LEXICAL_WEIGHT,
    LEXICAL_WEIGHT,
    OLLAMA_HOST,
    POSITIVE_RATE_MIN,
    SEMANTIC_WEIGHT,
    SKIP_PENALTY,
    TOKEN_TRIGGER_BONUS,
    TRIGGER_THRESHOLD,
)
from runner.validation import validate_trigger_suite

LOGGER = logging.getLogger(__name__)

# Universal stop words
STOPWORDS = {
    "a",
    "about",
    "above",
    "after",
    "again",
    "against",
    "all",
    "am",
    "an",
    "and",
    "any",
    "are",
    "as",
    "at",
    "be",
    "because",
    "been",
    "before",
    "being",
    "below",
    "between",
    "both",
    "but",
    "by",
    "can",
    "did",
    "do",
    "does",
    "doing",
    "don",
    "down",
    "during",
    "each",
    "few",
    "for",
    "from",
    "further",
    "had",
    "has",
    "have",
    "having",
    "he",
    "her",
    "here",
    "hers",
    "herself",
    "him",
    "himself",
    "his",
    "how",
    "i",
    "if",
    "in",
    "into",
    "is",
    "it",
    "its",
    "itself",
    "just",
    "me",
    "more",
    "most",
    "my",
    "myself",
    "no",
    "nor",
    "not",
    "now",
    "of",
    "off",
    "on",
    "once",
    "only",
    "or",
    "other",
    "our",
    "ours",
    "ourselves",
    "out",
    "over",
    "own",
    "s",
    "same",
    "she",
    "should",
    "so",
    "some",
    "such",
    "t",
    "than",
    "that",
    "the",
    "their",
    "theirs",
    "them",
    "themselves",
    "then",
    "there",
    "these",
    "they",
    "this",
    "those",
    "through",
    "to",
    "too",
    "under",
    "until",
    "up",
    "very",
    "was",
    "we",
    "were",
    "what",
    "when",
    "where",
    "which",
    "while",
    "who",
    "whom",
    "why",
    "will",
    "with",
    "you",
    "your",
    "yours",
    "yourself",
}


def tokenize(text: str) -> List[str]:
    return [
        t for t in re.findall(r"[a-z0-9_-]+", text.lower()) if len(t) > 1 and t not in STOPWORDS
    ]


def _valid_embedding(vector) -> bool:
    """Accept finite, nonzero numeric vectors; booleans are not coordinates."""
    if not isinstance(vector, (list, tuple)) or not vector:
        return False
    try:
        if not all(
            isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)
            for value in vector
        ):
            return False
        norm = math.hypot(*vector)
        return math.isfinite(norm) and norm > 0
    except (TypeError, ValueError, OverflowError):
        return False


def get_embedding(text: str, host: str = OLLAMA_HOST, model: str = EMBEDDING_MODEL) -> List[float]:
    """Retrieve text embedding from local Ollama (via the shared ollama-client); [] on any failure.

    The model stays pinned to qwen3-embedding:4b (the library default is mxbai-embed-large and its
    vectors are not comparable). 3s timeout, no retry rounds, as before. Uses /api/embed instead of
    the legacy /api/embeddings: same model, same direction (the new endpoint L2-normalises, which
    cosine similarity ignores).
    """
    try:
        LOGGER.debug("Embedding request started")
        client = OllamaClient(
            OllamaPool(host, timeout=EMBEDDING_TIMEOUT_SECONDS, retries=EMBEDDING_RETRIES),
            embed_model=model,
        )
        vector = client.embed(text, model=model)[0]
        if not _valid_embedding(vector):
            LOGGER.warning("Embedding unavailable; lexical scoring fallback required")
            return []
        LOGGER.debug("Embedding request completed")
        return vector
    except Exception:
        # Errors may contain input text or credentials from a configured endpoint.
        LOGGER.warning("Embedding unavailable; lexical scoring fallback required")
        return []


def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    return cosine(v1, v2)


def extract_skill_profile(skill_path: str) -> Dict[str, Any]:
    """Extract frontmatter, triggers, skips, and full text from SKILL.md."""
    p = Path(skill_path).resolve()
    if not p.is_file():
        raise ValueError("Target SKILL.md must be an existing file")
    content = p.read_text(encoding="utf-8")
    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("SKILL.md requires YAML frontmatter")
    closing = next((index for index in range(1, len(lines)) if lines[index].strip() == "---"), None)
    if closing is None:
        raise ValueError("SKILL.md frontmatter is not closed")
    import yaml

    try:
        fm = yaml.safe_load("\n".join(lines[1:closing]))
    except yaml.YAMLError:
        raise ValueError("SKILL.md frontmatter is invalid YAML") from None
    if not isinstance(fm, dict):
        raise ValueError("SKILL.md frontmatter must be a mapping")
    name = fm.get("name", p.parent.name)
    description = fm.get("description")
    if not isinstance(name, str) or not name.strip():
        raise ValueError("SKILL.md name must be a nonempty string")
    if not isinstance(description, str) or not description.strip():
        raise ValueError("SKILL.md description must be a nonempty string")

    triggers = []
    skips = []

    # Extract TRIGGER clause
    trig_m = re.search(r"TRIGGER:\s*(.*?)(?:SKIP:|$)", description, re.DOTALL)
    if trig_m:
        raw_trig = trig_m.group(1).strip()
        triggers = [
            t.strip(" \"',.;") for t in re.split(r"[,;]|\band\b", raw_trig) if len(t.strip()) > 2
        ]

    # Extract SKIP clause
    skip_m = re.search(r"SKIP:\s*(.*?)(?:$)", description, re.DOTALL)
    if skip_m:
        raw_skip = skip_m.group(1).strip()
        skips = [
            s.strip(" \"',.;") for s in re.split(r"[;]|\band\b", raw_skip) if len(s.strip()) > 2
        ]

    return {
        "name": name,
        "description": description,
        "triggers": triggers,
        "skips": skips,
        "full_text": content,
        "token_bag": set(tokenize(f"{name} {description} {' '.join(triggers)}")),
    }


def score_query_match(
    query: str, profile: Dict[str, Any], skill_emb: List[float] = None, lexical_only: bool = False
) -> Tuple[float, str]:
    """
    Score a user query against the skill profile.
    Returns: (score between 0.0 and 1.0, reasoning string)
    """
    q_tokens = tokenize(query)
    if not q_tokens:
        mode = "lexical-only" if lexical_only else "lexical-fallback"
        return 0.0, f"mode={mode} Empty tokenized query"

    query_tokens = set(q_tokens)

    skill_bag = profile.get("token_bag", set())
    if not skill_bag:
        mode = "lexical-only" if lexical_only else "lexical-fallback"
        return 0.0, f"mode={mode} Empty skill profile"

    # 1. Token overlap / Jaccard-style coverage
    overlap = [t for t in q_tokens if t in skill_bag]
    coverage = len(overlap) / len(q_tokens)

    # 2. Trigger phrase exact or fuzzy inclusion
    trigger_hit = 0.0
    q_lower = query.lower()
    for tr in profile.get("triggers", []):
        tr_clean = tr.lower().strip()
        if tr_clean and tr_clean in q_lower:
            trigger_hit = max(trigger_hit, EXACT_TRIGGER_BONUS)
        else:
            # Check partial trigger match
            tr_toks = set(tokenize(tr_clean))
            if tr_toks and tr_toks.issubset(query_tokens):
                trigger_hit = max(trigger_hit, TOKEN_TRIGGER_BONUS)

    # 3. Skip clause penalty (explicit negative tripwires)
    skip_penalty = 0.0
    for sk in profile.get("skips", []):
        sk_clean = sk.lower().split("->")[0].split("→")[0].strip()
        sk_toks = set(tokenize(sk_clean))
        if sk_toks and len(sk_toks.intersection(query_tokens)) >= max(1, len(sk_toks) // 2):
            skip_penalty = max(skip_penalty, SKIP_PENALTY)

    # 4. Semantic embedding similarity (if server available)
    cos_sim = 0.0
    hybrid = False
    if not lexical_only and _valid_embedding(skill_emb):
        q_emb = get_embedding(query)
        if _valid_embedding(q_emb) and len(q_emb) == len(skill_emb):
            cos_sim = cosine_similarity(skill_emb, q_emb)
            hybrid = math.isfinite(cos_sim)
        if not hybrid:
            cos_sim = 0.0
            LOGGER.warning("Compatible embeddings unavailable; using lexical scoring fallback")

    # Combined hybrid score calculation
    if hybrid:
        # Hybrid blend: 60% semantic + 40% lexical/trigger bonus - skip penalty
        raw_score = (
            (SEMANTIC_WEIGHT * cos_sim)
            + (HYBRID_LEXICAL_WEIGHT * coverage)
            + trigger_hit
            - skip_penalty
        )
    else:
        # Lexical fallback: coverage + trigger bonus - skip penalty
        raw_score = (LEXICAL_WEIGHT * coverage) + trigger_hit - skip_penalty

    final_score = max(0.0, min(1.0, raw_score))
    mode = "hybrid" if hybrid else "lexical-only" if lexical_only else "lexical-fallback"
    evidence = f"mode={mode} score={final_score:.3f} (cov={coverage:.2f}, trig={trigger_hit:.2f}, cos={cos_sim:.2f}, skip_pen={skip_penalty:.2f})"
    return final_score, evidence


def evaluate_triggers(
    trigger_file: str,
    skill_path: str = None,
    threshold: float = TRIGGER_THRESHOLD,
    lexical_only: bool = False,
) -> Dict[str, Any]:
    p = Path(trigger_file).resolve()
    if not p.is_file():
        raise ValueError("Trigger suite must be an existing JSON file")
    # Check the range first so oversized integer API inputs cannot overflow
    # the conversion performed by math.isfinite.
    if (
        not isinstance(threshold, (int, float))
        or isinstance(threshold, bool)
        or not 0.0 <= threshold <= 1.0
        or not math.isfinite(threshold)
    ):
        raise ValueError("Threshold must be a finite number between 0 and 1")

    try:
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (ValueError, UnicodeError, RecursionError):
        raise ValueError(f"{p.name}: trigger suite is not valid UTF-8 JSON") from None
    errors = validate_trigger_suite(data)
    if errors:
        raise ValueError("Invalid trigger suite: " + "; ".join(errors))

    # If skill_path not specified, infer from trigger_file location
    if not skill_path:
        candidate = p.parent.parent / "SKILL.md"
        if candidate.exists():
            skill_path = str(candidate)

    if not skill_path:
        raise ValueError("Target SKILL.md not found; supply --skill-path")

    profile = extract_skill_profile(skill_path)
    # Pre-embed skill description if semantic server available
    skill_emb = (
        [] if lexical_only else get_embedding(f"{profile['name']}: {profile['description']}")
    )

    positives = [q for q in data if q.get("should_trigger") is True]
    negatives = [q for q in data if q.get("should_trigger") is False]

    print(
        f"Evaluating trigger queries for '{profile.get('name')}': {len(positives)} positives, {len(negatives)} negatives"
    )

    pos_passed = 0
    pos_details = []
    for item in positives:
        query = item.get("query", "")
        score, evidence = score_query_match(query, profile, skill_emb, lexical_only=lexical_only)
        passed = score >= threshold
        if passed:
            pos_passed += 1
        pos_details.append({"query": query, "passed": passed, "score": score, "evidence": evidence})

    neg_passed = 0
    neg_details = []
    for item in negatives:
        query = item.get("query", "")
        score, evidence = score_query_match(query, profile, skill_emb, lexical_only=lexical_only)
        # For negative trigger, passed means it did NOT trigger (score < threshold)
        passed = score < threshold
        if passed:
            neg_passed += 1
        neg_details.append({"query": query, "passed": passed, "score": score, "evidence": evidence})

    pos_rate = (pos_passed / len(positives) * 100) if positives else 0.0
    neg_false_rate = ((len(negatives) - neg_passed) / len(negatives) * 100) if negatives else 0.0

    modes = {
        detail["evidence"].split()[0].removeprefix("mode=") for detail in pos_details + neg_details
    }
    scoring_mode = next(iter(modes)) if len(modes) == 1 else "mixed"
    print(f"  Scoring mode: {scoring_mode}")
    print(
        f"  Positive Trigger Rate: {pos_passed}/{len(positives)} ({pos_rate:.1f}%) [Bar: >= {POSITIVE_RATE_MIN:g}%]"
    )
    print(
        f"  Negative False Trigger Rate: {len(negatives) - neg_passed}/{len(negatives)} ({neg_false_rate:.1f}%) [Bar: <= {FALSE_POSITIVE_RATE_MAX:g}%]"
    )

    verdict = (
        "PASSED"
        if pos_rate >= POSITIVE_RATE_MIN and neg_false_rate <= FALSE_POSITIVE_RATE_MAX
        else "FAILED"
    )
    print(f"\nVerdict: {verdict}")

    if verdict == "FAILED":
        print("\nFailures:")
        for pd in pos_details:
            if not pd["passed"]:
                print(
                    f"  [MISSED POSITIVE] (score={pd['score']:.3f} < {threshold}): '{pd['query']}'"
                )
        for nd in neg_details:
            if not nd["passed"]:
                print(
                    f"  [FALSE TRIGGER] (score={nd['score']:.3f} >= {threshold}): '{nd['query']}'"
                )

    return {
        "skill": profile.get("name"),
        "total": len(data),
        "positives": len(positives),
        "negatives": len(negatives),
        "positive_rate": pos_rate,
        "negative_false_rate": neg_false_rate,
        "scoring_mode": scoring_mode,
        "embedding_model": None if lexical_only else EMBEDDING_MODEL,
        "verdict": verdict,
        "positive_details": pos_details,
        "negative_details": neg_details,
    }


def main():
    parser = argparse.ArgumentParser(description="Trigger Eval Runner (Falsifiable Multi-Track)")
    parser.add_argument("trigger_file", help="Path to trigger-eval.json")
    parser.add_argument("--skill-path", help="Path to target SKILL.md", default=None)
    parser.add_argument(
        "--threshold",
        type=float,
        default=TRIGGER_THRESHOLD,
        help=f"Classification decision threshold (default: {TRIGGER_THRESHOLD})",
    )
    parser.add_argument(
        "--lexical-only",
        action="store_true",
        help="Disable embedding requests for an offline token-overlap evaluation",
    )
    args = parser.parse_args()

    try:
        res = evaluate_triggers(
            args.trigger_file, args.skill_path, args.threshold, lexical_only=args.lexical_only
        )
    except (OSError, ValueError, UnicodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    if res.get("verdict") != "PASSED":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
