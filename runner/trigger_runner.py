#!/usr/bin/env python3
"""
Trigger Evaluation Runner.
Evaluates should-trigger vs should-not-trigger accuracy for a skill
using genuine dual-track evaluation:
1. Hybrid scoring: cosine similarity (via Ollama embeddings) + BM25 token overlap.
2. Explicit boundary checks: checks match against TRIGGER clauses and penalty for SKIP clauses.
"""

import sys
import os
import re
import json
import math
import argparse
import urllib.request
from pathlib import Path
from collections import Counter
from typing import Dict, Any, List, Tuple, Set

# Universal stop words
STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are",
    "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but",
    "by", "can", "did", "do", "does", "doing", "don", "down", "during", "each", "few", "for",
    "from", "further", "had", "has", "have", "having", "he", "her", "here", "hers", "herself",
    "him", "himself", "his", "how", "i", "if", "in", "into", "is", "it", "its", "itself", "just",
    "me", "more", "most", "my", "myself", "no", "nor", "not", "now", "of", "off", "on", "once",
    "only", "or", "other", "our", "ours", "ourselves", "out", "over", "own", "s", "same", "she",
    "should", "so", "some", "such", "t", "than", "that", "the", "their", "theirs", "them",
    "themselves", "then", "there", "these", "they", "this", "those", "through", "to", "too",
    "under", "until", "up", "very", "was", "we", "were", "what", "when", "where", "which",
    "while", "who", "whom", "why", "will", "with", "you", "your", "yours", "yourself"
}

def tokenize(text: str) -> List[str]:
    return [t for t in re.findall(r'[a-z0-9_-]+', text.lower()) if len(t) > 1 and t not in STOPWORDS]

def get_embedding(text: str, host: str = "http://localhost:11434", model: str = "qwen3-embedding:4b") -> List[float]:
    """Retrieve text embedding from local Ollama instance with fallback to None."""
    try:
        data = json.dumps({"model": model, "prompt": text}).encode("utf-8")
        req = urllib.request.Request(f"{host}/api/embeddings", data=data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
            return payload.get("embedding", [])
    except Exception:
        return []

def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    dot = sum(a * b for a, b in zip(v1, v2))
    norm1 = math.sqrt(sum(a * a for a, b in zip(v1, v2)))
    norm2 = math.sqrt(sum(b * b for a, b in zip(v1, v2)))
    if norm1 == 0.0 or norm2 == 0.0:
        return 0.0
    return dot / (norm1 * norm2)

def extract_skill_profile(skill_path: str) -> Dict[str, Any]:
    """Extract frontmatter, triggers, skips, and full text from SKILL.md."""
    p = Path(skill_path).resolve()
    if not p.exists():
        return {}

    with open(p, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    triggers = []
    skips = []
    description = ""
    name = p.parent.name

    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            import yaml
            try:
                fm = yaml.safe_load(parts[1]) or {}
                name = fm.get("name", name)
                description = fm.get("description", "")
            except Exception:
                pass

    # Extract TRIGGER clause
    trig_m = re.search(r'TRIGGER:\s*(.*?)(?:SKIP:|$)', description, re.DOTALL)
    if trig_m:
        raw_trig = trig_m.group(1).strip()
        triggers = [t.strip(' "\',.;') for t in re.split(r'[,;]|\band\b', raw_trig) if len(t.strip()) > 2]

    # Extract SKIP clause
    skip_m = re.search(r'SKIP:\s*(.*?)(?:$)', description, re.DOTALL)
    if skip_m:
        raw_skip = skip_m.group(1).strip()
        skips = [s.strip(' "\',.;') for s in re.split(r'[;]|\band\b', raw_skip) if len(s.strip()) > 2]

    return {
        "name": name,
        "description": description,
        "triggers": triggers,
        "skips": skips,
        "full_text": content,
        "token_bag": set(tokenize(f"{name} {description} {' '.join(triggers)}"))
    }

def score_query_match(query: str, profile: Dict[str, Any], skill_emb: List[float] = None) -> Tuple[float, str]:
    """
    Score a user query against the skill profile.
    Returns: (score between 0.0 and 1.0, reasoning string)
    """
    q_tokens = tokenize(query)
    if not q_tokens:
        return 0.0, "Empty tokenized query"

    skill_bag = profile.get("token_bag", set())
    if not skill_bag:
        return 0.0, "Empty skill profile"

    # 1. Token overlap / Jaccard-style coverage
    overlap = [t for t in q_tokens if t in skill_bag]
    coverage = len(overlap) / len(q_tokens)

    # 2. Trigger phrase exact or fuzzy inclusion
    trigger_hit = 0.0
    q_lower = query.lower()
    for tr in profile.get("triggers", []):
        tr_clean = tr.lower().strip()
        if tr_clean and tr_clean in q_lower:
            trigger_hit = max(trigger_hit, 0.45)
        else:
            # Check partial trigger match
            tr_toks = set(tokenize(tr_clean))
            if tr_toks and tr_toks.issubset(set(q_tokens)):
                trigger_hit = max(trigger_hit, 0.35)

    # 3. Skip clause penalty (explicit negative tripwires)
    skip_penalty = 0.0
    for sk in profile.get("skips", []):
        sk_clean = sk.lower().split("->")[0].split("→")[0].strip()
        sk_toks = set(tokenize(sk_clean))
        if sk_toks and len(sk_toks.intersection(set(q_tokens))) >= max(1, len(sk_toks) // 2):
            skip_penalty = max(skip_penalty, 0.35)

    # 4. Semantic embedding similarity (if server available)
    cos_sim = 0.0
    if skill_emb:
        q_emb = get_embedding(query)
        if q_emb:
            cos_sim = cosine_similarity(skill_emb, q_emb)

    # Combined hybrid score calculation
    if cos_sim > 0.0:
        # Hybrid blend: 60% semantic + 40% lexical/trigger bonus - skip penalty
        raw_score = (0.60 * cos_sim) + (0.25 * coverage) + trigger_hit - skip_penalty
    else:
        # Lexical fallback: coverage + trigger bonus - skip penalty
        raw_score = (0.60 * coverage) + trigger_hit - skip_penalty

    final_score = max(0.0, min(1.0, raw_score))
    evidence = f"score={final_score:.3f} (cov={coverage:.2f}, trig={trigger_hit:.2f}, cos={cos_sim:.2f}, skip_pen={skip_penalty:.2f})"
    return final_score, evidence

def evaluate_triggers(trigger_file: str, skill_path: str = None, threshold: float = 0.28) -> Dict[str, Any]:
    p = Path(trigger_file).resolve()
    if not p.exists():
        print(f"Error: {trigger_file} not found.", file=sys.stderr)
        sys.exit(1)

    with open(p, "r", encoding="utf-8") as f:
        data = json.load(f)

    # If skill_path not specified, infer from trigger_file location
    if not skill_path:
        candidate = p.parent.parent / "SKILL.md"
        if candidate.exists():
            skill_path = str(candidate)

    if not skill_path or not Path(skill_path).exists():
        print(f"Error: Target SKILL.md not found at '{skill_path}'", file=sys.stderr)
        sys.exit(1)

    profile = extract_skill_profile(skill_path)
    # Pre-embed skill description if semantic server available
    skill_emb = get_embedding(f"{profile.get('name', '')}: {profile.get('description', '')}")

    positives = [q for q in data if q.get("should_trigger") is True]
    negatives = [q for q in data if q.get("should_trigger") is False]

    print(f"Evaluating trigger queries for '{profile.get('name')}': {len(positives)} positives, {len(negatives)} negatives")

    pos_passed = 0
    pos_details = []
    for item in positives:
        query = item.get("query", "")
        score, evidence = score_query_match(query, profile, skill_emb)
        passed = score >= threshold
        if passed:
            pos_passed += 1
        pos_details.append({"query": query, "passed": passed, "score": score, "evidence": evidence})

    neg_passed = 0
    neg_details = []
    for item in negatives:
        query = item.get("query", "")
        score, evidence = score_query_match(query, profile, skill_emb)
        # For negative trigger, passed means it did NOT trigger (score < threshold)
        passed = score < threshold
        if passed:
            neg_passed += 1
        neg_details.append({"query": query, "passed": passed, "score": score, "evidence": evidence})

    pos_rate = (pos_passed / len(positives) * 100) if positives else 0.0
    neg_false_rate = ((len(negatives) - neg_passed) / len(negatives) * 100) if negatives else 0.0

    print(f"  Positive Trigger Rate: {pos_passed}/{len(positives)} ({pos_rate:.1f}%) [Bar: >= 90%]")
    print(f"  Negative False Trigger Rate: {len(negatives) - neg_passed}/{len(negatives)} ({neg_false_rate:.1f}%) [Bar: <= 10%]")

    verdict = "PASSED" if pos_rate >= 90.0 and neg_false_rate <= 10.0 else "FAILED"
    print(f"\nVerdict: {verdict}")

    if verdict == "FAILED":
        print("\nFailures:")
        for pd in pos_details:
            if not pd["passed"]:
                print(f"  [MISSED POSITIVE] (score={pd['score']:.3f} < {threshold}): '{pd['query']}'")
        for nd in neg_details:
            if not nd["passed"]:
                print(f"  [FALSE TRIGGER] (score={nd['score']:.3f} >= {threshold}): '{nd['query']}'")

    return {
        "skill": profile.get("name"),
        "total": len(data),
        "positives": len(positives),
        "negatives": len(negatives),
        "positive_rate": pos_rate,
        "negative_false_rate": neg_false_rate,
        "verdict": verdict,
        "positive_details": pos_details,
        "negative_details": neg_details
    }

def main():
    parser = argparse.ArgumentParser(description="Trigger Eval Runner (Falsifiable Multi-Track)")
    parser.add_argument("trigger_file", help="Path to trigger-eval.json")
    parser.add_argument("--skill-path", help="Path to target SKILL.md", default=None)
    parser.add_argument("--threshold", type=float, default=0.28, help="Classification decision threshold (default: 0.28)")
    args = parser.parse_args()

    res = evaluate_triggers(args.trigger_file, args.skill_path, args.threshold)
    if res.get("verdict") != "PASSED":
        sys.exit(1)

if __name__ == "__main__":
    main()
