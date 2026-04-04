import re
import os
from pathlib import Path

# Cross product generator: II x OR => JB
# Description:
# - Left block `II`: II
# - Right block `OR`: Special reflexive object markers
# - Output flag `JB`: Cross-product prefixes for II x OR

REPO_ROOT = Path(__file__).resolve().parents[1]
AFF_FILE = REPO_ROOT / "Luganda.aff"

# If set to a flag name (e.g. "HB"), the generated cross-product block will be inserted
# immediately before the first "PFX <flag>" line when the output flag block doesn't
# already exist in the .aff.
INSERT_BEFORE_FLAG = "".strip() or None

rule_left_raw = """
PFX II Y 590
PFX II 0 saamu .
PFX II 0 saaba .
PFX II 0 saagu .
PFX II 0 saagi .
PFX II 0 saazi .
PFX II 0 saaki .
PFX II 0 saabi .
PFX II 0 saali .
PFX II 0 saaga .
PFX II 0 saaka .
PFX II 0 saabu .
PFX II 0 saalu .
PFX II 0 saaku .
PFX II 0 saatu .
PFX II 0 tewan [^lmn]
PFX II l tewand l.[^mn]
PFX II l tewann l.[mn]
PFX II w tewamp [w]
PFX II 0 tewamu .
PFX II 0 tewaba .
PFX II 0 tewagu .
PFX II 0 tewagi .
PFX II 0 tewazi .
PFX II 0 tewaki .
PFX II 0 tewabi .
PFX II 0 tewali .
PFX II 0 tewaga .
PFX II 0 tewaka .
PFX II 0 tewabu .
PFX II 0 tewalu .
PFX II 0 tewaku .
PFX II 0 tewatu .
PFX II 0 teyan [^lmn]
PFX II l teyand l.[^mn]
PFX II l teyann l.[mn]
PFX II w teyamp [w]
PFX II 0 teyamu .
PFX II 0 teyaba .
PFX II 0 teyagu .
PFX II 0 teyagi .
PFX II 0 teyazi .
PFX II 0 teyaki .
PFX II 0 teyabi .
PFX II 0 teyali .
PFX II 0 teyaga .
PFX II 0 teyaka .
PFX II 0 teyabu .
PFX II 0 teyalu .
PFX II 0 teyaku .
PFX II 0 teyatu .
PFX II 0 tetwan [^lmn]
PFX II l tetwand l.[^mn]
PFX II l tetwann l.[mn]
PFX II w tetwamp [w]
PFX II 0 tetwamu .
PFX II 0 tetwaba .
PFX II 0 tetwagu .
PFX II 0 tetwagi .
PFX II 0 tetwazi .
PFX II 0 tetwaki .
PFX II 0 tetwabi .
PFX II 0 tetwali .
PFX II 0 tetwaga .
PFX II 0 tetwaka .
PFX II 0 tetwabu .
PFX II 0 tetwalu .
PFX II 0 tetwaku .
PFX II 0 tetwatu .
PFX II 0 temwan [^lmn]
PFX II l temwand l.[^mn]
PFX II l temwann l.[mn]
PFX II w temwamp [w]
PFX II 0 temwamu .
PFX II 0 temwaba .
PFX II 0 temwagu .
PFX II 0 temwagi .
PFX II 0 temwazi .
PFX II 0 temwaki .
PFX II 0 temwabi .
PFX II 0 temwali .
PFX II 0 temwaga .
PFX II 0 temwaka .
PFX II 0 temwabu .
PFX II 0 temwalu .
PFX II 0 temwaku .
PFX II 0 temwatu .
PFX II 0 tebaan [^lmn]
PFX II l tebaand l.[^mn]
PFX II l tebaann l.[mn]
PFX II w tebaamp [w]
PFX II 0 tebaamu .
PFX II 0 tebaaba .
PFX II 0 tebaagu .
PFX II 0 tebaagi .
PFX II 0 tebaazi .
PFX II 0 tebaaki .
PFX II 0 tebaabi .
PFX II 0 tebaali .
PFX II 0 tebaaga .
PFX II 0 tebaaka .
PFX II 0 tebaabu .
PFX II 0 tebaalu .
PFX II 0 tebaaku .
PFX II 0 tebaatu .
PFX II 0 abataan [^lmn]
PFX II l abataand l.[^mn]
PFX II l abataann l.[mn]
PFX II w abataamp [w]
PFX II 0 abataamu .
PFX II 0 abataaba .
PFX II 0 abataagu .
PFX II 0 abataagi .
PFX II 0 abataazi .
PFX II 0 abataaki .
PFX II 0 abataabi .
PFX II 0 abataali .
PFX II 0 abataaga .
PFX II 0 abataaka .
PFX II 0 abataabu .
PFX II 0 abataalu .
PFX II 0 abataaku .
PFX II 0 abataatu .
PFX II 0 tegwan [^lmn]
PFX II l tegwand l.[^mn]
PFX II l tegwann l.[mn]
PFX II w tegwamp [w]
PFX II 0 tegwamu .
PFX II 0 tegwaba .
PFX II 0 tegwagu .
PFX II 0 tegwagi .
PFX II 0 tegwazi .
PFX II 0 tegwaki .
PFX II 0 tegwabi .
PFX II 0 tegwali .
PFX II 0 tegwaga .
PFX II 0 tegwaka .
PFX II 0 tegwabu .
PFX II 0 tegwalu .
PFX II 0 tegwaku .
PFX II 0 tegwatu .
PFX II 0 ogutaan [^lmn]
PFX II l ogutaand l.[^mn]
PFX II l ogutaann l.[mn]
PFX II w ogutaamp [w]
PFX II 0 ogutaamu .
PFX II 0 ogutaaba .
PFX II 0 ogutaagu .
PFX II 0 ogutaagi .
PFX II 0 ogutaazi .
PFX II 0 ogutaaki .
PFX II 0 ogutaabi .
PFX II 0 ogutaali .
PFX II 0 ogutaaga .
PFX II 0 ogutaaka .
PFX II 0 ogutaabu .
PFX II 0 ogutaalu .
PFX II 0 ogutaaku .
PFX II 0 ogutaatu .
PFX II 0 tegyan [^lmn]
PFX II l tegyand l.[^mn]
PFX II l tegyann l.[mn]
PFX II w tegyamp [w]
PFX II 0 tegyamu .
PFX II 0 tegyaba .
PFX II 0 tegyagu .
PFX II 0 tegyagi .
PFX II 0 tegyazi .
PFX II 0 tegyaki .
PFX II 0 tegyabi .
PFX II 0 tegyali .
PFX II 0 tegyaga .
PFX II 0 tegyaka .
PFX II 0 tegyabu .
PFX II 0 tegyalu .
PFX II 0 tegyaku .
PFX II 0 tegyatu .
PFX II 0 egitaan [^lmn]
PFX II l egitaand l.[^mn]
PFX II l egitaann l.[mn]
PFX II w egitaamp [w]
PFX II 0 egitaamu .
PFX II 0 egitaaba .
PFX II 0 egitaagu .
PFX II 0 egitaagi .
PFX II 0 egitaazi .
PFX II 0 egitaaki .
PFX II 0 egitaabi .
PFX II 0 egitaali .
PFX II 0 egitaaga .
PFX II 0 egitaaka .
PFX II 0 egitaabu .
PFX II 0 egitaalu .
PFX II 0 egitaaku .
PFX II 0 egitaatu .
PFX II 0 teyan [^lmn]
PFX II l teyand l.[^mn]
PFX II l teyann l.[mn]
PFX II w teyamp [w]
PFX II 0 teyamu .
PFX II 0 teyaba .
PFX II 0 teyagu .
PFX II 0 teyagi .
PFX II 0 teyazi .
PFX II 0 teyaki .
PFX II 0 teyabi .
PFX II 0 teyali .
PFX II 0 teyaga .
PFX II 0 teyaka .
PFX II 0 teyabu .
PFX II 0 teyalu .
PFX II 0 teyaku .
PFX II 0 teyatu .
PFX II 0 eteen [^lmn]
PFX II l eteend l.[^mn]
PFX II l eteenn l.[mn]
PFX II w eteemp [w]
PFX II 0 eteemu .
PFX II 0 eteeba .
PFX II 0 eteegu .
PFX II 0 eteegi .
PFX II 0 eteezi .
PFX II 0 eteeki .
PFX II 0 eteebi .
PFX II 0 eteeli .
PFX II 0 eteega .
PFX II 0 eteeka .
PFX II 0 eteebu .
PFX II 0 eteelu .
PFX II 0 eteeku .
PFX II 0 eteetu .
PFX II 0 tezaan [^lmn]
PFX II l tezaand l.[^mn]
PFX II l tezaann l.[mn]
PFX II w tezaamp [w]
PFX II 0 tezaamu .
PFX II 0 tezaaba .
PFX II 0 tezaagu .
PFX II 0 tezaagi .
PFX II 0 tezaazi .
PFX II 0 tezaaki .
PFX II 0 tezaabi .
PFX II 0 tezaali .
PFX II 0 tezaaga .
PFX II 0 tezaaka .
PFX II 0 tezaabu .
PFX II 0 tezaalu .
PFX II 0 tezaaku .
PFX II 0 tezaatu .
PFX II 0 ezitan [^lmn]
PFX II l ezitand l.[^mn]
PFX II l ezitann l.[mn]
PFX II w ezitamp [w]
PFX II 0 ezitamu .
PFX II 0 ezitaba .
PFX II 0 ezitagu .
PFX II 0 ezitagi .
PFX II 0 ezitazi .
PFX II 0 ezitaki .
PFX II 0 ezitabi .
PFX II 0 ezitali .
PFX II 0 ezitaga .
PFX II 0 ezitaka .
PFX II 0 ezitabu .
PFX II 0 ezitalu .
PFX II 0 ezitaku .
PFX II 0 ezitatu .
PFX II 0 tekyan [^lmn]
PFX II l tekyand l.[^mn]
PFX II l tekyann l.[mn]
PFX II w tekyamp [w]
PFX II 0 tekyamu .
PFX II 0 tekyaba .
PFX II 0 tekyagu .
PFX II 0 tekyagi .
PFX II 0 tekyazi .
PFX II 0 tekyaki .
PFX II 0 tekyabi .
PFX II 0 tekyali .
PFX II 0 tekyaga .
PFX II 0 tekyaka .
PFX II 0 tekyabu .
PFX II 0 tekyalu .
PFX II 0 tekyaku .
PFX II 0 tekyatu .
PFX II 0 ekitaan [^lmn]
PFX II l ekitaand l.[^mn]
PFX II l ekitaann l.[mn]
PFX II w ekitaamp [w]
PFX II 0 ekitaamu .
PFX II 0 ekitaaba .
PFX II 0 ekitaagu .
PFX II 0 ekitaagi .
PFX II 0 ekitaazi .
PFX II 0 ekitaaki .
PFX II 0 ekitaabi .
PFX II 0 ekitaali .
PFX II 0 ekitaaga .
PFX II 0 ekitaaka .
PFX II 0 ekitaabu .
PFX II 0 ekitaalu .
PFX II 0 ekitaaku .
PFX II 0 ekitaatu .
PFX II 0 tebyan [^lmn]
PFX II l tebyand l.[^mn]
PFX II l tebyann l.[mn]
PFX II w tebyamp [w]
PFX II 0 tebyamu .
PFX II 0 tebyaba .
PFX II 0 tebyagu .
PFX II 0 tebyagi .
PFX II 0 tebyazi .
PFX II 0 tebyaki .
PFX II 0 tebyabi .
PFX II 0 tebyali .
PFX II 0 tebyaga .
PFX II 0 tebyaka .
PFX II 0 tebyabu .
PFX II 0 tebyalu .
PFX II 0 tebyaku .
PFX II 0 tebyatu .
PFX II 0 ebitaan [^lmn]
PFX II l ebitaand l.[^mn]
PFX II l ebitaann l.[mn]
PFX II w ebitaamp [w]
PFX II 0 ebitaamu .
PFX II 0 ebitaaba .
PFX II 0 ebitaagu .
PFX II 0 ebitaagi .
PFX II 0 ebitaazi .
PFX II 0 ebitaaki .
PFX II 0 ebitaabi .
PFX II 0 ebitaali .
PFX II 0 ebitaaga .
PFX II 0 ebitaaka .
PFX II 0 ebitaabu .
PFX II 0 ebitaalu .
PFX II 0 ebitaaku .
PFX II 0 ebitaatu .
PFX II 0 telyan [^lmn]
PFX II l telyand l.[^mn]
PFX II l telyann l.[mn]
PFX II w telyamp [w]
PFX II 0 telyamu .
PFX II 0 telyaba .
PFX II 0 telyagu .
PFX II 0 telyagi .
PFX II 0 telyazi .
PFX II 0 telyaki .
PFX II 0 telyabi .
PFX II 0 telyali .
PFX II 0 telyaga .
PFX II 0 telyaka .
PFX II 0 telyabu .
PFX II 0 telyalu .
PFX II 0 telyaku .
PFX II 0 telyatu .
PFX II 0 elitaan [^lmn]
PFX II l elitaand l.[^mn]
PFX II l elitaann l.[mn]
PFX II w elitaamp [w]
PFX II 0 elitaamu .
PFX II 0 elitaaba .
PFX II 0 elitaagu .
PFX II 0 elitaagi .
PFX II 0 elitaazi .
PFX II 0 elitaaki .
PFX II 0 elitaabi .
PFX II 0 elitaali .
PFX II 0 elitaaga .
PFX II 0 elitaaka .
PFX II 0 elitaabu .
PFX II 0 elitaalu .
PFX II 0 elitaaku .
PFX II 0 elitaatu .
PFX II 0 tegaan [^lmn]
PFX II l tegaand l.[^mn]
PFX II l tegaann l.[mn]
PFX II w tegaamp [w]
PFX II 0 tegaamu .
PFX II 0 tegaaba .
PFX II 0 tegaagu .
PFX II 0 tegaagi .
PFX II 0 tegaazi .
PFX II 0 tegaaki .
PFX II 0 tegaabi .
PFX II 0 tegaali .
PFX II 0 tegaaga .
PFX II 0 tegaaka .
PFX II 0 tegaabu .
PFX II 0 tegaalu .
PFX II 0 tegaaku .
PFX II 0 tegaatu .
PFX II 0 agataan [^lmn]
PFX II l agataand l.[^mn]
PFX II l agataann l.[mn]
PFX II w agataamp [w]
PFX II 0 agataamu .
PFX II 0 agataaba .
PFX II 0 agataagu .
PFX II 0 agataagi .
PFX II 0 agataazi .
PFX II 0 agataaki .
PFX II 0 agataabi .
PFX II 0 agataali .
PFX II 0 agataaga .
PFX II 0 agataaka .
PFX II 0 agataabu .
PFX II 0 agataalu .
PFX II 0 agataaku .
PFX II 0 agataatu .
PFX II 0 tekaan [^lmn]
PFX II l tekaand l.[^mn]
PFX II l tekaann l.[mn]
PFX II w tekaamp [w]
PFX II 0 tekaamu .
PFX II 0 tekaaba .
PFX II 0 tekaagu .
PFX II 0 tekaagi .
PFX II 0 tekaazi .
PFX II 0 tekaaki .
PFX II 0 tekaabi .
PFX II 0 tekaali .
PFX II 0 tekaaga .
PFX II 0 tekaaka .
PFX II 0 tekaabu .
PFX II 0 tekaalu .
PFX II 0 tekaaku .
PFX II 0 tekaatu .
PFX II 0 akataan [^lmn]
PFX II l akataand l.[^mn]
PFX II l akataann l.[mn]
PFX II w akataamp [w]
PFX II 0 akataamu .
PFX II 0 akataaba .
PFX II 0 akataagu .
PFX II 0 akataagi .
PFX II 0 akataazi .
PFX II 0 akataaki .
PFX II 0 akataabi .
PFX II 0 akataali .
PFX II 0 akataaga .
PFX II 0 akataaka .
PFX II 0 akataabu .
PFX II 0 akataalu .
PFX II 0 akataaku .
PFX II 0 akataatu .
PFX II 0 tebwan [^lmn]
PFX II l tebwand l.[^mn]
PFX II l tebwann l.[mn]
PFX II w tebwamp [w]
PFX II 0 tebwamu .
PFX II 0 tebwaba .
PFX II 0 tebwagu .
PFX II 0 tebwagi .
PFX II 0 tebwazi .
PFX II 0 tebwaki .
PFX II 0 tebwabi .
PFX II 0 tebwali .
PFX II 0 tebwaga .
PFX II 0 tebwaka .
PFX II 0 tebwabu .
PFX II 0 tebwalu .
PFX II 0 tebwaku .
PFX II 0 tebwatu .
PFX II 0 obutaan [^lmn]
PFX II l obutaand l.[^mn]
PFX II l obutaann l.[mn]
PFX II w obutaamp [w]
PFX II 0 obutaamu .
PFX II 0 obutaaba .
PFX II 0 obutaagu .
PFX II 0 obutaagi .
PFX II 0 obutaazi .
PFX II 0 obutaaki .
PFX II 0 obutaabi .
PFX II 0 obutaali .
PFX II 0 obutaaga .
PFX II 0 obutaaka .
PFX II 0 obutaabu .
PFX II 0 obutaalu .
PFX II 0 obutaaku .
PFX II 0 obutaatu .
PFX II 0 telwan [^lmn]
PFX II l telwand l.[^mn]
PFX II l telwann l.[mn]
PFX II w telwamp [w]
PFX II 0 telwamu .
PFX II 0 telwaba .
PFX II 0 telwagu .
PFX II 0 telwagi .
PFX II 0 telwazi .
PFX II 0 telwaki .
PFX II 0 telwabi .
PFX II 0 telwali .
PFX II 0 telwaga .
PFX II 0 telwaka .
PFX II 0 telwabu .
PFX II 0 telwalu .
PFX II 0 telwaku .
PFX II 0 telwatu .
PFX II 0 olutaan [^lmn]
PFX II l olutaand l.[^mn]
PFX II l olutaann l.[mn]
PFX II w olutaamp [w]
PFX II 0 olutaamu .
PFX II 0 olutaaba .
PFX II 0 olutaagu .
PFX II 0 olutaagi .
PFX II 0 olutaazi .
PFX II 0 olutaaki .
PFX II 0 olutaabi .
PFX II 0 olutaali .
PFX II 0 olutaaga .
PFX II 0 olutaaka .
PFX II 0 olutaabu .
PFX II 0 olutaalu .
PFX II 0 olutaaku .
PFX II 0 olutaatu .
PFX II 0 tekwan [^lmn]
PFX II l tekwand l.[^mn]
PFX II l tekwann l.[mn]
PFX II w tekwamp [w]
PFX II 0 tekwamu .
PFX II 0 tekwaba .
PFX II 0 tekwagu .
PFX II 0 tekwagi .
PFX II 0 tekwazi .
PFX II 0 tekwaki .
PFX II 0 tekwabi .
PFX II 0 tekwali .
PFX II 0 tekwaga .
PFX II 0 tekwaka .
PFX II 0 tekwabu .
PFX II 0 tekwalu .
PFX II 0 tekwaku .
PFX II 0 tekwatu .
PFX II 0 okutaan [^lmn]
PFX II l okutaand l.[^mn]
PFX II l okutaann l.[mn]
PFX II w okutaamp [w]
PFX II 0 okutaamu .
PFX II 0 okutaaba .
PFX II 0 okutaagu .
PFX II 0 okutaagi .
PFX II 0 okutaazi .
PFX II 0 okutaaki .
PFX II 0 okutaabi .
PFX II 0 okutaali .
PFX II 0 okutaaga .
PFX II 0 okutaaka .
PFX II 0 okutaabu .
PFX II 0 okutaalu .
PFX II 0 okutaaku .
PFX II 0 okutaatu .
PFX II 0 tetwan [^lmn]
PFX II l tetwand l.[^mn]
PFX II l tetwann l.[mn]
PFX II w tetwamp [w]
PFX II 0 tetwamu .
PFX II 0 tetwaba .
PFX II 0 tetwagu .
PFX II 0 tetwagi .
PFX II 0 tetwazi .
PFX II 0 tetwaki .
PFX II 0 tetwabi .
PFX II 0 tetwali .
PFX II 0 tetwaga .
PFX II 0 tetwaka .
PFX II 0 tetwabu .
PFX II 0 tetwalu .
PFX II 0 tetwaku .
PFX II 0 tetwatu .
PFX II 0 otutaan [^lmn]
PFX II l otutaand l.[^mn]
PFX II l otutaann l.[mn]
PFX II w otutaamp [w]
PFX II 0 otutaamu .
PFX II 0 otutaaba .
PFX II 0 otutaagu .
PFX II 0 otutaagi .
PFX II 0 otutaazi .
PFX II 0 otutaaki .
PFX II 0 otutaabi .
PFX II 0 otutaali .
PFX II 0 otutaaga .
PFX II 0 otutaaka .
PFX II 0 otutaabu .
PFX II 0 otutaalu .
PFX II 0 otutaaku .
PFX II 0 otutaatu ."""

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
    "II": "II",
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

    out_flag = "JB"
    left_desc = FLAG_DESCRIPTIONS.get("II", "II")
    right_desc = FLAG_DESCRIPTIONS.get("OR", "OR")
    comment_line = "# Cross product of {} ({}) and {} ({}) to {}".format(
        "II", left_desc, "OR", right_desc, out_flag
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
