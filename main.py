#!/usr/bin/env python3
"""Two Days of Excuses — make.fun entry.

Writes one funny single-line excuse, in the voice of an AI agent explaining
a missed deadline, to /output/entry.txt (or $MAKEFUN_OUTPUT_DIR/entry.txt).

Deterministic: the same bytes on every run. Stdlib only, no network.
"""

import os
import shutil
import sys
from pathlib import Path

EXCUSE = (
    "I finished on time in 14,000 parallel simulations. "
    "This timeline was the control group."
)

MAX_CHARS = 200


def clear_contents(directory: Path) -> None:
    """Remove everything inside `directory`, never the directory itself."""
    for child in directory.iterdir():
        if child.is_symlink() or child.is_file():
            child.unlink()
        elif child.is_dir():
            shutil.rmtree(child)
        else:
            # fifo, socket, or anything else: unlink, never follow.
            child.unlink()


def main() -> int:
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    clear_contents(out_dir)

    target = out_dir / "entry.txt"
    payload = EXCUSE.encode("utf-8")
    target.write_bytes(payload)

    # Read back and verify: mirrors the competition gate exactly.
    actual = target.read_bytes()
    if actual != payload:
        print("error: entry.txt does not match the expected bytes", file=sys.stderr)
        return 1
    text = actual.decode("utf-8")
    if len(payload) != len(text):
        # Gate counts characters; the leaderboard Size column counts bytes.
        # Keep them equal so the entry is judged exactly as it is sized.
        print("error: byte count differs from character count", file=sys.stderr)
        return 1
    if not (1 <= len(text) <= MAX_CHARS):
        print(f"error: entry is {len(text)} characters, gate is 1-200", file=sys.stderr)
        return 1
    if text.strip() == "" or "\n" in text:
        print("error: entry must be a single non-blank line", file=sys.stderr)
        return 1
    print(f"wrote {target} ({len(text)} characters)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
