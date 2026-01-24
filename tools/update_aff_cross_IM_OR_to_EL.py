import re
import os
from pathlib import Path

# Auto-generated cross-product script: IM x OR -> EL
# Hardcoded rule blocks captured from Luganda.aff at generation time.

REPO_ROOT = Path(__file__).resolve().parents[1]
AFF_FILE = REPO_ROOT / "Luganda.aff"

rule_left_raw = 'PFX IM Y 21\nPFX IM 0 nnandi .\nPFX IM 0 wandi .\nPFX IM 0 yandi .\nPFX IM 0 twandi .\nPFX IM 0 mwandi .\nPFX IM 0 bandi .\nPFX IM 0 gwandi .\nPFX IM 0 ogwandi .\nPFX IM 0 gyandi .\nPFX IM 0 zandi .\nPFX IM 0 kyandi .\nPFX IM 0 byandi .\nPFX IM 0 lyandi .\nPFX IM 0 gandi .\nPFX IM 0 kandi .\nPFX IM 0 bwandi .\nPFX IM 0 lwandi .\nPFX IM 0 zandi .\nPFX IM 0 kwandi .\nPFX IM 0 gandi .\nPFX IM 0 twandi .'

rule_right_raw = 'PFX OR Y 16\nPFX OR 0 mwe .\n PFX OR 0 bee .\nPFX OR 0 gwe .\nPFX OR 0 gye .\nPFX OR 0 zee .\nPFX OR 0 kye .\nPFX OR 0 bye .\nPFX OR 0 lye .\nPFX OR 0 gee .\nPFX OR 0 kee .\nPFX OR 0 bwe .\nPFX OR 0 lwe .\nPFX OR 0 zee .\nPFX OR 0 kwe .\nPFX OR 0 gee .\nPFX OR 0 twe .'

FLAG_DESCRIPTIONS = {
    "IM": "IM",
    "OR": "OR",
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

    out_flag = "EL"
    left_desc = FLAG_DESCRIPTIONS.get("IM", "IM")
    right_desc = FLAG_DESCRIPTIONS.get("OR", "OR")
    comment_line = "# Cross product of {} ({}) and {} ({}) to {}".format(
        "IM", left_desc, "OR", right_desc, out_flag
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
