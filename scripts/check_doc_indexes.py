#!/usr/bin/env python3
"""Check retrieval-index drift and local links in maintained project guidance."""

import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

try:
    from .generate_doc_indexes import OUTPUTS, ROOT, render_indexes
except ImportError:
    from generate_doc_indexes import OUTPUTS, ROOT, render_indexes


def check_indexes(root: Path = ROOT) -> list[str]:
    errors = []
    expected = render_indexes(root)
    for path in OUTPUTS:
        target = root / path
        if not target.is_file():
            errors.append(f"missing index: {path}; run make docs-index")
            continue
        content = target.read_text(encoding="utf-8")
        if path.endswith(".json"):
            try:
                data = json.loads(content)
                for card in data["files"]:
                    name = card["path"]
                    relative = Path(name)
                    if (
                        relative.is_absolute()
                        or ".." in relative.parts
                        or "\\" in name
                        or not (root / name).resolve().is_relative_to(root.resolve())
                    ):
                        errors.append(f"unsafe path in {path}: {name!r}")
                    elif not (root / name).is_file():
                        errors.append(f"dead path in {path}: {name!r}")
            except (ValueError, TypeError, KeyError):
                errors.append(f"invalid index schema: {path}")
        if content != expected[path]:
            errors.append(f"stale index: {path}; run make docs-index")
    return errors


def check_links(root: Path = ROOT) -> list[str]:
    errors = []
    sources = list((root / "docs").rglob("*.md")) + list((root / ".github").rglob("*.md"))
    sources.extend(
        root / name
        for name in ("README.md", "AGENTS.md", "CLAUDE.md", "GEMINI.md", "CONTRIBUTING.md")
    )
    for source in sources:
        if not source.is_file():
            continue
        visible_lines = []
        fence = None
        for line in source.read_text(encoding="utf-8").splitlines():
            marker = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
            if fence is None:
                if marker:
                    fence = marker.group(1)
                else:
                    visible_lines.append(line)
            elif re.fullmatch(
                r" {0,3}" + re.escape(fence[0]) + "{" + str(len(fence)) + r",}[ \t]*", line
            ):
                fence = None
        text = "\n".join(visible_lines)
        for destination in re.findall(r"(?<!!)\[[^\]]+\]\(([^)\n]+)\)", text):
            parsed = urlsplit(destination.strip("<>"))
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            target = (source.parent / unquote(parsed.path)).resolve()
            if not target.is_relative_to(root.resolve()) or not target.exists():
                errors.append(f"broken local link in {source.relative_to(root)}: {destination}")
    return errors


def main() -> int:
    try:
        errors = check_indexes() + check_links()
    except (OSError, SyntaxError, ValueError) as error:
        print(f"Documentation check failed: {type(error).__name__}", file=sys.stderr)
        return 1
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("Documentation indexes and maintained local links are current.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
