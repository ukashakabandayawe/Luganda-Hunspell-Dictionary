import re
import os
from pathlib import Path

# Cross product generator: BI x OR => IG
# Description:
# - Left block `BI`: BI
# - Right block `OR`: Special reflexive object markers
# - Output flag `IG`: Cross-product prefixes for BI x OR

REPO_ROOT = Path(__file__).resolve().parents[1]
AFF_FILE = REPO_ROOT / "Luganda.aff"

# If set to a flag name (e.g. "HB"), the generated cross-product block will be inserted
# immediately before the first "PFX <flag>" line when the output flag block doesn't
# already exist in the .aff.
INSERT_BEFORE_FLAG = "".strip() or None

rule_left_raw = """
PFX BI Y 320
PFX BI 0 bendi .
PFX BI 0 betuli .
PFX BI 0 bemuli .
PFX BI 0 bebali .
PFX BI 0 bebali .
PFX BI 0 beguli .
PFX BI 0 begili .
PFX BI 0 bezili .
PFX BI 0 bekili .
PFX BI 0 bebili .
PFX BI 0 belili .
PFX BI 0 begali .
PFX BI 0 bekali .
PFX BI 0 bebuli .
PFX BI 0 beluli .
PFX BI 0 bezili .
PFX BI 0 bekuli .
PFX BI 0 begali .
PFX BI 0 begali .
PFX BI 0 betuli .
PFX BI 0 gwendi .
PFX BI 0 gwetuli .
PFX BI 0 gwemuli .
PFX BI 0 gwebali .
PFX BI 0 gwebali .
PFX BI 0 gweguli .
PFX BI 0 gwegili .
PFX BI 0 gwezili .
PFX BI 0 gwekili .
PFX BI 0 gwebili .
PFX BI 0 gwelili .
PFX BI 0 gwegali .
PFX BI 0 gwekali .
PFX BI 0 gwebuli .
PFX BI 0 gweluli .
PFX BI 0 gwezili .
PFX BI 0 gwekuli .
PFX BI 0 gwegali .
PFX BI 0 gwegali .
PFX BI 0 gwetuli .
PFX BI 0 gyendi .
PFX BI 0 gyetuli .
PFX BI 0 gyemuli .
PFX BI 0 gyebali .
PFX BI 0 gyebali .
PFX BI 0 gyeguli .
PFX BI 0 gyegili .
PFX BI 0 gyezili .
PFX BI 0 gyekili .
PFX BI 0 gyebili .
PFX BI 0 gyelili .
PFX BI 0 gyegali .
PFX BI 0 gyekali .
PFX BI 0 gyebuli .
PFX BI 0 gyeluli .
PFX BI 0 gyezili .
PFX BI 0 gyekuli .
PFX BI 0 gyegali .
PFX BI 0 gyegali .
PFX BI 0 gyetuli .
PFX BI 0 zendi .
PFX BI 0 zetuli .
PFX BI 0 zemuli .
PFX BI 0 zebali .
PFX BI 0 zebali .
PFX BI 0 zeguli .
PFX BI 0 zegili .
PFX BI 0 zezili .
PFX BI 0 zekili .
PFX BI 0 zebili .
PFX BI 0 zelili .
PFX BI 0 zegali .
PFX BI 0 zekali .
PFX BI 0 zebuli .
PFX BI 0 zeluli .
PFX BI 0 zezili .
PFX BI 0 zekuli .
PFX BI 0 zegali .
PFX BI 0 zegali .
PFX BI 0 zetuli .
PFX BI 0 kyendi .
PFX BI 0 kyetuli .
PFX BI 0 kyemuli .
PFX BI 0 kyebali .
PFX BI 0 kyebali .
PFX BI 0 kyeguli .
PFX BI 0 kyegili .
PFX BI 0 kyezili .
PFX BI 0 kyekili .
PFX BI 0 kyebili .
PFX BI 0 kyelili .
PFX BI 0 kyegali .
PFX BI 0 kyekali .
PFX BI 0 kyebuli .
PFX BI 0 kyeluli .
PFX BI 0 kyezili .
PFX BI 0 kyekuli .
PFX BI 0 kyegali .
PFX BI 0 kyegali .
PFX BI 0 kyetuli .
PFX BI 0 kyendi .
PFX BI 0 kyetuli .
PFX BI 0 kyemuli .
PFX BI 0 kyebali .
PFX BI 0 kyebali .
PFX BI 0 kyeguli .
PFX BI 0 kyegili .
PFX BI 0 kyezili .
PFX BI 0 kyekili .
PFX BI 0 kyebili .
PFX BI 0 kyelili .
PFX BI 0 kyegali .
PFX BI 0 kyekali .
PFX BI 0 kyebuli .
PFX BI 0 kyeluli .
PFX BI 0 kyezili .
PFX BI 0 kyekuli .
PFX BI 0 kyegali .
PFX BI 0 kyegali .
PFX BI 0 kyetuli .
PFX BI 0 byendi .
PFX BI 0 byetuli .
PFX BI 0 byemuli .
PFX BI 0 byebali .
PFX BI 0 byebali .
PFX BI 0 byeguli .
PFX BI 0 byegili .
PFX BI 0 byezili .
PFX BI 0 byekili .
PFX BI 0 byebili .
PFX BI 0 byelili .
PFX BI 0 byegali .
PFX BI 0 byekali .
PFX BI 0 byebuli .
PFX BI 0 byeluli .
PFX BI 0 byezili .
PFX BI 0 byekuli .
PFX BI 0 byegali .
PFX BI 0 byegali .
PFX BI 0 byetuli .
PFX BI 0 lyendi .
PFX BI 0 lyetuli .
PFX BI 0 lyemuli .
PFX BI 0 lyebali .
PFX BI 0 lyebali .
PFX BI 0 lyeguli .
PFX BI 0 lyegili .
PFX BI 0 lyezili .
PFX BI 0 lyekili .
PFX BI 0 lyebili .
PFX BI 0 lyelili .
PFX BI 0 lyegali .
PFX BI 0 lyekali .
PFX BI 0 lyebuli .
PFX BI 0 lyeluli .
PFX BI 0 lyezili .
PFX BI 0 lyekuli .
PFX BI 0 lyegali .
PFX BI 0 lyegali .
PFX BI 0 lyetuli .
PFX BI 0 gendi .
PFX BI 0 getuli .
PFX BI 0 gemuli .
PFX BI 0 gebali .
PFX BI 0 gebali .
PFX BI 0 geguli .
PFX BI 0 gegili .
PFX BI 0 gezili .
PFX BI 0 gekili .
PFX BI 0 gebili .
PFX BI 0 gelili .
PFX BI 0 gegali .
PFX BI 0 gekali .
PFX BI 0 gebuli .
PFX BI 0 geluli .
PFX BI 0 gezili .
PFX BI 0 gekuli .
PFX BI 0 gegali .
PFX BI 0 gegali .
PFX BI 0 getuli .
PFX BI 0 kendi .
PFX BI 0 ketuli .
PFX BI 0 kemuli .
PFX BI 0 kebali .
PFX BI 0 kebali .
PFX BI 0 keguli .
PFX BI 0 kegili .
PFX BI 0 kezili .
PFX BI 0 kekili .
PFX BI 0 kebili .
PFX BI 0 kelili .
PFX BI 0 kegali .
PFX BI 0 kekali .
PFX BI 0 kebuli .
PFX BI 0 keluli .
PFX BI 0 kezili .
PFX BI 0 kekuli .
PFX BI 0 kegali .
PFX BI 0 kegali .
PFX BI 0 ketuli .
PFX BI 0 bwendi .
PFX BI 0 bwetuli .
PFX BI 0 bwemuli .
PFX BI 0 bwebali .
PFX BI 0 bwebali .
PFX BI 0 bweguli .
PFX BI 0 bwegili .
PFX BI 0 bwezili .
PFX BI 0 bwekili .
PFX BI 0 bwebili .
PFX BI 0 bwelili .
PFX BI 0 bwegali .
PFX BI 0 bwekali .
PFX BI 0 bwebuli .
PFX BI 0 bweluli .
PFX BI 0 bwezili .
PFX BI 0 bwekuli .
PFX BI 0 bwegali .
PFX BI 0 bwegali .
PFX BI 0 bwetuli .
PFX BI 0 lwendi .
PFX BI 0 lwetuli .
PFX BI 0 lwemuli .
PFX BI 0 lwebali .
PFX BI 0 lwebali .
PFX BI 0 lweguli .
PFX BI 0 lwegili .
PFX BI 0 lwezili .
PFX BI 0 lwekili .
PFX BI 0 lwebili .
PFX BI 0 lwelili .
PFX BI 0 lwegali .
PFX BI 0 lwekali .
PFX BI 0 lwebuli .
PFX BI 0 lweluli .
PFX BI 0 lwezili .
PFX BI 0 lwekuli .
PFX BI 0 lwegali .
PFX BI 0 lwegali .
PFX BI 0 lwetuli .
PFX BI 0 zendi .
PFX BI 0 zetuli .
PFX BI 0 zemuli .
PFX BI 0 zebali .
PFX BI 0 zebali .
PFX BI 0 zeguli .
PFX BI 0 zegili .
PFX BI 0 zezili .
PFX BI 0 zekili .
PFX BI 0 zebili .
PFX BI 0 zelili .
PFX BI 0 zegali .
PFX BI 0 zekali .
PFX BI 0 zebuli .
PFX BI 0 zeluli .
PFX BI 0 zezili .
PFX BI 0 zekuli .
PFX BI 0 zegali .
PFX BI 0 zegali .
PFX BI 0 zetuli .
PFX BI 0 kwendi .
PFX BI 0 kwetuli .
PFX BI 0 kwemuli .
PFX BI 0 kwebali .
PFX BI 0 kwebali .
PFX BI 0 kweguli .
PFX BI 0 kwegili .
PFX BI 0 kwezili .
PFX BI 0 kwekili .
PFX BI 0 kwebili .
PFX BI 0 kwelili .
PFX BI 0 kwegali .
PFX BI 0 kwekali .
PFX BI 0 kwebuli .
PFX BI 0 kweluli .
PFX BI 0 kwezili .
PFX BI 0 kwekuli .
PFX BI 0 kwegali .
PFX BI 0 kwegali .
PFX BI 0 kwetuli .
PFX BI 0 gendi .
PFX BI 0 getuli .
PFX BI 0 gemuli .
PFX BI 0 gebali .
PFX BI 0 gebali .
PFX BI 0 geguli .
PFX BI 0 gegili .
PFX BI 0 gezili .
PFX BI 0 gekili .
PFX BI 0 gebili .
PFX BI 0 gelili .
PFX BI 0 gegali .
PFX BI 0 gekali .
PFX BI 0 gebuli .
PFX BI 0 geluli .
PFX BI 0 gezili .
PFX BI 0 gekuli .
PFX BI 0 gegali .
PFX BI 0 gegali .
PFX BI 0 getuli .
PFX BI 0 twendi .
PFX BI 0 twetuli .
PFX BI 0 twemuli .
PFX BI 0 twebali .
PFX BI 0 twebali .
PFX BI 0 tweguli .
PFX BI 0 twegili .
PFX BI 0 twezili .
PFX BI 0 twekili .
PFX BI 0 twebili .
PFX BI 0 twelili .
PFX BI 0 twegali .
PFX BI 0 twekali .
PFX BI 0 twebuli .
PFX BI 0 tweluli .
PFX BI 0 twezili .
PFX BI 0 twekuli .
PFX BI 0 twegali .
PFX BI 0 twegali .
PFX BI 0 twetuli ."""

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
    "BI": "BI",
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

    out_flag = "IG"
    left_desc = FLAG_DESCRIPTIONS.get("BI", "BI")
    right_desc = FLAG_DESCRIPTIONS.get("OR", "OR")
    comment_line = "# Cross product of {} ({}) and {} ({}) to {}".format(
        "BI", left_desc, "OR", right_desc, out_flag
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
