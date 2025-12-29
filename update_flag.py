#!/usr/bin/env python
"""Update/rename Hunspell flags across Luganda.aff and Luganda.dic.

Default behavior (safe): renames a single-character flag to another single-character
flag in:
  - Luganda.aff: PFX/SFX rule identifiers (2nd token)
  - Luganda.dic: word flag lists after '/'

If you provide a 2-character new flag while the aff file is still in the default
"character flag" mode, the script will offer a one-shot conversion to `FLAG long`:
  - Inserts `FLAG long` into Luganda.aff
  - Converts ALL existing 1-char flags to 2-char flags (by default: doubled, e.g. E -> EE)
  - Replaces the chosen old flag with your chosen 2-char new flag

This avoids the dangerous intermediate state where 2-character flags would be
interpreted as two separate 1-character flags.

Run:
  python update_flag.py

Optional:
  python update_flag.py --old E --new AB
  python update_flag.py --old E --new F   # simple rename within char-flag mode

"""

from __future__ import annotations

import argparse
import datetime as _dt
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional, Tuple


AFF_NAME = "Luganda.aff"
DIC_NAME = "Luganda.dic"


@dataclass(frozen=True)
class HunspellFlagMode:
    # hunspell supports: char(default), long, num, UTF-8 (still char semantics)
    kind: str  # "char" | "long" | "num"


def _detect_newline(text: str) -> str:
    # Prefer CRLF if present, else LF.
    if "\r\n" in text:
        return "\r\n"
    return "\n"


def _read_text(path: Path) -> Tuple[str, str]:
    data = path.read_text(encoding="utf-8")
    return data, _detect_newline(data)


def _write_text(path: Path, text: str, newline: str) -> None:
    # Ensure newline consistency
    if newline != "\n":
        text = text.replace("\n", newline)
    path.write_text(text, encoding="utf-8", newline="")


def _timestamp() -> str:
    return _dt.datetime.now().strftime("%Y%m%d-%H%M%S")


def _backup(path: Path) -> Path:
    backup_path = path.with_suffix(path.suffix + f".bak-{_timestamp()}")
    backup_path.write_text(path.read_text(encoding="utf-8"), encoding="utf-8", newline="")
    return backup_path


def _detect_flag_mode(aff_text: str) -> HunspellFlagMode:
    for raw_line in aff_text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.upper().startswith("FLAG "):
            value = line.split(None, 1)[1].strip().lower()
            if value.startswith("long"):
                return HunspellFlagMode("long")
            if value.startswith("num"):
                return HunspellFlagMode("num")
            # Anything else: treat as char semantics.
            return HunspellFlagMode("char")
    return HunspellFlagMode("char")


def _validate_flag_for_mode(flag: str, mode: HunspellFlagMode) -> None:
    if mode.kind == "char":
        if len(flag) != 1:
            raise ValueError(
                f"In character-flag mode, flags must be exactly 1 character. Got {flag!r}."
            )
    elif mode.kind == "long":
        if len(flag) != 2:
            raise ValueError(f"In FLAG long mode, flags must be exactly 2 characters. Got {flag!r}.")
    elif mode.kind == "num":
        if not flag.isdigit():
            raise ValueError(f"In FLAG num mode, flags must be digits. Got {flag!r}.")
    else:
        raise ValueError(f"Unsupported flag mode: {mode.kind!r}")


def _split_dic_head_and_tail(line: str) -> Tuple[str, str]:
    """Return (head_token, rest_including_leading_whitespace).

    Hunspell allows extra morphological fields after whitespace.
    We only rewrite the first token (word[/flags]).
    """
    if not line:
        return "", ""
    if line[0].isspace():
        # Unusual; treat whole line as tail
        return "", line
    for i, ch in enumerate(line):
        if ch.isspace():
            return line[:i], line[i:]
    return line, ""


def _update_dic_flags_char_mode(dic_text: str, old_flag: str, new_flag: str) -> Tuple[str, int]:
    out_lines: list[str] = []
    changed = 0

    lines = dic_text.splitlines()
    for idx, raw in enumerate(lines):
        line = raw
        if idx == 0:
            # Preserve count line verbatim
            out_lines.append(line)
            continue
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            out_lines.append(line)
            continue

        head, tail = _split_dic_head_and_tail(line)
        if "/" not in head:
            out_lines.append(line)
            continue

        word, flags = head.split("/", 1)
        new_flags = "".join(new_flag if ch == old_flag else ch for ch in flags)
        if new_flags != flags:
            changed += 1
            head = f"{word}/{new_flags}"
            out_lines.append(head + tail)
        else:
            out_lines.append(line)

    return "\n".join(out_lines), changed


def _update_aff_pfx_sfx_tokens(aff_text: str, replace_flag_fn) -> Tuple[str, int]:
    """Rewrite only PFX/SFX rule identifiers (2nd token) using replace_flag_fn(token)->token."""
    out_lines: list[str] = []
    changed = 0

    for raw in aff_text.splitlines():
        line = raw
        stripped = line.lstrip()
        if not stripped or stripped.startswith("#"):
            out_lines.append(line)
            continue

        # Keep inline comments as-is by only rewriting the leading part.
        comment = ""
        code = line
        if "#" in line:
            # Hunspell treats # as comment-start; keep simplest split.
            code, comment = line.split("#", 1)
            comment = "#" + comment

        parts = code.split()
        if len(parts) >= 2 and parts[0] in {"PFX", "SFX"}:
            old = parts[1]
            new = replace_flag_fn(old)
            if new != old:
                parts[1] = new
                changed += 1
                rebuilt = " ".join(parts)
                out_lines.append(rebuilt + ("" if not comment else " " + comment.strip("\n")))
            else:
                out_lines.append(line)
        else:
            out_lines.append(line)

    return "\n".join(out_lines), changed


def _ensure_flag_long_line(aff_text: str, newline: str) -> Tuple[str, bool]:
    """Insert `FLAG long` after the first `SET ...` line (or at top if not found)."""
    lines = aff_text.splitlines()
    for i, raw in enumerate(lines):
        if raw.strip().upper().startswith("FLAG "):
            # Already has FLAG; replace it with FLAG long
            lines[i] = "FLAG long"
            return "\n".join(lines), True

    for i, raw in enumerate(lines):
        if raw.strip().upper().startswith("SET "):
            lines.insert(i + 1, "FLAG long")
            return "\n".join(lines), True

    lines.insert(0, "FLAG long")
    return "\n".join(lines), True


def _convert_dic_char_to_long(dic_text: str, old_char: str, new_long: str) -> Tuple[str, int]:
    out_lines: list[str] = []
    changed = 0

    lines = dic_text.splitlines()
    for idx, raw in enumerate(lines):
        line = raw
        if idx == 0:
            out_lines.append(line)
            continue
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            out_lines.append(line)
            continue

        head, tail = _split_dic_head_and_tail(line)
        if "/" not in head:
            out_lines.append(line)
            continue

        word, flags = head.split("/", 1)

        # Convert each single-char flag -> two-char flag.
        long_flags_parts: list[str] = []
        for ch in flags:
            if ch == old_char:
                long_flags_parts.append(new_long)
            else:
                long_flags_parts.append(ch + ch)
        new_flags = "".join(long_flags_parts)

        # Always counts as changed because flags are rewritten in long-mode conversion
        changed += 1
        out_lines.append(f"{word}/{new_flags}" + tail)

    return "\n".join(out_lines), changed


def _convert_aff_char_to_long(aff_text: str, old_char: str, new_long: str) -> Tuple[str, int]:
    def replace_flag(tok: str) -> str:
        if tok == old_char:
            return new_long
        # Only convert 1-char tokens that look like flags; leave other tokens alone.
        if len(tok) == 1:
            return tok + tok
        return tok

    return _update_aff_pfx_sfx_tokens(aff_text, replace_flag)


def _simple_rename_aff(aff_text: str, old_flag: str, new_flag: str) -> Tuple[str, int]:
    def replace_flag(tok: str) -> str:
        return new_flag if tok == old_flag else tok

    return _update_aff_pfx_sfx_tokens(aff_text, replace_flag)


def _confirm(prompt: str, assume_yes: bool) -> bool:
    if assume_yes:
        return True
    ans = input(prompt).strip().lower()
    return ans in {"y", "yes"}


def main(argv: Optional[Iterable[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Rename Hunspell flags across Luganda.aff and Luganda.dic")
    parser.add_argument("--old", dest="old_flag", help="Old flag (rule id) to replace")
    parser.add_argument("--new", dest="new_flag", help="New flag to use")
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Don’t prompt for confirmation (still validates inputs).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would change, but don’t write files.",
    )

    args = parser.parse_args(list(argv) if argv is not None else None)

    workspace = Path(__file__).resolve().parent
    aff_path = workspace / AFF_NAME
    dic_path = workspace / DIC_NAME

    if not aff_path.exists() or not dic_path.exists():
        raise SystemExit(f"Expected {AFF_NAME} and {DIC_NAME} next to this script (in {workspace}).")

    old_flag = args.old_flag or input("Old flag to replace (e.g. E): ").strip()
    new_flag = args.new_flag or input("New flag to use (e.g. F or AB): ").strip()

    if not old_flag or not new_flag:
        raise SystemExit("Both old and new flags are required.")

    aff_text, aff_nl = _read_text(aff_path)
    dic_text, dic_nl = _read_text(dic_path)

    mode = _detect_flag_mode(aff_text)

    # If user typed a 2-character new flag but we're in char mode, offer a safe full conversion.
    if mode.kind == "char" and len(new_flag) == 2:
        if len(old_flag) != 1:
            raise SystemExit(
                "In the current file (character-flag mode), the old flag must be 1 character for conversion."
            )

        print(
            "\nYour Luganda.aff is currently in single-character flag mode (no `FLAG long`).\n"
            "A 2-character flag would be interpreted as TWO separate flags unless you convert the whole dictionary\n"
            "to `FLAG long`.\n"
        )

        if not _confirm("Convert the whole dictionary to `FLAG long` now? (y/N): ", assume_yes=args.yes):
            raise SystemExit(
                "Aborted. If you want a simple rename without converting, use a 1-character new flag."
            )

        # Plan: convert all flags to long by doubling each char, except old->new_long.
        new_long = new_flag

        new_aff_text, aff_changed = _convert_aff_char_to_long(aff_text, old_flag, new_long)
        new_aff_text, _ = _ensure_flag_long_line(new_aff_text, aff_nl)

        new_dic_text, dic_changed = _convert_dic_char_to_long(dic_text, old_flag, new_long)

        print(f"Planned changes: {AFF_NAME} PFX/SFX lines updated: {aff_changed}")
        print(f"Planned changes: {DIC_NAME} flagged entries rewritten: {dic_changed}")

        if args.dry_run:
            print("Dry-run: not writing files.")
            return 0

        aff_bak = _backup(aff_path)
        dic_bak = _backup(dic_path)
        _write_text(aff_path, new_aff_text, aff_nl)
        _write_text(dic_path, new_dic_text, dic_nl)

        print(f"\nWrote {AFF_NAME} and {DIC_NAME}.")
        print(f"Backups: {aff_bak.name}, {dic_bak.name}")
        print("NOTE: After this conversion, every flag is now 2 characters (FLAG long).")
        return 0

    # Otherwise: do a safe rename within the current mode.
    _validate_flag_for_mode(old_flag, mode)
    _validate_flag_for_mode(new_flag, mode)

    if old_flag == new_flag:
        raise SystemExit("Old flag and new flag are the same; nothing to do.")

    if not _confirm(
        f"Rename flag {old_flag!r} -> {new_flag!r} in {AFF_NAME} and {DIC_NAME}? (y/N): ",
        assume_yes=args.yes,
    ):
        print("Aborted.")
        return 1

    new_aff_text, aff_changed = _simple_rename_aff(aff_text, old_flag, new_flag)

    if mode.kind == "char":
        new_dic_text, dic_changed = _update_dic_flags_char_mode(dic_text, old_flag, new_flag)
    elif mode.kind == "long":
        # Long-mode rename: flags in .dic are 2-char chunks.
        out_lines: list[str] = []
        dic_changed = 0
        lines = dic_text.splitlines()
        for idx, raw in enumerate(lines):
            line = raw
            if idx == 0:
                out_lines.append(line)
                continue
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                out_lines.append(line)
                continue

            head, tail = _split_dic_head_and_tail(line)
            if "/" not in head:
                out_lines.append(line)
                continue

            word, flags = head.split("/", 1)
            if len(flags) % 2 != 0:
                raise SystemExit(
                    f"Found odd-length flag string in long mode: {head!r}. "
                    "Fix this before renaming."
                )
            chunks = [flags[i : i + 2] for i in range(0, len(flags), 2)]
            new_chunks = [new_flag if c == old_flag else c for c in chunks]
            new_flags = "".join(new_chunks)
            if new_flags != flags:
                dic_changed += 1
                out_lines.append(f"{word}/{new_flags}" + tail)
            else:
                out_lines.append(line)
        new_dic_text = "\n".join(out_lines)
    else:
        raise SystemExit("FLAG num mode not implemented for .dic renames in this script.")

    print(f"Planned changes: {AFF_NAME} PFX/SFX lines updated: {aff_changed}")
    print(f"Planned changes: {DIC_NAME} flagged entries updated: {dic_changed}")

    if args.dry_run:
        print("Dry-run: not writing files.")
        return 0

    aff_bak = _backup(aff_path)
    dic_bak = _backup(dic_path)
    _write_text(aff_path, new_aff_text, aff_nl)
    _write_text(dic_path, new_dic_text, dic_nl)

    print(f"\nWrote {AFF_NAME} and {DIC_NAME}.")
    print(f"Backups: {aff_bak.name}, {dic_bak.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
