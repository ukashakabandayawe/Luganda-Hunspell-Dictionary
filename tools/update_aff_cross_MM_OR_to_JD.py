import re
import os
from pathlib import Path

# Cross product generator: MM x OR => JD
# Description:
# - Left block `MM`: MM
# - Right block `OR`: Special reflexive object markers
# - Output flag `JD`: Cross-product prefixes for MM x OR

REPO_ROOT = Path(__file__).resolve().parents[1]
AFF_FILE = REPO_ROOT / "Luganda.aff"

# If set to a flag name (e.g. "HB"), the generated cross-product block will be inserted
# immediately before the first "PFX <flag>" line when the output flag block doesn't
# already exist in the .aff.
INSERT_BEFORE_FLAG = "".strip() or None

rule_left_raw = """
PFX MM Y 72
PFX MM 0 okun [^lmnb]
PFX MM l okund l.[^mn]
PFX MM l okunn l.[mn]
PFX MM w okump [w]
PFX MM 0 okumu .
PFX MM 0 okuba .
PFX MM 0 okugu .
PFX MM 0 okugi .
PFX MM 0 okuzi .
PFX MM 0 okuki .
PFX MM 0 okubi .
PFX MM 0 okuli .
PFX MM 0 okuga .
PFX MM 0 okuka .
PFX MM 0 okubu .
PFX MM 0 okulu .
PFX MM 0 okuku .
PFX MM 0 okutu .
PFX MM 0 kun [^lmnb]
PFX MM l kund l.[^mn]
PFX MM l kunn l.[mn]
PFX MM w kump [w]
PFX MM 0 kumu .
PFX MM 0 kuba .
PFX MM 0 kugu .
PFX MM 0 kugi .
PFX MM 0 kuzi .
PFX MM 0 kuki .
PFX MM 0 kubi .
PFX MM 0 kuli .
PFX MM 0 kuga .
PFX MM 0 kuka .
PFX MM 0 kubu .
PFX MM 0 kulu .
PFX MM 0 kuku .
PFX MM 0 kutu .
PFX MM 0 obutan [^lmnb]
PFX MM l obutand l.[^mn]
PFX MM l obutann l.[mn]
PFX MM w obutamp [w]
PFX MM 0 obutamu .
PFX MM 0 obutaba .
PFX MM 0 obutagu .
PFX MM 0 obutagi .
PFX MM 0 obutazi .
PFX MM 0 obutaki .
PFX MM 0 obutabi .
PFX MM 0 obutali .
PFX MM 0 obutaga .
PFX MM 0 obutaka .
PFX MM 0 obutabu .
PFX MM 0 obutalu .
PFX MM 0 obutaku .
PFX MM 0 obutatu .
PFX MM 0 butan [^lmnb]
PFX MM l butand l.[^mn]
PFX MM l butann l.[mn]
PFX MM w butamp [w]
PFX MM 0 butamu .
PFX MM 0 butaba .
PFX MM 0 butagu .
PFX MM 0 butagi .
PFX MM 0 butazi .
PFX MM 0 butaki .
PFX MM 0 butabi .
PFX MM 0 butali .
PFX MM 0 butaga .
PFX MM 0 butaka .
PFX MM 0 butabu .
PFX MM 0 butalu .
PFX MM 0 butaku .
PFX MM 0 butatu ."""

rule_right_raw = """
PFX OR Y 16
PFX OR 0 mwe .
PFX OR 0 bee .
PFX OR 0 gwe .
PFX OR 0 gye .
PFX OR 0 zee .
PFX OR 0 kye .
PFX OR 0 bye .
PFX OR 0 lye .
PFX OR 0 gee .
PFX OR 0 kee .
PFX OR 0 bwe .
PFX OR 0 lwe .
PFX OR 0 zee .
PFX OR 0 kwe .
PFX OR 0 gee .
PFX OR 0 twe ."""

FLAG_DESCRIPTIONS = {
    "MM": "MM",
    "OR": "Special reflexive object markers",
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

    out_flag = "JD"
    left_desc = FLAG_DESCRIPTIONS.get("MM", "MM")
    right_desc = FLAG_DESCRIPTIONS.get("OR", "OR")
    comment_line = "# Cross product of {} ({}) and {} ({}) to {}".format(
        "MM", left_desc, "OR", right_desc, out_flag
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
        # Replace existing block in-place.
        new_lines = lines[:start_idx] + [block] + lines[last_flag_idx + 1:]
    else:
        # Insert before an anchor flag if requested; otherwise append.
        insert_idx = None
        if INSERT_BEFORE_FLAG:
            anchor_prefix = "PFX {} ".format(INSERT_BEFORE_FLAG)
            for i, line in enumerate(lines):
                if line.strip().startswith(anchor_prefix):
                    insert_idx = i
                    # If the anchor PFX block is preceded by one or more cross-product
                    # comment lines, insert before those comments to keep them attached
                    # to the anchor block.
                    while insert_idx > 0 and lines[insert_idx - 1].strip().startswith("# Cross product"):
                        insert_idx -= 1
                    break

        if insert_idx is not None:
            new_lines = lines[:insert_idx] + [block] + lines[insert_idx:]
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
