import os
import re
from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class PfxRule:
    strip: str
    add: str
    cond: str


def read_aff_lines(file_path: str) -> List[str]:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.readlines()


def parse_all_pfx_blocks(lines: List[str], flag: str) -> List[PfxRule]:
    """Parse *all* PFX blocks for a given flag (case-sensitive).

    Luganda.aff currently contains duplicate `PFX ip` blocks (non-reflexive + reflexive-negative).
    For cross-products we want to respect the file as-is and include all rules.
    """
    rules: List[PfxRule] = []

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        parts = line.split()
        if len(parts) >= 4 and parts[0] == "PFX" and parts[1] == flag and parts[2] in {"Y", "N"}:
            try:
                count = int(parts[3])
            except ValueError:
                i += 1
                continue

            i += 1
            found = 0
            while i < len(lines) and found < count:
                cur = lines[i].strip()
                if not cur or cur.startswith("#"):
                    i += 1
                    continue

                cur_parts = cur.split()
                if len(cur_parts) >= 4 and cur_parts[0] == "PFX" and cur_parts[1] == flag:
                    strip = cur_parts[2]
                    add = cur_parts[3]
                    cond = cur_parts[4] if len(cur_parts) > 4 else "."
                    rules.append(PfxRule(strip=strip, add=add, cond=cond))
                    found += 1
                    i += 1
                    continue

                # If the block is malformed, stop consuming it.
                break

            continue

        i += 1

    return rules


def is_1st_person_subject_marker(subject_add: str) -> bool:
    """Heuristic used in existing scripts: avoid 1st-person subject + 1st-person object.

    For these tense prefixes in Luganda.aff, 1st-person forms reliably begin with:
    - `ndi...` (e.g. `ndimuku...`)
    - `nna...` (e.g. `nnalimuku...`, `nnaaka...`)
    - `si...`  (negative)
    - `saa...` (negative past)
    """
    return (
        subject_add.startswith("ndi")
        or subject_add.startswith("nna")
        or subject_add.startswith("si")
        or subject_add.startswith("saa")
    )


def is_1st_person_object_marker(object_add: str) -> bool:
    return object_add in {"n", "nd", "nn", "mp"}


def generate_cross_product_rules(
    subject_rules: List[PfxRule],
    object_rules: List[PfxRule],
    filter_1st_person: bool,
) -> List[PfxRule]:
    new_rules: List[PfxRule] = []

    for s in subject_rules:
        for o in object_rules:
            # 1) Subject condition must allow attaching to object add-string.
            if s.cond != ".":
                if not re.match(s.cond, o.add):
                    continue

            # 2) Strip/Add compatibility: if subject strips, object must start with strip.
            if s.strip != "0":
                if not o.add.startswith(s.strip):
                    continue
                combined_add = s.add + o.add[len(s.strip) :]
            else:
                combined_add = s.add + o.add

            # 3) Optional filter: avoid 1st-person subject + 1st-person object
            if filter_1st_person:
                if is_1st_person_subject_marker(s.add) and is_1st_person_object_marker(o.add):
                    continue

            new_rules.append(PfxRule(strip=o.strip, add=combined_add, cond=o.cond))

    return new_rules


def render_pfx_block(target_flag: str, rules: List[PfxRule]) -> List[str]:
    out: List[str] = []
    out.append(f"PFX {target_flag} Y {len(rules)}\n")
    for r in rules:
        out.append(f"PFX {target_flag} {r.strip} {r.add} {r.cond}\n")
    return out


def upsert_pfx_block(
    aff_file: str,
    subject_flag: str,
    object_flag: str,
    target_flag: str,
    filter_1st_person: bool,
    comment: Optional[str] = None,
) -> None:
    if not os.path.exists(aff_file):
        raise FileNotFoundError(f"AFF file not found: {aff_file}")

    lines = read_aff_lines(aff_file)

    subject_rules = parse_all_pfx_blocks(lines, subject_flag)
    object_rules = parse_all_pfx_blocks(lines, object_flag)

    if not subject_rules:
        raise ValueError(f"Source PFX block(s) not found for subject flag: {subject_flag}")
    if not object_rules:
        raise ValueError(f"Source PFX block(s) not found for object flag: {object_flag}")

    new_rules = generate_cross_product_rules(subject_rules, object_rules, filter_1st_person)
    new_block = render_pfx_block(target_flag, new_rules)

    # Replace all existing blocks for the target flag; if none exist, append at end.
    final_lines: List[str] = []
    i = 0
    inserted = False

    while i < len(lines):
        stripped = lines[i].strip()
        parts = stripped.split()

        is_target_header = (
            len(parts) >= 4
            and parts[0] == "PFX"
            and parts[1] == target_flag
            and parts[2] in {"Y", "N"}
        )

        if not is_target_header:
            final_lines.append(lines[i])
            i += 1
            continue

        # Consume the old block
        try:
            old_count = int(parts[3])
        except ValueError:
            old_count = 0

        if not inserted:
            final_lines.extend(new_block)
            inserted = True

        i += 1
        found = 0
        while i < len(lines) and found < old_count:
            cur = lines[i].strip()
            if not cur or cur.startswith("#"):
                i += 1
                continue
            if cur.startswith(f"PFX {target_flag} "):
                found += 1
                i += 1
                continue
            break

    if not inserted:
        # Ensure a clean separation at EOF
        if final_lines and not final_lines[-1].endswith("\n"):
            final_lines[-1] += "\n"
        final_lines.append("\n")
        if comment:
            if not comment.endswith("\n"):
                comment += "\n"
            final_lines.append(comment)
        else:
            final_lines.append(f"# Cross product {subject_flag} x {object_flag} (generated flag {target_flag})\n")
        final_lines.extend(new_block)

    with open(aff_file, "w", encoding="utf-8") as f:
        f.writelines(final_lines)
