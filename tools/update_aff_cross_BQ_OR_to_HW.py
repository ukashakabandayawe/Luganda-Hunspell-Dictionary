import re
import os
from pathlib import Path

# Cross product generator: BQ x OR => HW
# Description:
# - Left block `BQ`: BQ
# - Right block `OR`: Special reflexive object markers
# - Output flag `HW`: Cross-product prefixes for BQ x OR

REPO_ROOT = Path(__file__).resolve().parents[1]
AFF_FILE = REPO_ROOT / "Luganda.aff"

# If set to a flag name (e.g. "HB"), the generated cross-product block will be inserted
# immediately before the first "PFX <flag>" line when the output flag block doesn't
# already exist in the .aff.
INSERT_BEFORE_FLAG = "".strip() or None

rule_left_raw = """
PFX BQ Y 288
PFX BQ 0 besilimuku .
PFX BQ 0 betutalimuku .
PFX BQ 0 bemutalimuku .
PFX BQ 0 bebatalimuku .
PFX BQ 0 begutalimuku .
PFX BQ 0 begitalimuku .
PFX BQ 0 bezitalimuku .
PFX BQ 0 bekitalimuku .
PFX BQ 0 bebitalimuku .
PFX BQ 0 belitalimuku .
PFX BQ 0 begatalimuku .
PFX BQ 0 bekatalimuku .
PFX BQ 0 bebutalimuku .
PFX BQ 0 belutalimuku .
PFX BQ 0 bezitalimuku .
PFX BQ 0 bekutalimuku .
PFX BQ 0 begatalimuku .
PFX BQ 0 betutalimuku .
PFX BQ 0 gwesilimuku .
PFX BQ 0 gwetutalimuku .
PFX BQ 0 gwemutalimuku .
PFX BQ 0 gwebatalimuku .
PFX BQ 0 gwegutalimuku .
PFX BQ 0 gwegitalimuku .
PFX BQ 0 gwezitalimuku .
PFX BQ 0 gwekitalimuku .
PFX BQ 0 gwebitalimuku .
PFX BQ 0 gwelitalimuku .
PFX BQ 0 gwegatalimuku .
PFX BQ 0 gwekatalimuku .
PFX BQ 0 gwebutalimuku .
PFX BQ 0 gwelutalimuku .
PFX BQ 0 gwezitalimuku .
PFX BQ 0 gwekutalimuku .
PFX BQ 0 gwegatalimuku .
PFX BQ 0 gwetutalimuku .
PFX BQ 0 gyesilimuku .
PFX BQ 0 gyetutalimuku .
PFX BQ 0 gyemutalimuku .
PFX BQ 0 gyebatalimuku .
PFX BQ 0 gyegutalimuku .
PFX BQ 0 gyegitalimuku .
PFX BQ 0 gyezitalimuku .
PFX BQ 0 gyekitalimuku .
PFX BQ 0 gyebitalimuku .
PFX BQ 0 gyelitalimuku .
PFX BQ 0 gyegatalimuku .
PFX BQ 0 gyekatalimuku .
PFX BQ 0 gyebutalimuku .
PFX BQ 0 gyelutalimuku .
PFX BQ 0 gyezitalimuku .
PFX BQ 0 gyekutalimuku .
PFX BQ 0 gyegatalimuku .
PFX BQ 0 gyetutalimuku .
PFX BQ 0 zesilimuku .
PFX BQ 0 zetutalimuku .
PFX BQ 0 zemutalimuku .
PFX BQ 0 zebatalimuku .
PFX BQ 0 zegutalimuku .
PFX BQ 0 zegitalimuku .
PFX BQ 0 zezitalimuku .
PFX BQ 0 zekitalimuku .
PFX BQ 0 zebitalimuku .
PFX BQ 0 zelitalimuku .
PFX BQ 0 zegatalimuku .
PFX BQ 0 zekatalimuku .
PFX BQ 0 zebutalimuku .
PFX BQ 0 zelutalimuku .
PFX BQ 0 zezitalimuku .
PFX BQ 0 zekutalimuku .
PFX BQ 0 zegatalimuku .
PFX BQ 0 zetutalimuku .
PFX BQ 0 kyesilimuku .
PFX BQ 0 kyetutalimuku .
PFX BQ 0 kyemutalimuku .
PFX BQ 0 kyebatalimuku .
PFX BQ 0 kyegutalimuku .
PFX BQ 0 kyegitalimuku .
PFX BQ 0 kyezitalimuku .
PFX BQ 0 kyekitalimuku .
PFX BQ 0 kyebitalimuku .
PFX BQ 0 kyelitalimuku .
PFX BQ 0 kyegatalimuku .
PFX BQ 0 kyekatalimuku .
PFX BQ 0 kyebutalimuku .
PFX BQ 0 kyelutalimuku .
PFX BQ 0 kyezitalimuku .
PFX BQ 0 kyekutalimuku .
PFX BQ 0 kyegatalimuku .
PFX BQ 0 kyetutalimuku .
PFX BQ 0 kyesilimuku .
PFX BQ 0 kyetutalimuku .
PFX BQ 0 kyemutalimuku .
PFX BQ 0 kyebatalimuku .
PFX BQ 0 kyegutalimuku .
PFX BQ 0 kyegitalimuku .
PFX BQ 0 kyezitalimuku .
PFX BQ 0 kyekitalimuku .
PFX BQ 0 kyebitalimuku .
PFX BQ 0 kyelitalimuku .
PFX BQ 0 kyegatalimuku .
PFX BQ 0 kyekatalimuku .
PFX BQ 0 kyebutalimuku .
PFX BQ 0 kyelutalimuku .
PFX BQ 0 kyezitalimuku .
PFX BQ 0 kyekutalimuku .
PFX BQ 0 kyegatalimuku .
PFX BQ 0 kyetutalimuku .
PFX BQ 0 byesilimuku .
PFX BQ 0 byetutalimuku .
PFX BQ 0 byemutalimuku .
PFX BQ 0 byebatalimuku .
PFX BQ 0 byegutalimuku .
PFX BQ 0 byegitalimuku .
PFX BQ 0 byezitalimuku .
PFX BQ 0 byekitalimuku .
PFX BQ 0 byebitalimuku .
PFX BQ 0 byelitalimuku .
PFX BQ 0 byegatalimuku .
PFX BQ 0 byekatalimuku .
PFX BQ 0 byebutalimuku .
PFX BQ 0 byelutalimuku .
PFX BQ 0 byezitalimuku .
PFX BQ 0 byekutalimuku .
PFX BQ 0 byegatalimuku .
PFX BQ 0 byetutalimuku .
PFX BQ 0 lyesilimuku .
PFX BQ 0 lyetutalimuku .
PFX BQ 0 lyemutalimuku .
PFX BQ 0 lyebatalimuku .
PFX BQ 0 lyegutalimuku .
PFX BQ 0 lyegitalimuku .
PFX BQ 0 lyezitalimuku .
PFX BQ 0 lyekitalimuku .
PFX BQ 0 lyebitalimuku .
PFX BQ 0 lyelitalimuku .
PFX BQ 0 lyegatalimuku .
PFX BQ 0 lyekatalimuku .
PFX BQ 0 lyebutalimuku .
PFX BQ 0 lyelutalimuku .
PFX BQ 0 lyezitalimuku .
PFX BQ 0 lyekutalimuku .
PFX BQ 0 lyegatalimuku .
PFX BQ 0 lyetutalimuku .
PFX BQ 0 gesilimuku .
PFX BQ 0 getutalimuku .
PFX BQ 0 gemutalimuku .
PFX BQ 0 gebatalimuku .
PFX BQ 0 gegutalimuku .
PFX BQ 0 gegitalimuku .
PFX BQ 0 gezitalimuku .
PFX BQ 0 gekitalimuku .
PFX BQ 0 gebitalimuku .
PFX BQ 0 gelitalimuku .
PFX BQ 0 gegatalimuku .
PFX BQ 0 gekatalimuku .
PFX BQ 0 gebutalimuku .
PFX BQ 0 gelutalimuku .
PFX BQ 0 gezitalimuku .
PFX BQ 0 gekutalimuku .
PFX BQ 0 gegatalimuku .
PFX BQ 0 getutalimuku .
PFX BQ 0 kesilimuku .
PFX BQ 0 ketutalimuku .
PFX BQ 0 kemutalimuku .
PFX BQ 0 kebatalimuku .
PFX BQ 0 kegutalimuku .
PFX BQ 0 kegitalimuku .
PFX BQ 0 kezitalimuku .
PFX BQ 0 kekitalimuku .
PFX BQ 0 kebitalimuku .
PFX BQ 0 kelitalimuku .
PFX BQ 0 kegatalimuku .
PFX BQ 0 kekatalimuku .
PFX BQ 0 kebutalimuku .
PFX BQ 0 kelutalimuku .
PFX BQ 0 kezitalimuku .
PFX BQ 0 kekutalimuku .
PFX BQ 0 kegatalimuku .
PFX BQ 0 ketutalimuku .
PFX BQ 0 bwesilimuku .
PFX BQ 0 bwetutalimuku .
PFX BQ 0 bwemutalimuku .
PFX BQ 0 bwebatalimuku .
PFX BQ 0 bwegutalimuku .
PFX BQ 0 bwegitalimuku .
PFX BQ 0 bwezitalimuku .
PFX BQ 0 bwekitalimuku .
PFX BQ 0 bwebitalimuku .
PFX BQ 0 bwelitalimuku .
PFX BQ 0 bwegatalimuku .
PFX BQ 0 bwekatalimuku .
PFX BQ 0 bwebutalimuku .
PFX BQ 0 bwelutalimuku .
PFX BQ 0 bwezitalimuku .
PFX BQ 0 bwekutalimuku .
PFX BQ 0 bwegatalimuku .
PFX BQ 0 bwetutalimuku .
PFX BQ 0 lwesilimuku .
PFX BQ 0 lwetutalimuku .
PFX BQ 0 lwemutalimuku .
PFX BQ 0 lwebatalimuku .
PFX BQ 0 lwegutalimuku .
PFX BQ 0 lwegitalimuku .
PFX BQ 0 lwezitalimuku .
PFX BQ 0 lwekitalimuku .
PFX BQ 0 lwebitalimuku .
PFX BQ 0 lwelitalimuku .
PFX BQ 0 lwegatalimuku .
PFX BQ 0 lwekatalimuku .
PFX BQ 0 lwebutalimuku .
PFX BQ 0 lwelutalimuku .
PFX BQ 0 lwezitalimuku .
PFX BQ 0 lwekutalimuku .
PFX BQ 0 lwegatalimuku .
PFX BQ 0 lwetutalimuku .
PFX BQ 0 zesilimuku .
PFX BQ 0 zetutalimuku .
PFX BQ 0 zemutalimuku .
PFX BQ 0 zebatalimuku .
PFX BQ 0 zegutalimuku .
PFX BQ 0 zegitalimuku .
PFX BQ 0 zezitalimuku .
PFX BQ 0 zekitalimuku .
PFX BQ 0 zebitalimuku .
PFX BQ 0 zelitalimuku .
PFX BQ 0 zegatalimuku .
PFX BQ 0 zekatalimuku .
PFX BQ 0 zebutalimuku .
PFX BQ 0 zelutalimuku .
PFX BQ 0 zezitalimuku .
PFX BQ 0 zekutalimuku .
PFX BQ 0 zegatalimuku .
PFX BQ 0 zetutalimuku .
PFX BQ 0 kwesilimuku .
PFX BQ 0 kwetutalimuku .
PFX BQ 0 kwemutalimuku .
PFX BQ 0 kwebatalimuku .
PFX BQ 0 kwegutalimuku .
PFX BQ 0 kwegitalimuku .
PFX BQ 0 kwezitalimuku .
PFX BQ 0 kwekitalimuku .
PFX BQ 0 kwebitalimuku .
PFX BQ 0 kwelitalimuku .
PFX BQ 0 kwegatalimuku .
PFX BQ 0 kwekatalimuku .
PFX BQ 0 kwebutalimuku .
PFX BQ 0 kwelutalimuku .
PFX BQ 0 kwezitalimuku .
PFX BQ 0 kwekutalimuku .
PFX BQ 0 kwegatalimuku .
PFX BQ 0 kwetutalimuku .
PFX BQ 0 gesilimuku .
PFX BQ 0 getutalimuku .
PFX BQ 0 gemutalimuku .
PFX BQ 0 gebatalimuku .
PFX BQ 0 gegutalimuku .
PFX BQ 0 gegitalimuku .
PFX BQ 0 gezitalimuku .
PFX BQ 0 gekitalimuku .
PFX BQ 0 gebitalimuku .
PFX BQ 0 gelitalimuku .
PFX BQ 0 gegatalimuku .
PFX BQ 0 gekatalimuku .
PFX BQ 0 gebutalimuku .
PFX BQ 0 gelutalimuku .
PFX BQ 0 gezitalimuku .
PFX BQ 0 gekutalimuku .
PFX BQ 0 gegatalimuku .
PFX BQ 0 getutalimuku .
PFX BQ 0 twesilimuku .
PFX BQ 0 twetutalimuku .
PFX BQ 0 twemutalimuku .
PFX BQ 0 twebatalimuku .
PFX BQ 0 twegutalimuku .
PFX BQ 0 twegitalimuku .
PFX BQ 0 twezitalimuku .
PFX BQ 0 twekitalimuku .
PFX BQ 0 twebitalimuku .
PFX BQ 0 twelitalimuku .
PFX BQ 0 twegatalimuku .
PFX BQ 0 twekatalimuku .
PFX BQ 0 twebutalimuku .
PFX BQ 0 twelutalimuku .
PFX BQ 0 twezitalimuku .
PFX BQ 0 twekutalimuku .
PFX BQ 0 twegatalimuku .
PFX BQ 0 twetutalimuku ."""

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
    "BQ": "BQ",
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

    out_flag = "HW"
    left_desc = FLAG_DESCRIPTIONS.get("BQ", "BQ")
    right_desc = FLAG_DESCRIPTIONS.get("OR", "OR")
    comment_line = "# Cross product of {} ({}) and {} ({}) to {}".format(
        "BQ", left_desc, "OR", right_desc, out_flag
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
