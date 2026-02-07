import re
import os
from pathlib import Path

# Cross product generator: wn x Ob => FH
# Description:
# - Left block `wn`: Subordinating conjunction when with negative subjects in near and distant past tense
# - Right block `Ob`: Object markers
# - Output flag `FH`: Cross-product prefixes for wn x Ob

REPO_ROOT = Path(__file__).resolve().parents[1]
AFF_FILE = REPO_ROOT / "Luganda.aff"

# If set to a flag name (e.g. "HB"), the generated cross-product block will be inserted
# immediately before the first "PFX <flag>" line when the output flag block doesn't
# already exist in the .aff.
INSERT_BEFORE_FLAG = "".strip() or None

rule_left_raw = """
PFX wn Y 177
PFX wn 0 wessaa [^mn]
PFX wn 0 wessaa mu
PFX wn 0 wetutaa .
PFX wn 0 wemutaa .
PFX wn 0 webataa .
PFX wn 0 wegutaa .
PFX wn 0 wegitaa .
PFX wn 0 wezitaa .
PFX wn 0 wekitaa .
PFX wn 0 webitaa .
PFX wn 0 welitaa .
PFX wn 0 wegataa .
PFX wn 0 wekataa .
PFX wn 0 webutaa .
PFX wn 0 welutaa .
PFX wn 0 wekutaa .
PFX wn 0 wetutaa .
PFX wn 0 bwessaa [^mn]
PFX wn 0 bwessaa mu
PFX wn 0 bwetutaa .
PFX wn 0 bwemutaa .
PFX wn 0 bwebataa .
PFX wn 0 bwegutaa .
PFX wn 0 bwegitaa .
PFX wn 0 bwezitaa .
PFX wn 0 bwekitaa .
PFX wn 0 bwebitaa .
PFX wn 0 bwelitaa .
PFX wn 0 bwegataa .
PFX wn 0 bwekataa .
PFX wn 0 bwebutaa .
PFX wn 0 bwelutaa .
PFX wn 0 bwekutaa .
PFX wn 0 bwetutaa .
PFX wn 0 bwessaa [^mn]
PFX wn 0 bwessaa mu
PFX wn 0 lwessaa [^mn]
PFX wn 0 lwessaa mu
PFX wn 0 lwetutaa .
PFX wn 0 lwemutaa .
PFX wn 0 lwebataa .
PFX wn 0 lwegutaa .
PFX wn 0 lwegitaa .
PFX wn 0 lwezitaa .
PFX wn 0 lwekitaa .
PFX wn 0 lwebitaa .
PFX wn 0 lwelitaa .
PFX wn 0 lwegataa .
PFX wn 0 lwekataa .
PFX wn 0 lwebutaa .
PFX wn 0 lwelutaa .
PFX wn 0 lwekutaa .
PFX wn 0 lwetutaa .
PFX wn 0 lwessaa [^mn]
PFX wn 0 lwessaa mu
PFX wn 0 zessaa [^mn]
PFX wn 0 zessaa mu
PFX wn 0 zetutaa .
PFX wn 0 zemutaa .
PFX wn 0 zebataa .
PFX wn 0 zegutaa .
PFX wn 0 zegitaa .
PFX wn 0 zezitaa .
PFX wn 0 zekitaa .
PFX wn 0 zebitaa .
PFX wn 0 zelitaa .
PFX wn 0 zegataa .
PFX wn 0 zekataa .
PFX wn 0 zebutaa .
PFX wn 0 zelutaa .
PFX wn 0 zekutaa .
PFX wn 0 zetutaa .
PFX wn 0 gwessaa [^mn]
PFX wn 0 gwessaa mu
PFX wn 0 gwetutaa .
PFX wn 0 gwemutaa .
PFX wn 0 gwebataa .
PFX wn 0 gwegutaa .
PFX wn 0 gwegitaa .
PFX wn 0 gwezitaa .
PFX wn 0 gwekitaa .
PFX wn 0 gwebitaa .
PFX wn 0 gwelitaa .
PFX wn 0 gwegataa .
PFX wn 0 gwekataa .
PFX wn 0 gwebutaa .
PFX wn 0 gwelutaa .
PFX wn 0 gwekutaa .
PFX wn 0 gwetutaa .
PFX wn 0 gyessaa [^mn]
PFX wn 0 gyessaa mu
PFX wn 0 gyetutaa .
PFX wn 0 gyemutaa .
PFX wn 0 gyebataa .
PFX wn 0 gyegutaa .
PFX wn 0 gyegitaa .
PFX wn 0 gyezitaa .
PFX wn 0 gyekitaa .
PFX wn 0 gyebitaa .
PFX wn 0 gyelitaa .
PFX wn 0 gyegataa .
PFX wn 0 gyekataa .
PFX wn 0 gyebutaa .
PFX wn 0 gyelutaa .
PFX wn 0 gyekutaa .
PFX wn 0 gyetutaa .
PFX wn 0 kyessaa [^mn]
PFX wn 0 kyessaa mu
PFX wn 0 kyetutaa .
PFX wn 0 kyemutaa .
PFX wn 0 kyebataa .
PFX wn 0 kyegutaa .
PFX wn 0 kyegitaa .
PFX wn 0 kyezitaa .
PFX wn 0 kyekitaa .
PFX wn 0 kyebitaa .
PFX wn 0 kyelitaa .
PFX wn 0 kyegataa .
PFX wn 0 kyekataa .
PFX wn 0 kyebutaa .
PFX wn 0 kyelutaa .
PFX wn 0 kyekutaa .
PFX wn 0 kyetutaa .
PFX wn 0 byessaa [^mn]
PFX wn 0 byessaa mu
PFX wn 0 byetutaa .
PFX wn 0 byemutaa .
PFX wn 0 byebataa .
PFX wn 0 byegutaa .
PFX wn 0 byegitaa .
PFX wn 0 byezitaa .
PFX wn 0 byekitaa .
PFX wn 0 byebitaa .
PFX wn 0 byelitaa .
PFX wn 0 byegataa .
PFX wn 0 byekataa .
PFX wn 0 byebutaa .
PFX wn 0 byelutaa .
PFX wn 0 byekutaa .
PFX wn 0 byetutaa .
PFX wn 0 lyessaa [^mn]
PFX wn 0 lyessaa mu
PFX wn 0 lyetutaa .
PFX wn 0 lyemutaa .
PFX wn 0 lyebataa .
PFX wn 0 lyegutaa .
PFX wn 0 lyegitaa .
PFX wn 0 lyezitaa .
PFX wn 0 lyekitaa .
PFX wn 0 lyebitaa .
PFX wn 0 lyelitaa .
PFX wn 0 lyegataa .
PFX wn 0 lyekataa .
PFX wn 0 lyebutaa .
PFX wn 0 lyelutaa .
PFX wn 0 lyekutaa .
PFX wn 0 lyetutaa .
PFX wn 0 kessaa [^mn]
PFX wn 0 kessaa mu
PFX wn 0 ketutaa .
PFX wn 0 kemutaa .
PFX wn 0 kebataa .
PFX wn 0 kegutaa .
PFX wn 0 kegitaa .
PFX wn 0 kezitaa .
PFX wn 0 kekitaa .
PFX wn 0 kebitaa .
PFX wn 0 kelitaa .
PFX wn 0 kegataa .
PFX wn 0 kekataa .
PFX wn 0 kebutaa .
PFX wn 0 kelutaa .
PFX wn 0 kekutaa .
PFX wn 0 ketutaa .
PFX wn 0 otaa .
PFX wn 0 ataa .
PFX wn 0 etaa ."""

rule_right_raw = """
PFX Ob Y 18
PFX Ob 0 n [^lmnb]
PFX Ob l nd l.[^mn][^u]
PFX Ob l nn l.[mn]
PFX Ob w mp [w]
PFX Ob 0 mu .
PFX Ob 0 ba .
PFX Ob 0 gu .
PFX Ob 0 gi .
PFX Ob 0 zi .
PFX Ob 0 ki .
PFX Ob 0 bi .
PFX Ob 0 li .
PFX Ob 0 ga .
PFX Ob 0 ka .
PFX Ob 0 bu .
PFX Ob 0 lu .
PFX Ob 0 ku .
PFX Ob 0 tu ."""

FLAG_DESCRIPTIONS = {
    "wn": "Subordinating conjunction when with negative subjects in near and distant past tense",
    "Ob": "Object markers",
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

    out_flag = "FH"
    left_desc = FLAG_DESCRIPTIONS.get("wn", "wn")
    right_desc = FLAG_DESCRIPTIONS.get("Ob", "Ob")
    comment_line = "# Cross product of {} ({}) and {} ({}) to {}".format(
        "wn", left_desc, "Ob", right_desc, out_flag
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
