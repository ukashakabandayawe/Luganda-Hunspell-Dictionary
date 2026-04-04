import re
import os
from pathlib import Path

# Cross product generator: BV x Ob => IB
# Description:
# - Left block `BV`: BV
# - Right block `Ob`: Object markers
# - Output flag `IB`: Cross-product prefixes for BV x Ob

REPO_ROOT = Path(__file__).resolve().parents[1]
AFF_FILE = REPO_ROOT / "Luganda.aff"

# If set to a flag name (e.g. "HB"), the generated cross-product block will be inserted
# immediately before the first "PFX <flag>" line when the output flag block doesn't
# already exist in the .aff.
INSERT_BEFORE_FLAG = "".strip() or None

rule_left_raw = """
PFX BV Y 272
PFX BV 0 besii .
PFX BV 0 bemutaa .
PFX BV 0 bebataa .
PFX BV 0 begutaa .
PFX BV 0 begitaa .
PFX BV 0 bezitaa .
PFX BV 0 bekitaa .
PFX BV 0 bebitaa .
PFX BV 0 belitaa .
PFX BV 0 begataa .
PFX BV 0 bekataa .
PFX BV 0 bebutaa .
PFX BV 0 belutaa .
PFX BV 0 bezitaa .
PFX BV 0 bekutaa .
PFX BV 0 begataa .
PFX BV 0 betutaa .
PFX BV 0 gwesii .
PFX BV 0 gwemutaa .
PFX BV 0 gwebataa .
PFX BV 0 gwegutaa .
PFX BV 0 gwegitaa .
PFX BV 0 gwezitaa .
PFX BV 0 gwekitaa .
PFX BV 0 gwebitaa .
PFX BV 0 gwelitaa .
PFX BV 0 gwegataa .
PFX BV 0 gwekataa .
PFX BV 0 gwebutaa .
PFX BV 0 gwelutaa .
PFX BV 0 gwezitaa .
PFX BV 0 gwekutaa .
PFX BV 0 gwegataa .
PFX BV 0 gwetutaa .
PFX BV 0 gyesii .
PFX BV 0 gyemutaa .
PFX BV 0 gyebataa .
PFX BV 0 gyegutaa .
PFX BV 0 gyegitaa .
PFX BV 0 gyezitaa .
PFX BV 0 gyekitaa .
PFX BV 0 gyebitaa .
PFX BV 0 gyelitaa .
PFX BV 0 gyegataa .
PFX BV 0 gyekataa .
PFX BV 0 gyebutaa .
PFX BV 0 gyelutaa .
PFX BV 0 gyezitaa .
PFX BV 0 gyekutaa .
PFX BV 0 gyegataa .
PFX BV 0 gyetutaa .
PFX BV 0 zesii .
PFX BV 0 zemutaa .
PFX BV 0 zebataa .
PFX BV 0 zegutaa .
PFX BV 0 zegitaa .
PFX BV 0 zezitaa .
PFX BV 0 zekitaa .
PFX BV 0 zebitaa .
PFX BV 0 zelitaa .
PFX BV 0 zegataa .
PFX BV 0 zekataa .
PFX BV 0 zebutaa .
PFX BV 0 zelutaa .
PFX BV 0 zezitaa .
PFX BV 0 zekutaa .
PFX BV 0 zegataa .
PFX BV 0 zetutaa .
PFX BV 0 kyesii .
PFX BV 0 kyemutaa .
PFX BV 0 kyebataa .
PFX BV 0 kyegutaa .
PFX BV 0 kyegitaa .
PFX BV 0 kyezitaa .
PFX BV 0 kyekitaa .
PFX BV 0 kyebitaa .
PFX BV 0 kyelitaa .
PFX BV 0 kyegataa .
PFX BV 0 kyekataa .
PFX BV 0 kyebutaa .
PFX BV 0 kyelutaa .
PFX BV 0 kyezitaa .
PFX BV 0 kyekutaa .
PFX BV 0 kyegataa .
PFX BV 0 kyetutaa .
PFX BV 0 kyesii .
PFX BV 0 kyemutaa .
PFX BV 0 kyebataa .
PFX BV 0 kyegutaa .
PFX BV 0 kyegitaa .
PFX BV 0 kyezitaa .
PFX BV 0 kyekitaa .
PFX BV 0 kyebitaa .
PFX BV 0 kyelitaa .
PFX BV 0 kyegataa .
PFX BV 0 kyekataa .
PFX BV 0 kyebutaa .
PFX BV 0 kyelutaa .
PFX BV 0 kyezitaa .
PFX BV 0 kyekutaa .
PFX BV 0 kyegataa .
PFX BV 0 kyetutaa .
PFX BV 0 byesii .
PFX BV 0 byemutaa .
PFX BV 0 byebataa .
PFX BV 0 byegutaa .
PFX BV 0 byegitaa .
PFX BV 0 byezitaa .
PFX BV 0 byekitaa .
PFX BV 0 byebitaa .
PFX BV 0 byelitaa .
PFX BV 0 byegataa .
PFX BV 0 byekataa .
PFX BV 0 byebutaa .
PFX BV 0 byelutaa .
PFX BV 0 byezitaa .
PFX BV 0 byekutaa .
PFX BV 0 byegataa .
PFX BV 0 byetutaa .
PFX BV 0 lyesii .
PFX BV 0 lyemutaa .
PFX BV 0 lyebataa .
PFX BV 0 lyegutaa .
PFX BV 0 lyegitaa .
PFX BV 0 lyezitaa .
PFX BV 0 lyekitaa .
PFX BV 0 lyebitaa .
PFX BV 0 lyelitaa .
PFX BV 0 lyegataa .
PFX BV 0 lyekataa .
PFX BV 0 lyebutaa .
PFX BV 0 lyelutaa .
PFX BV 0 lyezitaa .
PFX BV 0 lyekutaa .
PFX BV 0 lyegataa .
PFX BV 0 lyetutaa .
PFX BV 0 gesii .
PFX BV 0 gemutaa .
PFX BV 0 gebataa .
PFX BV 0 gegutaa .
PFX BV 0 gegitaa .
PFX BV 0 gezitaa .
PFX BV 0 gekitaa .
PFX BV 0 gebitaa .
PFX BV 0 gelitaa .
PFX BV 0 gegataa .
PFX BV 0 gekataa .
PFX BV 0 gebutaa .
PFX BV 0 gelutaa .
PFX BV 0 gezitaa .
PFX BV 0 gekutaa .
PFX BV 0 gegataa .
PFX BV 0 getutaa .
PFX BV 0 kesii .
PFX BV 0 kemutaa .
PFX BV 0 kebataa .
PFX BV 0 kegutaa .
PFX BV 0 kegitaa .
PFX BV 0 kezitaa .
PFX BV 0 kekitaa .
PFX BV 0 kebitaa .
PFX BV 0 kelitaa .
PFX BV 0 kegataa .
PFX BV 0 kekataa .
PFX BV 0 kebutaa .
PFX BV 0 kelutaa .
PFX BV 0 kezitaa .
PFX BV 0 kekutaa .
PFX BV 0 kegataa .
PFX BV 0 ketutaa .
PFX BV 0 bwesii .
PFX BV 0 bwemutaa .
PFX BV 0 bwebataa .
PFX BV 0 bwegutaa .
PFX BV 0 bwegitaa .
PFX BV 0 bwezitaa .
PFX BV 0 bwekitaa .
PFX BV 0 bwebitaa .
PFX BV 0 bwelitaa .
PFX BV 0 bwegataa .
PFX BV 0 bwekataa .
PFX BV 0 bwebutaa .
PFX BV 0 bwelutaa .
PFX BV 0 bwezitaa .
PFX BV 0 bwekutaa .
PFX BV 0 bwegataa .
PFX BV 0 bwetutaa .
PFX BV 0 lwesii .
PFX BV 0 lwemutaa .
PFX BV 0 lwebataa .
PFX BV 0 lwegutaa .
PFX BV 0 lwegitaa .
PFX BV 0 lwezitaa .
PFX BV 0 lwekitaa .
PFX BV 0 lwebitaa .
PFX BV 0 lwelitaa .
PFX BV 0 lwegataa .
PFX BV 0 lwekataa .
PFX BV 0 lwebutaa .
PFX BV 0 lwelutaa .
PFX BV 0 lwezitaa .
PFX BV 0 lwekutaa .
PFX BV 0 lwegataa .
PFX BV 0 lwetutaa .
PFX BV 0 zesii .
PFX BV 0 zemutaa .
PFX BV 0 zebataa .
PFX BV 0 zegutaa .
PFX BV 0 zegitaa .
PFX BV 0 zezitaa .
PFX BV 0 zekitaa .
PFX BV 0 zebitaa .
PFX BV 0 zelitaa .
PFX BV 0 zegataa .
PFX BV 0 zekataa .
PFX BV 0 zebutaa .
PFX BV 0 zelutaa .
PFX BV 0 zezitaa .
PFX BV 0 zekutaa .
PFX BV 0 zegataa .
PFX BV 0 zetutaa .
PFX BV 0 kwesii .
PFX BV 0 kwemutaa .
PFX BV 0 kwebataa .
PFX BV 0 kwegutaa .
PFX BV 0 kwegitaa .
PFX BV 0 kwezitaa .
PFX BV 0 kwekitaa .
PFX BV 0 kwebitaa .
PFX BV 0 kwelitaa .
PFX BV 0 kwegataa .
PFX BV 0 kwekataa .
PFX BV 0 kwebutaa .
PFX BV 0 kwelutaa .
PFX BV 0 kwezitaa .
PFX BV 0 kwekutaa .
PFX BV 0 kwegataa .
PFX BV 0 kwetutaa .
PFX BV 0 gesii .
PFX BV 0 gemutaa .
PFX BV 0 gebataa .
PFX BV 0 gegutaa .
PFX BV 0 gegitaa .
PFX BV 0 gezitaa .
PFX BV 0 gekitaa .
PFX BV 0 gebitaa .
PFX BV 0 gelitaa .
PFX BV 0 gegataa .
PFX BV 0 gekataa .
PFX BV 0 gebutaa .
PFX BV 0 gelutaa .
PFX BV 0 gezitaa .
PFX BV 0 gekutaa .
PFX BV 0 gegataa .
PFX BV 0 getutaa .
PFX BV 0 twesii .
PFX BV 0 twemutaa .
PFX BV 0 twebataa .
PFX BV 0 twegutaa .
PFX BV 0 twegitaa .
PFX BV 0 twezitaa .
PFX BV 0 twekitaa .
PFX BV 0 twebitaa .
PFX BV 0 twelitaa .
PFX BV 0 twegataa .
PFX BV 0 twekataa .
PFX BV 0 twebutaa .
PFX BV 0 twelutaa .
PFX BV 0 twezitaa .
PFX BV 0 twekutaa .
PFX BV 0 twegataa .
PFX BV 0 twetutaa ."""

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
    "BV": "BV",
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

    out_flag = "IB"
    left_desc = FLAG_DESCRIPTIONS.get("BV", "BV")
    right_desc = FLAG_DESCRIPTIONS.get("Ob", "Ob")
    comment_line = "# Cross product of {} ({}) and {} ({}) to {}".format(
        "BV", left_desc, "Ob", right_desc, out_flag
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
