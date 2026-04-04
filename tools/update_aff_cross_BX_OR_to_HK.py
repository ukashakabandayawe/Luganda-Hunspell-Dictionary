import re
import os
from pathlib import Path

# Cross product generator: BX x OR => HK
# Description:
# - Left block `BX`: BX
# - Right block `OR`: Special reflexive object markers
# - Output flag `HK`: Cross-product prefixes for BX x OR

REPO_ROOT = Path(__file__).resolve().parents[1]
AFF_FILE = REPO_ROOT / "Luganda.aff"

# If set to a flag name (e.g. "HB"), the generated cross-product block will be inserted
# immediately before the first "PFX <flag>" line when the output flag block doesn't
# already exist in the .aff.
INSERT_BEFORE_FLAG = "".strip() or None

rule_left_raw = """
PFX BX Y 221
PFX BX 0 besaa .
PFX BX 0 bemutaa .
PFX BX 0 bebataa .
PFX BX 0 begutaa .
PFX BX 0 begitaa .
PFX BX 0 bezitaa .
PFX BX 0 bekitaa .
PFX BX 0 bebitaa .
PFX BX 0 belitaa .
PFX BX 0 begataa .
PFX BX 0 bekataa .
PFX BX 0 bebutaa .
PFX BX 0 belutaa .
PFX BX 0 bezitaa .
PFX BX 0 bekutaa .
PFX BX 0 begataa .
PFX BX 0 betutaa .
PFX BX 0 gwesaa .
PFX BX 0 gwemutaa .
PFX BX 0 gwebataa .
PFX BX 0 gwegutaa .
PFX BX 0 gwegitaa .
PFX BX 0 gwezitaa .
PFX BX 0 gwekitaa .
PFX BX 0 gwebitaa .
PFX BX 0 gwelitaa .
PFX BX 0 gwegataa .
PFX BX 0 gwekataa .
PFX BX 0 gwebutaa .
PFX BX 0 gwelutaa .
PFX BX 0 gwezitaa .
PFX BX 0 gwekutaa .
PFX BX 0 gwegataa .
PFX BX 0 gwetutaa .
PFX BX 0 gyesaa .
PFX BX 0 gyemutaa .
PFX BX 0 gyebataa .
PFX BX 0 gyegutaa .
PFX BX 0 gyegitaa .
PFX BX 0 gyezitaa .
PFX BX 0 gyekitaa .
PFX BX 0 gyebitaa .
PFX BX 0 gyelitaa .
PFX BX 0 gyegataa .
PFX BX 0 gyekataa .
PFX BX 0 gyebutaa .
PFX BX 0 gyelutaa .
PFX BX 0 gyezitaa .
PFX BX 0 gyekutaa .
PFX BX 0 gyegataa .
PFX BX 0 gyetutaa .
PFX BX 0 zesaa .
PFX BX 0 zemutaa .
PFX BX 0 zebataa .
PFX BX 0 zegutaa .
PFX BX 0 zegitaa .
PFX BX 0 zezitaa .
PFX BX 0 zekitaa .
PFX BX 0 zebitaa .
PFX BX 0 zelitaa .
PFX BX 0 zegataa .
PFX BX 0 zekataa .
PFX BX 0 zebutaa .
PFX BX 0 zelutaa .
PFX BX 0 zezitaa .
PFX BX 0 zekutaa .
PFX BX 0 zegataa .
PFX BX 0 zetutaa .
PFX BX 0 kyesaa .
PFX BX 0 kyemutaa .
PFX BX 0 kyebataa .
PFX BX 0 kyegutaa .
PFX BX 0 kyegitaa .
PFX BX 0 kyezitaa .
PFX BX 0 kyekitaa .
PFX BX 0 kyebitaa .
PFX BX 0 kyelitaa .
PFX BX 0 kyegataa .
PFX BX 0 kyekataa .
PFX BX 0 kyebutaa .
PFX BX 0 kyelutaa .
PFX BX 0 kyezitaa .
PFX BX 0 kyekutaa .
PFX BX 0 kyegataa .
PFX BX 0 kyetutaa .
PFX BX 0 byesaa .
PFX BX 0 byemutaa .
PFX BX 0 byebataa .
PFX BX 0 byegutaa .
PFX BX 0 byegitaa .
PFX BX 0 byezitaa .
PFX BX 0 byekitaa .
PFX BX 0 byebitaa .
PFX BX 0 byelitaa .
PFX BX 0 byegataa .
PFX BX 0 byekataa .
PFX BX 0 byebutaa .
PFX BX 0 byelutaa .
PFX BX 0 byezitaa .
PFX BX 0 byekutaa .
PFX BX 0 byegataa .
PFX BX 0 byetutaa .
PFX BX 0 lyesaa .
PFX BX 0 lyemutaa .
PFX BX 0 lyebataa .
PFX BX 0 lyegutaa .
PFX BX 0 lyegitaa .
PFX BX 0 lyezitaa .
PFX BX 0 lyekitaa .
PFX BX 0 lyebitaa .
PFX BX 0 lyelitaa .
PFX BX 0 lyegataa .
PFX BX 0 lyekataa .
PFX BX 0 lyebutaa .
PFX BX 0 lyelutaa .
PFX BX 0 lyezitaa .
PFX BX 0 lyekutaa .
PFX BX 0 lyegataa .
PFX BX 0 lyetutaa .
PFX BX 0 gesaa .
PFX BX 0 gemutaa .
PFX BX 0 gebataa .
PFX BX 0 gegutaa .
PFX BX 0 gegitaa .
PFX BX 0 gezitaa .
PFX BX 0 gekitaa .
PFX BX 0 gebitaa .
PFX BX 0 gelitaa .
PFX BX 0 gegataa .
PFX BX 0 gekataa .
PFX BX 0 gebutaa .
PFX BX 0 gelutaa .
PFX BX 0 gezitaa .
PFX BX 0 gekutaa .
PFX BX 0 gegataa .
PFX BX 0 getutaa .
PFX BX 0 kesaa .
PFX BX 0 kemutaa .
PFX BX 0 kebataa .
PFX BX 0 kegutaa .
PFX BX 0 kegitaa .
PFX BX 0 kezitaa .
PFX BX 0 kekitaa .
PFX BX 0 kebitaa .
PFX BX 0 kelitaa .
PFX BX 0 kegataa .
PFX BX 0 kekataa .
PFX BX 0 kebutaa .
PFX BX 0 kelutaa .
PFX BX 0 kezitaa .
PFX BX 0 kekutaa .
PFX BX 0 kegataa .
PFX BX 0 ketutaa .
PFX BX 0 bwesaa .
PFX BX 0 bwemutaa .
PFX BX 0 bwebataa .
PFX BX 0 bwegutaa .
PFX BX 0 bwegitaa .
PFX BX 0 bwezitaa .
PFX BX 0 bwekitaa .
PFX BX 0 bwebitaa .
PFX BX 0 bwelitaa .
PFX BX 0 bwegataa .
PFX BX 0 bwekataa .
PFX BX 0 bwebutaa .
PFX BX 0 bwelutaa .
PFX BX 0 bwezitaa .
PFX BX 0 bwekutaa .
PFX BX 0 bwegataa .
PFX BX 0 bwetutaa .
PFX BX 0 lwesaa .
PFX BX 0 lwemutaa .
PFX BX 0 lwebataa .
PFX BX 0 lwegutaa .
PFX BX 0 lwegitaa .
PFX BX 0 lwezitaa .
PFX BX 0 lwekitaa .
PFX BX 0 lwebitaa .
PFX BX 0 lwelitaa .
PFX BX 0 lwegataa .
PFX BX 0 lwekataa .
PFX BX 0 lwebutaa .
PFX BX 0 lwelutaa .
PFX BX 0 lwezitaa .
PFX BX 0 lwekutaa .
PFX BX 0 lwegataa .
PFX BX 0 lwetutaa .
PFX BX 0 kwesaa .
PFX BX 0 kwemutaa .
PFX BX 0 kwebataa .
PFX BX 0 kwegutaa .
PFX BX 0 kwegitaa .
PFX BX 0 kwezitaa .
PFX BX 0 kwekitaa .
PFX BX 0 kwebitaa .
PFX BX 0 kwelitaa .
PFX BX 0 kwegataa .
PFX BX 0 kwekataa .
PFX BX 0 kwebutaa .
PFX BX 0 kwelutaa .
PFX BX 0 kwezitaa .
PFX BX 0 kwekutaa .
PFX BX 0 kwegataa .
PFX BX 0 kwetutaa .
PFX BX 0 twesaa .
PFX BX 0 twemutaa .
PFX BX 0 twebataa .
PFX BX 0 twegutaa .
PFX BX 0 twegitaa .
PFX BX 0 twezitaa .
PFX BX 0 twekitaa .
PFX BX 0 twebitaa .
PFX BX 0 twelitaa .
PFX BX 0 twegataa .
PFX BX 0 twekataa .
PFX BX 0 twebutaa .
PFX BX 0 twelutaa .
PFX BX 0 twezitaa .
PFX BX 0 twekutaa .
PFX BX 0 twegataa .
PFX BX 0 twetutaa ."""

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
    "BX": "BX",
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

    out_flag = "HK"
    left_desc = FLAG_DESCRIPTIONS.get("BX", "BX")
    right_desc = FLAG_DESCRIPTIONS.get("OR", "OR")
    comment_line = "# Cross product of {} ({}) and {} ({}) to {}".format(
        "BX", left_desc, "OR", right_desc, out_flag
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
