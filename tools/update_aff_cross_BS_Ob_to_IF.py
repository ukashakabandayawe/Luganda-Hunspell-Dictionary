import re
import os
from pathlib import Path

# Cross product generator: BS x Ob => IF
# Description:
# - Left block `BS`: BS
# - Right block `Ob`: Object markers
# - Output flag `IF`: Cross-product prefixes for BS x Ob

REPO_ROOT = Path(__file__).resolve().parents[1]
AFF_FILE = REPO_ROOT / "Luganda.aff"

# If set to a flag name (e.g. "HB"), the generated cross-product block will be inserted
# immediately before the first "PFX <flag>" line when the output flag block doesn't
# already exist in the .aff.
INSERT_BEFORE_FLAG = "".strip() or None

rule_left_raw = """
PFX BS Y 288
PFX BS 0 bessili .
PFX BS 0 betutali .
PFX BS 0 bemutali .
PFX BS 0 bebatali .
PFX BS 0 begutali .
PFX BS 0 begitali .
PFX BS 0 bezitali .
PFX BS 0 bekitali .
PFX BS 0 bebitali .
PFX BS 0 belitali .
PFX BS 0 begatali .
PFX BS 0 bekatali .
PFX BS 0 bebutali .
PFX BS 0 belutali .
PFX BS 0 bezitali .
PFX BS 0 bekutali .
PFX BS 0 begatali .
PFX BS 0 betutali .
PFX BS 0 gwessili .
PFX BS 0 gwetutali .
PFX BS 0 gwemutali .
PFX BS 0 gwebatali .
PFX BS 0 gwegutali .
PFX BS 0 gwegitali .
PFX BS 0 gwezitali .
PFX BS 0 gwekitali .
PFX BS 0 gwebitali .
PFX BS 0 gwelitali .
PFX BS 0 gwegatali .
PFX BS 0 gwekatali .
PFX BS 0 gwebutali .
PFX BS 0 gwelutali .
PFX BS 0 gwezitali .
PFX BS 0 gwekutali .
PFX BS 0 gwegatali .
PFX BS 0 gwetutali .
PFX BS 0 gyessili .
PFX BS 0 gyetutali .
PFX BS 0 gyemutali .
PFX BS 0 gyebatali .
PFX BS 0 gyegutali .
PFX BS 0 gyegitali .
PFX BS 0 gyezitali .
PFX BS 0 gyekitali .
PFX BS 0 gyebitali .
PFX BS 0 gyelitali .
PFX BS 0 gyegatali .
PFX BS 0 gyekatali .
PFX BS 0 gyebutali .
PFX BS 0 gyelutali .
PFX BS 0 gyezitali .
PFX BS 0 gyekutali .
PFX BS 0 gyegatali .
PFX BS 0 gyetutali .
PFX BS 0 zessili .
PFX BS 0 zetutali .
PFX BS 0 zemutali .
PFX BS 0 zebatali .
PFX BS 0 zegutali .
PFX BS 0 zegitali .
PFX BS 0 zezitali .
PFX BS 0 zekitali .
PFX BS 0 zebitali .
PFX BS 0 zelitali .
PFX BS 0 zegatali .
PFX BS 0 zekatali .
PFX BS 0 zebutali .
PFX BS 0 zelutali .
PFX BS 0 zezitali .
PFX BS 0 zekutali .
PFX BS 0 zegatali .
PFX BS 0 zetutali .
PFX BS 0 kyessili .
PFX BS 0 kyetutali .
PFX BS 0 kyemutali .
PFX BS 0 kyebatali .
PFX BS 0 kyegutali .
PFX BS 0 kyegitali .
PFX BS 0 kyezitali .
PFX BS 0 kyekitali .
PFX BS 0 kyebitali .
PFX BS 0 kyelitali .
PFX BS 0 kyegatali .
PFX BS 0 kyekatali .
PFX BS 0 kyebutali .
PFX BS 0 kyelutali .
PFX BS 0 kyezitali .
PFX BS 0 kyekutali .
PFX BS 0 kyegatali .
PFX BS 0 kyetutali .
PFX BS 0 kyessili .
PFX BS 0 kyetutali .
PFX BS 0 kyemutali .
PFX BS 0 kyebatali .
PFX BS 0 kyegutali .
PFX BS 0 kyegitali .
PFX BS 0 kyezitali .
PFX BS 0 kyekitali .
PFX BS 0 kyebitali .
PFX BS 0 kyelitali .
PFX BS 0 kyegatali .
PFX BS 0 kyekatali .
PFX BS 0 kyebutali .
PFX BS 0 kyelutali .
PFX BS 0 kyezitali .
PFX BS 0 kyekutali .
PFX BS 0 kyegatali .
PFX BS 0 kyetutali .
PFX BS 0 byessili .
PFX BS 0 byetutali .
PFX BS 0 byemutali .
PFX BS 0 byebatali .
PFX BS 0 byegutali .
PFX BS 0 byegitali .
PFX BS 0 byezitali .
PFX BS 0 byekitali .
PFX BS 0 byebitali .
PFX BS 0 byelitali .
PFX BS 0 byegatali .
PFX BS 0 byekatali .
PFX BS 0 byebutali .
PFX BS 0 byelutali .
PFX BS 0 byezitali .
PFX BS 0 byekutali .
PFX BS 0 byegatali .
PFX BS 0 byetutali .
PFX BS 0 lyessili .
PFX BS 0 lyetutali .
PFX BS 0 lyemutali .
PFX BS 0 lyebatali .
PFX BS 0 lyegutali .
PFX BS 0 lyegitali .
PFX BS 0 lyezitali .
PFX BS 0 lyekitali .
PFX BS 0 lyebitali .
PFX BS 0 lyelitali .
PFX BS 0 lyegatali .
PFX BS 0 lyekatali .
PFX BS 0 lyebutali .
PFX BS 0 lyelutali .
PFX BS 0 lyezitali .
PFX BS 0 lyekutali .
PFX BS 0 lyegatali .
PFX BS 0 lyetutali .
PFX BS 0 gessili .
PFX BS 0 getutali .
PFX BS 0 gemutali .
PFX BS 0 gebatali .
PFX BS 0 gegutali .
PFX BS 0 gegitali .
PFX BS 0 gezitali .
PFX BS 0 gekitali .
PFX BS 0 gebitali .
PFX BS 0 gelitali .
PFX BS 0 gegatali .
PFX BS 0 gekatali .
PFX BS 0 gebutali .
PFX BS 0 gelutali .
PFX BS 0 gezitali .
PFX BS 0 gekutali .
PFX BS 0 gegatali .
PFX BS 0 getutali .
PFX BS 0 kessili .
PFX BS 0 ketutali .
PFX BS 0 kemutali .
PFX BS 0 kebatali .
PFX BS 0 kegutali .
PFX BS 0 kegitali .
PFX BS 0 kezitali .
PFX BS 0 kekitali .
PFX BS 0 kebitali .
PFX BS 0 kelitali .
PFX BS 0 kegatali .
PFX BS 0 kekatali .
PFX BS 0 kebutali .
PFX BS 0 kelutali .
PFX BS 0 kezitali .
PFX BS 0 kekutali .
PFX BS 0 kegatali .
PFX BS 0 ketutali .
PFX BS 0 bwessili .
PFX BS 0 bwetutali .
PFX BS 0 bwemutali .
PFX BS 0 bwebatali .
PFX BS 0 bwegutali .
PFX BS 0 bwegitali .
PFX BS 0 bwezitali .
PFX BS 0 bwekitali .
PFX BS 0 bwebitali .
PFX BS 0 bwelitali .
PFX BS 0 bwegatali .
PFX BS 0 bwekatali .
PFX BS 0 bwebutali .
PFX BS 0 bwelutali .
PFX BS 0 bwezitali .
PFX BS 0 bwekutali .
PFX BS 0 bwegatali .
PFX BS 0 bwetutali .
PFX BS 0 lwessili .
PFX BS 0 lwetutali .
PFX BS 0 lwemutali .
PFX BS 0 lwebatali .
PFX BS 0 lwegutali .
PFX BS 0 lwegitali .
PFX BS 0 lwezitali .
PFX BS 0 lwekitali .
PFX BS 0 lwebitali .
PFX BS 0 lwelitali .
PFX BS 0 lwegatali .
PFX BS 0 lwekatali .
PFX BS 0 lwebutali .
PFX BS 0 lwelutali .
PFX BS 0 lwezitali .
PFX BS 0 lwekutali .
PFX BS 0 lwegatali .
PFX BS 0 lwetutali .
PFX BS 0 zessili .
PFX BS 0 zetutali .
PFX BS 0 zemutali .
PFX BS 0 zebatali .
PFX BS 0 zegutali .
PFX BS 0 zegitali .
PFX BS 0 zezitali .
PFX BS 0 zekitali .
PFX BS 0 zebitali .
PFX BS 0 zelitali .
PFX BS 0 zegatali .
PFX BS 0 zekatali .
PFX BS 0 zebutali .
PFX BS 0 zelutali .
PFX BS 0 zezitali .
PFX BS 0 zekutali .
PFX BS 0 zegatali .
PFX BS 0 zetutali .
PFX BS 0 kwessili .
PFX BS 0 kwetutali .
PFX BS 0 kwemutali .
PFX BS 0 kwebatali .
PFX BS 0 kwegutali .
PFX BS 0 kwegitali .
PFX BS 0 kwezitali .
PFX BS 0 kwekitali .
PFX BS 0 kwebitali .
PFX BS 0 kwelitali .
PFX BS 0 kwegatali .
PFX BS 0 kwekatali .
PFX BS 0 kwebutali .
PFX BS 0 kwelutali .
PFX BS 0 kwezitali .
PFX BS 0 kwekutali .
PFX BS 0 kwegatali .
PFX BS 0 kwetutali .
PFX BS 0 gessili .
PFX BS 0 getutali .
PFX BS 0 gemutali .
PFX BS 0 gebatali .
PFX BS 0 gegutali .
PFX BS 0 gegitali .
PFX BS 0 gezitali .
PFX BS 0 gekitali .
PFX BS 0 gebitali .
PFX BS 0 gelitali .
PFX BS 0 gegatali .
PFX BS 0 gekatali .
PFX BS 0 gebutali .
PFX BS 0 gelutali .
PFX BS 0 gezitali .
PFX BS 0 gekutali .
PFX BS 0 gegatali .
PFX BS 0 getutali .
PFX BS 0 twessili .
PFX BS 0 twetutali .
PFX BS 0 twemutali .
PFX BS 0 twebatali .
PFX BS 0 twegutali .
PFX BS 0 twegitali .
PFX BS 0 twezitali .
PFX BS 0 twekitali .
PFX BS 0 twebitali .
PFX BS 0 twelitali .
PFX BS 0 twegatali .
PFX BS 0 twekatali .
PFX BS 0 twebutali .
PFX BS 0 twelutali .
PFX BS 0 twezitali .
PFX BS 0 twekutali .
PFX BS 0 twegatali .
PFX BS 0 twetutali ."""

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
    "BS": "BS",
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

    out_flag = "IF"
    left_desc = FLAG_DESCRIPTIONS.get("BS", "BS")
    right_desc = FLAG_DESCRIPTIONS.get("Ob", "Ob")
    comment_line = "# Cross product of {} ({}) and {} ({}) to {}".format(
        "BS", left_desc, "Ob", right_desc, out_flag
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
