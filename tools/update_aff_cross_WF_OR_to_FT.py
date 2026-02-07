import re
import os
from pathlib import Path

# Cross product generator: WF x OR => FT
# Description:
# - Left block `WF`: Subordinating conjunction when with subjects in far future tense
# - Right block `OR`: Special reflexive object markers
# - Output flag `FT`: Cross-product prefixes for WF x OR

REPO_ROOT = Path(__file__).resolve().parents[1]
AFF_FILE = REPO_ROOT / "Luganda.aff"

# If set to a flag name (e.g. "HB"), the generated cross-product block will be inserted
# immediately before the first "PFX <flag>" line when the output flag block doesn't
# already exist in the .aff.
INSERT_BEFORE_FLAG = "".strip() or None

rule_left_raw = """
PFX WF Y 160
PFX WF 0 wendi . 
PFX WF 0 wetuli . 
PFX WF 0 wemuli . 
PFX WF 0 webali . 
PFX WF 0 weguli .
PFX WF 0 wegili .
PFX WF 0 wezili .
PFX WF 0 wekili .
PFX WF 0 webili .
PFX WF 0 welili .
PFX WF 0 wegali .
PFX WF 0 wekali .
PFX WF 0 webuli .
PFX WF 0 weluli .
PFX WF 0 wekuli .
PFX WF 0 wetuli .
PFX WF 0 bwendi . 
PFX WF 0 bwetuli . 
PFX WF 0 bwemuli . 
PFX WF 0 bwebali . 
PFX WF 0 bweguli .
PFX WF 0 bwegili .
PFX WF 0 bwezili .
PFX WF 0 bwekili .
PFX WF 0 bwebili .
PFX WF 0 bwelili .
PFX WF 0 bwegali .
PFX WF 0 bwekali .
PFX WF 0 bwebuli .
PFX WF 0 bweluli .
PFX WF 0 bwekuli .
PFX WF 0 bwetuli .
PFX WF 0 lwendi . 
PFX WF 0 lwetuli . 
PFX WF 0 lwemuli . 
PFX WF 0 lwebali . 
PFX WF 0 lweguli .
PFX WF 0 lwegili .
PFX WF 0 lwezili .
PFX WF 0 lwekili .
PFX WF 0 lwebili .
PFX WF 0 lwelili .
PFX WF 0 lwegali .
PFX WF 0 lwekali .
PFX WF 0 lwebuli .
PFX WF 0 lweluli .
PFX WF 0 lwekuli .
PFX WF 0 lwetuli .
PFX WF 0 zendi . 
PFX WF 0 zetuli . 
PFX WF 0 zemuli . 
PFX WF 0 zebali . 
PFX WF 0 zeguli .
PFX WF 0 zegili .
PFX WF 0 zezili .
PFX WF 0 zekili .
PFX WF 0 zebili .
PFX WF 0 zelili .
PFX WF 0 zegali .
PFX WF 0 zekali .
PFX WF 0 zebuli .
PFX WF 0 zeluli .
PFX WF 0 zekuli .
PFX WF 0 zetuli .
PFX WF 0 gwendi . 
PFX WF 0 gwetuli . 
PFX WF 0 gwemuli . 
PFX WF 0 gwebali . 
PFX WF 0 gweguli .
PFX WF 0 gwegili .
PFX WF 0 gwezili .
PFX WF 0 gwekili .
PFX WF 0 gwebili .
PFX WF 0 gwelili .
PFX WF 0 gwegali .
PFX WF 0 gwekali .
PFX WF 0 gwebuli .
PFX WF 0 gweluli .
PFX WF 0 gwekuli .
PFX WF 0 gwetuli .
PFX WF 0 gyendi . 
PFX WF 0 gyetuli . 
PFX WF 0 gyemuli . 
PFX WF 0 gyebali . 
PFX WF 0 gyeguli .
PFX WF 0 gyegili .
PFX WF 0 gyezili .
PFX WF 0 gyekili .
PFX WF 0 gyebili .
PFX WF 0 gyelili .
PFX WF 0 gyegali .
PFX WF 0 gyekali .
PFX WF 0 gyebuli .
PFX WF 0 gyeluli .
PFX WF 0 gyekuli .
PFX WF 0 gyetuli .
PFX WF 0 kyendi . 
PFX WF 0 kyetuli . 
PFX WF 0 kyemuli . 
PFX WF 0 kyebali . 
PFX WF 0 kyeguli .
PFX WF 0 kyegili .
PFX WF 0 kyezili .
PFX WF 0 kyekili .
PFX WF 0 kyebili .
PFX WF 0 kyelili .
PFX WF 0 kyegali .
PFX WF 0 kyekali .
PFX WF 0 kyebuli .
PFX WF 0 kyeluli .
PFX WF 0 kyekuli .
PFX WF 0 kyetuli .
PFX WF 0 byendi . 
PFX WF 0 byetuli . 
PFX WF 0 byemuli . 
PFX WF 0 byebali . 
PFX WF 0 byeguli .
PFX WF 0 byegili .
PFX WF 0 byezili .
PFX WF 0 byekili .
PFX WF 0 byebili .
PFX WF 0 byelili .
PFX WF 0 byegali .
PFX WF 0 byekali .
PFX WF 0 byebuli .
PFX WF 0 byeluli .
PFX WF 0 byekuli .
PFX WF 0 byetuli .
PFX WF 0 lyendi . 
PFX WF 0 lyetuli . 
PFX WF 0 lyemuli . 
PFX WF 0 lyebali . 
PFX WF 0 lyeguli .
PFX WF 0 lyegili .
PFX WF 0 lyezili .
PFX WF 0 lyekili .
PFX WF 0 lyebili .
PFX WF 0 lyelili .
PFX WF 0 lyegali .
PFX WF 0 lyekali .
PFX WF 0 lyebuli .
PFX WF 0 lyeluli .
PFX WF 0 lyekuli .
PFX WF 0 lyetuli .
PFX WF 0 kendi . 
PFX WF 0 ketuli . 
PFX WF 0 kemuli . 
PFX WF 0 kebali . 
PFX WF 0 keguli .
PFX WF 0 kegili .
PFX WF 0 kezili .
PFX WF 0 kekili .
PFX WF 0 kebili .
PFX WF 0 kelili .
PFX WF 0 kegali .
PFX WF 0 kekali .
PFX WF 0 kebuli .
PFX WF 0 keluli .
PFX WF 0 kekuli .
PFX WF 0 ketuli ."""

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
    "WF": "Subordinating conjunction when with subjects in far future tense",
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

    out_flag = "FT"
    left_desc = FLAG_DESCRIPTIONS.get("WF", "WF")
    right_desc = FLAG_DESCRIPTIONS.get("OR", "OR")
    comment_line = "# Cross product of {} ({}) and {} ({}) to {}".format(
        "WF", left_desc, "OR", right_desc, out_flag
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
