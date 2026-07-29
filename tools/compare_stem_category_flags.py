from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


SECTION_RE = re.compile(r"^(?P<title>.+?)\s+TYPE-(?P<kind>I|II)\s+STEMS\s*$", re.IGNORECASE)
COMMON_FLAGS_RE = re.compile(
    r"^(?:Common flags(?:\s+\((?:raw|tokens)\))?|Suggested common group flags)\s*:?(?P<flags>.*)$",
    re.IGNORECASE,
)
TYPE_MARKER_RE = re.compile(r"\s+TYPE-(?:I|II)\s+STEMS\s*$", re.IGNORECASE)


@dataclass(frozen=True)
class Section:
    key: str
    title: str
    kind: str
    flags: frozenset[str]
    line_no: int


def normalize_key(title: str) -> str:
    cleaned = TYPE_MARKER_RE.sub("", title).strip()
    return re.sub(r"\s+", " ", cleaned)


def parse_flags(flag_text: str) -> frozenset[str]:
    tokens = [token.strip() for token in re.split(r"[\s,]+", flag_text.strip())]
    return frozenset(token for token in tokens if token)


def parse_report(path: Path) -> dict[tuple[str, str], Section]:
    sections: dict[tuple[str, str], Section] = {}
    current_key: tuple[str, str] | None = None

    for line_no, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue

        section_match = SECTION_RE.match(line)
        if section_match:
            title = section_match.group("title").strip()
            kind = section_match.group("kind").upper()
            key = normalize_key(title)
            current_key = (key, kind)
            sections[current_key] = Section(key=key, title=title, kind=kind, flags=frozenset(), line_no=line_no)
            continue

        if current_key is None:
            continue

        section = sections[current_key]
        if section.flags:
            continue

        flags_match = COMMON_FLAGS_RE.match(line)
        if not flags_match:
            continue

        flags = parse_flags(flags_match.group("flags").strip())
        sections[current_key] = Section(
            key=section.key,
            title=section.title,
            kind=section.kind,
            flags=flags,
            line_no=section.line_no,
        )

    return sections


def format_flags(flags: frozenset[str]) -> str:
    if not flags:
        return "(none)"
    return ", ".join(sorted(flags))


def compare_sections(type_i: Section, type_ii: Section) -> str:
    flags_i = type_i.flags
    flags_ii = type_ii.flags
    shared = flags_i & flags_ii
    union = flags_i | flags_ii
    only_i = flags_i - flags_ii
    only_ii = flags_ii - flags_i

    lines = [
        f"{type_i.key}",
        f"  Type-I ({type_i.title}): {len(flags_i)} flags",
        f"  Type-II ({type_ii.title}): {len(flags_ii)} flags",
        f"  Intersection ({len(shared)}): {format_flags(shared)}",
        f"  Union ({len(union)}): {format_flags(union)}",
        f"  Type-I only ({len(only_i)}): {format_flags(only_i)}",
        f"  Type-II only ({len(only_ii)}): {format_flags(only_ii)}",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compare corresponding flag sections in the Type-I and Type-II stem reports."
    )
    parser.add_argument(
        "--type-i",
        type=Path,
        default=Path("resources/Type-I stems common flags.txt"),
        help="Path to the Type-I report file.",
    )
    parser.add_argument(
        "--type-ii",
        type=Path,
        default=Path("resources/Type-II stems common flags.txt"),
        help="Path to the Type-II report file.",
    )
    parser.add_argument(
        "--only-differences",
        action="store_true",
        help="Hide sections whose flags are identical across Type-I and Type-II.",
    )
    args = parser.parse_args()

    sections_i = parse_report(args.type_i)
    sections_ii = parse_report(args.type_ii)

    keys_i = {key for key in sections_i if key[1] == "I"}
    keys_ii = {key for key in sections_ii if key[1] == "II"}

    paired_keys = sorted({key for key, kind in keys_i if (key, "II") in sections_ii})
    missing_i = sorted(key for key, kind in keys_ii if (key, "I") not in sections_i)
    missing_ii = sorted(key for key, kind in keys_i if (key, "II") not in sections_ii)

    print(f"Type-I report: {args.type_i}")
    print(f"Type-II report: {args.type_ii}")
    print()

    if not paired_keys:
        print("No matching category pairs were found.")
        return 1

    total_pairs = 0
    differing_pairs = 0

    for key in paired_keys:
        type_i = sections_i[(key, "I")]
        type_ii = sections_ii[(key, "II")]
        only_i = type_i.flags - type_ii.flags
        only_ii = type_ii.flags - type_i.flags
        if args.only_differences and not only_i and not only_ii:
            continue

        total_pairs += 1
        if only_i or only_ii:
            differing_pairs += 1

        print(compare_sections(type_i, type_ii))
        print()

    print(f"Compared pairs: {total_pairs}")
    print(f"Pairs with differences: {differing_pairs}")

    if missing_i:
        print(f"Unpaired Type-II sections: {len(missing_i)}")
        for key in missing_i:
            print(f"  {key}")

    if missing_ii:
        print(f"Unpaired Type-I sections: {len(missing_ii)}")
        for key in missing_ii:
            print(f"  {key}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())