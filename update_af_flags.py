#!/usr/bin/env python3
"""Replace human-readable Hunspell AF labels with the real flag sequences from the
resource documents.

The resource files in resources/ list the headings and their corresponding
"Common flags (raw)" values. This script reads those resource files, maps each
heading to the name used in Luganda.aff, and replaces those AF entries while
preserving the comma formatting from the resource documents.

Usage:
    python update_af_flags.py --file Luganda.aff --dry-run
    python update_af_flags.py --file Luganda.aff
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

RESOURCE_FILES = [
    Path("resources/Transitive stems common flags.txt"),
    Path("resources/Intrasitive stems common flags.txt"),
    Path("resources/Deadjective stems common flags.txt"),
    Path("resources/Reflexive stems common flags.txt"),
]

# Normalized heading -> candidate AF names to replace.
# The left-hand side is built from the resource headings after normalizing casing,
# dashes, and the common "INTRASITIVE" typo. The values are the actual AF names
# that appear in Luganda.aff.
HEADER_ALIASES = {
    "ORIGINAL TYPE I TRANSITIVE STEMS": ["OriginalType-ITransitive"],
    "MODIFIED TYPE I TRANSITIVE STEMS": ["ModifiedType-ITransitive"],
    "PAST TENSE TYPE I TRANSITIVE STEMS": ["PastType-ITransitive"],
    "PASSIVE TRANSITIVE STEMS": ["PassiveTransitive"],
    "MODIFIED PASSIVE TRANSITIVE STEMS": ["ModifiedPassiveTransitive"],
    "PAST PASSIVE TRANSITIVE STEMS": ["PastPassiveTransitive"],
    "CAUSATIVE TRANSITIVE STEMS": ["CausativeTransitive"],
    "MODIFIED CAUSATIVE TRANSITIVE STEMS": ["ModifiedCausativeTransitive"],
    "PAST CAUSATIVE TRANSITIVE STEMS": ["PastCausativeTransitive"],
    "LOCATIVE TRANSITIVE STEMS": ["LocativeTransitive"],
    "MODIFIED LOCATIVE TRANSITIVE STEMS": ["ModifiedLocativeTransitive"],
    "PAST LOCATIVE TRANSITIVE STEMS": ["PastLocativeTransitive"],
    "BENEFACTIVE TRANSITIVE STEMS": ["BenefactiveTransitive"],
    "MODIFIED BENEFACTIVE TRANSITIVE STEMS": ["ModifiedBenefactiveTransitive"],
    "PAST BENEFACTIVE TRANSITIVE STEMS": ["PastBenefactiveTransitive"],
    "ORIGINAL TYPE II TRANSITIVE STEMS": ["OriginalType-IITransitive"],
    "MODIFIED TYPE II TRANSITIVE STEMS": ["ModifiedType-IITransitive"],
    "PAST TENSE TYPE II TRANSITIVE STEMS": ["PastType-IITransitive"],

    "ORIGINAL INTRANSITIVE STEMS": ["OriginalIntrasitive", "OriginalIntransitive"],
    "MODIFIED INTRANSITIVE STEMS": ["ModifiedIntransitive", "ModifiedIntrasitive"],
    "PAST TENSE INTRANSITIVE STEMS": ["PastIntransitive"],
    "CAUSATIVE INTRANSITIVE STEMS": ["CausativeIntransitive"],
    "MODIFIED CAUSATIVE INTRANSITIVE STEMS": ["ModifiedCausativeIntransitive"],
    "PAST CAUSATIVE INTRANSITIVE STEMS": ["PastCausativeIntransitive"],
    "PASSIVE INTRANSITIVE STEMS": ["PassiveIntransitive"],
    "MODIFIED PASSIVE INTRANSITIVE STEMS": ["ModifiedPassiveIntransitive"],
    "PAST PASSIVE INTRANSITIVE STEMS": ["PastPassiveIntransitive"],
    "BENEFACTIVE INTRANSITIVE STEMS": ["BenefactiveIntransitive"],
    "MODIFIED BENEFACTIVE INTRANSITIVE STEMS": ["ModifiedBenefactiveIntransitive"],
    "PAST BENEFACTIVE INTRANSITIVE STEMS": ["PastBenefactiveIntransitive"],
    "LOCATIVE INTRANSITIVE STEMS": ["LocativeIntransitive"],
    "MODIFIED LOCATIVE INTRANSITIVE STEMS": ["ModifiedLocativeIntransitive"],
    "PAST LOCATIVE INTRANSITIVE STEMS": ["PastLocativeIntransitive"],
    "COMBINATION OF PAST TENSE INTRANSITIVE STEMS AND MODIFIED CAUSATIVE INTRANSITIVE STEMS HYBRID INTRANSITIVE STEMS": ["HybridIntransitive"],

    "ORIGINAL DEADJECTIVE STEMS": ["OriginalDeadjective"],
    "MODIFIED DEADJECTIVE STEMS": ["ModifiedDeadjective"],
    "PAST TENSE DEADJECTIVE STEMS": ["PastDeadjective"],
    "PASSIVE DEADJECTIVE STEMS": ["PassiveDeadjective"],
    "MODIFIED PASSIVE DEADJECTIVE STEMS": ["ModifiedPassiveDeadjective"],
    "PAST PASSIVE DEADJECTIVE STEMS": ["PastPassiveDeadjective"],
    "CAUSATIVE DEADJECTIVE STEMS": ["CausativeDeadjective"],
    "MODIFIED CAUSATIVE DEADJECTIVE STEMS": ["ModifiedCausativeDeadjective"],
    "PAST CAUSATIVE DEADJECTIVE STEMS": ["PastCausativeDeadjective"],
    "COMBINATION OF PAST TENSE STEMS AND MODIFIED CAUSATIVE STEMS HYBRID DEADJECTIVE STEMS": ["HybridDeadjective"],
    "BENEFACTIVE DEADJECTIVE STEMS": ["BenefactiveDeadjective"],
    "MODIFIED BENEFACTIVE DEADJECTIVE STEMS": ["ModifiedBenefactiveDeadjective"],
    "PAST BENEFACTIVE DEADJECTIVE STEMS": ["PastBenefactiveDeadjective"],
    "LOCATIVE DEADJECTIVE STEMS": ["LocativeDeadjective"],
    "MODIFIED LOCATIVE DEADJECTIVE STEMS": ["ModifiedLocativeDeadjective"],
    "PAST LOCATIVE DEADJECTIVE STEMS": ["PastLocativeDeadjective"],

    "ORIGINAL REFLEXIVE STEMS": ["OriginalReflexive"],
    "MODIFIED REFLEXIVE STEMS": ["ModifiedReflexive"],
    "PAST REFLEXIVE STEMS": ["PastReflexive"],
    "ORIGINAL INTRANSITIVE REFLEXIVE STEMS": ["OriginalIntransitiveReflexive", "OriginalIntrasitiveReflexive"],
    "MODIFIED INTRANSITIVE REFLEXIVE STEMS": ["ModifiedIntransitiveReflexive", "ModifiedIntrasitiveReflexive"],
    "PAST INTRANSITIVE REFLEXIVE STEMS": ["PastIntransitiveReflexive", "PastIntrasitiveReflexive"],
    "COMBINATION OF PAST TENSE INTRANSITIVE REFLEXIVE STEMS AND MODIFIED CAUSATIVE STEMS HYBRID INTRANSITIVE REFLEXIVE STEMS": ["HybridIntransitiveReflexive"],
    "CAUSATIVE REFLEXIVE STEMS": ["CausativeReflexive"],
    "MODIFIED CAUSATIVE REFLEXIVE STEMS": ["ModifiedCausativeReflexive"],
    "PAST CAUSATIVE REFLEXIVE STEMS": ["PastCausativeReflexive"],
    "PASSIVE REFLEXIVE STEMS": ["PassiveReflexive"],
    "MODIFIED PASSIVE REFLEXIVE STEMS": ["ModifiedPassiveReflexive"],
    "PAST PASSIVE REFLEXIVE STEMS": ["PastPassiveReflexive"],
    "LOCATIVE REFLEXIVE STEMS": ["LocativeReflexive"],
    "MODIFIED LOCATIVE REFLEXIVE STEMS": ["ModifiedLocativeReflexive"],
    "PAST LOCATIVE REFLEXIVE STEMS": ["PastLocativeReflexive"],
    "BENEFACTIVE REFLEXIVE STEMS": ["BenefactiveReflexive"],
    "MODIFIED BENEFACTIVE REFLEXIVE STEMS": ["ModifiedBenefactiveReflexive"],
    "PAST BENEFACTIVE REFLEXIVE STEMS": ["PastBenefactiveReflexive"],
}


def normalize_heading(raw_heading: str) -> str:
    cleaned = re.sub(r"^\d+\.\s*", "", raw_heading).strip()
    cleaned = cleaned.replace("-", " ")
    cleaned = cleaned.replace("INTRASITIVE", "INTRANSITIVE")
    cleaned = cleaned.replace("TYPE I", "TYPE I").replace("TYPE II", "TYPE II")
    cleaned = re.sub(r"[^A-Z0-9]+", " ", cleaned.upper()).strip()
    return " ".join(cleaned.split())


def collect_document_map() -> dict[str, str]:
    result: dict[str, str] = {}
    for resource_file in RESOURCE_FILES:
        current_heading = None
        for raw_line in resource_file.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line:
                continue
            if re.match(r"^(common flags|flags)\b", line, flags=re.IGNORECASE):
                if current_heading is not None:
                    value = line.split(":", 1)[1].strip() if ":" in line else line.strip()
                    for af_name in HEADER_ALIASES.get(current_heading, []):
                        result[af_name] = value
                current_heading = None
                continue

            if not line.startswith("#"):
                cleaned = normalize_heading(line)
                if cleaned in HEADER_ALIASES:
                    current_heading = cleaned
    return result


def is_likely_human_flag_name(name: str) -> bool:
    if len(name) < 8:
        return False
    if not any(ch.islower() for ch in name):
        return False
    if "-" in name or "_" in name:
        return True
    lower_count = sum(1 for ch in name if ch.islower())
    upper_count = sum(1 for ch in name if ch.isupper())
    return lower_count >= 2 and upper_count >= 2


def find_unknown_af_names(aff_path: Path, known_names: set[str]) -> list[str]:
    unknown: list[str] = []
    for line in aff_path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("AF "):
            continue
        match = re.match(r"AF\s+([A-Za-z0-9_-]+)\s*#\s*\d+\s*$", line.strip())
        if not match:
            continue
        name = match.group(1)
        if name and name not in known_names and is_likely_human_flag_name(name):
            unknown.append(name)
    return sorted(set(unknown))


def update_aff_file(aff_path: Path, dry_run: bool = False) -> tuple[int, list[str], list[str]]:
    resource_map = collect_document_map()
    known_names = set(resource_map)

    updated_lines: list[str] = []
    replacements = 0
    unknown_names: list[str] = []

    for line in aff_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("AF "):
            match = re.match(r"^(AF\s+)([A-Za-z0-9_-]+)(\s*#\s*\d+\s*)$", stripped)
            if match:
                prefix, name, suffix = match.groups()
                if name in resource_map:
                    updated_lines.append(f"{prefix}{resource_map[name]}{suffix}")
                    replacements += 1
                    continue
                if is_likely_human_flag_name(name):
                    unknown_names.append(name)
        updated_lines.append(line)

    if not dry_run:
        aff_path.write_text("\n".join(updated_lines) + "\n", encoding="utf-8")

    return replacements, sorted(set(unknown_names)), sorted(find_unknown_af_names(aff_path, known_names))


def main() -> int:
    parser = argparse.ArgumentParser(description="Replace human-readable AF labels using the resource files.")
    parser.add_argument("--file", type=Path, required=True, help="Path to the AFF file to update.")
    parser.add_argument("--dry-run", action="store_true", help="Preview the changes without writing the file.")
    args = parser.parse_args()

    if not args.file.exists():
        raise SystemExit(f"File not found: {args.file}")

    resource_map = collect_document_map()
    known_names = set(resource_map)
    replacements, unknown_in_file, unknown_names = update_aff_file(args.file, dry_run=args.dry_run)

    print(f"Mapped entries found: {len(resource_map)}")
    print(f"AF lines replaced: {replacements}")

    if unknown_names:
        print("\nWarning: remaining human-readable AF labels without a matching heading in the four resource files:")
        for name in unknown_names:
            print(f"  - {name}")
    else:
        print("\nNo unmapped human-readable AF labels remain in the target file.")

    if unknown_in_file:
        print("\nAF lines not replaced because they are not in the mapping set:")
        for name in unknown_in_file:
            print(f"  - {name}")

    if args.dry_run:
        print("\nDry run only: no file was written.")
    else:
        print(f"\nUpdated file: {args.file}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
