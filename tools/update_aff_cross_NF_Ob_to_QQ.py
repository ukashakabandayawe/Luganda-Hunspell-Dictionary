import re
import os
from pathlib import Path

# Cross product generator: NF x Ob => QQ
# Description:
# - Left block `NF`: NF
# - Right block `Ob`: Object markers
# - Output flag `QQ`: Cross-product prefixes for NF x Ob

REPO_ROOT = Path(__file__).resolve().parents[1]
AFF_FILE = REPO_ROOT / "Luganda.aff"

rule_left_raw = """
PFX NF Y 39
PFX NF 0 naa [^mn]
PFX NF 0 naa mu
PFX NF 0 munaa .
PFX NF 0 onoo .
PFX NF 0 onaa .
PFX NF 0 anaa .
PFX NF 0 tunaa .
PFX NF 0 munaa .
PFX NF 0 banaa .
PFX NF 0 abanaa .
PFX NF 0 gunaa .
PFX NF 0 ogunaa .
PFX NF 0 ginaa .
PFX NF 0 eginaa .
PFX NF 0 enaa .
PFX NF 0 zinaa .
PFX NF 0 ezinaa .
PFX NF 0 kinaa .
PFX NF 0 ekinaa .
PFX NF 0 binaa .
PFX NF 0 ebinaa .
PFX NF 0 linaa .
PFX NF 0 elinaa .
PFX NF 0 ganaa .
PFX NF 0 aganaa .
PFX NF 0 kanaa .
PFX NF 0 akanaa .
PFX NF 0 bunaa .
PFX NF 0 obunaa .
PFX NF 0 lunaa .
PFX NF 0 olunaa .
PFX NF 0 zinaa .
PFX NF 0 ezinaa .
PFX NF 0 kunaa .
PFX NF 0 okunaa .
PFX NF 0 ganaa .
PFX NF 0 ogunaa .
PFX NF 0 tunaa .
PFX NF 0 otunaa ."""

rule_right_raw = """
PFX Ob Y 18
PFX Ob 0 n [^lmnb]
PFX Ob l nd l.[^mn]
PFX Ob l nn l.[mn]
PFX Ob w mp [w]
PFX Ob 0 mu .
PFX Ob 0 ba .
PFX Ob 0 gu .
PFX Ob 0 gi .
PFX Ob 0 zi .
PFX Ob 0 ki .
PFX Ob 0 bi .
PFX Ob 0 li .
PFX Ob 0 ga .
PFX Ob 0 ka .
PFX Ob 0 bu .
PFX Ob 0 lu .
PFX Ob 0 ku .
PFX Ob 0 tu ."""

FLAG_DESCRIPTIONS = {
    "NF": "NF",
    "Ob": "Object markers",
}

def parse_rules(raw_text):
    rules = []
    for line in raw_text.strip().split('\n'):
        s = line.strip()
        if not s or s.startswith('#'):
            continue
        s = s.split('#', 1)[0].strip()
        parts = s.split()
        if len(parts) < 4:
            continue
        if parts[2] == 'Y':
            continue
        cond = parts[4] if len(parts) > 4 else '.'
        rules.append({'strip': parts[2], 'add': parts[3], 'cond': cond})
    return rules

def generate_block():
    lefts = parse_rules(rule_left_raw)
    rights = parse_rules(rule_right_raw)
    new_rules = []

    for left in lefts:
        for right in rights:
            if left['strip'] != '0':
                if not right['add'].startswith(left['strip']):
                    continue
                combined = left['add'] + right['add'][len(left['strip']):]
            else:
                combined = left['add'] + right['add']

            if left['cond'] != '.':
                if not re.match(left['cond'], right['add']):
                    continue

            new_rules.append({'strip': right['strip'], 'add': combined, 'cond': right['cond']})

    out_flag = "QQ"
    left_desc = FLAG_DESCRIPTIONS.get("NF", "NF")
    right_desc = FLAG_DESCRIPTIONS.get("Ob", "Ob")
    comment_line = "# Cross product of {} ({}) and {} ({}) to {}".format(
        "NF", left_desc, "Ob", right_desc, out_flag
    )

    output = ["PFX {} Y {}".format(out_flag, len(new_rules))]
    for r in new_rules:
        output.append("PFX {} {} {} {}".format(out_flag, r['strip'], r['add'], r['cond']))

    return (out_flag, "\n".join([comment_line] + output) + "\n")

def main():
    if not os.path.exists(AFF_FILE):
        print("Error: {} not found.".format(AFF_FILE))
        return

    out_flag, block = generate_block()

    with open(AFF_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    first_flag_idx = None
    last_flag_idx = None

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("PFX {} ".format(out_flag)):
            if first_flag_idx is None:
                first_flag_idx = i
            last_flag_idx = i

    if first_flag_idx is not None and first_flag_idx > 0:
        prev_line = lines[first_flag_idx - 1].strip()
        if prev_line.startswith("# Cross product"):
            start_idx = first_flag_idx - 1
        else:
            start_idx = first_flag_idx
    elif first_flag_idx is not None:
        start_idx = first_flag_idx
    else:
        start_idx = None

    if start_idx is not None and last_flag_idx is not None:
        new_lines = lines[:start_idx] + [block] + lines[last_flag_idx + 1:]
    else:
        new_lines = lines
        if new_lines and not new_lines[-1].endswith(chr(10)):
            new_lines[-1] += chr(10)
        new_lines.append(block)

    with open(AFF_FILE, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

    print("{}: updated in place.".format(out_flag))

if __name__ == '__main__':
    main()
