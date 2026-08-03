from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import re
from typing import Iterable


HEADER_RE = re.compile(r"^#\s*-+\s+(?P<name>.+?)\s+-+\s*#\s*$")
FOOTER_RE = re.compile(r"^#\s*-+\s*#\s*$")
COUNT_RE = re.compile(r"^\d+$")
DEFAULT_OUTPUT_SUFFIX = ".organized"


@dataclass(frozen=True)
class GroupBlock:
    name: str
    lines: list[str]
    order: int


def detect_line_ending(text: str) -> str:
    if "\r\n" in text:
        return "\r\n"
    return "\n"


def split_stem_key(line: str) -> str:
    stripped = line.strip().lstrip("\ufeff")
    if not stripped or stripped.startswith("#"):
        return ""

    token = stripped.split(None, 1)[0]
    stem = token.split("/", 1)[0].strip()
    return stem


def parse_group_header(line: str) -> str | None:
    match = HEADER_RE.match(line.strip().lstrip("\ufeff"))
    if match is None:
        return None
    name = match.group("name").strip()
    return name or None


def format_output(lines: Iterable[str]) -> str:
    return "".join(lines)


def organize_dictionary_text(text: str) -> str:
    lines = text.splitlines(keepends=True)
    line_ending = detect_line_ending(text)

    prefix_end = 0
    for index, line in enumerate(lines):
        stripped = line.strip().lstrip("\ufeff")
        if not stripped:
            prefix_end = index + 1
            continue
        if stripped.startswith("#"):
            prefix_end = index + 1
            continue
        if COUNT_RE.match(stripped) and prefix_end == index:
            prefix_end = index + 1
            continue
        break

    prefix_lines = lines[:prefix_end]
    body_lines = lines[prefix_end:]

    free_stems: list[tuple[str, int, str]] = []
    groups: list[GroupBlock] = []
    separators: list[str] = []

    index = 0
    while index < len(body_lines):
        line = body_lines[index]
        stripped = line.strip().lstrip("\ufeff")

        if not stripped:
            separators.append(line)
            index += 1
            continue

        header_name = parse_group_header(line)
        if header_name is not None:
            block_lines = [line]
            index += 1

            while index < len(body_lines):
                block_lines.append(body_lines[index])
                if FOOTER_RE.match(body_lines[index].strip()):
                    break
                index += 1

            if not block_lines or not FOOTER_RE.match(block_lines[-1].strip()):
                raise ValueError(f"Unterminated grouped stem block starting with: {line.rstrip()}")

            groups.append(GroupBlock(name=header_name, lines=block_lines, order=len(groups)))
            index += 1
            continue

        if stripped.startswith("#"):
            separators.append(line)
            index += 1
            continue

        stem_key = split_stem_key(line)
        if not stem_key:
            index += 1
            continue

        free_stems.append((stem_key.casefold(), len(free_stems), line))
        index += 1

    free_stems.sort(key=lambda item: (item[0], item[1]))
    groups.sort(key=lambda item: (item.name.casefold(), item.order))

    output_lines: list[str] = []
    output_lines.extend(prefix_lines)

    for _, _, line in free_stems:
        if output_lines and not output_lines[-1].endswith(("\n", "\r\n")):
            output_lines.append(line_ending)
        output_lines.append(line if line.endswith(("\n", "\r\n")) else line + line_ending)

    if separators:
        if output_lines and not output_lines[-1].endswith(("\n", "\r\n")):
            output_lines.append(line_ending)
        output_lines.extend(separators)

    for group in groups:
        if output_lines and not output_lines[-1].endswith(("\n", "\r\n")):
            output_lines.append(line_ending)
        output_lines.extend(group.lines)

    return format_output(output_lines)


def organize_dictionary_file(input_path: Path, output_path: Path | None, in_place: bool) -> Path:
    original_text = input_path.read_text(encoding="utf-8", errors="replace")
    organized_text = organize_dictionary_text(original_text)

    if in_place:
        target_path = input_path
        backup_path = input_path.with_name(input_path.name + ".bak")
        backup_path.write_text(original_text, encoding="utf-8")
    else:
        target_path = output_path or input_path.with_name(input_path.stem + DEFAULT_OUTPUT_SUFFIX + input_path.suffix)

    target_path.write_text(organized_text, encoding="utf-8")
    return target_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Sort free stems and manual stem groups in Luganda dictionary files."
    )
    parser.add_argument("input", type=Path, help="Dictionary file to organize")
    parser.add_argument("--output", type=Path, help="Write the organized file to this path")
    parser.add_argument("--in-place", action="store_true", help="Rewrite the input file and create a .bak backup")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.in_place and args.output is not None:
        raise SystemExit("Use either --in-place or --output, not both.")

    target_path = organize_dictionary_file(args.input, args.output, args.in_place)
    print(f"Wrote organized dictionary to {target_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())