import re
import os
from pathlib import Path

# Cross product generator: NN x OR => JO
# Description:
# - Left block `NN`: NN
# - Right block `OR`: Special reflexive object markers
# - Output flag `JO`: Cross-product prefixes for NN x OR

REPO_ROOT = Path(__file__).resolve().parents[1]
AFF_FILE = REPO_ROOT / "Luganda.aff"

# If set to a flag name (e.g. "HB"), the generated cross-product block will be inserted
# immediately before the first "PFX <flag>" line when the output flag block doesn't
# already exist in the .aff.
INSERT_BEFORE_FLAG = "".strip() or None

rule_left_raw = """
PFX NN Y 553
PFX NN 0 ngu .
PFX NN 0 ngi .
PFX NN 0 nzi .
PFX NN 0 nki .
PFX NN 0 nga .
PFX NN 0 nka .
PFX NN 0 nku .
PFX NN 0 ntu .
PFX NN 0 mba .
PFX NN 0 mbi .
PFX NN 0 mbu .
PFX NN 0 on [^lmn]
PFX NN l ond l.[^mn]
PFX NN l onn l.[mn]
PFX NN w omp [w]
PFX NN 0 omu .
PFX NN 0 oba .
PFX NN 0 ogu .
PFX NN 0 ogi .
PFX NN 0 ozi .
PFX NN 0 oki .
PFX NN 0 obi .
PFX NN 0 oli .
PFX NN 0 oga .
PFX NN 0 oka .
PFX NN 0 obu .
PFX NN 0 olu .
PFX NN 0 oku .
PFX NN 0 otu .
PFX NN 0 ndi .
PFX NN 0 ndu .
PFX NN 0 an [^lmn]
PFX NN l and l.[^mn]
PFX NN l ann l.[mn]
PFX NN w amp [w]
PFX NN 0 amu .
PFX NN 0 aba .
PFX NN 0 agu .
PFX NN 0 agi .
PFX NN 0 azi .
PFX NN 0 aki .
PFX NN 0 abi .
PFX NN 0 ali .
PFX NN 0 aga .
PFX NN 0 aka .
PFX NN 0 abu .
PFX NN 0 alu .
PFX NN 0 aku .
PFX NN 0 atu .
PFX NN 0 tun [^lmn]
PFX NN l tund l.[^mn]
PFX NN l tunn l.[mn]
PFX NN w tump [w]
PFX NN 0 tumu .
PFX NN 0 tuba .
PFX NN 0 tugu .
PFX NN 0 tugi .
PFX NN 0 tuzi .
PFX NN 0 tuki .
PFX NN 0 tubi .
PFX NN 0 tuli .
PFX NN 0 tuga .
PFX NN 0 tuka .
PFX NN 0 tubu .
PFX NN 0 tulu .
PFX NN 0 tuku .
PFX NN 0 tutu .
PFX NN 0 mun [^lmn]
PFX NN l mund l.[^mn]
PFX NN l munn l.[mn]
PFX NN w mump [w]
PFX NN 0 mumu .
PFX NN 0 muba .
PFX NN 0 mugu .
PFX NN 0 mugi .
PFX NN 0 muzi .
PFX NN 0 muki .
PFX NN 0 mubi .
PFX NN 0 muli .
PFX NN 0 muga .
PFX NN 0 muka .
PFX NN 0 mubu .
PFX NN 0 mulu .
PFX NN 0 muku .
PFX NN 0 mutu .
PFX NN 0 ban [^lmn]
PFX NN l band l.[^mn]
PFX NN l bann l.[mn]
PFX NN w bamp [w]
PFX NN 0 bamu .
PFX NN 0 baba .
PFX NN 0 bagu .
PFX NN 0 bagi .
PFX NN 0 bazi .
PFX NN 0 baki .
PFX NN 0 babi .
PFX NN 0 bali .
PFX NN 0 baga .
PFX NN 0 baka .
PFX NN 0 babu .
PFX NN 0 balu .
PFX NN 0 baku .
PFX NN 0 batu .
PFX NN 0 aban [^lmn]
PFX NN l aband l.[^mn]
PFX NN l abann l.[mn]
PFX NN w abamp [w]
PFX NN 0 abamu .
PFX NN 0 ababa .
PFX NN 0 abagu .
PFX NN 0 abagi .
PFX NN 0 abazi .
PFX NN 0 abaki .
PFX NN 0 ababi .
PFX NN 0 abali .
PFX NN 0 abaga .
PFX NN 0 abaka .
PFX NN 0 ababu .
PFX NN 0 abalu .
PFX NN 0 abaku .
PFX NN 0 abatu .
PFX NN 0 gun [^lmn]
PFX NN l gund l.[^mn]
PFX NN l gunn l.[mn]
PFX NN w gump [w]
PFX NN 0 gumu .
PFX NN 0 guba .
PFX NN 0 gugu .
PFX NN 0 gugi .
PFX NN 0 guzi .
PFX NN 0 guki .
PFX NN 0 gubi .
PFX NN 0 guli .
PFX NN 0 guga .
PFX NN 0 guka .
PFX NN 0 gubu .
PFX NN 0 gulu .
PFX NN 0 guku .
PFX NN 0 gutu .
PFX NN 0 ogun [^lmn]
PFX NN l ogund l.[^mn]
PFX NN l ogunn l.[mn]
PFX NN w ogump [w]
PFX NN 0 ogumu .
PFX NN 0 oguba .
PFX NN 0 ogugu .
PFX NN 0 ogugi .
PFX NN 0 oguzi .
PFX NN 0 oguki .
PFX NN 0 ogubi .
PFX NN 0 oguli .
PFX NN 0 oguga .
PFX NN 0 oguka .
PFX NN 0 ogubu .
PFX NN 0 ogulu .
PFX NN 0 oguku .
PFX NN 0 ogutu .
PFX NN 0 gin [^lmn]
PFX NN l gind l.[^mn]
PFX NN l ginn l.[mn]
PFX NN w gimp [w]
PFX NN 0 gimu .
PFX NN 0 giba .
PFX NN 0 gigu .
PFX NN 0 gigi .
PFX NN 0 gizi .
PFX NN 0 giki .
PFX NN 0 gibi .
PFX NN 0 gili .
PFX NN 0 giga .
PFX NN 0 gika .
PFX NN 0 gibu .
PFX NN 0 gilu .
PFX NN 0 giku .
PFX NN 0 gitu .
PFX NN 0 egin [^lmn]
PFX NN l egind l.[^mn]
PFX NN l eginn l.[mn]
PFX NN w egimp [w]
PFX NN 0 egimu .
PFX NN 0 egiba .
PFX NN 0 egigu .
PFX NN 0 egigi .
PFX NN 0 egizi .
PFX NN 0 egiki .
PFX NN 0 egibi .
PFX NN 0 egili .
PFX NN 0 egiga .
PFX NN 0 egika .
PFX NN 0 egibu .
PFX NN 0 egilu .
PFX NN 0 egiku .
PFX NN 0 egitu .
PFX NN 0 en [^lmn]
PFX NN l end l.[^mn]
PFX NN l enn l.[mn]
PFX NN w emp [w]
PFX NN 0 emu .
PFX NN 0 eba .
PFX NN 0 egu .
PFX NN 0 egi .
PFX NN 0 ezi .
PFX NN 0 eki .
PFX NN 0 ebi .
PFX NN 0 eli .
PFX NN 0 ega .
PFX NN 0 eka .
PFX NN 0 ebu .
PFX NN 0 elu .
PFX NN 0 eku .
PFX NN 0 etu .
PFX NN 0 zin [^lmn]
PFX NN l zind l.[^mn]
PFX NN l zinn l.[mn]
PFX NN w zimp [w]
PFX NN 0 zimu .
PFX NN 0 ziba .
PFX NN 0 zigu .
PFX NN 0 zigi .
PFX NN 0 zizi .
PFX NN 0 ziki .
PFX NN 0 zibi .
PFX NN 0 zili .
PFX NN 0 ziga .
PFX NN 0 zika .
PFX NN 0 zibu .
PFX NN 0 zilu .
PFX NN 0 ziku .
PFX NN 0 zitu .
PFX NN 0 ezin [^lmn]
PFX NN l ezind l.[^mn]
PFX NN l ezinn l.[mn]
PFX NN w ezimp [w]
PFX NN 0 ezimu .
PFX NN 0 eziba .
PFX NN 0 ezigu .
PFX NN 0 ezigi .
PFX NN 0 ezizi .
PFX NN 0 eziki .
PFX NN 0 ezibi .
PFX NN 0 ezili .
PFX NN 0 eziga .
PFX NN 0 ezika .
PFX NN 0 ezibu .
PFX NN 0 ezilu .
PFX NN 0 eziku .
PFX NN 0 ezitu .
PFX NN 0 kin [^lmn]
PFX NN l kind l.[^mn]
PFX NN l kinn l.[mn]
PFX NN w kimp [w]
PFX NN 0 kimu .
PFX NN 0 kiba .
PFX NN 0 kigu .
PFX NN 0 kigi .
PFX NN 0 kizi .
PFX NN 0 kiki .
PFX NN 0 kibi .
PFX NN 0 kili .
PFX NN 0 kiga .
PFX NN 0 kika .
PFX NN 0 kibu .
PFX NN 0 kilu .
PFX NN 0 kiku .
PFX NN 0 kitu .
PFX NN 0 ekin [^lmn]
PFX NN l ekind l.[^mn]
PFX NN l ekinn l.[mn]
PFX NN w ekimp [w]
PFX NN 0 ekimu .
PFX NN 0 ekiba .
PFX NN 0 ekigu .
PFX NN 0 ekigi .
PFX NN 0 ekizi .
PFX NN 0 ekiki .
PFX NN 0 ekibi .
PFX NN 0 ekili .
PFX NN 0 ekiga .
PFX NN 0 ekika .
PFX NN 0 ekibu .
PFX NN 0 ekilu .
PFX NN 0 ekiku .
PFX NN 0 ekitu .
PFX NN 0 bin [^lmn]
PFX NN l bind l.[^mn]
PFX NN l binn l.[mn]
PFX NN w bimp [w]
PFX NN 0 bimu .
PFX NN 0 biba .
PFX NN 0 bigu .
PFX NN 0 bigi .
PFX NN 0 bizi .
PFX NN 0 biki .
PFX NN 0 bibi .
PFX NN 0 bili .
PFX NN 0 biga .
PFX NN 0 bika .
PFX NN 0 bibu .
PFX NN 0 bilu .
PFX NN 0 biku .
PFX NN 0 bitu .
PFX NN 0 ebin [^lmn]
PFX NN l ebind l.[^mn]
PFX NN l ebinn l.[mn]
PFX NN w ebimp [w]
PFX NN 0 ebimu .
PFX NN 0 ebiba .
PFX NN 0 ebigu .
PFX NN 0 ebigi .
PFX NN 0 ebizi .
PFX NN 0 ebiki .
PFX NN 0 ebibi .
PFX NN 0 ebili .
PFX NN 0 ebiga .
PFX NN 0 ebika .
PFX NN 0 ebibu .
PFX NN 0 ebilu .
PFX NN 0 ebiku .
PFX NN 0 ebitu .
PFX NN 0 lin [^lmn]
PFX NN l lind l.[^mn]
PFX NN l linn l.[mn]
PFX NN w limp [w]
PFX NN 0 limu .
PFX NN 0 liba .
PFX NN 0 ligu .
PFX NN 0 ligi .
PFX NN 0 lizi .
PFX NN 0 liki .
PFX NN 0 libi .
PFX NN 0 lili .
PFX NN 0 liga .
PFX NN 0 lika .
PFX NN 0 libu .
PFX NN 0 lilu .
PFX NN 0 liku .
PFX NN 0 litu .
PFX NN 0 elin [^lmn]
PFX NN l elind l.[^mn]
PFX NN l elinn l.[mn]
PFX NN w elimp [w]
PFX NN 0 elimu .
PFX NN 0 eliba .
PFX NN 0 eligu .
PFX NN 0 eligi .
PFX NN 0 elizi .
PFX NN 0 eliki .
PFX NN 0 elibi .
PFX NN 0 elili .
PFX NN 0 eliga .
PFX NN 0 elika .
PFX NN 0 elibu .
PFX NN 0 elilu .
PFX NN 0 eliku .
PFX NN 0 elitu .
PFX NN 0 gan [^lmn]
PFX NN l gand l.[^mn]
PFX NN l gann l.[mn]
PFX NN w gamp [w]
PFX NN 0 gamu .
PFX NN 0 gaba .
PFX NN 0 gagu .
PFX NN 0 gagi .
PFX NN 0 gazi .
PFX NN 0 gaki .
PFX NN 0 gabi .
PFX NN 0 gali .
PFX NN 0 gaga .
PFX NN 0 gaka .
PFX NN 0 gabu .
PFX NN 0 galu .
PFX NN 0 gaku .
PFX NN 0 gatu .
PFX NN 0 agan [^lmn]
PFX NN l agand l.[^mn]
PFX NN l agann l.[mn]
PFX NN w agamp [w]
PFX NN 0 agamu .
PFX NN 0 agaba .
PFX NN 0 agagu .
PFX NN 0 agagi .
PFX NN 0 agazi .
PFX NN 0 agaki .
PFX NN 0 agabi .
PFX NN 0 agali .
PFX NN 0 agaga .
PFX NN 0 agaka .
PFX NN 0 agabu .
PFX NN 0 agalu .
PFX NN 0 agaku .
PFX NN 0 agatu .
PFX NN 0 kan [^lmn]
PFX NN l kand l.[^mn]
PFX NN l kann l.[mn]
PFX NN w kamp [w]
PFX NN 0 kamu .
PFX NN 0 kaba .
PFX NN 0 kagu .
PFX NN 0 kagi .
PFX NN 0 kazi .
PFX NN 0 kaki .
PFX NN 0 kabi .
PFX NN 0 kali .
PFX NN 0 kaga .
PFX NN 0 kaka .
PFX NN 0 kabu .
PFX NN 0 kalu .
PFX NN 0 kaku .
PFX NN 0 katu .
PFX NN 0 akan [^lmn]
PFX NN l akand l.[^mn]
PFX NN l akann l.[mn]
PFX NN w akamp [w]
PFX NN 0 akamu .
PFX NN 0 akaba .
PFX NN 0 akagu .
PFX NN 0 akagi .
PFX NN 0 akazi .
PFX NN 0 akaki .
PFX NN 0 akabi .
PFX NN 0 akali .
PFX NN 0 akaga .
PFX NN 0 akaka .
PFX NN 0 akabu .
PFX NN 0 akalu .
PFX NN 0 akaku .
PFX NN 0 akatu .
PFX NN 0 bun [^lmn]
PFX NN l bund l.[^mn]
PFX NN l bunn l.[mn]
PFX NN w bump [w]
PFX NN 0 bumu .
PFX NN 0 buba .
PFX NN 0 bugu .
PFX NN 0 bugi .
PFX NN 0 buzi .
PFX NN 0 buki .
PFX NN 0 bubi .
PFX NN 0 buli .
PFX NN 0 buga .
PFX NN 0 buka .
PFX NN 0 bubu .
PFX NN 0 bulu .
PFX NN 0 buku .
PFX NN 0 butu .
PFX NN 0 obun [^lmn]
PFX NN l obund l.[^mn]
PFX NN l obunn l.[mn]
PFX NN w obump [w]
PFX NN 0 obumu .
PFX NN 0 obuba .
PFX NN 0 obugu .
PFX NN 0 obugi .
PFX NN 0 obuzi .
PFX NN 0 obuki .
PFX NN 0 obubi .
PFX NN 0 obuli .
PFX NN 0 obuga .
PFX NN 0 obuka .
PFX NN 0 obubu .
PFX NN 0 obulu .
PFX NN 0 obuku .
PFX NN 0 obutu .
PFX NN 0 lun [^lmn]
PFX NN l lund l.[^mn]
PFX NN l lunn l.[mn]
PFX NN w lump [w]
PFX NN 0 lumu .
PFX NN 0 luba .
PFX NN 0 lugu .
PFX NN 0 lugi .
PFX NN 0 luzi .
PFX NN 0 luki .
PFX NN 0 lubi .
PFX NN 0 luli .
PFX NN 0 luga .
PFX NN 0 luka .
PFX NN 0 lubu .
PFX NN 0 lulu .
PFX NN 0 luku .
PFX NN 0 lutu .
PFX NN 0 olun [^lmn]
PFX NN l olund l.[^mn]
PFX NN l olunn l.[mn]
PFX NN w olump [w]
PFX NN 0 olumu .
PFX NN 0 oluba .
PFX NN 0 olugu .
PFX NN 0 olugi .
PFX NN 0 oluzi .
PFX NN 0 oluki .
PFX NN 0 olubi .
PFX NN 0 oluli .
PFX NN 0 oluga .
PFX NN 0 oluka .
PFX NN 0 olubu .
PFX NN 0 olulu .
PFX NN 0 oluku .
PFX NN 0 olutu .
PFX NN 0 kun [^lmn]
PFX NN l kund l.[^mn]
PFX NN l kunn l.[mn]
PFX NN w kump [w]
PFX NN 0 kumu .
PFX NN 0 kuba .
PFX NN 0 kugu .
PFX NN 0 kugi .
PFX NN 0 kuzi .
PFX NN 0 kuki .
PFX NN 0 kubi .
PFX NN 0 kuli .
PFX NN 0 kuga .
PFX NN 0 kuka .
PFX NN 0 kubu .
PFX NN 0 kulu .
PFX NN 0 kuku .
PFX NN 0 kutu .
PFX NN 0 okun [^lmn]
PFX NN l okund l.[^mn]
PFX NN l okunn l.[mn]
PFX NN w okump [w]
PFX NN 0 okumu .
PFX NN 0 okuba .
PFX NN 0 okugu .
PFX NN 0 okugi .
PFX NN 0 okuzi .
PFX NN 0 okuki .
PFX NN 0 okubi .
PFX NN 0 okuli .
PFX NN 0 okuga .
PFX NN 0 okuka .
PFX NN 0 okubu .
PFX NN 0 okulu .
PFX NN 0 okuku .
PFX NN 0 okutu .
PFX NN 0 otun [^lmn]
PFX NN l otund l.[^mn]
PFX NN l otunn l.[mn]
PFX NN w otump [w]
PFX NN 0 otumu .
PFX NN 0 otuba .
PFX NN 0 otugu .
PFX NN 0 otugi .
PFX NN 0 otuzi .
PFX NN 0 otuki .
PFX NN 0 otubi .
PFX NN 0 otuli .
PFX NN 0 otuga .
PFX NN 0 otuka .
PFX NN 0 otubu .
PFX NN 0 otulu .
PFX NN 0 otuku .
PFX NN 0 otutu ."""

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
    "NN": "NN",
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

    out_flag = "JO"
    left_desc = FLAG_DESCRIPTIONS.get("NN", "NN")
    right_desc = FLAG_DESCRIPTIONS.get("OR", "OR")
    comment_line = "# Cross product of {} ({}) and {} ({}) to {}".format(
        "NN", left_desc, "OR", right_desc, out_flag
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
