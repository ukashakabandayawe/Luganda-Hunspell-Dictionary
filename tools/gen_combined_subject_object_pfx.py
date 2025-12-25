from __future__ import annotations

from pathlib import Path
import re

AFF_PATH = Path(r"e:\Luganda Hunspell Dictionary\New.aff")

# Matches: PFX <flag> <strip> <add> <cond> [continuation...]
PFX_LINE_RE = re.compile(
    r"^\s*PFX\s+"
    r"(?P<flag>\S+)\s+"
    r"(?P<strip>\S+)\s+"
    r"(?P<add>\S+)\s+"
    r"(?P<cond>\S+)"
    r"(?:\s+(?P<cont>.+?))?"
    r"\s*$"
)

def read_adds(aff_text: str, flag: str) -> list[str]:
    adds: list[str] = []
    for line in aff_text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        m = PFX_LINE_RE.match(line)
        if not m:
            continue
        if m.group("flag") != flag:
            continue

        add = m.group("add")
        # Treat add "0" as empty (Hunspell convention)
        if add == "0":
            add = ""
        adds.append(add)
    return adds

def main() -> None:
    aff = AFF_PATH.read_text(encoding="utf-8")

    subjects = read_adds(aff, "E")
    objects = read_adds(aff, "F")

    total = len(subjects) * len(objects)

    out: list[str] = []
    out.append("# Auto-generated combined subject×object prefixes")
    out.append("# NOTE: This generator ignores real strip+condition behavior and forces: strip=0, cond=.")
    out.append(f"PFX N Y {total}")

    for s in subjects:
        for o in objects:
            out.append(f"PFX N 0 {s}{o} .")

    print("\n".join(out))

if __name__ == "__main__":
    main()