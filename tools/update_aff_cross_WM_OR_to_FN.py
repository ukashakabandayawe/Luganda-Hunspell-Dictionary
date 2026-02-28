import re
import os
from pathlib import Path

# Cross product generator: WM x OR => FN
# Description:
# - Left block `WM`: Subordinating conjunction when with subjects in near future tense
# - Right block `OR`: Special reflexive object markers
# - Output flag `FN`: Cross-product prefixes for WM x OR

REPO_ROOT = Path(__file__).resolve().parents[1]
AFF_FILE = REPO_ROOT / "Luganda.aff"

# If set to a flag name (e.g. "HB"), the generated cross-product block will be inserted
# immediately before the first "PFX <flag>" line when the output flag block doesn't
# already exist in the .aff.
INSERT_BEFORE_FLAG = "".strip() or None

rule_left_raw = """
PFX WM Y 230
PFX WM 0 w'onoo .
PFX WM 0 w'onaa .
PFX WM 0 w'anaa .
PFX WM 0 w'enaa .
PFX WM 0 wennaa .
PFX WM 0 wemunaa .
PFX WM 0 wetunaa .
PFX WM 0 wemunaa .
PFX WM 0 webanaa .
PFX WM 0 wegunaa .
PFX WM 0 weginaa .
PFX WM 0 wezinaa .
PFX WM 0 wekinaa .
PFX WM 0 webinaa .
PFX WM 0 welinaa .
PFX WM 0 weganaa .
PFX WM 0 wekanaa .
PFX WM 0 webunaa .
PFX WM 0 welunaa .
PFX WM 0 wezinaa .
PFX WM 0 wekunaa .
PFX WM 0 weganaa .
PFX WM 0 wetunaa .
PFX WM 0 bw'onoo .
PFX WM 0 bw'onaa .
PFX WM 0 bw'anaa .
PFX WM 0 bw'enaa .
PFX WM 0 bwennaa .
PFX WM 0 bwemunaa .
PFX WM 0 bwetunaa .
PFX WM 0 bwemunaa .
PFX WM 0 bwebanaa .
PFX WM 0 bwegunaa .
PFX WM 0 bweginaa .
PFX WM 0 bwezinaa .
PFX WM 0 bwekinaa .
PFX WM 0 bwebinaa .
PFX WM 0 bwelinaa .
PFX WM 0 bweganaa .
PFX WM 0 bwekanaa .
PFX WM 0 bwebunaa .
PFX WM 0 bwelunaa .
PFX WM 0 bwezinaa .
PFX WM 0 bwekunaa .
PFX WM 0 bweganaa .
PFX WM 0 bwetunaa .
PFX WM 0 lw'onoo .
PFX WM 0 lw'onaa .
PFX WM 0 lw'anaa .
PFX WM 0 lw'enaa .
PFX WM 0 lwennaa .
PFX WM 0 lwemunaa .
PFX WM 0 lwetunaa .
PFX WM 0 lwemunaa .
PFX WM 0 lwebanaa .
PFX WM 0 lwegunaa .
PFX WM 0 lweginaa .
PFX WM 0 lwezinaa .
PFX WM 0 lwekinaa .
PFX WM 0 lwebinaa .
PFX WM 0 lwelinaa .
PFX WM 0 lweganaa .
PFX WM 0 lwekanaa .
PFX WM 0 lwebunaa .
PFX WM 0 lwelunaa .
PFX WM 0 lwezinaa .
PFX WM 0 lwekunaa .
PFX WM 0 lweganaa .
PFX WM 0 lwetunaa .
PFX WM 0 z'onoo .
PFX WM 0 z'onaa .
PFX WM 0 z'anaa .
PFX WM 0 z'enaa .
PFX WM 0 zennaa .
PFX WM 0 zemunaa .
PFX WM 0 zetunaa .
PFX WM 0 zemunaa .
PFX WM 0 zebanaa .
PFX WM 0 zegunaa .
PFX WM 0 zeginaa .
PFX WM 0 zezinaa .
PFX WM 0 zekinaa .
PFX WM 0 zebinaa .
PFX WM 0 zelinaa .
PFX WM 0 zeganaa .
PFX WM 0 zekanaa .
PFX WM 0 zebunaa .
PFX WM 0 zelunaa .
PFX WM 0 zezinaa .
PFX WM 0 zekunaa .
PFX WM 0 zeganaa .
PFX WM 0 zetunaa .
PFX WM 0 gw'onoo .
PFX WM 0 gw'onaa .
PFX WM 0 gw'anaa .
PFX WM 0 gw'enaa .
PFX WM 0 gwennaa .
PFX WM 0 gwemunaa .
PFX WM 0 gwetunaa .
PFX WM 0 gwemunaa .
PFX WM 0 gwebanaa .
PFX WM 0 gwegunaa .
PFX WM 0 gweginaa .
PFX WM 0 gwezinaa .
PFX WM 0 gwekinaa .
PFX WM 0 gwebinaa .
PFX WM 0 gwelinaa .
PFX WM 0 gweganaa .
PFX WM 0 gwekanaa .
PFX WM 0 gwebunaa .
PFX WM 0 gwelunaa .
PFX WM 0 gwezinaa .
PFX WM 0 gwekunaa .
PFX WM 0 gweganaa .
PFX WM 0 gwetunaa .
PFX WM 0 gy'onoo .
PFX WM 0 gy'onaa .
PFX WM 0 gy'anaa .
PFX WM 0 gy'enaa .
PFX WM 0 gyennaa .
PFX WM 0 gyemunaa .
PFX WM 0 gyetunaa .
PFX WM 0 gyemunaa .
PFX WM 0 gyebanaa .
PFX WM 0 gyegunaa .
PFX WM 0 gyeginaa .
PFX WM 0 gyezinaa .
PFX WM 0 gyekinaa .
PFX WM 0 gyebinaa .
PFX WM 0 gyelinaa .
PFX WM 0 gyeganaa .
PFX WM 0 gyekanaa .
PFX WM 0 gyebunaa .
PFX WM 0 gyelunaa .
PFX WM 0 gyezinaa .
PFX WM 0 gyekunaa .
PFX WM 0 gyeganaa .
PFX WM 0 gyetunaa .
PFX WM 0 ky'onoo .
PFX WM 0 ky'onaa .
PFX WM 0 ky'anaa .
PFX WM 0 ky'enaa .
PFX WM 0 kyennaa .
PFX WM 0 kyemunaa .
PFX WM 0 kyetunaa .
PFX WM 0 kyemunaa .
PFX WM 0 kyebanaa .
PFX WM 0 kyegunaa .
PFX WM 0 kyeginaa .
PFX WM 0 kyezinaa .
PFX WM 0 kyekinaa .
PFX WM 0 kyebinaa .
PFX WM 0 kyelinaa .
PFX WM 0 kyeganaa .
PFX WM 0 kyekanaa .
PFX WM 0 kyebunaa .
PFX WM 0 kyelunaa .
PFX WM 0 kyezinaa .
PFX WM 0 kyekunaa .
PFX WM 0 kyeganaa .
PFX WM 0 kyetunaa .
PFX WM 0 by'onoo .
PFX WM 0 by'onaa .
PFX WM 0 by'anaa .
PFX WM 0 by'enaa .
PFX WM 0 byennaa .
PFX WM 0 byemunaa .
PFX WM 0 byetunaa .
PFX WM 0 byemunaa .
PFX WM 0 byebanaa .
PFX WM 0 byegunaa .
PFX WM 0 byeginaa .
PFX WM 0 byezinaa .
PFX WM 0 byekinaa .
PFX WM 0 byebinaa .
PFX WM 0 byelinaa .
PFX WM 0 byeganaa .
PFX WM 0 byekanaa .
PFX WM 0 byebunaa .
PFX WM 0 byelunaa .
PFX WM 0 byezinaa .
PFX WM 0 byekunaa .
PFX WM 0 byeganaa .
PFX WM 0 byetunaa .
PFX WM 0 ly'onoo .
PFX WM 0 ly'onaa .
PFX WM 0 ly'anaa .
PFX WM 0 ly'enaa .
PFX WM 0 lyennaa .
PFX WM 0 lyemunaa .
PFX WM 0 lyetunaa .
PFX WM 0 lyemunaa .
PFX WM 0 lyebanaa .
PFX WM 0 lyegunaa .
PFX WM 0 lyeginaa .
PFX WM 0 lyezinaa .
PFX WM 0 lyekinaa .
PFX WM 0 lyebinaa .
PFX WM 0 lyelinaa .
PFX WM 0 lyeganaa .
PFX WM 0 lyekanaa .
PFX WM 0 lyebunaa .
PFX WM 0 lyelunaa .
PFX WM 0 lyezinaa .
PFX WM 0 lyekunaa .
PFX WM 0 lyeganaa .
PFX WM 0 lyetunaa .
PFX WM 0 k'onoo .
PFX WM 0 k'onaa .
PFX WM 0 k'anaa .
PFX WM 0 k'enaa .
PFX WM 0 kennaa .
PFX WM 0 kemunaa .
PFX WM 0 ketunaa .
PFX WM 0 kemunaa .
PFX WM 0 kebanaa .
PFX WM 0 kegunaa .
PFX WM 0 keginaa .
PFX WM 0 kezinaa .
PFX WM 0 kekinaa .
PFX WM 0 kebinaa .
PFX WM 0 kelinaa .
PFX WM 0 keganaa .
PFX WM 0 kekanaa .
PFX WM 0 kebunaa .
PFX WM 0 kelunaa .
PFX WM 0 kezinaa .
PFX WM 0 kekunaa .
PFX WM 0 keganaa .
PFX WM 0 ketunaa ."""

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
    "WM": "Subordinating conjunction when with subjects in near future tense",
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

    out_flag = "FN"
    left_desc = FLAG_DESCRIPTIONS.get("WM", "WM")
    right_desc = FLAG_DESCRIPTIONS.get("OR", "OR")
    comment_line = "# Cross product of {} ({}) and {} ({}) to {}".format(
        "WM", left_desc, "OR", right_desc, out_flag
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
