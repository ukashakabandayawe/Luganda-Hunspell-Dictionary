from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple

import shutil

from filelock import FileLock

from .hunspell import merge_flags


@dataclass(frozen=True)
class DicEntry:
    stem: str
    flags_raw: str
    trailing: str


def index_of_whitespace(s: str) -> int:
    for i, ch in enumerate(s):
        if ch.isspace():
            return i
    return -1


def parse_dic_entry_line(line: str) -> Optional[DicEntry]:
    if line is None:
        return None
    if not line.strip():
        return None
    if line.lstrip().startswith("#"):
        return None

    first_ws = index_of_whitespace(line)
    token = line[:first_ws] if first_ws >= 0 else line
    trailing = line[first_ws:] if first_ws >= 0 else ""

    slash = token.find("/")
    stem = token[:slash] if slash >= 0 else token
    flags_raw = token[slash + 1 :] if slash >= 0 else ""

    stem = stem.strip()
    if not stem:
        return None

    return DicEntry(stem=stem, flags_raw=flags_raw, trailing=trailing)


def apply_flags_to_dic_file(
    dic_path: Path,
    flags_to_add_by_stem: Dict[str, Set[str]],
    flag_mode: str,
) -> Tuple[int, int, Dict[str, int], Dict[str, int]]:
    """Update an on-disk .dic file in place.

    Returns: (total_matched_lines, total_changed_lines, matched_by_stem, changed_by_stem)
    """
    if not flags_to_add_by_stem:
        return 0, 0, {}, {}

    dic_path = Path(dic_path)
    lock = FileLock(str(dic_path) + ".lock")

    matched_by: Dict[str, int] = {k: 0 for k in flags_to_add_by_stem.keys()}
    changed_by: Dict[str, int] = {k: 0 for k in flags_to_add_by_stem.keys()}

    total_matched = 0
    total_changed = 0

    with lock:
        lines = dic_path.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)
        if not lines:
            return 0, 0, matched_by, changed_by

        for i, line in enumerate(lines):
            if i == 0:
                continue  # count line
            entry = parse_dic_entry_line(line)
            if not entry:
                continue

            to_add = flags_to_add_by_stem.get(entry.stem)
            if not to_add:
                continue

            matched_by[entry.stem] = matched_by.get(entry.stem, 0) + 1
            total_matched += 1

            merged = merge_flags(entry.flags_raw, to_add, flag_mode)
            changed = merged != (entry.flags_raw or "")
            new_token = entry.stem + ("" if not merged else "/" + merged)
            new_line = new_token + entry.trailing

            if changed:
                lines[i] = new_line
                changed_by[entry.stem] = changed_by.get(entry.stem, 0) + 1
                total_changed += 1

        if total_changed > 0:
            dic_path.write_text("".join(lines), encoding="utf-8")

    return total_matched, total_changed, matched_by, changed_by


def ensure_working_dic_exists(source_dic: Path, working_dic: Path) -> None:
    working_dic = Path(working_dic)
    source_dic = Path(source_dic)
    if working_dic.exists():
        return
    working_dic.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source_dic, working_dic)


def rebuild_working_dic(
    source_dic: Path,
    working_dic: Path,
    flags_to_add_by_stem: Dict[str, Set[str]],
    flag_mode: str,
) -> Tuple[int, int, Dict[str, int], Dict[str, int]]:
    """Rebuild the working .dic from the source, then apply all approvals."""
    working_dic = Path(working_dic)
    source_dic = Path(source_dic)
    working_dic.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source_dic, working_dic)
    return apply_flags_to_dic_file(working_dic, flags_to_add_by_stem, flag_mode)
