import re
import os
from pathlib import Path

# Cross product generator: EK x Ob => GE
# Description:
# - Left block `EK`: EK
# - Right block `Ob`: Object markers
# - Output flag `GE`: Cross-product prefixes for EK x Ob

REPO_ROOT = Path(__file__).resolve().parents[1]
AFF_FILE = REPO_ROOT / "Luganda.aff"

# If set to a flag name (e.g. "HB"), the generated cross-product block will be inserted
# immediately before the first "PFX <flag>" line when the output flag block doesn't
# already exist in the .aff.
INSERT_BEFORE_FLAG = "".strip() or None

rule_left_raw = """
PFX EK Y 374
PFX EK 0 nnandiba .
PFX EK 0 nnandigu .
PFX EK 0 nnandigi .
PFX EK 0 nnandizi .
PFX EK 0 nnandiki .
PFX EK 0 nnandibi .
PFX EK 0 nnandili .
PFX EK 0 nnandiga .
PFX EK 0 nnandika .
PFX EK 0 nnandibu .
PFX EK 0 nnandilu .
PFX EK 0 nnandiku .
PFX EK 0 nnanditu .
PFX EK 0 nnandimu .
PFX EK 0 wandin [^lmnb]
PFX EK l wandind l.[^mn]
PFX EK l wandinn l.[mn]
PFX EK w wandimp [w]
PFX EK 0 wandimu .
PFX EK 0 wandiba .
PFX EK 0 wandigu .
PFX EK 0 wandigi .
PFX EK 0 wandizi .
PFX EK 0 wandiki .
PFX EK 0 wandibi .
PFX EK 0 wandili .
PFX EK 0 wandiga .
PFX EK 0 wandika .
PFX EK 0 wandibu .
PFX EK 0 wandilu .
PFX EK 0 wandiku .
PFX EK 0 wanditu .
PFX EK 0 yandin [^lmnb]
PFX EK l yandind l.[^mn]
PFX EK l yandinn l.[mn]
PFX EK w yandimp [w]
PFX EK 0 yandimu .
PFX EK 0 yandiba .
PFX EK 0 yandigu .
PFX EK 0 yandigi .
PFX EK 0 yandizi .
PFX EK 0 yandiki .
PFX EK 0 yandibi .
PFX EK 0 yandili .
PFX EK 0 yandiga .
PFX EK 0 yandika .
PFX EK 0 yandibu .
PFX EK 0 yandilu .
PFX EK 0 yandiku .
PFX EK 0 yanditu .
PFX EK 0 twandin [^lmnb]
PFX EK l twandind l.[^mn]
PFX EK l twandinn l.[mn]
PFX EK w twandimp [w]
PFX EK 0 twandimu .
PFX EK 0 twandiba .
PFX EK 0 twandigu .
PFX EK 0 twandigi .
PFX EK 0 twandizi .
PFX EK 0 twandiki .
PFX EK 0 twandibi .
PFX EK 0 twandili .
PFX EK 0 twandiga .
PFX EK 0 twandika .
PFX EK 0 twandibu .
PFX EK 0 twandilu .
PFX EK 0 twandiku .
PFX EK 0 twanditu .
PFX EK 0 mwandin [^lmnb]
PFX EK l mwandind l.[^mn]
PFX EK l mwandinn l.[mn]
PFX EK w mwandimp [w]
PFX EK 0 mwandimu .
PFX EK 0 mwandiba .
PFX EK 0 mwandigu .
PFX EK 0 mwandigi .
PFX EK 0 mwandizi .
PFX EK 0 mwandiki .
PFX EK 0 mwandibi .
PFX EK 0 mwandili .
PFX EK 0 mwandiga .
PFX EK 0 mwandika .
PFX EK 0 mwandibu .
PFX EK 0 mwandilu .
PFX EK 0 mwandiku .
PFX EK 0 mwanditu .
PFX EK 0 bandin [^lmnb]
PFX EK l bandind l.[^mn]
PFX EK l bandinn l.[mn]
PFX EK w bandimp [w]
PFX EK 0 bandimu .
PFX EK 0 bandiba .
PFX EK 0 bandigu .
PFX EK 0 bandigi .
PFX EK 0 bandizi .
PFX EK 0 bandiki .
PFX EK 0 bandibi .
PFX EK 0 bandili .
PFX EK 0 bandiga .
PFX EK 0 bandika .
PFX EK 0 bandibu .
PFX EK 0 bandilu .
PFX EK 0 bandiku .
PFX EK 0 banditu .
PFX EK 0 gwandin [^lmnb]
PFX EK l gwandind l.[^mn]
PFX EK l gwandinn l.[mn]
PFX EK w gwandimp [w]
PFX EK 0 gwandimu .
PFX EK 0 gwandiba .
PFX EK 0 gwandigu .
PFX EK 0 gwandigi .
PFX EK 0 gwandizi .
PFX EK 0 gwandiki .
PFX EK 0 gwandibi .
PFX EK 0 gwandili .
PFX EK 0 gwandiga .
PFX EK 0 gwandika .
PFX EK 0 gwandibu .
PFX EK 0 gwandilu .
PFX EK 0 gwandiku .
PFX EK 0 gwanditu .
PFX EK 0 ogwandin [^lmnb]
PFX EK l ogwandind l.[^mn]
PFX EK l ogwandinn l.[mn]
PFX EK w ogwandimp [w]
PFX EK 0 ogwandimu .
PFX EK 0 ogwandiba .
PFX EK 0 ogwandigu .
PFX EK 0 ogwandigi .
PFX EK 0 ogwandizi .
PFX EK 0 ogwandiki .
PFX EK 0 ogwandibi .
PFX EK 0 ogwandili .
PFX EK 0 ogwandiga .
PFX EK 0 ogwandika .
PFX EK 0 ogwandibu .
PFX EK 0 ogwandilu .
PFX EK 0 ogwandiku .
PFX EK 0 ogwanditu .
PFX EK 0 gyandin [^lmnb]
PFX EK l gyandind l.[^mn]
PFX EK l gyandinn l.[mn]
PFX EK w gyandimp [w]
PFX EK 0 gyandimu .
PFX EK 0 gyandiba .
PFX EK 0 gyandigu .
PFX EK 0 gyandigi .
PFX EK 0 gyandizi .
PFX EK 0 gyandiki .
PFX EK 0 gyandibi .
PFX EK 0 gyandili .
PFX EK 0 gyandiga .
PFX EK 0 gyandika .
PFX EK 0 gyandibu .
PFX EK 0 gyandilu .
PFX EK 0 gyandiku .
PFX EK 0 gyanditu .
PFX EK 0 zandin [^lmnb]
PFX EK l zandind l.[^mn]
PFX EK l zandinn l.[mn]
PFX EK w zandimp [w]
PFX EK 0 zandimu .
PFX EK 0 zandiba .
PFX EK 0 zandigu .
PFX EK 0 zandigi .
PFX EK 0 zandizi .
PFX EK 0 zandiki .
PFX EK 0 zandibi .
PFX EK 0 zandili .
PFX EK 0 zandiga .
PFX EK 0 zandika .
PFX EK 0 zandibu .
PFX EK 0 zandilu .
PFX EK 0 zandiku .
PFX EK 0 zanditu .
PFX EK 0 kyandin [^lmnb]
PFX EK l kyandind l.[^mn]
PFX EK l kyandinn l.[mn]
PFX EK w kyandimp [w]
PFX EK 0 kyandimu .
PFX EK 0 kyandiba .
PFX EK 0 kyandigu .
PFX EK 0 kyandigi .
PFX EK 0 kyandizi .
PFX EK 0 kyandiki .
PFX EK 0 kyandibi .
PFX EK 0 kyandili .
PFX EK 0 kyandiga .
PFX EK 0 kyandika .
PFX EK 0 kyandibu .
PFX EK 0 kyandilu .
PFX EK 0 kyandiku .
PFX EK 0 kyanditu .
PFX EK 0 byandin [^lmnb]
PFX EK l byandind l.[^mn]
PFX EK l byandinn l.[mn]
PFX EK w byandimp [w]
PFX EK 0 byandimu .
PFX EK 0 byandiba .
PFX EK 0 byandigu .
PFX EK 0 byandigi .
PFX EK 0 byandizi .
PFX EK 0 byandiki .
PFX EK 0 byandibi .
PFX EK 0 byandili .
PFX EK 0 byandiga .
PFX EK 0 byandika .
PFX EK 0 byandibu .
PFX EK 0 byandilu .
PFX EK 0 byandiku .
PFX EK 0 byanditu .
PFX EK 0 lyandin [^lmnb]
PFX EK l lyandind l.[^mn]
PFX EK l lyandinn l.[mn]
PFX EK w lyandimp [w]
PFX EK 0 lyandimu .
PFX EK 0 lyandiba .
PFX EK 0 lyandigu .
PFX EK 0 lyandigi .
PFX EK 0 lyandizi .
PFX EK 0 lyandiki .
PFX EK 0 lyandibi .
PFX EK 0 lyandili .
PFX EK 0 lyandiga .
PFX EK 0 lyandika .
PFX EK 0 lyandibu .
PFX EK 0 lyandilu .
PFX EK 0 lyandiku .
PFX EK 0 lyanditu .
PFX EK 0 gandin [^lmnb]
PFX EK l gandind l.[^mn]
PFX EK l gandinn l.[mn]
PFX EK w gandimp [w]
PFX EK 0 gandimu .
PFX EK 0 gandiba .
PFX EK 0 gandigu .
PFX EK 0 gandigi .
PFX EK 0 gandizi .
PFX EK 0 gandiki .
PFX EK 0 gandibi .
PFX EK 0 gandili .
PFX EK 0 gandiga .
PFX EK 0 gandika .
PFX EK 0 gandibu .
PFX EK 0 gandilu .
PFX EK 0 gandiku .
PFX EK 0 ganditu .
PFX EK 0 kandin [^lmnb]
PFX EK l kandind l.[^mn]
PFX EK l kandinn l.[mn]
PFX EK w kandimp [w]
PFX EK 0 kandimu .
PFX EK 0 kandiba .
PFX EK 0 kandigu .
PFX EK 0 kandigi .
PFX EK 0 kandizi .
PFX EK 0 kandiki .
PFX EK 0 kandibi .
PFX EK 0 kandili .
PFX EK 0 kandiga .
PFX EK 0 kandika .
PFX EK 0 kandibu .
PFX EK 0 kandilu .
PFX EK 0 kandiku .
PFX EK 0 kanditu .
PFX EK 0 bwandin [^lmnb]
PFX EK l bwandind l.[^mn]
PFX EK l bwandinn l.[mn]
PFX EK w bwandimp [w]
PFX EK 0 bwandimu .
PFX EK 0 bwandiba .
PFX EK 0 bwandigu .
PFX EK 0 bwandigi .
PFX EK 0 bwandizi .
PFX EK 0 bwandiki .
PFX EK 0 bwandibi .
PFX EK 0 bwandili .
PFX EK 0 bwandiga .
PFX EK 0 bwandika .
PFX EK 0 bwandibu .
PFX EK 0 bwandilu .
PFX EK 0 bwandiku .
PFX EK 0 bwanditu .
PFX EK 0 lwandin [^lmnb]
PFX EK l lwandind l.[^mn]
PFX EK l lwandinn l.[mn]
PFX EK w lwandimp [w]
PFX EK 0 lwandimu .
PFX EK 0 lwandiba .
PFX EK 0 lwandigu .
PFX EK 0 lwandigi .
PFX EK 0 lwandizi .
PFX EK 0 lwandiki .
PFX EK 0 lwandibi .
PFX EK 0 lwandili .
PFX EK 0 lwandiga .
PFX EK 0 lwandika .
PFX EK 0 lwandibu .
PFX EK 0 lwandilu .
PFX EK 0 lwandiku .
PFX EK 0 lwanditu .
PFX EK 0 zandin [^lmnb]
PFX EK l zandind l.[^mn]
PFX EK l zandinn l.[mn]
PFX EK w zandimp [w]
PFX EK 0 zandimu .
PFX EK 0 zandiba .
PFX EK 0 zandigu .
PFX EK 0 zandigi .
PFX EK 0 zandizi .
PFX EK 0 zandiki .
PFX EK 0 zandibi .
PFX EK 0 zandili .
PFX EK 0 zandiga .
PFX EK 0 zandika .
PFX EK 0 zandibu .
PFX EK 0 zandilu .
PFX EK 0 zandiku .
PFX EK 0 zanditu .
PFX EK 0 kwandin [^lmnb]
PFX EK l kwandind l.[^mn]
PFX EK l kwandinn l.[mn]
PFX EK w kwandimp [w]
PFX EK 0 kwandimu .
PFX EK 0 kwandiba .
PFX EK 0 kwandigu .
PFX EK 0 kwandigi .
PFX EK 0 kwandizi .
PFX EK 0 kwandiki .
PFX EK 0 kwandibi .
PFX EK 0 kwandili .
PFX EK 0 kwandiga .
PFX EK 0 kwandika .
PFX EK 0 kwandibu .
PFX EK 0 kwandilu .
PFX EK 0 kwandiku .
PFX EK 0 kwanditu .
PFX EK 0 gandin [^lmnb]
PFX EK l gandind l.[^mn]
PFX EK l gandinn l.[mn]
PFX EK w gandimp [w]
PFX EK 0 gandimu .
PFX EK 0 gandiba .
PFX EK 0 gandigu .
PFX EK 0 gandigi .
PFX EK 0 gandizi .
PFX EK 0 gandiki .
PFX EK 0 gandibi .
PFX EK 0 gandili .
PFX EK 0 gandiga .
PFX EK 0 gandika .
PFX EK 0 gandibu .
PFX EK 0 gandilu .
PFX EK 0 gandiku .
PFX EK 0 ganditu .
PFX EK 0 twandin [^lmnb]
PFX EK l twandind l.[^mn]
PFX EK l twandinn l.[mn]
PFX EK w twandimp [w]
PFX EK 0 twandimu .
PFX EK 0 twandiba .
PFX EK 0 twandigu .
PFX EK 0 twandigi .
PFX EK 0 twandizi .
PFX EK 0 twandiki .
PFX EK 0 twandibi .
PFX EK 0 twandili .
PFX EK 0 twandiga .
PFX EK 0 twandika .
PFX EK 0 twandibu .
PFX EK 0 twandilu .
PFX EK 0 twandiku .
PFX EK 0 twanditu ."""

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
    "EK": "EK",
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

    out_flag = "GE"
    left_desc = FLAG_DESCRIPTIONS.get("EK", "EK")
    right_desc = FLAG_DESCRIPTIONS.get("Ob", "Ob")
    comment_line = "# Cross product of {} ({}) and {} ({}) to {}".format(
        "EK", left_desc, "Ob", right_desc, out_flag
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
