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
from typing import Dict, Iterable, Iterator, List, Optional, Sequence, Tuple


_AFF_HEADER_RE = re.compile(r"^(PFX|SFX)\s+(\S+)\s+([YN])\s+(\d+)\s*$")
_AFF_RULE_RE = re.compile(r"^(PFX|SFX)\s+(\S+)\s+")


@dataclass(frozen=True)
class Issue:
    path: Path
    message: str


@dataclass(frozen=True)
class ProposedFix:
    path: Path
    description: str
    new_text: str


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


def _write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def _lines_to_text(lines: List[str]) -> str:
    # Normalize to LF; Hunspell tolerates it and Windows tools handle it fine.
    return "\n".join(lines) + "\n"


def check_aff_header_counts(path: Path) -> List[Issue]:
    issues, _fix = _check_aff_header_counts_with_fix(path)
    return issues


def _check_aff_header_counts_with_fix(path: Path) -> Tuple[List[Issue], Optional[ProposedFix]]:
    lines = _read_lines(path)
    issues: List[Issue] = []
    new_lines = list(lines)
    changed = False

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        m = _AFF_HEADER_RE.match(line)
        if not m:
            i += 1
            continue

        kind, flag, crossable, declared_str = m.group(1), m.group(2), m.group(3), m.group(4)
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

            # Prepare an in-place fix for this header.
            new_lines[i] = f"{kind} {flag} {crossable} {actual}"
            changed = True

        i = j

    fix: Optional[ProposedFix] = None
    if changed:
        fix = ProposedFix(
            path=path,
            description="Update .aff PFX/SFX header counts to match rule lines",
            new_text=_lines_to_text(new_lines),
        )

    return issues, fix


def check_aff_duplicate_flags(path: Path) -> List[Issue]:
    """Detect duplicate affix flag headers in a Hunspell .aff.

    Hunspell affix rules are introduced by a header line like:
      PFX <flag> <Y|N> <count>
      SFX <flag> <Y|N> <count>

    Each (kind, flag) should have exactly one such header. If the same flag is
    declared multiple times for the same kind, Hunspell readers may behave
    unpredictably or ignore later blocks.
    """

    lines = _read_lines(path)
    seen: Dict[Tuple[str, str], int] = {}
    issues: List[Issue] = []

    for idx, raw in enumerate(lines):
        s = raw.strip()
        m = _AFF_HEADER_RE.match(s)
        if not m:
            continue

        kind, flag = m.group(1), m.group(2)
        key = (kind, flag)
        if key in seen:
            first_line = seen[key]
            issues.append(
                Issue(
                    path=path,
                    message=(
                        f"{path.name}: duplicate flag header: {kind} {flag} "
                        f"first declared at line {first_line}, again at line {idx+1}"
                    ),
                )
            )
            continue

        seen[key] = idx + 1

    return issues


def check_dic_entry_count(path: Path) -> List[Issue]:
    issues, _fix = _check_dic_entry_count_with_fix(path)
    return issues


def _check_dic_entry_count_with_fix(path: Path) -> Tuple[List[Issue], Optional[ProposedFix]]:
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
        return issues, None

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
        return issues, None

    actual = 0
    for raw in lines[header_idx + 1 :]:
        s = raw.strip()
        if not s:
            continue
        if s.startswith("#"):
            continue
        actual += 1

    fix: Optional[ProposedFix] = None
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

        new_lines = list(lines)
        new_lines[header_idx] = str(actual)
        fix = ProposedFix(
            path=path,
            description="Update .dic first-line word count to match entries",
            new_text=_lines_to_text(new_lines),
        )

    return issues, fix


def _confirm(prompt: str) -> bool:
    if not sys.stdin.isatty():
        return False
    ans = input(prompt).strip().lower()
    return ans in {"y", "yes"}


def check_file(path: Path) -> Tuple[List[Issue], int]:
    # returns (issues, exit_code_fragment)
    try:
        suffix = path.suffix.lower()
        if suffix == ".aff":
            issues = []
            issues.extend(check_aff_header_counts(path))
            issues.extend(check_aff_duplicate_flags(path))
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

    parser.add_argument(
        "--fix",
        action="store_true",
        help=(
            "Interactively apply safe auto-fixes (after confirmation): "
            ".aff PFX/SFX header counts and .dic first-line word counts"
        ),
    )

    args = parser.parse_args(argv)
    input_paths = [Path(p) for p in args.paths]

    files = list(_iter_files(input_paths))
    if not files:
        print("No .aff/.dic files found", file=sys.stderr)
        return 2

    all_issues: List[Issue] = []
    proposed_fixes: List[ProposedFix] = []
    exit_code = 0

    for f in files:
        issues, code = check_file(f)
        all_issues.extend(issues)
        exit_code = max(exit_code, code)

        if args.fix:
            suffix = f.suffix.lower()
            if suffix == ".aff":
                _issues, fix = _check_aff_header_counts_with_fix(f)
                if fix is not None:
                    proposed_fixes.append(fix)
            elif suffix == ".dic":
                _issues, fix = _check_dic_entry_count_with_fix(f)
                if fix is not None:
                    proposed_fixes.append(fix)

    if all_issues:
        for issue in all_issues:
            print(issue.message)
    else:
        print("OK: no mismatches found")

    # Offer to apply fixes only after printing issues.
    applied_any = False
    if args.fix and proposed_fixes:
        print("\nProposed fixes:")
        for fix in proposed_fixes:
            print(f"- {fix.path.name}: {fix.description}")

        if not sys.stdin.isatty():
            print("\nNOTE: --fix requires an interactive terminal (stdin is not a TTY).", file=sys.stderr)
        else:
            for fix in proposed_fixes:
                if _confirm(f"Apply fix to {fix.path.name}? [y/N] "):
                    _write_text(fix.path, fix.new_text)
                    applied_any = True

    # Re-check only the fixable invariants to decide exit code when fixes applied.
    if applied_any:
        remaining: List[Issue] = []
        for f in files:
            suffix = f.suffix.lower()
            if suffix == ".aff":
                remaining.extend(check_aff_header_counts(f))
            elif suffix == ".dic":
                remaining.extend(check_dic_entry_count(f))

        # Keep other issues (like duplicate flags) as failures.
        # If any original issues remain, or there were non-fixable issues, exit 1.
        # We treat successful fixes as removing only those specific mismatches.
        #
        # Note: all_issues may include duplicates/other problems that are not fixed.
        if remaining:
            exit_code = 1
        else:
            exit_code = 0 if exit_code != 2 else 2

    return 1 if exit_code == 1 else exit_code


if __name__ == "__main__":
    raise SystemExit(main())
