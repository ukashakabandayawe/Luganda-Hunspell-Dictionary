import re
import os
from pathlib import Path

# Cross product generator: wf x OR => FW
# Description:
# - Left block `wf`: Subordinating conjunction when with negative subjects in far future tense
# - Right block `OR`: Special reflexive object markers
# - Output flag `FW`: Cross-product prefixes for wf x OR

REPO_ROOT = Path(__file__).resolve().parents[1]
AFF_FILE = REPO_ROOT / "Luganda.aff"

# If set to a flag name (e.g. "HB"), the generated cross-product block will be inserted
# immediately before the first "PFX <flag>" line when the output flag block doesn't
# already exist in the .aff.
INSERT_BEFORE_FLAG = "".strip() or None

rule_left_raw = """
PFX wf Y 163
PFX wf 0 wessili .
PFX wf 0 wetutali .
PFX wf 0 wemutali .
PFX wf 0 webatali .
PFX wf 0 wegutali .
PFX wf 0 wegitali .
PFX wf 0 wezitali .
PFX wf 0 wekitali .
PFX wf 0 webitali .
PFX wf 0 welitali .
PFX wf 0 wegatali .
PFX wf 0 wekatali .
PFX wf 0 webutali .
PFX wf 0 welutali .
PFX wf 0 wekutali .
PFX wf 0 wetutali .
PFX wf 0 bwessili .
PFX wf 0 bwetutali .
PFX wf 0 bwemutali .
PFX wf 0 bwebatali .
PFX wf 0 bwegutali .
PFX wf 0 bwegitali .
PFX wf 0 bwezitali .
PFX wf 0 bwekitali .
PFX wf 0 bwebitali .
PFX wf 0 bwelitali .
PFX wf 0 bwegatali .
PFX wf 0 bwekatali .
PFX wf 0 bwebutali .
PFX wf 0 bwelutali .
PFX wf 0 bwekutali .
PFX wf 0 bwetutali .
PFX wf 0 lwessili .
PFX wf 0 lwetutali .
PFX wf 0 lwemutali .
PFX wf 0 lwebatali .
PFX wf 0 lwegutali .
PFX wf 0 lwegitali .
PFX wf 0 lwezitali .
PFX wf 0 lwekitali .
PFX wf 0 lwebitali .
PFX wf 0 lwelitali .
PFX wf 0 lwegatali .
PFX wf 0 lwekatali .
PFX wf 0 lwebutali .
PFX wf 0 lwelutali .
PFX wf 0 lwekutali .
PFX wf 0 lwetutali .
PFX wf 0 zessili .
PFX wf 0 zetutali .
PFX wf 0 zemutali .
PFX wf 0 zebatali .
PFX wf 0 zegutali .
PFX wf 0 zegitali .
PFX wf 0 zezitali .
PFX wf 0 zekitali .
PFX wf 0 zebitali .
PFX wf 0 zelitali .
PFX wf 0 zegatali .
PFX wf 0 zekatali .
PFX wf 0 zebutali .
PFX wf 0 zelutali .
PFX wf 0 zekutali .
PFX wf 0 zetutali .
PFX wf 0 gwessili .
PFX wf 0 gwetutali .
PFX wf 0 gwemutali .
PFX wf 0 gwebatali .
PFX wf 0 gwegutali .
PFX wf 0 gwegitali .
PFX wf 0 gwezitali .
PFX wf 0 gwekitali .
PFX wf 0 gwebitali .
PFX wf 0 gwelitali .
PFX wf 0 gwegatali .
PFX wf 0 gwekatali .
PFX wf 0 gwebutali .
PFX wf 0 gwelutali .
PFX wf 0 gwekutali .
PFX wf 0 gwetutali .
PFX wf 0 gyessili .
PFX wf 0 gyetutali .
PFX wf 0 gyemutali .
PFX wf 0 gyebatali .
PFX wf 0 gyegutali .
PFX wf 0 gyegitali .
PFX wf 0 gyezitali .
PFX wf 0 gyekitali .
PFX wf 0 gyebitali .
PFX wf 0 gyelitali .
PFX wf 0 gyegatali .
PFX wf 0 gyekatali .
PFX wf 0 gyebutali .
PFX wf 0 gyelutali .
PFX wf 0 gyekutali .
PFX wf 0 gyetutali .
PFX wf 0 kyessili .
PFX wf 0 kyetutali .
PFX wf 0 kyemutali .
PFX wf 0 kyebatali .
PFX wf 0 kyegutali .
PFX wf 0 kyegitali .
PFX wf 0 kyezitali .
PFX wf 0 kyekitali .
PFX wf 0 kyebitali .
PFX wf 0 kyelitali .
PFX wf 0 kyegatali .
PFX wf 0 kyekatali .
PFX wf 0 kyebutali .
PFX wf 0 kyelutali .
PFX wf 0 kyekutali .
PFX wf 0 kyetutali .
PFX wf 0 byessili .
PFX wf 0 byetutali .
PFX wf 0 byemutali .
PFX wf 0 byebatali .
PFX wf 0 byegutali .
PFX wf 0 byegitali .
PFX wf 0 byezitali .
PFX wf 0 byekitali .
PFX wf 0 byebitali .
PFX wf 0 byelitali .
PFX wf 0 byegatali .
PFX wf 0 byekatali .
PFX wf 0 byebutali .
PFX wf 0 byelutali .
PFX wf 0 byekutali .
PFX wf 0 byetutali .
PFX wf 0 lyessili .
PFX wf 0 lyetutali .
PFX wf 0 lyemutali .
PFX wf 0 lyebatali .
PFX wf 0 lyegutali .
PFX wf 0 lyegitali .
PFX wf 0 lyezitali .
PFX wf 0 lyekitali .
PFX wf 0 lyebitali .
PFX wf 0 lyelitali .
PFX wf 0 lyegatali .
PFX wf 0 lyekatali .
PFX wf 0 lyebutali .
PFX wf 0 lyelutali .
PFX wf 0 lyekutali .
PFX wf 0 lyetutali .
PFX wf 0 kessili .
PFX wf 0 ketutali .
PFX wf 0 kemutali .
PFX wf 0 kebatali .
PFX wf 0 kegutali .
PFX wf 0 kegitali .
PFX wf 0 kezitali .
PFX wf 0 kekitali .
PFX wf 0 kebitali .
PFX wf 0 kelitali .
PFX wf 0 kegatali .
PFX wf 0 kekatali .
PFX wf 0 kebutali .
PFX wf 0 kelutali .
PFX wf 0 kekutali .
PFX wf 0 ketutali .
PFX wf 0 otoli .
PFX wf 0 atali .
PFX wf 0 eteli ."""

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
    "wf": "Subordinating conjunction when with negative subjects in far future tense",
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

    out_flag = "FW"
    left_desc = FLAG_DESCRIPTIONS.get("wf", "wf")
    right_desc = FLAG_DESCRIPTIONS.get("OR", "OR")
    comment_line = "# Cross product of {} ({}) and {} ({}) to {}".format(
        "wf", left_desc, "OR", right_desc, out_flag
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
