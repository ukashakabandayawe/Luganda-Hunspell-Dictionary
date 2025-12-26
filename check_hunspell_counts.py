"""Hunspell sanity checker.

Checks:
- .aff: PFX/SFX header counts match the number of rule lines in each block.
- .dic: first-line word count matches the number of entries that follow.

Usage examples:
  python check_hunspell_counts.py New.aff New.dic
  python check_hunspell_counts.py .

Exit codes:
  0 - all checks passed
  1 - one or more mismatches found
  2 - invalid usage / unreadable file
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
import re
from typing import Iterable, Iterator, List, Optional, Sequence, Tuple


_AFF_HEADER_RE = re.compile(r"^(PFX|SFX)\s+(\S+)\s+([YN])\s+(\d+)\s*$")
_AFF_RULE_RE = re.compile(r"^(PFX|SFX)\s+(\S+)\s+")


@dataclass(frozen=True)
class Issue:
    path: Path
    message: str


def _iter_files(paths: Sequence[Path]) -> Iterator[Path]:
    for p in paths:
        if p.is_dir():
            yield from (x for x in sorted(p.rglob("*.aff")) if x.is_file())
            yield from (x for x in sorted(p.rglob("*.dic")) if x.is_file())
        else:
            yield p


def _read_lines(path: Path) -> List[str]:
    # Hunspell files are typically UTF-8; be resilient to odd characters.
    return path.read_text(encoding="utf-8", errors="replace").splitlines()


def check_aff_header_counts(path: Path) -> List[Issue]:
    lines = _read_lines(path)
    issues: List[Issue] = []

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        m = _AFF_HEADER_RE.match(line)
        if not m:
            i += 1
            continue

        kind, flag, _crossable, declared_str = m.group(1), m.group(2), m.group(3), m.group(4)
        declared = int(declared_str)

        actual = 0
        j = i + 1
        while j < len(lines):
            s = lines[j].strip()
            if not s or s.startswith("#"):
                j += 1
                continue

            # Stop at the next affix header.
            if _AFF_HEADER_RE.match(s):
                break

            mr = _AFF_RULE_RE.match(s)
            if not mr:
                # Any other directive (e.g., SET, TRY, FLAG) ends this block.
                break

            rk, rf = mr.group(1), mr.group(2)
            if rk != kind or rf != flag:
                break

            actual += 1
            j += 1

        if actual != declared:
            issues.append(
                Issue(
                    path=path,
                    message=(
                        f"{path.name}: header mismatch at line {i+1}: "
                        f"{kind} {flag} declares {declared} but has {actual} rule line(s)"
                    ),
                )
            )

        i = j

    return issues


def check_dic_entry_count(path: Path) -> List[Issue]:
    lines = _read_lines(path)
    issues: List[Issue] = []

    # Find the header line (first non-empty, non-comment line)
    header_idx: Optional[int] = None
    for idx, raw in enumerate(lines):
        s = raw.strip()
        if not s:
            continue
        if s.startswith("#"):
            continue
        header_idx = idx
        break

    if header_idx is None:
        issues.append(Issue(path=path, message=f"{path.name}: empty .dic file"))
        return issues

    header_text = lines[header_idx].strip().lstrip("\ufeff")
    try:
        declared = int(header_text)
    except ValueError:
        issues.append(
            Issue(
                path=path,
                message=(
                    f"{path.name}: first non-comment line (line {header_idx+1}) "
                    f"is not an integer word count: {lines[header_idx]!r}"
                ),
            )
        )
        return issues

    actual = 0
    for raw in lines[header_idx + 1 :]:
        s = raw.strip()
        if not s:
            continue
        if s.startswith("#"):
            continue
        actual += 1

    if actual != declared:
        issues.append(
            Issue(
                path=path,
                message=(
                    f"{path.name}: word count mismatch: header says {declared} "
                    f"but counted {actual} entr(ies)"
                ),
            )
        )

    return issues


def check_file(path: Path) -> Tuple[List[Issue], int]:
    # returns (issues, exit_code_fragment)
    try:
        suffix = path.suffix.lower()
        if suffix == ".aff":
            issues = check_aff_header_counts(path)
            return issues, 1 if issues else 0
        if suffix == ".dic":
            issues = check_dic_entry_count(path)
            return issues, 1 if issues else 0

        return [], 0
    except OSError as e:
        return [Issue(path=path, message=f"{path.name}: could not read file: {e}")], 2


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Check Hunspell .aff/.dic header counts")
    parser.add_argument(
        "paths",
        nargs="*",
        default=["."],
        help="Files or directories to scan (default: current directory)",
    )

    args = parser.parse_args(argv)
    input_paths = [Path(p) for p in args.paths]

    files = list(_iter_files(input_paths))
    if not files:
        print("No .aff/.dic files found", file=sys.stderr)
        return 2

    all_issues: List[Issue] = []
    exit_code = 0

    for f in files:
        issues, code = check_file(f)
        all_issues.extend(issues)
        exit_code = max(exit_code, code)

    if all_issues:
        for issue in all_issues:
            print(issue.message)
    else:
        print("OK: no mismatches found")

    return 1 if exit_code == 1 else exit_code


if __name__ == "__main__":
    raise SystemExit(main())
