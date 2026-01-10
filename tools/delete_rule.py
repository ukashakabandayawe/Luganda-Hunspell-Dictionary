#!/usr/bin/env python3
"""Delete a Hunspell PFX/SFX rule block from an .aff file.

This script is designed for Hunspell .aff files that define rules like:

  PFX gg Y 684
  PFX gg 0 oku .
  ... (684 continuation lines)

or:

  SFX ko Y 1
  SFX ko 0 ko [aeiou]

It prompts for a flag (case-sensitive) and deletes matching rule block(s).
A timestamped backup of the .aff file is created next to the file.

Usage:
  python delete_rule.py
"""

from __future__ import annotations

import datetime as _dt
from pathlib import Path
from typing import List, Tuple


HEADER_KINDS = {"PFX", "SFX"}


def _is_header_line(line: str, flag: str) -> Tuple[bool, str, int]:
    """Return (is_header, kind, count)."""
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return False, "", 0

    parts = stripped.split()
    if len(parts) < 4:
        return False, "", 0

    kind, hdr_flag, _cross, count_str = parts[0], parts[1], parts[2], parts[3]
    if kind not in HEADER_KINDS:
        return False, "", 0
    if hdr_flag != flag:
        return False, "", 0

    try:
        count = int(count_str)
    except ValueError:
        return False, "", 0

    if count < 0:
        return False, "", 0

    return True, kind, count


def _find_blocks(lines: List[str], flag: str) -> List[Tuple[int, int]]:
    """Find (start, end_exclusive) for rule blocks matching `flag`."""
    blocks: List[Tuple[int, int]] = []
    i = 0
    while i < len(lines):
        is_header, kind, count = _is_header_line(lines[i], flag)
        if not is_header:
            i += 1
            continue

        start = i
        end = min(len(lines), start + 1 + count)

        # Best-effort validation: continuation lines should usually start with the same kind+flag.
        # If they don't, fall back to scanning until the next header line.
        expected_prefix = f"{kind} {flag} "
        bad_continuation = False
        for j in range(start + 1, end):
            s = lines[j].lstrip()
            if not s.startswith(expected_prefix) and s.strip() != "":
                bad_continuation = True
                break

        if bad_continuation:
            # Scan forward until the next header (PFX/SFX <something> ...)
            k = start + 1
            while k < len(lines):
                s = lines[k].strip()
                if s and not s.startswith("#"):
                    p = s.split()
                    if len(p) >= 4 and p[0] in HEADER_KINDS:
                        break
                k += 1
            end = k

        blocks.append((start, end))
        i = end

    return blocks


def _timestamp() -> str:
    return _dt.datetime.now().strftime("%Y%m%d-%H%M%S")


def main() -> int:
    # Default to repository root Luganda.aff (parent of tools/)
    default_aff = Path(__file__).resolve().parents[1] / "Luganda.aff"

    aff_input = input(f".aff path (Enter for {default_aff.name}): ").strip()
    aff_path = Path(aff_input) if aff_input else default_aff

    if not aff_path.exists():
        print(f"ERROR: File not found: {aff_path}")
        return 2

    flag = input("Flag to delete (case-sensitive): ").strip()
    if not flag:
        print("ERROR: Flag cannot be empty.")
        return 2

    raw = aff_path.read_bytes()
    # Preserve newline style when possible.
    text = raw.decode("utf-8", errors="strict")
    newline = "\r\n" if b"\r\n" in raw else "\n"

    lines = text.splitlines(keepends=True)

    blocks = _find_blocks(lines, flag)
    if not blocks:
        print(f"No PFX/SFX rule blocks found for flag '{flag}'.")
        return 0

    print(f"Found {len(blocks)} block(s) for flag '{flag}'.")
    if len(blocks) > 1:
        resp = input("Delete ALL of them? (y/N): ").strip().lower()
        if resp not in {"y", "yes"}:
            print("Aborted.")
            return 1

    backup_path = aff_path.with_name(f"{aff_path.name}.bak-{_timestamp()}")
    backup_path.write_bytes(raw)

    # Delete blocks from the end to keep indices valid.
    removed_lines = 0
    removed_blocks = 0
    for start, end in sorted(blocks, reverse=True):
        removed_lines += (end - start)
        removed_blocks += 1
        del lines[start:end]

    # Ensure the file ends with a newline.
    out = "".join(lines)
    if out and not out.endswith(("\n", "\r\n")):
        out += newline

    aff_path.write_text(out, encoding="utf-8", newline="")

    print(f"Backup written: {backup_path.name}")
    print(f"Removed {removed_blocks} block(s), {removed_lines} lines.")
    print(f"Updated: {aff_path.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
