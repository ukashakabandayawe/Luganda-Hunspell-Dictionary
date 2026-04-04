import re
import os
from pathlib import Path

# Cross product generator: EM x OR => GB
# Description:
# - Left block `EM`: EM
# - Right block `OR`: Special reflexive object markers
# - Output flag `GB`: Cross-product prefixes for EM x OR

REPO_ROOT = Path(__file__).resolve().parents[1]
AFF_FILE = REPO_ROOT / "Luganda.aff"

# If set to a flag name (e.g. "HB"), the generated cross-product block will be inserted
# immediately before the first "PFX <flag>" line when the output flag block doesn't
# already exist in the .aff.
INSERT_BEFORE_FLAG = "".strip() or None

rule_left_raw = """
PFX EM Y 605
PFX EM 0 ngu .
PFX EM 0 ngi .
PFX EM 0 nzi .
PFX EM 0 nki .
PFX EM 0 nga .
PFX EM 0 nka .
PFX EM 0 nku .
PFX EM 0 ntu .
PFX EM 0 mba .
PFX EM 0 mbi .
PFX EM 0 mbu .
PFX EM 0 on [^lmnb]
PFX EM l ond l.[^mn]
PFX EM l onn l.[mn]
PFX EM w omp [w]
PFX EM 0 omu .
PFX EM 0 oba .
PFX EM 0 ogu .
PFX EM 0 ogi .
PFX EM 0 ozi .
PFX EM 0 oki .
PFX EM 0 obi .
PFX EM 0 oli .
PFX EM 0 oga .
PFX EM 0 oka .
PFX EM 0 obu .
PFX EM 0 olu .
PFX EM 0 oku .
PFX EM 0 otu .
PFX EM 0 an [^lmnb]
PFX EM l and l.[^mn]
PFX EM l ann l.[mn]
PFX EM w amp [w]
PFX EM 0 amu .
PFX EM 0 aba .
PFX EM 0 agu .
PFX EM 0 agi .
PFX EM 0 azi .
PFX EM 0 aki .
PFX EM 0 abi .
PFX EM 0 ali .
PFX EM 0 aga .
PFX EM 0 aka .
PFX EM 0 abu .
PFX EM 0 alu .
PFX EM 0 aku .
PFX EM 0 atu .
PFX EM 0 tun [^lmnb]
PFX EM l tund l.[^mn]
PFX EM l tunn l.[mn]
PFX EM w tump [w]
PFX EM 0 tumu .
PFX EM 0 tuba .
PFX EM 0 tugu .
PFX EM 0 tugi .
PFX EM 0 tuzi .
PFX EM 0 tuki .
PFX EM 0 tubi .
PFX EM 0 tuli .
PFX EM 0 tuga .
PFX EM 0 tuka .
PFX EM 0 tubu .
PFX EM 0 tulu .
PFX EM 0 tuku .
PFX EM 0 tutu .
PFX EM 0 mun [^lmnb]
PFX EM l mund l.[^mn]
PFX EM l munn l.[mn]
PFX EM w mump [w]
PFX EM 0 mumu .
PFX EM 0 muba .
PFX EM 0 mugu .
PFX EM 0 mugi .
PFX EM 0 muzi .
PFX EM 0 muki .
PFX EM 0 mubi .
PFX EM 0 muli .
PFX EM 0 muga .
PFX EM 0 muka .
PFX EM 0 mubu .
PFX EM 0 mulu .
PFX EM 0 muku .
PFX EM 0 mutu .
PFX EM 0 ban [^lmnb]
PFX EM l band l.[^mn]
PFX EM l bann l.[mn]
PFX EM w bamp [w]
PFX EM 0 bamu .
PFX EM 0 baba .
PFX EM 0 bagu .
PFX EM 0 bagi .
PFX EM 0 bazi .
PFX EM 0 baki .
PFX EM 0 babi .
PFX EM 0 bali .
PFX EM 0 baga .
PFX EM 0 baka .
PFX EM 0 babu .
PFX EM 0 balu .
PFX EM 0 baku .
PFX EM 0 batu .
PFX EM 0 an [^lmnb]
PFX EM l and l.[^mn]
PFX EM l ann l.[mn]
PFX EM w amp [w]
PFX EM 0 amu .
PFX EM 0 aba .
PFX EM 0 agu .
PFX EM 0 agi .
PFX EM 0 azi .
PFX EM 0 aki .
PFX EM 0 abi .
PFX EM 0 ali .
PFX EM 0 aga .
PFX EM 0 aka .
PFX EM 0 abu .
PFX EM 0 alu .
PFX EM 0 aku .
PFX EM 0 atu .
PFX EM 0 ban [^lmnb]
PFX EM l band l.[^mn]
PFX EM l bann l.[mn]
PFX EM w bamp [w]
PFX EM 0 bamu .
PFX EM 0 baba .
PFX EM 0 bagu .
PFX EM 0 bagi .
PFX EM 0 bazi .
PFX EM 0 baki .
PFX EM 0 babi .
PFX EM 0 bali .
PFX EM 0 baga .
PFX EM 0 baka .
PFX EM 0 babu .
PFX EM 0 balu .
PFX EM 0 baku .
PFX EM 0 batu .
PFX EM 0 aban [^lmnb]
PFX EM l aband l.[^mn]
PFX EM l abann l.[mn]
PFX EM w abamp [w]
PFX EM 0 abamu .
PFX EM 0 ababa .
PFX EM 0 abagu .
PFX EM 0 abagi .
PFX EM 0 abazi .
PFX EM 0 abaki .
PFX EM 0 ababi .
PFX EM 0 abali .
PFX EM 0 abaga .
PFX EM 0 abaka .
PFX EM 0 ababu .
PFX EM 0 abalu .
PFX EM 0 abaku .
PFX EM 0 abatu .
PFX EM 0 gun [^lmnb]
PFX EM l gund l.[^mn]
PFX EM l gunn l.[mn]
PFX EM w gump [w]
PFX EM 0 gumu .
PFX EM 0 guba .
PFX EM 0 gugu .
PFX EM 0 gugi .
PFX EM 0 guzi .
PFX EM 0 guki .
PFX EM 0 gubi .
PFX EM 0 guli .
PFX EM 0 guga .
PFX EM 0 guka .
PFX EM 0 gubu .
PFX EM 0 gulu .
PFX EM 0 guku .
PFX EM 0 gutu .
PFX EM 0 ogun [^lmnb]
PFX EM l ogund l.[^mn]
PFX EM l ogunn l.[mn]
PFX EM w ogump [w]
PFX EM 0 ogumu .
PFX EM 0 oguba .
PFX EM 0 ogugu .
PFX EM 0 ogugi .
PFX EM 0 oguzi .
PFX EM 0 oguki .
PFX EM 0 ogubi .
PFX EM 0 oguli .
PFX EM 0 oguga .
PFX EM 0 oguka .
PFX EM 0 ogubu .
PFX EM 0 ogulu .
PFX EM 0 oguku .
PFX EM 0 ogutu .
PFX EM 0 gin [^lmnb]
PFX EM l gind l.[^mn]
PFX EM l ginn l.[mn]
PFX EM w gimp [w]
PFX EM 0 gimu .
PFX EM 0 giba .
PFX EM 0 gigu .
PFX EM 0 gigi .
PFX EM 0 gizi .
PFX EM 0 giki .
PFX EM 0 gibi .
PFX EM 0 gili .
PFX EM 0 giga .
PFX EM 0 gika .
PFX EM 0 gibu .
PFX EM 0 gilu .
PFX EM 0 giku .
PFX EM 0 gitu .
PFX EM 0 egin [^lmnb]
PFX EM l egind l.[^mn]
PFX EM l eginn l.[mn]
PFX EM w egimp [w]
PFX EM 0 egimu .
PFX EM 0 egiba .
PFX EM 0 egigu .
PFX EM 0 egigi .
PFX EM 0 egizi .
PFX EM 0 egiki .
PFX EM 0 egibi .
PFX EM 0 egili .
PFX EM 0 egiga .
PFX EM 0 egika .
PFX EM 0 egibu .
PFX EM 0 egilu .
PFX EM 0 egiku .
PFX EM 0 egitu .
PFX EM 0 en [^lmnb]
PFX EM l end l.[^mn]
PFX EM l enn l.[mn]
PFX EM w emp [w]
PFX EM 0 emu .
PFX EM 0 eba .
PFX EM 0 egu .
PFX EM 0 egi .
PFX EM 0 ezi .
PFX EM 0 eki .
PFX EM 0 ebi .
PFX EM 0 eli .
PFX EM 0 ega .
PFX EM 0 eka .
PFX EM 0 ebu .
PFX EM 0 elu .
PFX EM 0 eku .
PFX EM 0 etu .
PFX EM 0 zin [^lmnb]
PFX EM l zind l.[^mn]
PFX EM l zinn l.[mn]
PFX EM w zimp [w]
PFX EM 0 zimu .
PFX EM 0 ziba .
PFX EM 0 zigu .
PFX EM 0 zigi .
PFX EM 0 zizi .
PFX EM 0 ziki .
PFX EM 0 zibi .
PFX EM 0 zili .
PFX EM 0 ziga .
PFX EM 0 zika .
PFX EM 0 zibu .
PFX EM 0 zilu .
PFX EM 0 ziku .
PFX EM 0 zitu .
PFX EM 0 ezin [^lmnb]
PFX EM l ezind l.[^mn]
PFX EM l ezinn l.[mn]
PFX EM w ezimp [w]
PFX EM 0 ezimu .
PFX EM 0 eziba .
PFX EM 0 ezigu .
PFX EM 0 ezigi .
PFX EM 0 ezizi .
PFX EM 0 eziki .
PFX EM 0 ezibi .
PFX EM 0 ezili .
PFX EM 0 eziga .
PFX EM 0 ezika .
PFX EM 0 ezibu .
PFX EM 0 ezilu .
PFX EM 0 eziku .
PFX EM 0 ezitu .
PFX EM 0 kin [^lmnb]
PFX EM l kind l.[^mn]
PFX EM l kinn l.[mn]
PFX EM w kimp [w]
PFX EM 0 kimu .
PFX EM 0 kiba .
PFX EM 0 kigu .
PFX EM 0 kigi .
PFX EM 0 kizi .
PFX EM 0 kiki .
PFX EM 0 kibi .
PFX EM 0 kili .
PFX EM 0 kiga .
PFX EM 0 kika .
PFX EM 0 kibu .
PFX EM 0 kilu .
PFX EM 0 kiku .
PFX EM 0 kitu .
PFX EM 0 ekin [^lmnb]
PFX EM l ekind l.[^mn]
PFX EM l ekinn l.[mn]
PFX EM w ekimp [w]
PFX EM 0 ekimu .
PFX EM 0 ekiba .
PFX EM 0 ekigu .
PFX EM 0 ekigi .
PFX EM 0 ekizi .
PFX EM 0 ekiki .
PFX EM 0 ekibi .
PFX EM 0 ekili .
PFX EM 0 ekiga .
PFX EM 0 ekika .
PFX EM 0 ekibu .
PFX EM 0 ekilu .
PFX EM 0 ekiku .
PFX EM 0 ekitu .
PFX EM 0 bin [^lmnb]
PFX EM l bind l.[^mn]
PFX EM l binn l.[mn]
PFX EM w bimp [w]
PFX EM 0 bimu .
PFX EM 0 biba .
PFX EM 0 bigu .
PFX EM 0 bigi .
PFX EM 0 bizi .
PFX EM 0 biki .
PFX EM 0 bibi .
PFX EM 0 bili .
PFX EM 0 biga .
PFX EM 0 bika .
PFX EM 0 bibu .
PFX EM 0 bilu .
PFX EM 0 biku .
PFX EM 0 bitu .
PFX EM 0 ebin [^lmnb]
PFX EM l ebind l.[^mn]
PFX EM l ebinn l.[mn]
PFX EM w ebimp [w]
PFX EM 0 ebimu .
PFX EM 0 ebiba .
PFX EM 0 ebigu .
PFX EM 0 ebigi .
PFX EM 0 ebizi .
PFX EM 0 ebiki .
PFX EM 0 ebibi .
PFX EM 0 ebili .
PFX EM 0 ebiga .
PFX EM 0 ebika .
PFX EM 0 ebibu .
PFX EM 0 ebilu .
PFX EM 0 ebiku .
PFX EM 0 ebitu .
PFX EM 0 lin [^lmnb]
PFX EM l lind l.[^mn]
PFX EM l linn l.[mn]
PFX EM w limp [w]
PFX EM 0 limu .
PFX EM 0 liba .
PFX EM 0 ligu .
PFX EM 0 ligi .
PFX EM 0 lizi .
PFX EM 0 liki .
PFX EM 0 libi .
PFX EM 0 lili .
PFX EM 0 liga .
PFX EM 0 lika .
PFX EM 0 libu .
PFX EM 0 lilu .
PFX EM 0 liku .
PFX EM 0 litu .
PFX EM 0 elin [^lmnb]
PFX EM l elind l.[^mn]
PFX EM l elinn l.[mn]
PFX EM w elimp [w]
PFX EM 0 elimu .
PFX EM 0 eliba .
PFX EM 0 eligu .
PFX EM 0 eligi .
PFX EM 0 elizi .
PFX EM 0 eliki .
PFX EM 0 elibi .
PFX EM 0 elili .
PFX EM 0 eliga .
PFX EM 0 elika .
PFX EM 0 elibu .
PFX EM 0 elilu .
PFX EM 0 eliku .
PFX EM 0 elitu .
PFX EM 0 gan [^lmnb]
PFX EM l gand l.[^mn]
PFX EM l gann l.[mn]
PFX EM w gamp [w]
PFX EM 0 gamu .
PFX EM 0 gaba .
PFX EM 0 gagu .
PFX EM 0 gagi .
PFX EM 0 gazi .
PFX EM 0 gaki .
PFX EM 0 gabi .
PFX EM 0 gali .
PFX EM 0 gaga .
PFX EM 0 gaka .
PFX EM 0 gabu .
PFX EM 0 galu .
PFX EM 0 gaku .
PFX EM 0 gatu .
PFX EM 0 agan [^lmnb]
PFX EM l agand l.[^mn]
PFX EM l agann l.[mn]
PFX EM w agamp [w]
PFX EM 0 agamu .
PFX EM 0 agaba .
PFX EM 0 agagu .
PFX EM 0 agagi .
PFX EM 0 agazi .
PFX EM 0 agaki .
PFX EM 0 agabi .
PFX EM 0 agali .
PFX EM 0 agaga .
PFX EM 0 agaka .
PFX EM 0 agabu .
PFX EM 0 agalu .
PFX EM 0 agaku .
PFX EM 0 agatu .
PFX EM 0 kan [^lmnb]
PFX EM l kand l.[^mn]
PFX EM l kann l.[mn]
PFX EM w kamp [w]
PFX EM 0 kamu .
PFX EM 0 kaba .
PFX EM 0 kagu .
PFX EM 0 kagi .
PFX EM 0 kazi .
PFX EM 0 kaki .
PFX EM 0 kabi .
PFX EM 0 kali .
PFX EM 0 kaga .
PFX EM 0 kaka .
PFX EM 0 kabu .
PFX EM 0 kalu .
PFX EM 0 kaku .
PFX EM 0 katu .
PFX EM 0 akan [^lmnb]
PFX EM l akand l.[^mn]
PFX EM l akann l.[mn]
PFX EM w akamp [w]
PFX EM 0 akamu .
PFX EM 0 akaba .
PFX EM 0 akagu .
PFX EM 0 akagi .
PFX EM 0 akazi .
PFX EM 0 akaki .
PFX EM 0 akabi .
PFX EM 0 akali .
PFX EM 0 akaga .
PFX EM 0 akaka .
PFX EM 0 akabu .
PFX EM 0 akalu .
PFX EM 0 akaku .
PFX EM 0 akatu .
PFX EM 0 bun [^lmnb]
PFX EM l bund l.[^mn]
PFX EM l bunn l.[mn]
PFX EM w bump [w]
PFX EM 0 bumu .
PFX EM 0 buba .
PFX EM 0 bugu .
PFX EM 0 bugi .
PFX EM 0 buzi .
PFX EM 0 buki .
PFX EM 0 bubi .
PFX EM 0 buli .
PFX EM 0 buga .
PFX EM 0 buka .
PFX EM 0 bubu .
PFX EM 0 bulu .
PFX EM 0 buku .
PFX EM 0 butu .
PFX EM 0 obun [^lmnb]
PFX EM l obund l.[^mn]
PFX EM l obunn l.[mn]
PFX EM w obump [w]
PFX EM 0 obumu .
PFX EM 0 obuba .
PFX EM 0 obugu .
PFX EM 0 obugi .
PFX EM 0 obuzi .
PFX EM 0 obuki .
PFX EM 0 obubi .
PFX EM 0 obuli .
PFX EM 0 obuga .
PFX EM 0 obuka .
PFX EM 0 obubu .
PFX EM 0 obulu .
PFX EM 0 obuku .
PFX EM 0 obutu .
PFX EM 0 lun [^lmnb]
PFX EM l lund l.[^mn]
PFX EM l lunn l.[mn]
PFX EM w lump [w]
PFX EM 0 lumu .
PFX EM 0 luba .
PFX EM 0 lugu .
PFX EM 0 lugi .
PFX EM 0 luzi .
PFX EM 0 luki .
PFX EM 0 lubi .
PFX EM 0 luli .
PFX EM 0 luga .
PFX EM 0 luka .
PFX EM 0 lubu .
PFX EM 0 lulu .
PFX EM 0 luku .
PFX EM 0 lutu .
PFX EM 0 olun [^lmnb]
PFX EM l olund l.[^mn]
PFX EM l olunn l.[mn]
PFX EM w olump [w]
PFX EM 0 olumu .
PFX EM 0 oluba .
PFX EM 0 olugu .
PFX EM 0 olugi .
PFX EM 0 oluzi .
PFX EM 0 oluki .
PFX EM 0 olubi .
PFX EM 0 oluli .
PFX EM 0 oluga .
PFX EM 0 oluka .
PFX EM 0 olubu .
PFX EM 0 olulu .
PFX EM 0 oluku .
PFX EM 0 olutu .
PFX EM 0 kun [^lmnb]
PFX EM l kund l.[^mn]
PFX EM l kunn l.[mn]
PFX EM w kump [w]
PFX EM 0 kumu .
PFX EM 0 kuba .
PFX EM 0 kugu .
PFX EM 0 kugi .
PFX EM 0 kuzi .
PFX EM 0 kuki .
PFX EM 0 kubi .
PFX EM 0 kuli .
PFX EM 0 kuga .
PFX EM 0 kuka .
PFX EM 0 kubu .
PFX EM 0 kulu .
PFX EM 0 kuku .
PFX EM 0 kutu .
PFX EM 0 okun [^lmnb]
PFX EM l okund l.[^mn]
PFX EM l okunn l.[mn]
PFX EM w okump [w]
PFX EM 0 okumu .
PFX EM 0 okuba .
PFX EM 0 okugu .
PFX EM 0 okugi .
PFX EM 0 okuzi .
PFX EM 0 okuki .
PFX EM 0 okubi .
PFX EM 0 okuli .
PFX EM 0 okuga .
PFX EM 0 okuka .
PFX EM 0 okubu .
PFX EM 0 okulu .
PFX EM 0 okuku .
PFX EM 0 okutu .
PFX EM 0 tun [^lmnb]
PFX EM l tund l.[^mn]
PFX EM l tunn l.[mn]
PFX EM w tump [w]
PFX EM 0 tumu .
PFX EM 0 tuba .
PFX EM 0 tugu .
PFX EM 0 tugi .
PFX EM 0 tuzi .
PFX EM 0 tuki .
PFX EM 0 tubi .
PFX EM 0 tuli .
PFX EM 0 tuga .
PFX EM 0 tuka .
PFX EM 0 tubu .
PFX EM 0 tulu .
PFX EM 0 tuku .
PFX EM 0 tutu .
PFX EM 0 otun [^lmnb]
PFX EM l otund l.[^mn]
PFX EM l otunn l.[mn]
PFX EM w otump [w]
PFX EM 0 otumu .
PFX EM 0 otuba .
PFX EM 0 otugu .
PFX EM 0 otugi .
PFX EM 0 otuzi .
PFX EM 0 otuki .
PFX EM 0 otubi .
PFX EM 0 otuli .
PFX EM 0 otuga .
PFX EM 0 otuka .
PFX EM 0 otubu .
PFX EM 0 otulu .
PFX EM 0 otuku .
PFX EM 0 otutu ."""

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
    "EM": "EM",
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

    out_flag = "GB"
    left_desc = FLAG_DESCRIPTIONS.get("EM", "EM")
    right_desc = FLAG_DESCRIPTIONS.get("OR", "OR")
    comment_line = "# Cross product of {} ({}) and {} ({}) to {}".format(
        "EM", left_desc, "OR", right_desc, out_flag
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
