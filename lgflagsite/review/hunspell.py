from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple


class HunspellFlagMode:
    DEFAULT = "default"
    LONG = "long"
    NUM = "num"


@dataclass(frozen=True)
class AffixEntry:
    affix_type: str  # 'P' or 'S'
    flag: str
    strip: str
    add: str
    condition: str
    combinable: bool


def detect_flag_mode(aff_path: Path) -> str:
    aff_path_str, mtime_ns, size = _aff_signature(aff_path)
    return _detect_flag_mode_cached(aff_path_str, mtime_ns, size)


@lru_cache(maxsize=4)
def _detect_flag_mode_cached(aff_path_str: str, mtime_ns: int, size: int) -> str:
    try:
        for raw in _read_aff_lines(Path(aff_path_str)):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if not line.upper().startswith("FLAG"):
                continue
            toks = line.split()
            if len(toks) < 2:
                continue
            mode = toks[1].strip().lower()
            if mode == "long":
                return HunspellFlagMode.LONG
            if mode == "num":
                return HunspellFlagMode.NUM
            return HunspellFlagMode.DEFAULT
    except OSError:
        return HunspellFlagMode.DEFAULT
    return HunspellFlagMode.DEFAULT


def split_long_flags(flags_raw: str) -> List[str]:
    if not flags_raw:
        return []
    s = flags_raw.strip().replace("+", "")
    if not s:
        return []
    out: List[str] = []
    for i in range(0, len(s), 2):
        out.append(s[i : min(i + 2, len(s))])
    return out


def merge_flags(existing_flags_raw: str, flags_to_add: Set[str], mode: str) -> str:
    existing_flags_raw = existing_flags_raw or ""
    if not flags_to_add:
        return existing_flags_raw

    if mode == HunspellFlagMode.LONG:
        tokens: List[str] = []
        seen: Set[str] = set()
        for tok in split_long_flags(existing_flags_raw):
            if tok and tok not in seen:
                seen.add(tok)
                tokens.append(tok)

        for f in flags_to_add:
            if not f:
                continue
            for part in f.split("+"):
                t = (part or "").strip()
                if not t:
                    continue
                if t not in seen:
                    seen.add(t)
                    tokens.append(t)
        return "".join(tokens)

    if mode == HunspellFlagMode.NUM:
        tokens: List[str] = []
        seen: Set[str] = set()
        s = (existing_flags_raw or "").strip().replace("+", "")
        if s:
            for part in s.split(","):
                t = part.strip()
                if t and t not in seen:
                    seen.add(t)
                    tokens.append(t)
        for f in flags_to_add:
            if not f:
                continue
            for part in f.split("+"):
                t = (part or "").strip()
                if t and t not in seen:
                    seen.add(t)
                    tokens.append(t)
        return ",".join(tokens)

    # DEFAULT
    tokens: List[str] = []
    seen: Set[str] = set()
    s = existing_flags_raw or ""
    for ch in s:
        if ch == "+":
            continue
        if ch not in seen:
            seen.add(ch)
            tokens.append(ch)

    for f in flags_to_add:
        if not f:
            continue
        for part in f.split("+"):
            t = (part or "").strip()
            if not t:
                continue
            if len(t) == 1:
                if t not in seen:
                    seen.add(t)
                    tokens.append(t)
            else:
                for ch in t:
                    if ch not in seen:
                        seen.add(ch)
                        tokens.append(ch)

    return "".join(tokens)


def parse_flag_descriptions(aff_path: Path) -> Dict[str, str]:
    """Best-effort extraction of flag descriptions.

    Prefer canonical lines near the top like: `# XX = ...`.
    Otherwise fall back to the comment block immediately above the first PFX/SFX header.
    """
    out: Dict[str, str] = {}
    try:
        lines = _read_aff_lines(aff_path)

        # 1) Canonical `# XX = ...`
        for raw in lines[:3000]:
            line = raw.strip()
            if not line.startswith("#"):
                continue
            m = re.match(r"^#\s*([^\s=]{1,16})\s*=\s*(.+?)\s*$", line)
            if not m:
                continue
            code = m.group(1).strip()
            desc = m.group(2).strip()
            if code and code not in out:
                out[code] = desc

        # 2) Comment block above the first header
        # We only fill missing descriptions here.
        for flag in parse_affix_types(aff_path).keys():
            if flag in out:
                continue
            d = describe_flag_from_comments(lines, flag)
            if d:
                out[flag] = d
    except OSError:
        return {}
    return out


def _aff_signature(aff_path: Path) -> tuple[str, int, int]:
    """Return a cache-friendly signature for an .aff file.

    We key caches by (path, mtime_ns, size) so edits invalidate naturally.
    """

    p = Path(aff_path)
    try:
        st = p.stat()
        return str(p), int(st.st_mtime_ns), int(st.st_size)
    except OSError:
        return str(p), 0, 0


@lru_cache(maxsize=2)
def _flag_description_cached(aff_path_str: str, mtime_ns: int, size: int, flag: str) -> str:
    if not flag:
        return ""
    lines = _read_aff_lines(Path(aff_path_str))
    return describe_flag_from_comments(lines, flag) or ""


@lru_cache(maxsize=2)
def _read_aff_lines(aff_path: Path) -> List[str]:
    return aff_path.read_text(encoding="utf-8", errors="replace").splitlines()


def describe_flag_from_comments(lines: List[str], flag: str) -> Optional[str]:
    header_re = re.compile(rf"^\s*(PFX|SFX)\s+{re.escape(flag)}\s+[YN]\s+\d+")
    header_index: Optional[int] = None
    for i, raw in enumerate(lines):
        if header_re.match(raw):
            header_index = i
            break
    if header_index is None:
        return None

    comment_lines: List[str] = []
    j = header_index - 1
    while j >= 0:
        t = lines[j].strip()
        if not t:
            break
        if not t.startswith("#"):
            break
        s = t.lstrip("#").strip()
        for marker in (" e.g.", " E.g.", " for example:", " For example:"):
            if marker in s:
                s = s.split(marker, 1)[0].rstrip(" :")
        if s and not s.lower().startswith(("e.g.", "for example:", "since ")):
            comment_lines.append(s)
        j -= 1

    comment_lines.reverse()
    if not comment_lines:
        return None
    return " ".join(comment_lines[:2]).strip() or None


def parse_affix_types(aff_path: Path) -> Dict[str, str]:
    """Map flag -> 'P' or 'S' based on PFX/SFX headers."""
    out: Dict[str, str] = {}
    try:
        for raw in _read_aff_lines(aff_path):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            toks = line.split()
            if len(toks) < 2:
                continue
            if toks[0].upper() == "PFX":
                out.setdefault(toks[1], "P")
            elif toks[0].upper() == "SFX":
                out.setdefault(toks[1], "S")
    except OSError:
        return {}
    return out


@lru_cache(maxsize=2)
def _affix_entry_index_cached(aff_path_str: str, mtime_ns: int, size: int) -> Dict[str, Tuple[AffixEntry, ...]]:
    """Build an index of flag -> entries for a given .aff signature."""

    aff_path = Path(aff_path_str)
    lines = _read_aff_lines(aff_path)

    out: Dict[str, List[AffixEntry]] = {}
    combinable: Dict[tuple[str, str], bool] = {}

    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        toks = line.split()
        if len(toks) < 2:
            continue
        kind = toks[0].upper()
        if kind not in ("PFX", "SFX"):
            continue

        flag = toks[1]
        affix_type = "P" if kind == "PFX" else "S"

        # Header: PFX XX Y 2
        is_header = len(toks) >= 4 and toks[2].upper() in ("Y", "N")
        if is_header:
            combinable[(flag, affix_type)] = toks[2].upper() == "Y"
            continue

        # Rule line: PFX XX 0 tu .
        if len(toks) < 4:
            continue
        strip = "" if toks[2] == "0" else toks[2]
        add = "" if toks[3] == "0" else toks[3]
        condition = toks[4] if len(toks) >= 5 else "."
        out.setdefault(flag, []).append(
            AffixEntry(
                affix_type=affix_type,
                flag=flag,
                strip=strip,
                add=add,
                condition=condition or ".",
                combinable=combinable.get((flag, affix_type), False),
            )
        )

    return {k: tuple(v) for k, v in out.items()}


def iter_affix_entries_for_flag(aff_path: Path, flag: str) -> List[AffixEntry]:
    if not flag:
        return []
    aff_path_str, mtime_ns, size = _aff_signature(aff_path)
    idx = _affix_entry_index_cached(aff_path_str, mtime_ns, size)
    # Return a copy to avoid accidental mutations affecting cached data.
    return list(idx.get(flag, ()))


def apply_entry(entry: AffixEntry, root: str) -> Optional[str]:
    if not root:
        return None

    # Condition checking (mirror LugandaAffParser.apply for consistency)
    cond = (entry.condition or ".").strip()
    if cond and cond != ".":
        if entry.affix_type == "S":
            if not re.match(r".*" + cond + r"$", root):
                return None
        else:
            if not re.match(r"^" + cond + r".*", root):
                return None

    result = root

    if entry.strip:
        if entry.affix_type == "S":
            if not result.endswith(entry.strip):
                return None
            result = result[: -len(entry.strip)]
        else:
            if not result.startswith(entry.strip):
                return None
            result = result[len(entry.strip) :]

    if entry.add:
        if entry.affix_type == "S":
            result = result + entry.add
        else:
            result = entry.add + result

    return result


def generate_examples_for_flag(
    aff_path: Path,
    flag: str,
    root: str,
    limit: int = 200,
) -> List[str]:
    return list(_generate_examples_cached(*_aff_signature(aff_path), flag, root, int(limit)))


@lru_cache(maxsize=8192)
def _generate_examples_cached(
    aff_path_str: str,
    mtime_ns: int,
    size: int,
    flag: str,
    root: str,
    limit: int,
) -> Tuple[str, ...]:
    if not flag or not root or limit <= 0:
        return ()
    entries = _affix_entry_index_cached(aff_path_str, mtime_ns, size).get(flag, ())
    out: List[str] = []
    seen: Set[str] = set()
    for e in entries:
        w = apply_entry(e, root)
        if not w:
            continue
        if w in seen:
            continue
        seen.add(w)
        out.append(w)
        if len(out) >= limit:
            break
    return tuple(out)


def get_flag_description(aff_path: Path, flag: str) -> str:
    """Cached best-effort description for a flag from the .aff comments."""

    aff_path_str, mtime_ns, size = _aff_signature(aff_path)
    return _flag_description_cached(aff_path_str, mtime_ns, size, flag)
