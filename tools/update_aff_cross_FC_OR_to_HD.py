import re
import os
from pathlib import Path

# Cross product generator: FC x OR => HD
# Description:
# - Left block `FC`: FC
# - Right block `OR`: Special reflexive object markers
# - Output flag `HD`: Cross-product prefixes for FC x OR

REPO_ROOT = Path(__file__).resolve().parents[1]
AFF_FILE = REPO_ROOT / "Luganda.aff"

# If set to a flag name (e.g. "HB"), the generated cross-product block will be inserted
# immediately before the first "PFX <flag>" line when the output flag block doesn't
# already exist in the .aff.
INSERT_BEFORE_FLAG = "".strip() or None

rule_left_raw = """
PFX FC Y 256
PFX FC 0 bessinna .
PFX FC 0 betutanna .
PFX FC 0 bemutanna .
PFX FC 0 bebatanna .
PFX FC 0 begutanna .
PFX FC 0 begitanna .
PFX FC 0 bezitanna .
PFX FC 0 bekitanna .
PFX FC 0 bebitanna .
PFX FC 0 belitanna .
PFX FC 0 begatanna .
PFX FC 0 bekatanna .
PFX FC 0 bebutanna .
PFX FC 0 belutanna .
PFX FC 0 bekutanna .
PFX FC 0 betutanna .
PFX FC 0 gwessinna .
PFX FC 0 gwetutanna .
PFX FC 0 gwemutanna .
PFX FC 0 gwebatanna .
PFX FC 0 gwegutanna .
PFX FC 0 gwegitanna .
PFX FC 0 gwezitanna .
PFX FC 0 gwekitanna .
PFX FC 0 gwebitanna .
PFX FC 0 gwelitanna .
PFX FC 0 gwegatanna .
PFX FC 0 gwekatanna .
PFX FC 0 gwebutanna .
PFX FC 0 gwelutanna .
PFX FC 0 gwekutanna .
PFX FC 0 gwetutanna .
PFX FC 0 gyessinna .
PFX FC 0 gyetutanna .
PFX FC 0 gyemutanna .
PFX FC 0 gyebatanna .
PFX FC 0 gyegutanna .
PFX FC 0 gyegitanna .
PFX FC 0 gyezitanna .
PFX FC 0 gyekitanna .
PFX FC 0 gyebitanna .
PFX FC 0 gyelitanna .
PFX FC 0 gyegatanna .
PFX FC 0 gyekatanna .
PFX FC 0 gyebutanna .
PFX FC 0 gyelutanna .
PFX FC 0 gyekutanna .
PFX FC 0 gyetutanna .
PFX FC 0 zessinna .
PFX FC 0 zetutanna .
PFX FC 0 zemutanna .
PFX FC 0 zebatanna .
PFX FC 0 zegutanna .
PFX FC 0 zegitanna .
PFX FC 0 zezitanna .
PFX FC 0 zekitanna .
PFX FC 0 zebitanna .
PFX FC 0 zelitanna .
PFX FC 0 zegatanna .
PFX FC 0 zekatanna .
PFX FC 0 zebutanna .
PFX FC 0 zelutanna .
PFX FC 0 zekutanna .
PFX FC 0 zetutanna .
PFX FC 0 kyessinna .
PFX FC 0 kyetutanna .
PFX FC 0 kyemutanna .
PFX FC 0 kyebatanna .
PFX FC 0 kyegutanna .
PFX FC 0 kyegitanna .
PFX FC 0 kyezitanna .
PFX FC 0 kyekitanna .
PFX FC 0 kyebitanna .
PFX FC 0 kyelitanna .
PFX FC 0 kyegatanna .
PFX FC 0 kyekatanna .
PFX FC 0 kyebutanna .
PFX FC 0 kyelutanna .
PFX FC 0 kyekutanna .
PFX FC 0 kyetutanna .
PFX FC 0 kyessinna .
PFX FC 0 kyetutanna .
PFX FC 0 kyemutanna .
PFX FC 0 kyebatanna .
PFX FC 0 kyegutanna .
PFX FC 0 kyegitanna .
PFX FC 0 kyezitanna .
PFX FC 0 kyekitanna .
PFX FC 0 kyebitanna .
PFX FC 0 kyelitanna .
PFX FC 0 kyegatanna .
PFX FC 0 kyekatanna .
PFX FC 0 kyebutanna .
PFX FC 0 kyelutanna .
PFX FC 0 kyekutanna .
PFX FC 0 kyetutanna .
PFX FC 0 byessinna .
PFX FC 0 byetutanna .
PFX FC 0 byemutanna .
PFX FC 0 byebatanna .
PFX FC 0 byegutanna .
PFX FC 0 byegitanna .
PFX FC 0 byezitanna .
PFX FC 0 byekitanna .
PFX FC 0 byebitanna .
PFX FC 0 byelitanna .
PFX FC 0 byegatanna .
PFX FC 0 byekatanna .
PFX FC 0 byebutanna .
PFX FC 0 byelutanna .
PFX FC 0 byekutanna .
PFX FC 0 byetutanna .
PFX FC 0 lyessinna .
PFX FC 0 lyetutanna .
PFX FC 0 lyemutanna .
PFX FC 0 lyebatanna .
PFX FC 0 lyegutanna .
PFX FC 0 lyegitanna .
PFX FC 0 lyezitanna .
PFX FC 0 lyekitanna .
PFX FC 0 lyebitanna .
PFX FC 0 lyelitanna .
PFX FC 0 lyegatanna .
PFX FC 0 lyekatanna .
PFX FC 0 lyebutanna .
PFX FC 0 lyelutanna .
PFX FC 0 lyekutanna .
PFX FC 0 lyetutanna .
PFX FC 0 gessinna .
PFX FC 0 getutanna .
PFX FC 0 gemutanna .
PFX FC 0 gebatanna .
PFX FC 0 gegutanna .
PFX FC 0 gegitanna .
PFX FC 0 gezitanna .
PFX FC 0 gekitanna .
PFX FC 0 gebitanna .
PFX FC 0 gelitanna .
PFX FC 0 gegatanna .
PFX FC 0 gekatanna .
PFX FC 0 gebutanna .
PFX FC 0 gelutanna .
PFX FC 0 gekutanna .
PFX FC 0 getutanna .
PFX FC 0 kessinna .
PFX FC 0 ketutanna .
PFX FC 0 kemutanna .
PFX FC 0 kebatanna .
PFX FC 0 kegutanna .
PFX FC 0 kegitanna .
PFX FC 0 kezitanna .
PFX FC 0 kekitanna .
PFX FC 0 kebitanna .
PFX FC 0 kelitanna .
PFX FC 0 kegatanna .
PFX FC 0 kekatanna .
PFX FC 0 kebutanna .
PFX FC 0 kelutanna .
PFX FC 0 kekutanna .
PFX FC 0 ketutanna .
PFX FC 0 bwessinna .
PFX FC 0 bwetutanna .
PFX FC 0 bwemutanna .
PFX FC 0 bwebatanna .
PFX FC 0 bwegutanna .
PFX FC 0 bwegitanna .
PFX FC 0 bwezitanna .
PFX FC 0 bwekitanna .
PFX FC 0 bwebitanna .
PFX FC 0 bwelitanna .
PFX FC 0 bwegatanna .
PFX FC 0 bwekatanna .
PFX FC 0 bwebutanna .
PFX FC 0 bwelutanna .
PFX FC 0 bwekutanna .
PFX FC 0 bwetutanna .
PFX FC 0 lwessinna .
PFX FC 0 lwetutanna .
PFX FC 0 lwemutanna .
PFX FC 0 lwebatanna .
PFX FC 0 lwegutanna .
PFX FC 0 lwegitanna .
PFX FC 0 lwezitanna .
PFX FC 0 lwekitanna .
PFX FC 0 lwebitanna .
PFX FC 0 lwelitanna .
PFX FC 0 lwegatanna .
PFX FC 0 lwekatanna .
PFX FC 0 lwebutanna .
PFX FC 0 lwelutanna .
PFX FC 0 lwekutanna .
PFX FC 0 lwetutanna .
PFX FC 0 zessinna .
PFX FC 0 zetutanna .
PFX FC 0 zemutanna .
PFX FC 0 zebatanna .
PFX FC 0 zegutanna .
PFX FC 0 zegitanna .
PFX FC 0 zezitanna .
PFX FC 0 zekitanna .
PFX FC 0 zebitanna .
PFX FC 0 zelitanna .
PFX FC 0 zegatanna .
PFX FC 0 zekatanna .
PFX FC 0 zebutanna .
PFX FC 0 zelutanna .
PFX FC 0 zekutanna .
PFX FC 0 zetutanna .
PFX FC 0 kwessinna .
PFX FC 0 kwetutanna .
PFX FC 0 kwemutanna .
PFX FC 0 kwebatanna .
PFX FC 0 kwegutanna .
PFX FC 0 kwegitanna .
PFX FC 0 kwezitanna .
PFX FC 0 kwekitanna .
PFX FC 0 kwebitanna .
PFX FC 0 kwelitanna .
PFX FC 0 kwegatanna .
PFX FC 0 kwekatanna .
PFX FC 0 kwebutanna .
PFX FC 0 kwelutanna .
PFX FC 0 kwekutanna .
PFX FC 0 kwetutanna .
PFX FC 0 gessinna .
PFX FC 0 getutanna .
PFX FC 0 gemutanna .
PFX FC 0 gebatanna .
PFX FC 0 gegutanna .
PFX FC 0 gegitanna .
PFX FC 0 gezitanna .
PFX FC 0 gekitanna .
PFX FC 0 gebitanna .
PFX FC 0 gelitanna .
PFX FC 0 gegatanna .
PFX FC 0 gekatanna .
PFX FC 0 gebutanna .
PFX FC 0 gelutanna .
PFX FC 0 gekutanna .
PFX FC 0 getutanna .
PFX FC 0 twessinna .
PFX FC 0 twetutanna .
PFX FC 0 twemutanna .
PFX FC 0 twebatanna .
PFX FC 0 twegutanna .
PFX FC 0 twegitanna .
PFX FC 0 twezitanna .
PFX FC 0 twekitanna .
PFX FC 0 twebitanna .
PFX FC 0 twelitanna .
PFX FC 0 twegatanna .
PFX FC 0 twekatanna .
PFX FC 0 twebutanna .
PFX FC 0 twelutanna .
PFX FC 0 twekutanna .
PFX FC 0 twetutanna ."""

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
    "FC": "FC",
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

    out_flag = "HD"
    left_desc = FLAG_DESCRIPTIONS.get("FC", "FC")
    right_desc = FLAG_DESCRIPTIONS.get("OR", "OR")
    comment_line = "# Cross product of {} ({}) and {} ({}) to {}".format(
        "FC", left_desc, "OR", right_desc, out_flag
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
