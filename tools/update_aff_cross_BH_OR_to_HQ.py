import re
import os
from pathlib import Path

# Cross product generator: BH x OR => HQ
# Description:
# - Left block `BH`: BH
# - Right block `OR`: Special reflexive object markers
# - Output flag `HQ`: Cross-product prefixes for BH x OR

REPO_ROOT = Path(__file__).resolve().parents[1]
AFF_FILE = REPO_ROOT / "Luganda.aff"

# If set to a flag name (e.g. "HB"), the generated cross-product block will be inserted
# immediately before the first "PFX <flag>" line when the output flag block doesn't
# already exist in the .aff.
INSERT_BEFORE_FLAG = "".strip() or None

rule_left_raw = """
PFX BH Y 195
PFX BH 0 bemunaa .
PFX BH 0 betunaa .
PFX BH 0 bebanaa .
PFX BH 0 begunaa .
PFX BH 0 beginaa .
PFX BH 0 bezinaa .
PFX BH 0 bekinaa .
PFX BH 0 bebinaa .
PFX BH 0 belinaa .
PFX BH 0 beganaa .
PFX BH 0 bekanaa .
PFX BH 0 bebunaa .
PFX BH 0 belunaa .
PFX BH 0 bekunaa .
PFX BH 0 gwemunaa .
PFX BH 0 gwetunaa .
PFX BH 0 gwebanaa .
PFX BH 0 gwegunaa .
PFX BH 0 gweginaa .
PFX BH 0 gwezinaa .
PFX BH 0 gwekinaa .
PFX BH 0 gwebinaa .
PFX BH 0 gwelinaa .
PFX BH 0 gweganaa .
PFX BH 0 gwekanaa .
PFX BH 0 gwebunaa .
PFX BH 0 gwelunaa .
PFX BH 0 gwekunaa .
PFX BH 0 gyemunaa .
PFX BH 0 gyetunaa .
PFX BH 0 gyebanaa .
PFX BH 0 gyegunaa .
PFX BH 0 gyeginaa .
PFX BH 0 gyezinaa .
PFX BH 0 gyekinaa .
PFX BH 0 gyebinaa .
PFX BH 0 gyelinaa .
PFX BH 0 gyeganaa .
PFX BH 0 gyekanaa .
PFX BH 0 gyebunaa .
PFX BH 0 gyelunaa .
PFX BH 0 gyekunaa .
PFX BH 0 zemunaa .
PFX BH 0 zetunaa .
PFX BH 0 zebanaa .
PFX BH 0 zegunaa .
PFX BH 0 zeginaa .
PFX BH 0 zezinaa .
PFX BH 0 zekinaa .
PFX BH 0 zebinaa .
PFX BH 0 zelinaa .
PFX BH 0 zeganaa .
PFX BH 0 zekanaa .
PFX BH 0 zebunaa .
PFX BH 0 zelunaa .
PFX BH 0 zekunaa .
PFX BH 0 kyemunaa .
PFX BH 0 kyetunaa .
PFX BH 0 kyebanaa .
PFX BH 0 kyegunaa .
PFX BH 0 kyeginaa .
PFX BH 0 kyezinaa .
PFX BH 0 kyekinaa .
PFX BH 0 kyebinaa .
PFX BH 0 kyelinaa .
PFX BH 0 kyeganaa .
PFX BH 0 kyekanaa .
PFX BH 0 kyebunaa .
PFX BH 0 kyelunaa .
PFX BH 0 kyekunaa .
PFX BH 0 byemunaa .
PFX BH 0 byetunaa .
PFX BH 0 byebanaa .
PFX BH 0 byegunaa .
PFX BH 0 byeginaa .
PFX BH 0 byezinaa .
PFX BH 0 byekinaa .
PFX BH 0 byebinaa .
PFX BH 0 byelinaa .
PFX BH 0 byeganaa .
PFX BH 0 byekanaa .
PFX BH 0 byebunaa .
PFX BH 0 byelunaa .
PFX BH 0 byekunaa .
PFX BH 0 lyemunaa .
PFX BH 0 lyetunaa .
PFX BH 0 lyebanaa .
PFX BH 0 lyegunaa .
PFX BH 0 lyeginaa .
PFX BH 0 lyezinaa .
PFX BH 0 lyekinaa .
PFX BH 0 lyebinaa .
PFX BH 0 lyelinaa .
PFX BH 0 lyeganaa .
PFX BH 0 lyekanaa .
PFX BH 0 lyebunaa .
PFX BH 0 lyelunaa .
PFX BH 0 lyekunaa .
PFX BH 0 gemunaa .
PFX BH 0 getunaa .
PFX BH 0 gebanaa .
PFX BH 0 gegunaa .
PFX BH 0 geginaa .
PFX BH 0 gezinaa .
PFX BH 0 gekinaa .
PFX BH 0 gebinaa .
PFX BH 0 gelinaa .
PFX BH 0 geganaa .
PFX BH 0 gekanaa .
PFX BH 0 gebunaa .
PFX BH 0 gelunaa .
PFX BH 0 gekunaa .
PFX BH 0 kemunaa .
PFX BH 0 ketunaa .
PFX BH 0 kebanaa .
PFX BH 0 kegunaa .
PFX BH 0 keginaa .
PFX BH 0 kezinaa .
PFX BH 0 kekinaa .
PFX BH 0 kebinaa .
PFX BH 0 kelinaa .
PFX BH 0 keganaa .
PFX BH 0 kekanaa .
PFX BH 0 kebunaa .
PFX BH 0 kelunaa .
PFX BH 0 kekunaa .
PFX BH 0 bwemunaa .
PFX BH 0 bwetunaa .
PFX BH 0 bwebanaa .
PFX BH 0 bwegunaa .
PFX BH 0 bweginaa .
PFX BH 0 bwezinaa .
PFX BH 0 bwekinaa .
PFX BH 0 bwebinaa .
PFX BH 0 bwelinaa .
PFX BH 0 bweganaa .
PFX BH 0 bwekanaa .
PFX BH 0 bwebunaa .
PFX BH 0 bwelunaa .
PFX BH 0 bwekunaa .
PFX BH 0 lwemunaa .
PFX BH 0 lwetunaa .
PFX BH 0 lwebanaa .
PFX BH 0 lwegunaa .
PFX BH 0 lweginaa .
PFX BH 0 lwezinaa .
PFX BH 0 lwekinaa .
PFX BH 0 lwebinaa .
PFX BH 0 lwelinaa .
PFX BH 0 lweganaa .
PFX BH 0 lwekanaa .
PFX BH 0 lwebunaa .
PFX BH 0 lwelunaa .
PFX BH 0 lwekunaa .
PFX BH 0 kwemunaa .
PFX BH 0 kwetunaa .
PFX BH 0 kwebanaa .
PFX BH 0 kwegunaa .
PFX BH 0 kweginaa .
PFX BH 0 kwezinaa .
PFX BH 0 kwekinaa .
PFX BH 0 kwebinaa .
PFX BH 0 kwelinaa .
PFX BH 0 kweganaa .
PFX BH 0 kwekanaa .
PFX BH 0 kwebunaa .
PFX BH 0 kwelunaa .
PFX BH 0 kwekunaa .
PFX BH 0 twemunaa .
PFX BH 0 twetunaa .
PFX BH 0 twebanaa .
PFX BH 0 twegunaa .
PFX BH 0 tweginaa .
PFX BH 0 twezinaa .
PFX BH 0 twekinaa .
PFX BH 0 twebinaa .
PFX BH 0 twelinaa .
PFX BH 0 tweganaa .
PFX BH 0 twekanaa .
PFX BH 0 twebunaa .
PFX BH 0 twelunaa .
PFX BH 0 twekunaa .
PFX BH 0 bennaa .
PFX BH 0 gwennaa .
PFX BH 0 gyennaa .
PFX BH 0 zennaa .
PFX BH 0 kyennaa .
PFX BH 0 byennaa .
PFX BH 0 lyennaa .
PFX BH 0 gennaa .
PFX BH 0 kennaa .
PFX BH 0 bwennaa .
PFX BH 0 lwennaa .
PFX BH 0 kwennaa .
PFX BH 0 twennaa ."""

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
    "BH": "BH",
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

    out_flag = "HQ"
    left_desc = FLAG_DESCRIPTIONS.get("BH", "BH")
    right_desc = FLAG_DESCRIPTIONS.get("OR", "OR")
    comment_line = "# Cross product of {} ({}) and {} ({}) to {}".format(
        "BH", left_desc, "OR", right_desc, out_flag
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
