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
        with Path(aff_path_str).open("r", encoding="utf-8", errors="replace") as f:
            for raw in f:
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
    # This can be large; prefer using DB-synced descriptions.
    # Keep a best-effort streaming implementation for tools/tests.
    out: Dict[str, str] = {}
    try:
        with aff_path.open("r", encoding="utf-8", errors="replace") as f:
            for i, raw in enumerate(f, start=1):
                if i > 3000:
                    break
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


@lru_cache(maxsize=128)
def _flag_description_cached(aff_path_str: str, mtime_ns: int, size: int, flag: str) -> str:
    """Best-effort description from comments, without loading the whole file."""

    if not flag:
        return ""

    canonical = ""
    comment_block: List[str] = []

    def clean_comment(s: str) -> str:
        s = s.strip().lstrip("#").strip()
        for marker in (" e.g.", " E.g.", " for example:", " For example:"):
            if marker in s:
                s = s.split(marker, 1)[0].rstrip(" :")
        return s

    try:
        with Path(aff_path_str).open("r", encoding="utf-8", errors="replace") as f:
            for i, raw in enumerate(f, start=1):
                t = (raw or "").strip()
                if not t:
                    comment_block = []
                    continue
                if t.startswith("#"):
                    m = re.match(r"^#\s*([^\s=]{1,16})\s*=\s*(.+?)\s*$", t)
                    if m and m.group(1).strip() == flag:
                        canonical = m.group(2).strip()
                    c = clean_comment(t)
                    if c and not c.lower().startswith(("e.g.", "for example:", "since ")):
                        comment_block.append(c)
                    continue

                parts = t.split()
                if len(parts) >= 4 and parts[0].upper() in {"PFX", "SFX"} and parts[2].upper() in {"Y", "N"}:
                    code = parts[1]
                    if code == flag:
                        return canonical or (" ".join(comment_block[:2]).strip() if comment_block else "")
                    comment_block = []
                    continue

                comment_block = []
                if i > 2000000:  # safety guard for extremely large files
                    break
    except OSError:
        return ""

    return canonical or ""


def parse_affix_types(aff_path: Path) -> Dict[str, str]:
    """Map flag -> 'P' or 'S' based on PFX/SFX headers."""
    out: Dict[str, str] = {}
    try:
        with aff_path.open("r", encoding="utf-8", errors="replace") as f:
            for raw in f:
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


@lru_cache(maxsize=512)
def _affix_entries_for_flag_cached(
    aff_path_str: str,
    mtime_ns: int,
    size: int,
    flag: str,
) -> Tuple[AffixEntry, ...]:
    """Parse affix entries for a single flag by streaming the .aff file.

    This avoids loading the entire Luganda.aff into memory (which can exceed
    small-host RAM limits like Render's free tier).
    """

    if not flag:
        return ()

    combinable: Dict[str, bool] = {"P": False, "S": False}
    out: List[AffixEntry] = []

    try:
        with Path(aff_path_str).open("r", encoding="utf-8", errors="replace") as f:
            for raw in f:
                line = (raw or "").strip()
                if not line or line.startswith("#"):
                    continue
                toks = line.split()
                if len(toks) < 2:
                    continue
                kind = toks[0].upper()
                if kind not in ("PFX", "SFX"):
                    continue

                code = toks[1]
                if code != flag:
                    continue

                affix_type = "P" if kind == "PFX" else "S"

                # Header: PFX XX Y 2
                is_header = len(toks) >= 4 and toks[2].upper() in ("Y", "N")
                if is_header:
                    combinable[affix_type] = toks[2].upper() == "Y"
                    continue

                # Rule line: PFX XX 0 tu .
                if len(toks) < 4:
                    continue
                strip = "" if toks[2] == "0" else toks[2]
                add = "" if toks[3] == "0" else toks[3]
                condition = toks[4] if len(toks) >= 5 else "."
                out.append(
                    AffixEntry(
                        affix_type=affix_type,
                        flag=flag,
                        strip=strip,
                        add=add,
                        condition=condition or ".",
                        combinable=combinable.get(affix_type, False),
                    )
                )
    except OSError:
        return ()

    return tuple(out)


def iter_affix_entries_for_flag(aff_path: Path, flag: str) -> List[AffixEntry]:
    if not flag:
        return []
    aff_path_str, mtime_ns, size = _aff_signature(aff_path)
    # Return a copy to avoid accidental mutations affecting cached data.
    return list(_affix_entries_for_flag_cached(aff_path_str, mtime_ns, size, flag))


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
    entries = _affix_entries_for_flag_cached(aff_path_str, mtime_ns, size, flag)
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
