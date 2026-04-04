import re
import os
from pathlib import Path

# Cross product generator: FX x Ob => HC
# Description:
# - Left block `FX`: FX
# - Right block `Ob`: Object markers
# - Output flag `HC`: Cross-product prefixes for FX x Ob

REPO_ROOT = Path(__file__).resolve().parents[1]
AFF_FILE = REPO_ROOT / "Luganda.aff"

# If set to a flag name (e.g. "HB"), the generated cross-product block will be inserted
# immediately before the first "PFX <flag>" line when the output flag block doesn't
# already exist in the .aff.
INSERT_BEFORE_FLAG = "".strip() or None

rule_left_raw = """
PFX FX Y 300
PFX FX 0 kangu .
PFX FX 0 kangi .
PFX FX 0 kanzi .
PFX FX 0 kanki .
PFX FX 0 kanga .
PFX FX 0 kanka .
PFX FX 0 kanku .
PFX FX 0 kantu .
PFX FX 0 kamba .
PFX FX 0 kambi .
PFX FX 0 kambu .
PFX FX 0 k'on [^lmnb]
PFX FX l k'ond l.[^mn]
PFX FX l k'onn l.[mn]
PFX FX w k'omp [w]
PFX FX 0 k'omu .
PFX FX 0 k'oba .
PFX FX 0 k'ogu .
PFX FX 0 k'ogi .
PFX FX 0 k'ozi .
PFX FX 0 k'oki .
PFX FX 0 k'obi .
PFX FX 0 k'oli .
PFX FX 0 k'oga .
PFX FX 0 k'oka .
PFX FX 0 k'obu .
PFX FX 0 k'olu .
PFX FX 0 k'oku .
PFX FX 0 k'otu .
PFX FX 0 kandi .
PFX FX 0 k'an [^lmnb]
PFX FX l k'and l.[^mn]
PFX FX l k'ann l.[mn]
PFX FX w k'amp [w]
PFX FX 0 k'amu .
PFX FX 0 k'aba .
PFX FX 0 k'agu .
PFX FX 0 k'agi .
PFX FX 0 k'azi .
PFX FX 0 k'aki .
PFX FX 0 k'abi .
PFX FX 0 k'ali .
PFX FX 0 k'aga .
PFX FX 0 k'aka .
PFX FX 0 k'abu .
PFX FX 0 k'alu .
PFX FX 0 k'aku .
PFX FX 0 k'atu .
PFX FX 0 katun [^lmnb]
PFX FX l katund l.[^mn]
PFX FX l katunn l.[mn]
PFX FX w katump [w]
PFX FX 0 katumu .
PFX FX 0 katuba .
PFX FX 0 katugu .
PFX FX 0 katugi .
PFX FX 0 katuzi .
PFX FX 0 katuki .
PFX FX 0 katubi .
PFX FX 0 katuli .
PFX FX 0 katuga .
PFX FX 0 katuka .
PFX FX 0 katubu .
PFX FX 0 katulu .
PFX FX 0 katuku .
PFX FX 0 katutu .
PFX FX 0 kamun [^lmnb]
PFX FX l kamund l.[^mn]
PFX FX l kamunn l.[mn]
PFX FX w kamump [w]
PFX FX 0 kamumu .
PFX FX 0 kamuba .
PFX FX 0 kamugu .
PFX FX 0 kamugi .
PFX FX 0 kamuzi .
PFX FX 0 kamuki .
PFX FX 0 kamubi .
PFX FX 0 kamuli .
PFX FX 0 kamuga .
PFX FX 0 kamuka .
PFX FX 0 kamubu .
PFX FX 0 kamulu .
PFX FX 0 kamuku .
PFX FX 0 kamutu .
PFX FX 0 kaban [^lmnb]
PFX FX l kaband l.[^mn]
PFX FX l kabann l.[mn]
PFX FX w kabamp [w]
PFX FX 0 kabamu .
PFX FX 0 kababa .
PFX FX 0 kabagu .
PFX FX 0 kabagi .
PFX FX 0 kabazi .
PFX FX 0 kabaki .
PFX FX 0 kababi .
PFX FX 0 kabali .
PFX FX 0 kabaga .
PFX FX 0 kabaka .
PFX FX 0 kababu .
PFX FX 0 kabalu .
PFX FX 0 kabaku .
PFX FX 0 kabatu .
PFX FX 0 kagun [^lmnb]
PFX FX l kagund l.[^mn]
PFX FX l kagunn l.[mn]
PFX FX w kagump [w]
PFX FX 0 kagumu .
PFX FX 0 kaguba .
PFX FX 0 kagugu .
PFX FX 0 kagugi .
PFX FX 0 kaguzi .
PFX FX 0 kaguki .
PFX FX 0 kagubi .
PFX FX 0 kaguli .
PFX FX 0 kaguga .
PFX FX 0 kaguka .
PFX FX 0 kagubu .
PFX FX 0 kagulu .
PFX FX 0 kaguku .
PFX FX 0 kagutu .
PFX FX 0 kagin [^lmnb]
PFX FX l kagind l.[^mn]
PFX FX l kaginn l.[mn]
PFX FX w kagimp [w]
PFX FX 0 kagimu .
PFX FX 0 kagiba .
PFX FX 0 kagigu .
PFX FX 0 kagigi .
PFX FX 0 kagizi .
PFX FX 0 kagiki .
PFX FX 0 kagibi .
PFX FX 0 kagili .
PFX FX 0 kagiga .
PFX FX 0 kagika .
PFX FX 0 kagibu .
PFX FX 0 kagilu .
PFX FX 0 kagiku .
PFX FX 0 kagitu .
PFX FX 0 kazin [^lmnb]
PFX FX l kazind l.[^mn]
PFX FX l kazinn l.[mn]
PFX FX w kazimp [w]
PFX FX 0 kazimu .
PFX FX 0 kaziba .
PFX FX 0 kazigu .
PFX FX 0 kazigi .
PFX FX 0 kazizi .
PFX FX 0 kaziki .
PFX FX 0 kazibi .
PFX FX 0 kazili .
PFX FX 0 kaziga .
PFX FX 0 kazika .
PFX FX 0 kazibu .
PFX FX 0 kazilu .
PFX FX 0 kaziku .
PFX FX 0 kazitu .
PFX FX 0 kakin [^lmnb]
PFX FX l kakind l.[^mn]
PFX FX l kakinn l.[mn]
PFX FX w kakimp [w]
PFX FX 0 kakimu .
PFX FX 0 kakiba .
PFX FX 0 kakigu .
PFX FX 0 kakigi .
PFX FX 0 kakizi .
PFX FX 0 kakiki .
PFX FX 0 kakibi .
PFX FX 0 kakili .
PFX FX 0 kakiga .
PFX FX 0 kakika .
PFX FX 0 kakibu .
PFX FX 0 kakilu .
PFX FX 0 kakiku .
PFX FX 0 kakitu .
PFX FX 0 kabin [^lmnb]
PFX FX l kabind l.[^mn]
PFX FX l kabinn l.[mn]
PFX FX w kabimp [w]
PFX FX 0 kabimu .
PFX FX 0 kabiba .
PFX FX 0 kabigu .
PFX FX 0 kabigi .
PFX FX 0 kabizi .
PFX FX 0 kabiki .
PFX FX 0 kabibi .
PFX FX 0 kabili .
PFX FX 0 kabiga .
PFX FX 0 kabika .
PFX FX 0 kabibu .
PFX FX 0 kabilu .
PFX FX 0 kabiku .
PFX FX 0 kabitu .
PFX FX 0 kalin [^lmnb]
PFX FX l kalind l.[^mn]
PFX FX l kalinn l.[mn]
PFX FX w kalimp [w]
PFX FX 0 kalimu .
PFX FX 0 kaliba .
PFX FX 0 kaligu .
PFX FX 0 kaligi .
PFX FX 0 kalizi .
PFX FX 0 kaliki .
PFX FX 0 kalibi .
PFX FX 0 kalili .
PFX FX 0 kaliga .
PFX FX 0 kalika .
PFX FX 0 kalibu .
PFX FX 0 kalilu .
PFX FX 0 kaliku .
PFX FX 0 kalitu .
PFX FX 0 kagan [^lmnb]
PFX FX l kagand l.[^mn]
PFX FX l kagann l.[mn]
PFX FX w kagamp [w]
PFX FX 0 kagamu .
PFX FX 0 kagaba .
PFX FX 0 kagagu .
PFX FX 0 kagagi .
PFX FX 0 kagazi .
PFX FX 0 kagaki .
PFX FX 0 kagabi .
PFX FX 0 kagali .
PFX FX 0 kagaga .
PFX FX 0 kagaka .
PFX FX 0 kagabu .
PFX FX 0 kagalu .
PFX FX 0 kagaku .
PFX FX 0 kagatu .
PFX FX 0 kakan [^lmnb]
PFX FX l kakand l.[^mn]
PFX FX l kakann l.[mn]
PFX FX w kakamp [w]
PFX FX 0 kakamu .
PFX FX 0 kakaba .
PFX FX 0 kakagu .
PFX FX 0 kakagi .
PFX FX 0 kakazi .
PFX FX 0 kakaki .
PFX FX 0 kakabi .
PFX FX 0 kakali .
PFX FX 0 kakaga .
PFX FX 0 kakaka .
PFX FX 0 kakabu .
PFX FX 0 kakalu .
PFX FX 0 kakaku .
PFX FX 0 kakatu .
PFX FX 0 kabun [^lmnb]
PFX FX l kabund l.[^mn]
PFX FX l kabunn l.[mn]
PFX FX w kabump [w]
PFX FX 0 kabumu .
PFX FX 0 kabuba .
PFX FX 0 kabugu .
PFX FX 0 kabugi .
PFX FX 0 kabuzi .
PFX FX 0 kabuki .
PFX FX 0 kabubi .
PFX FX 0 kabuli .
PFX FX 0 kabuga .
PFX FX 0 kabuka .
PFX FX 0 kabubu .
PFX FX 0 kabulu .
PFX FX 0 kabuku .
PFX FX 0 kabutu .
PFX FX 0 kalun [^lmnb]
PFX FX l kalund l.[^mn]
PFX FX l kalunn l.[mn]
PFX FX w kalump [w]
PFX FX 0 kalumu .
PFX FX 0 kaluba .
PFX FX 0 kalugu .
PFX FX 0 kalugi .
PFX FX 0 kaluzi .
PFX FX 0 kaluki .
PFX FX 0 kalubi .
PFX FX 0 kaluli .
PFX FX 0 kaluga .
PFX FX 0 kaluka .
PFX FX 0 kalubu .
PFX FX 0 kalulu .
PFX FX 0 kaluku .
PFX FX 0 kalutu .
PFX FX 0 kakun [^lmnb]
PFX FX l kakund l.[^mn]
PFX FX l kakunn l.[mn]
PFX FX w kakump [w]
PFX FX 0 kakumu .
PFX FX 0 kakuba .
PFX FX 0 kakugu .
PFX FX 0 kakugi .
PFX FX 0 kakuzi .
PFX FX 0 kakuki .
PFX FX 0 kakubi .
PFX FX 0 kakuli .
PFX FX 0 kakuga .
PFX FX 0 kakuka .
PFX FX 0 kakubu .
PFX FX 0 kakulu .
PFX FX 0 kakuku .
PFX FX 0 kakutu ."""

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
    "FX": "FX",
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

    out_flag = "HC"
    left_desc = FLAG_DESCRIPTIONS.get("FX", "FX")
    right_desc = FLAG_DESCRIPTIONS.get("Ob", "Ob")
    comment_line = "# Cross product of {} ({}) and {} ({}) to {}".format(
        "FX", left_desc, "Ob", right_desc, out_flag
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
