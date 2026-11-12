#!/usr/bin/env python3
"""Archive old workflow sections without deleting history or active editor buffers."""

import argparse
import os
import re
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOGS = ("memory.md", "prompts.md")


def rotate_logs(root: Path = ROOT, max_bytes: int = 200_000, keep_sections: int = 3) -> list[str]:
    """Keep recent sections and retain the complete original inode in an archive.

    The original is moved before the replacement is published without clobbering.
    Writers with an already-open append handle continue writing into the archive.
    If another writer recreates the source path, publication refuses to overwrite it.
    """
    if max_bytes < 1 or keep_sections < 1:
        raise ValueError("max_bytes and keep_sections must be positive")
    for name in LOGS:
        if any(root.glob(f"*{name}*.sw[opx]")) or any(root.glob(f".*{name}*.sw[opx]")):
            raise ValueError(f"editor swap file is active for {name}")
    rotated = []
    for name in LOGS:
        source = root / name
        if source.is_symlink():
            raise ValueError(f"workflow log must not be a symlink: {name}")
        if not source.is_file() or source.stat().st_size <= max_bytes:
            continue
        content = source.read_text(encoding="utf-8")
        headings = list(re.finditer(r"^## (?:Prompt )?v\S+.*$", content, re.MULTILINE))
        if len(headings) <= keep_sections:
            continue
        cut = headings[keep_sections].start()
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", dir=root, delete=False
            ) as handle:
                temporary = Path(handle.name)
                handle.write(content[:cut])
                handle.flush()
                os.fsync(handle.fileno())
            temporary.chmod(source.stat().st_mode)
            if source.read_text(encoding="utf-8") != content:
                raise ValueError(
                    "workflow log changed during rotation; active edits were preserved"
                )
            if any(root.glob(f"*{name}*.sw[opx]")) or any(root.glob(f".*{name}*.sw[opx]")):
                raise ValueError(f"editor swap file became active for {name}")
            archive_dir = root / "docs/archive"
            archive_dir.mkdir(parents=True, exist_ok=True)
            descriptor, archive_name = tempfile.mkstemp(
                prefix=f"{source.stem}-", suffix=".md", dir=archive_dir
            )
            os.close(descriptor)
            archive = Path(archive_name)
            try:
                # Move the live inode, including appends after the comparison.
                # A copy followed by replace would still discard those writes.
                source.replace(archive)
            except OSError:
                archive.unlink(missing_ok=True)
                raise
            try:
                # Hard-link publication is atomic and fails if the path exists.
                os.link(temporary, source)
            except OSError as error:
                try:
                    os.link(archive, source)
                except FileExistsError:
                    pass
                raise ValueError(
                    "rotation publication refused; complete original preserved in "
                    f"docs/archive/{archive.name}"
                ) from error
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
        rotated.append(name)
    return rotated


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-bytes", type=int, default=200_000)
    parser.add_argument("--keep-sections", type=int, default=3)
    args = parser.parse_args()
    try:
        changed = rotate_logs(max_bytes=args.max_bytes, keep_sections=args.keep_sections)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    print("Rotated: " + (", ".join(changed) or "none"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
