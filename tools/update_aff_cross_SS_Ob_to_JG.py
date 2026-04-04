import re
import os
from pathlib import Path

# Cross product generator: SS x Ob => JG
# Description:
# - Left block `SS`: SS
# - Right block `Ob`: Object markers
# - Output flag `JG`: Cross-product prefixes for SS x Ob

REPO_ROOT = Path(__file__).resolve().parents[1]
AFF_FILE = REPO_ROOT / "Luganda.aff"

# If set to a flag name (e.g. "HB"), the generated cross-product block will be inserted
# immediately before the first "PFX <flag>" line when the output flag block doesn't
# already exist in the .aff.
INSERT_BEFORE_FLAG = "".strip() or None

rule_left_raw = """
PFX SS Y 590
PFX SS 0 simu .
PFX SS 0 siba .
PFX SS 0 sigu .
PFX SS 0 sigi .
PFX SS 0 sizi .
PFX SS 0 siki .
PFX SS 0 sibi .
PFX SS 0 sili .
PFX SS 0 siga .
PFX SS 0 sika .
PFX SS 0 sibu .
PFX SS 0 silu .
PFX SS 0 siku .
PFX SS 0 situ .
PFX SS 0 ton [^lmn]
PFX SS l tond l.[^mn]
PFX SS l tonn l.[mn]
PFX SS w tomp [w]
PFX SS 0 tomu .
PFX SS 0 toba .
PFX SS 0 togu .
PFX SS 0 togi .
PFX SS 0 tozi .
PFX SS 0 toki .
PFX SS 0 tobi .
PFX SS 0 toli .
PFX SS 0 toga .
PFX SS 0 toka .
PFX SS 0 tobu .
PFX SS 0 tolu .
PFX SS 0 toku .
PFX SS 0 totu .
PFX SS 0 tan [^lmn]
PFX SS l tand l.[^mn]
PFX SS l tann l.[mn]
PFX SS w tamp [w]
PFX SS 0 tamu .
PFX SS 0 taba .
PFX SS 0 tagu .
PFX SS 0 tagi .
PFX SS 0 tazi .
PFX SS 0 taki .
PFX SS 0 tabi .
PFX SS 0 tali .
PFX SS 0 taga .
PFX SS 0 taka .
PFX SS 0 tabu .
PFX SS 0 talu .
PFX SS 0 taku .
PFX SS 0 tatu .
PFX SS 0 tetun [^lmn]
PFX SS l tetund l.[^mn]
PFX SS l tetunn l.[mn]
PFX SS w tetump [w]
PFX SS 0 tetumu .
PFX SS 0 tetuba .
PFX SS 0 tetugu .
PFX SS 0 tetugi .
PFX SS 0 tetuzi .
PFX SS 0 tetuki .
PFX SS 0 tetubi .
PFX SS 0 tetuli .
PFX SS 0 tetuga .
PFX SS 0 tetuka .
PFX SS 0 tetubu .
PFX SS 0 tetulu .
PFX SS 0 tetuku .
PFX SS 0 tetutu .
PFX SS 0 temun [^lmn]
PFX SS l temund l.[^mn]
PFX SS l temunn l.[mn]
PFX SS w temump [w]
PFX SS 0 temumu .
PFX SS 0 temuba .
PFX SS 0 temugu .
PFX SS 0 temugi .
PFX SS 0 temuzi .
PFX SS 0 temuki .
PFX SS 0 temubi .
PFX SS 0 temuli .
PFX SS 0 temuga .
PFX SS 0 temuka .
PFX SS 0 temubu .
PFX SS 0 temulu .
PFX SS 0 temuku .
PFX SS 0 temutu .
PFX SS 0 teban [^lmn]
PFX SS l teband l.[^mn]
PFX SS l tebann l.[mn]
PFX SS w tebamp [w]
PFX SS 0 tebamu .
PFX SS 0 tebaba .
PFX SS 0 tebagu .
PFX SS 0 tebagi .
PFX SS 0 tebazi .
PFX SS 0 tebaki .
PFX SS 0 tebabi .
PFX SS 0 tebali .
PFX SS 0 tebaga .
PFX SS 0 tebaka .
PFX SS 0 tebabu .
PFX SS 0 tebalu .
PFX SS 0 tebaku .
PFX SS 0 tebatu .
PFX SS 0 abatan [^lmn]
PFX SS l abatand l.[^mn]
PFX SS l abatann l.[mn]
PFX SS w abatamp [w]
PFX SS 0 abatamu .
PFX SS 0 abataba .
PFX SS 0 abatagu .
PFX SS 0 abatagi .
PFX SS 0 abatazi .
PFX SS 0 abataki .
PFX SS 0 abatabi .
PFX SS 0 abatali .
PFX SS 0 abataga .
PFX SS 0 abataka .
PFX SS 0 abatabu .
PFX SS 0 abatalu .
PFX SS 0 abataku .
PFX SS 0 abatatu .
PFX SS 0 tegun [^lmn]
PFX SS l tegund l.[^mn]
PFX SS l tegunn l.[mn]
PFX SS w tegump [w]
PFX SS 0 tegumu .
PFX SS 0 teguba .
PFX SS 0 tegugu .
PFX SS 0 tegugi .
PFX SS 0 teguzi .
PFX SS 0 teguki .
PFX SS 0 tegubi .
PFX SS 0 teguli .
PFX SS 0 teguga .
PFX SS 0 teguka .
PFX SS 0 tegubu .
PFX SS 0 tegulu .
PFX SS 0 teguku .
PFX SS 0 tegutu .
PFX SS 0 ogutan [^lmn]
PFX SS l ogutand l.[^mn]
PFX SS l ogutann l.[mn]
PFX SS w ogutamp [w]
PFX SS 0 ogutamu .
PFX SS 0 ogutaba .
PFX SS 0 ogutagu .
PFX SS 0 ogutagi .
PFX SS 0 ogutazi .
PFX SS 0 ogutaki .
PFX SS 0 ogutabi .
PFX SS 0 ogutali .
PFX SS 0 ogutaga .
PFX SS 0 ogutaka .
PFX SS 0 ogutabu .
PFX SS 0 ogutalu .
PFX SS 0 ogutaku .
PFX SS 0 ogutatu .
PFX SS 0 tegin [^lmn]
PFX SS l tegind l.[^mn]
PFX SS l teginn l.[mn]
PFX SS w tegimp [w]
PFX SS 0 tegimu .
PFX SS 0 tegiba .
PFX SS 0 tegigu .
PFX SS 0 tegigi .
PFX SS 0 tegizi .
PFX SS 0 tegiki .
PFX SS 0 tegibi .
PFX SS 0 tegili .
PFX SS 0 tegiga .
PFX SS 0 tegika .
PFX SS 0 tegibu .
PFX SS 0 tegilu .
PFX SS 0 tegiku .
PFX SS 0 tegitu .
PFX SS 0 egitan [^lmn]
PFX SS l egitand l.[^mn]
PFX SS l egitann l.[mn]
PFX SS w egitamp [w]
PFX SS 0 egitamu .
PFX SS 0 egitaba .
PFX SS 0 egitagu .
PFX SS 0 egitagi .
PFX SS 0 egitazi .
PFX SS 0 egitaki .
PFX SS 0 egitabi .
PFX SS 0 egitali .
PFX SS 0 egitaga .
PFX SS 0 egitaka .
PFX SS 0 egitabu .
PFX SS 0 egitalu .
PFX SS 0 egitaku .
PFX SS 0 egitatu .
PFX SS 0 ten [^lmn]
PFX SS l tend l.[^mn]
PFX SS l tenn l.[mn]
PFX SS w temp [w]
PFX SS 0 temu .
PFX SS 0 teba .
PFX SS 0 tegu .
PFX SS 0 tegi .
PFX SS 0 tezi .
PFX SS 0 teki .
PFX SS 0 tebi .
PFX SS 0 teli .
PFX SS 0 tega .
PFX SS 0 teka .
PFX SS 0 tebu .
PFX SS 0 telu .
PFX SS 0 teku .
PFX SS 0 tetu .
PFX SS 0 eten [^lmn]
PFX SS l etend l.[^mn]
PFX SS l etenn l.[mn]
PFX SS w etemp [w]
PFX SS 0 etemu .
PFX SS 0 eteba .
PFX SS 0 etegu .
PFX SS 0 etegi .
PFX SS 0 etezi .
PFX SS 0 eteki .
PFX SS 0 etebi .
PFX SS 0 eteli .
PFX SS 0 etega .
PFX SS 0 eteka .
PFX SS 0 etebu .
PFX SS 0 etelu .
PFX SS 0 eteku .
PFX SS 0 etetu .
PFX SS 0 tezin [^lmn]
PFX SS l tezind l.[^mn]
PFX SS l tezinn l.[mn]
PFX SS w tezimp [w]
PFX SS 0 tezimu .
PFX SS 0 teziba .
PFX SS 0 tezigu .
PFX SS 0 tezigi .
PFX SS 0 tezizi .
PFX SS 0 teziki .
PFX SS 0 tezibi .
PFX SS 0 tezili .
PFX SS 0 teziga .
PFX SS 0 tezika .
PFX SS 0 tezibu .
PFX SS 0 tezilu .
PFX SS 0 teziku .
PFX SS 0 tezitu .
PFX SS 0 ezitan [^lmn]
PFX SS l ezitand l.[^mn]
PFX SS l ezitann l.[mn]
PFX SS w ezitamp [w]
PFX SS 0 ezitamu .
PFX SS 0 ezitaba .
PFX SS 0 ezitagu .
PFX SS 0 ezitagi .
PFX SS 0 ezitazi .
PFX SS 0 ezitaki .
PFX SS 0 ezitabi .
PFX SS 0 ezitali .
PFX SS 0 ezitaga .
PFX SS 0 ezitaka .
PFX SS 0 ezitabu .
PFX SS 0 ezitalu .
PFX SS 0 ezitaku .
PFX SS 0 ezitatu .
PFX SS 0 tekin [^lmn]
PFX SS l tekind l.[^mn]
PFX SS l tekinn l.[mn]
PFX SS w tekimp [w]
PFX SS 0 tekimu .
PFX SS 0 tekiba .
PFX SS 0 tekigu .
PFX SS 0 tekigi .
PFX SS 0 tekizi .
PFX SS 0 tekiki .
PFX SS 0 tekibi .
PFX SS 0 tekili .
PFX SS 0 tekiga .
PFX SS 0 tekika .
PFX SS 0 tekibu .
PFX SS 0 tekilu .
PFX SS 0 tekiku .
PFX SS 0 tekitu .
PFX SS 0 ekitan [^lmn]
PFX SS l ekitand l.[^mn]
PFX SS l ekitann l.[mn]
PFX SS w ekitamp [w]
PFX SS 0 ekitamu .
PFX SS 0 ekitaba .
PFX SS 0 ekitagu .
PFX SS 0 ekitagi .
PFX SS 0 ekitazi .
PFX SS 0 ekitaki .
PFX SS 0 ekitabi .
PFX SS 0 ekitali .
PFX SS 0 ekitaga .
PFX SS 0 ekitaka .
PFX SS 0 ekitabu .
PFX SS 0 ekitalu .
PFX SS 0 ekitaku .
PFX SS 0 ekitatu .
PFX SS 0 tebin [^lmn]
PFX SS l tebind l.[^mn]
PFX SS l tebinn l.[mn]
PFX SS w tebimp [w]
PFX SS 0 tebimu .
PFX SS 0 tebiba .
PFX SS 0 tebigu .
PFX SS 0 tebigi .
PFX SS 0 tebizi .
PFX SS 0 tebiki .
PFX SS 0 tebibi .
PFX SS 0 tebili .
PFX SS 0 tebiga .
PFX SS 0 tebika .
PFX SS 0 tebibu .
PFX SS 0 tebilu .
PFX SS 0 tebiku .
PFX SS 0 tebitu .
PFX SS 0 ebitan [^lmn]
PFX SS l ebitand l.[^mn]
PFX SS l ebitann l.[mn]
PFX SS w ebitamp [w]
PFX SS 0 ebitamu .
PFX SS 0 ebitaba .
PFX SS 0 ebitagu .
PFX SS 0 ebitagi .
PFX SS 0 ebitazi .
PFX SS 0 ebitaki .
PFX SS 0 ebitabi .
PFX SS 0 ebitali .
PFX SS 0 ebitaga .
PFX SS 0 ebitaka .
PFX SS 0 ebitabu .
PFX SS 0 ebitalu .
PFX SS 0 ebitaku .
PFX SS 0 ebitatu .
PFX SS 0 telin [^lmn]
PFX SS l telind l.[^mn]
PFX SS l telinn l.[mn]
PFX SS w telimp [w]
PFX SS 0 telimu .
PFX SS 0 teliba .
PFX SS 0 teligu .
PFX SS 0 teligi .
PFX SS 0 telizi .
PFX SS 0 teliki .
PFX SS 0 telibi .
PFX SS 0 telili .
PFX SS 0 teliga .
PFX SS 0 telika .
PFX SS 0 telibu .
PFX SS 0 telilu .
PFX SS 0 teliku .
PFX SS 0 telitu .
PFX SS 0 elitan [^lmn]
PFX SS l elitand l.[^mn]
PFX SS l elitann l.[mn]
PFX SS w elitamp [w]
PFX SS 0 elitamu .
PFX SS 0 elitaba .
PFX SS 0 elitagu .
PFX SS 0 elitagi .
PFX SS 0 elitazi .
PFX SS 0 elitaki .
PFX SS 0 elitabi .
PFX SS 0 elitali .
PFX SS 0 elitaga .
PFX SS 0 elitaka .
PFX SS 0 elitabu .
PFX SS 0 elitalu .
PFX SS 0 elitaku .
PFX SS 0 elitatu .
PFX SS 0 tegan [^lmn]
PFX SS l tegand l.[^mn]
PFX SS l tegann l.[mn]
PFX SS w tegamp [w]
PFX SS 0 tegamu .
PFX SS 0 tegaba .
PFX SS 0 tegagu .
PFX SS 0 tegagi .
PFX SS 0 tegazi .
PFX SS 0 tegaki .
PFX SS 0 tegabi .
PFX SS 0 tegali .
PFX SS 0 tegaga .
PFX SS 0 tegaka .
PFX SS 0 tegabu .
PFX SS 0 tegalu .
PFX SS 0 tegaku .
PFX SS 0 tegatu .
PFX SS 0 agatan [^lmn]
PFX SS l agatand l.[^mn]
PFX SS l agatann l.[mn]
PFX SS w agatamp [w]
PFX SS 0 agatamu .
PFX SS 0 agataba .
PFX SS 0 agatagu .
PFX SS 0 agatagi .
PFX SS 0 agatazi .
PFX SS 0 agataki .
PFX SS 0 agatabi .
PFX SS 0 agatali .
PFX SS 0 agataga .
PFX SS 0 agataka .
PFX SS 0 agatabu .
PFX SS 0 agatalu .
PFX SS 0 agataku .
PFX SS 0 agatatu .
PFX SS 0 tekan [^lmn]
PFX SS l tekand l.[^mn]
PFX SS l tekann l.[mn]
PFX SS w tekamp [w]
PFX SS 0 tekamu .
PFX SS 0 tekaba .
PFX SS 0 tekagu .
PFX SS 0 tekagi .
PFX SS 0 tekazi .
PFX SS 0 tekaki .
PFX SS 0 tekabi .
PFX SS 0 tekali .
PFX SS 0 tekaga .
PFX SS 0 tekaka .
PFX SS 0 tekabu .
PFX SS 0 tekalu .
PFX SS 0 tekaku .
PFX SS 0 tekatu .
PFX SS 0 akatan [^lmn]
PFX SS l akatand l.[^mn]
PFX SS l akatann l.[mn]
PFX SS w akatamp [w]
PFX SS 0 akatamu .
PFX SS 0 akataba .
PFX SS 0 akatagu .
PFX SS 0 akatagi .
PFX SS 0 akatazi .
PFX SS 0 akataki .
PFX SS 0 akatabi .
PFX SS 0 akatali .
PFX SS 0 akataga .
PFX SS 0 akataka .
PFX SS 0 akatabu .
PFX SS 0 akatalu .
PFX SS 0 akataku .
PFX SS 0 akatatu .
PFX SS 0 tebun [^lmn]
PFX SS l tebund l.[^mn]
PFX SS l tebunn l.[mn]
PFX SS w tebump [w]
PFX SS 0 tebumu .
PFX SS 0 tebuba .
PFX SS 0 tebugu .
PFX SS 0 tebugi .
PFX SS 0 tebuzi .
PFX SS 0 tebuki .
PFX SS 0 tebubi .
PFX SS 0 tebuli .
PFX SS 0 tebuga .
PFX SS 0 tebuka .
PFX SS 0 tebubu .
PFX SS 0 tebulu .
PFX SS 0 tebuku .
PFX SS 0 tebutu .
PFX SS 0 obutan [^lmn]
PFX SS l obutand l.[^mn]
PFX SS l obutann l.[mn]
PFX SS w obutamp [w]
PFX SS 0 obutamu .
PFX SS 0 obutaba .
PFX SS 0 obutagu .
PFX SS 0 obutagi .
PFX SS 0 obutazi .
PFX SS 0 obutaki .
PFX SS 0 obutabi .
PFX SS 0 obutali .
PFX SS 0 obutaga .
PFX SS 0 obutaka .
PFX SS 0 obutabu .
PFX SS 0 obutalu .
PFX SS 0 obutaku .
PFX SS 0 obutatu .
PFX SS 0 telun [^lmn]
PFX SS l telund l.[^mn]
PFX SS l telunn l.[mn]
PFX SS w telump [w]
PFX SS 0 telumu .
PFX SS 0 teluba .
PFX SS 0 telugu .
PFX SS 0 telugi .
PFX SS 0 teluzi .
PFX SS 0 teluki .
PFX SS 0 telubi .
PFX SS 0 teluli .
PFX SS 0 teluga .
PFX SS 0 teluka .
PFX SS 0 telubu .
PFX SS 0 telulu .
PFX SS 0 teluku .
PFX SS 0 telutu .
PFX SS 0 olutan [^lmn]
PFX SS l olutand l.[^mn]
PFX SS l olutann l.[mn]
PFX SS w olutamp [w]
PFX SS 0 olutamu .
PFX SS 0 olutaba .
PFX SS 0 olutagu .
PFX SS 0 olutagi .
PFX SS 0 olutazi .
PFX SS 0 olutaki .
PFX SS 0 olutabi .
PFX SS 0 olutali .
PFX SS 0 olutaga .
PFX SS 0 olutaka .
PFX SS 0 olutabu .
PFX SS 0 olutalu .
PFX SS 0 olutaku .
PFX SS 0 olutatu .
PFX SS 0 tekun [^lmn]
PFX SS l tekund l.[^mn]
PFX SS l tekunn l.[mn]
PFX SS w tekump [w]
PFX SS 0 tekumu .
PFX SS 0 tekuba .
PFX SS 0 tekugu .
PFX SS 0 tekugi .
PFX SS 0 tekuzi .
PFX SS 0 tekuki .
PFX SS 0 tekubi .
PFX SS 0 tekuli .
PFX SS 0 tekuga .
PFX SS 0 tekuka .
PFX SS 0 tekubu .
PFX SS 0 tekulu .
PFX SS 0 tekuku .
PFX SS 0 tekutu .
PFX SS 0 okutan [^lmn]
PFX SS l okutand l.[^mn]
PFX SS l okutann l.[mn]
PFX SS w okutamp [w]
PFX SS 0 okutamu .
PFX SS 0 okutaba .
PFX SS 0 okutagu .
PFX SS 0 okutagi .
PFX SS 0 okutazi .
PFX SS 0 okutaki .
PFX SS 0 okutabi .
PFX SS 0 okutali .
PFX SS 0 okutaga .
PFX SS 0 okutaka .
PFX SS 0 okutabu .
PFX SS 0 okutalu .
PFX SS 0 okutaku .
PFX SS 0 okutatu .
PFX SS 0 tetun [^lmn]
PFX SS l tetund l.[^mn]
PFX SS l tetunn l.[mn]
PFX SS w tetump [w]
PFX SS 0 tetumu .
PFX SS 0 tetuba .
PFX SS 0 tetugu .
PFX SS 0 tetugi .
PFX SS 0 tetuzi .
PFX SS 0 tetuki .
PFX SS 0 tetubi .
PFX SS 0 tetuli .
PFX SS 0 tetuga .
PFX SS 0 tetuka .
PFX SS 0 tetubu .
PFX SS 0 tetulu .
PFX SS 0 tetuku .
PFX SS 0 tetutu .
PFX SS 0 otutan [^lmn]
PFX SS l otutand l.[^mn]
PFX SS l otutann l.[mn]
PFX SS w otutamp [w]
PFX SS 0 otutamu .
PFX SS 0 otutaba .
PFX SS 0 otutagu .
PFX SS 0 otutagi .
PFX SS 0 otutazi .
PFX SS 0 otutaki .
PFX SS 0 otutabi .
PFX SS 0 otutali .
PFX SS 0 otutaga .
PFX SS 0 otutaka .
PFX SS 0 otutabu .
PFX SS 0 otutalu .
PFX SS 0 otutaku .
PFX SS 0 otutatu ."""

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
    "SS": "SS",
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

    out_flag = "JG"
    left_desc = FLAG_DESCRIPTIONS.get("SS", "SS")
    right_desc = FLAG_DESCRIPTIONS.get("Ob", "Ob")
    comment_line = "# Cross product of {} ({}) and {} ({}) to {}".format(
        "SS", left_desc, "Ob", right_desc, out_flag
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
