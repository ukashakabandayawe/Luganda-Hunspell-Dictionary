import re
import os
from pathlib import Path

# Cross product generator: ED x Ob => HG
# Description:
# - Left block `ED`: ED
# - Right block `Ob`: Object markers
# - Output flag `HG`: Cross-product prefixes for ED x Ob

REPO_ROOT = Path(__file__).resolve().parents[1]
AFF_FILE = REPO_ROOT / "Luganda.aff"

# If set to a flag name (e.g. "HB"), the generated cross-product block will be inserted
# immediately before the first "PFX <flag>" line when the output flag block doesn't
# already exist in the .aff.
INSERT_BEFORE_FLAG = "".strip() or None

rule_left_raw = """
PFX ED Y 272
PFX ED 0 benkya .
PFX ED 0 betukya .
PFX ED 0 bemukya .
PFX ED 0 bebakya .
PFX ED 0 bebakya .
PFX ED 0 begukya .
PFX ED 0 begikya .
PFX ED 0 bezikya .
PFX ED 0 bekikya .
PFX ED 0 bebikya .
PFX ED 0 belikya .
PFX ED 0 begakya .
PFX ED 0 bekakya .
PFX ED 0 bebukya .
PFX ED 0 belukya .
PFX ED 0 bekukya .
PFX ED 0 betukya .
PFX ED 0 gwenkya .
PFX ED 0 gwetukya .
PFX ED 0 gwemukya .
PFX ED 0 gwebakya .
PFX ED 0 gwebakya .
PFX ED 0 gwegukya .
PFX ED 0 gwegikya .
PFX ED 0 gwezikya .
PFX ED 0 gwekikya .
PFX ED 0 gwebikya .
PFX ED 0 gwelikya .
PFX ED 0 gwegakya .
PFX ED 0 gwekakya .
PFX ED 0 gwebukya .
PFX ED 0 gwelukya .
PFX ED 0 gwekukya .
PFX ED 0 gwetukya .
PFX ED 0 gyenkya .
PFX ED 0 gyetukya .
PFX ED 0 gyemukya .
PFX ED 0 gyebakya .
PFX ED 0 gyebakya .
PFX ED 0 gyegukya .
PFX ED 0 gyegikya .
PFX ED 0 gyezikya .
PFX ED 0 gyekikya .
PFX ED 0 gyebikya .
PFX ED 0 gyelikya .
PFX ED 0 gyegakya .
PFX ED 0 gyekakya .
PFX ED 0 gyebukya .
PFX ED 0 gyelukya .
PFX ED 0 gyekukya .
PFX ED 0 gyetukya .
PFX ED 0 zenkya .
PFX ED 0 zetukya .
PFX ED 0 zemukya .
PFX ED 0 zebakya .
PFX ED 0 zebakya .
PFX ED 0 zegukya .
PFX ED 0 zegikya .
PFX ED 0 zezikya .
PFX ED 0 zekikya .
PFX ED 0 zebikya .
PFX ED 0 zelikya .
PFX ED 0 zegakya .
PFX ED 0 zekakya .
PFX ED 0 zebukya .
PFX ED 0 zelukya .
PFX ED 0 zekukya .
PFX ED 0 zetukya .
PFX ED 0 kyenkya .
PFX ED 0 kyetukya .
PFX ED 0 kyemukya .
PFX ED 0 kyebakya .
PFX ED 0 kyebakya .
PFX ED 0 kyegukya .
PFX ED 0 kyegikya .
PFX ED 0 kyezikya .
PFX ED 0 kyekikya .
PFX ED 0 kyebikya .
PFX ED 0 kyelikya .
PFX ED 0 kyegakya .
PFX ED 0 kyekakya .
PFX ED 0 kyebukya .
PFX ED 0 kyelukya .
PFX ED 0 kyekukya .
PFX ED 0 kyetukya .
PFX ED 0 kyenkya .
PFX ED 0 kyetukya .
PFX ED 0 kyemukya .
PFX ED 0 kyebakya .
PFX ED 0 kyebakya .
PFX ED 0 kyegukya .
PFX ED 0 kyegikya .
PFX ED 0 kyezikya .
PFX ED 0 kyekikya .
PFX ED 0 kyebikya .
PFX ED 0 kyelikya .
PFX ED 0 kyegakya .
PFX ED 0 kyekakya .
PFX ED 0 kyebukya .
PFX ED 0 kyelukya .
PFX ED 0 kyekukya .
PFX ED 0 kyetukya .
PFX ED 0 byenkya .
PFX ED 0 byetukya .
PFX ED 0 byemukya .
PFX ED 0 byebakya .
PFX ED 0 byebakya .
PFX ED 0 byegukya .
PFX ED 0 byegikya .
PFX ED 0 byezikya .
PFX ED 0 byekikya .
PFX ED 0 byebikya .
PFX ED 0 byelikya .
PFX ED 0 byegakya .
PFX ED 0 byekakya .
PFX ED 0 byebukya .
PFX ED 0 byelukya .
PFX ED 0 byekukya .
PFX ED 0 byetukya .
PFX ED 0 lyenkya .
PFX ED 0 lyetukya .
PFX ED 0 lyemukya .
PFX ED 0 lyebakya .
PFX ED 0 lyebakya .
PFX ED 0 lyegukya .
PFX ED 0 lyegikya .
PFX ED 0 lyezikya .
PFX ED 0 lyekikya .
PFX ED 0 lyebikya .
PFX ED 0 lyelikya .
PFX ED 0 lyegakya .
PFX ED 0 lyekakya .
PFX ED 0 lyebukya .
PFX ED 0 lyelukya .
PFX ED 0 lyekukya .
PFX ED 0 lyetukya .
PFX ED 0 genkya .
PFX ED 0 getukya .
PFX ED 0 gemukya .
PFX ED 0 gebakya .
PFX ED 0 gebakya .
PFX ED 0 gegukya .
PFX ED 0 gegikya .
PFX ED 0 gezikya .
PFX ED 0 gekikya .
PFX ED 0 gebikya .
PFX ED 0 gelikya .
PFX ED 0 gegakya .
PFX ED 0 gekakya .
PFX ED 0 gebukya .
PFX ED 0 gelukya .
PFX ED 0 gekukya .
PFX ED 0 getukya .
PFX ED 0 kenkya .
PFX ED 0 ketukya .
PFX ED 0 kemukya .
PFX ED 0 kebakya .
PFX ED 0 kebakya .
PFX ED 0 kegukya .
PFX ED 0 kegikya .
PFX ED 0 kezikya .
PFX ED 0 kekikya .
PFX ED 0 kebikya .
PFX ED 0 kelikya .
PFX ED 0 kegakya .
PFX ED 0 kekakya .
PFX ED 0 kebukya .
PFX ED 0 kelukya .
PFX ED 0 kekukya .
PFX ED 0 ketukya .
PFX ED 0 bwenkya .
PFX ED 0 bwetukya .
PFX ED 0 bwemukya .
PFX ED 0 bwebakya .
PFX ED 0 bwebakya .
PFX ED 0 bwegukya .
PFX ED 0 bwegikya .
PFX ED 0 bwezikya .
PFX ED 0 bwekikya .
PFX ED 0 bwebikya .
PFX ED 0 bwelikya .
PFX ED 0 bwegakya .
PFX ED 0 bwekakya .
PFX ED 0 bwebukya .
PFX ED 0 bwelukya .
PFX ED 0 bwekukya .
PFX ED 0 bwetukya .
PFX ED 0 lwenkya .
PFX ED 0 lwetukya .
PFX ED 0 lwemukya .
PFX ED 0 lwebakya .
PFX ED 0 lwebakya .
PFX ED 0 lwegukya .
PFX ED 0 lwegikya .
PFX ED 0 lwezikya .
PFX ED 0 lwekikya .
PFX ED 0 lwebikya .
PFX ED 0 lwelikya .
PFX ED 0 lwegakya .
PFX ED 0 lwekakya .
PFX ED 0 lwebukya .
PFX ED 0 lwelukya .
PFX ED 0 lwekukya .
PFX ED 0 lwetukya .
PFX ED 0 zenkya .
PFX ED 0 zetukya .
PFX ED 0 zemukya .
PFX ED 0 zebakya .
PFX ED 0 zebakya .
PFX ED 0 zegukya .
PFX ED 0 zegikya .
PFX ED 0 zezikya .
PFX ED 0 zekikya .
PFX ED 0 zebikya .
PFX ED 0 zelikya .
PFX ED 0 zegakya .
PFX ED 0 zekakya .
PFX ED 0 zebukya .
PFX ED 0 zelukya .
PFX ED 0 zekukya .
PFX ED 0 zetukya .
PFX ED 0 kwenkya .
PFX ED 0 kwetukya .
PFX ED 0 kwemukya .
PFX ED 0 kwebakya .
PFX ED 0 kwebakya .
PFX ED 0 kwegukya .
PFX ED 0 kwegikya .
PFX ED 0 kwezikya .
PFX ED 0 kwekikya .
PFX ED 0 kwebikya .
PFX ED 0 kwelikya .
PFX ED 0 kwegakya .
PFX ED 0 kwekakya .
PFX ED 0 kwebukya .
PFX ED 0 kwelukya .
PFX ED 0 kwekukya .
PFX ED 0 kwetukya .
PFX ED 0 genkya .
PFX ED 0 getukya .
PFX ED 0 gemukya .
PFX ED 0 gebakya .
PFX ED 0 gebakya .
PFX ED 0 gegukya .
PFX ED 0 gegikya .
PFX ED 0 gezikya .
PFX ED 0 gekikya .
PFX ED 0 gebikya .
PFX ED 0 gelikya .
PFX ED 0 gegakya .
PFX ED 0 gekakya .
PFX ED 0 gebukya .
PFX ED 0 gelukya .
PFX ED 0 gekukya .
PFX ED 0 getukya .
PFX ED 0 twenkya .
PFX ED 0 twetukya .
PFX ED 0 twemukya .
PFX ED 0 twebakya .
PFX ED 0 twebakya .
PFX ED 0 twegukya .
PFX ED 0 twegikya .
PFX ED 0 twezikya .
PFX ED 0 twekikya .
PFX ED 0 twebikya .
PFX ED 0 twelikya .
PFX ED 0 twegakya .
PFX ED 0 twekakya .
PFX ED 0 twebukya .
PFX ED 0 twelukya .
PFX ED 0 twekukya .
PFX ED 0 twetukya ."""

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
    "ED": "ED",
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

    out_flag = "HG"
    left_desc = FLAG_DESCRIPTIONS.get("ED", "ED")
    right_desc = FLAG_DESCRIPTIONS.get("Ob", "Ob")
    comment_line = "# Cross product of {} ({}) and {} ({}) to {}".format(
        "ED", left_desc, "Ob", right_desc, out_flag
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
