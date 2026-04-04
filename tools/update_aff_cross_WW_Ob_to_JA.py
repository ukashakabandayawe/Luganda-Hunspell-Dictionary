import re
import os
from pathlib import Path

# Cross product generator: WW x Ob => JA
# Description:
# - Left block `WW`: WW
# - Right block `Ob`: Object markers
# - Output flag `JA`: Cross-product prefixes for WW x Ob

REPO_ROOT = Path(__file__).resolve().parents[1]
AFF_FILE = REPO_ROOT / "Luganda.aff"

# If set to a flag name (e.g. "HB"), the generated cross-product block will be inserted
# immediately before the first "PFX <flag>" line when the output flag block doesn't
# already exist in the .aff.
INSERT_BEFORE_FLAG = "".strip() or None

rule_left_raw = """
PFX WW Y 662
PFX WW 0 siimu .
PFX WW 0 siiba .
PFX WW 0 siigu .
PFX WW 0 siigi .
PFX WW 0 siizi .
PFX WW 0 siiki .
PFX WW 0 siibi .
PFX WW 0 siili .
PFX WW 0 siiga .
PFX WW 0 siika .
PFX WW 0 siibu .
PFX WW 0 siilu .
PFX WW 0 siiku .
PFX WW 0 siitu .
PFX WW 0 temuun [^lmn]
PFX WW l temuund l.[^mn]
PFX WW l temuunn l.[mn]
PFX WW w temuump [w]
PFX WW 0 temuumu .
PFX WW 0 temuuba .
PFX WW 0 temuugu .
PFX WW 0 temuugi .
PFX WW 0 temuuzi .
PFX WW 0 temuuki .
PFX WW 0 temuubi .
PFX WW 0 temuuli .
PFX WW 0 temuuga .
PFX WW 0 temuuka .
PFX WW 0 temuubu .
PFX WW 0 temuulu .
PFX WW 0 temuuku .
PFX WW 0 temuutu .
PFX WW 0 toon [^lmn]
PFX WW l toond l.[^mn]
PFX WW l toonn l.[mn]
PFX WW w toomp [w]
PFX WW 0 toomu .
PFX WW 0 tooba .
PFX WW 0 toogu .
PFX WW 0 toogi .
PFX WW 0 toozi .
PFX WW 0 tooki .
PFX WW 0 toobi .
PFX WW 0 tooli .
PFX WW 0 tooga .
PFX WW 0 tooka .
PFX WW 0 toobu .
PFX WW 0 toolu .
PFX WW 0 tooku .
PFX WW 0 tootu .
PFX WW 0 taan [^lmn]
PFX WW l taand l.[^mn]
PFX WW l taann l.[mn]
PFX WW w taamp [w]
PFX WW 0 taamu .
PFX WW 0 taaba .
PFX WW 0 taagu .
PFX WW 0 taagi .
PFX WW 0 taazi .
PFX WW 0 taaki .
PFX WW 0 taabi .
PFX WW 0 taali .
PFX WW 0 taaga .
PFX WW 0 taaka .
PFX WW 0 taabu .
PFX WW 0 taalu .
PFX WW 0 taaku .
PFX WW 0 taatu .
PFX WW 0 tetuun [^lmn]
PFX WW l tetuund l.[^mn]
PFX WW l tetuunn l.[mn]
PFX WW w tetuump [w]
PFX WW 0 tetuumu .
PFX WW 0 tetuuba .
PFX WW 0 tetuugu .
PFX WW 0 tetuugi .
PFX WW 0 tetuuzi .
PFX WW 0 tetuuki .
PFX WW 0 tetuubi .
PFX WW 0 tetuuli .
PFX WW 0 tetuuga .
PFX WW 0 tetuuka .
PFX WW 0 tetuubu .
PFX WW 0 tetuulu .
PFX WW 0 tetuuku .
PFX WW 0 tetuutu .
PFX WW 0 temuun [^lmn]
PFX WW l temuund l.[^mn]
PFX WW l temuunn l.[mn]
PFX WW w temuump [w]
PFX WW 0 temuumu .
PFX WW 0 temuuba .
PFX WW 0 temuugu .
PFX WW 0 temuugi .
PFX WW 0 temuuzi .
PFX WW 0 temuuki .
PFX WW 0 temuubi .
PFX WW 0 temuuli .
PFX WW 0 temuuga .
PFX WW 0 temuuka .
PFX WW 0 temuubu .
PFX WW 0 temuulu .
PFX WW 0 temuuku .
PFX WW 0 temuutu .
PFX WW 0 tebaan [^lmn]
PFX WW l tebaand l.[^mn]
PFX WW l tebaann l.[mn]
PFX WW w tebaamp [w]
PFX WW 0 tebaamu .
PFX WW 0 tebaaba .
PFX WW 0 tebaagu .
PFX WW 0 tebaagi .
PFX WW 0 tebaazi .
PFX WW 0 tebaaki .
PFX WW 0 tebaabi .
PFX WW 0 tebaali .
PFX WW 0 tebaaga .
PFX WW 0 tebaaka .
PFX WW 0 tebaabu .
PFX WW 0 tebaalu .
PFX WW 0 tebaaku .
PFX WW 0 tebaatu .
PFX WW 0 abataan [^lmn]
PFX WW l abataand l.[^mn]
PFX WW l abataann l.[mn]
PFX WW w abataamp [w]
PFX WW 0 abataamu .
PFX WW 0 abataaba .
PFX WW 0 abataagu .
PFX WW 0 abataagi .
PFX WW 0 abataazi .
PFX WW 0 abataaki .
PFX WW 0 abataabi .
PFX WW 0 abataali .
PFX WW 0 abataaga .
PFX WW 0 abataaka .
PFX WW 0 abataabu .
PFX WW 0 abataalu .
PFX WW 0 abataaku .
PFX WW 0 abataatu .
PFX WW 0 teguun [^lmn]
PFX WW l teguund l.[^mn]
PFX WW l teguunn l.[mn]
PFX WW w teguump [w]
PFX WW 0 teguumu .
PFX WW 0 teguuba .
PFX WW 0 teguugu .
PFX WW 0 teguugi .
PFX WW 0 teguuzi .
PFX WW 0 teguuki .
PFX WW 0 teguubi .
PFX WW 0 teguuli .
PFX WW 0 teguuga .
PFX WW 0 teguuka .
PFX WW 0 teguubu .
PFX WW 0 teguulu .
PFX WW 0 teguuku .
PFX WW 0 teguutu .
PFX WW 0 ogutaan [^lmn]
PFX WW l ogutaand l.[^mn]
PFX WW l ogutaann l.[mn]
PFX WW w ogutaamp [w]
PFX WW 0 ogutaamu .
PFX WW 0 ogutaaba .
PFX WW 0 ogutaagu .
PFX WW 0 ogutaagi .
PFX WW 0 ogutaazi .
PFX WW 0 ogutaaki .
PFX WW 0 ogutaabi .
PFX WW 0 ogutaali .
PFX WW 0 ogutaaga .
PFX WW 0 ogutaaka .
PFX WW 0 ogutaabu .
PFX WW 0 ogutaalu .
PFX WW 0 ogutaaku .
PFX WW 0 ogutaatu .
PFX WW 0 tegiin [^lmn]
PFX WW l tegiind l.[^mn]
PFX WW l tegiinn l.[mn]
PFX WW w tegiimp [w]
PFX WW 0 tegiimu .
PFX WW 0 tegiiba .
PFX WW 0 tegiigu .
PFX WW 0 tegiigi .
PFX WW 0 tegiizi .
PFX WW 0 tegiiki .
PFX WW 0 tegiibi .
PFX WW 0 tegiili .
PFX WW 0 tegiiga .
PFX WW 0 tegiika .
PFX WW 0 tegiibu .
PFX WW 0 tegiilu .
PFX WW 0 tegiiku .
PFX WW 0 tegiitu .
PFX WW 0 egitaan [^lmn]
PFX WW l egitaand l.[^mn]
PFX WW l egitaann l.[mn]
PFX WW w egitaamp [w]
PFX WW 0 egitaamu .
PFX WW 0 egitaaba .
PFX WW 0 egitaagu .
PFX WW 0 egitaagi .
PFX WW 0 egitaazi .
PFX WW 0 egitaaki .
PFX WW 0 egitaabi .
PFX WW 0 egitaali .
PFX WW 0 egitaaga .
PFX WW 0 egitaaka .
PFX WW 0 egitaabu .
PFX WW 0 egitaalu .
PFX WW 0 egitaaku .
PFX WW 0 egitaatu .
PFX WW 0 teen [^lmn]
PFX WW l teend l.[^mn]
PFX WW l teenn l.[mn]
PFX WW w teemp [w]
PFX WW 0 teemu .
PFX WW 0 teeba .
PFX WW 0 teegu .
PFX WW 0 teegi .
PFX WW 0 teezi .
PFX WW 0 teeki .
PFX WW 0 teebi .
PFX WW 0 teeli .
PFX WW 0 teega .
PFX WW 0 teeka .
PFX WW 0 teebu .
PFX WW 0 teelu .
PFX WW 0 teeku .
PFX WW 0 teetu .
PFX WW 0 teziin [^lmn]
PFX WW l teziind l.[^mn]
PFX WW l teziinn l.[mn]
PFX WW w teziimp [w]
PFX WW 0 teziimu .
PFX WW 0 teziiba .
PFX WW 0 teziigu .
PFX WW 0 teziigi .
PFX WW 0 teziizi .
PFX WW 0 teziiki .
PFX WW 0 teziibi .
PFX WW 0 teziili .
PFX WW 0 teziiga .
PFX WW 0 teziika .
PFX WW 0 teziibu .
PFX WW 0 teziilu .
PFX WW 0 teziiku .
PFX WW 0 teziitu .
PFX WW 0 ezitaan [^lmn]
PFX WW l ezitaand l.[^mn]
PFX WW l ezitaann l.[mn]
PFX WW w ezitaamp [w]
PFX WW 0 ezitaamu .
PFX WW 0 ezitaaba .
PFX WW 0 ezitaagu .
PFX WW 0 ezitaagi .
PFX WW 0 ezitaazi .
PFX WW 0 ezitaaki .
PFX WW 0 ezitaabi .
PFX WW 0 ezitaali .
PFX WW 0 ezitaaga .
PFX WW 0 ezitaaka .
PFX WW 0 ezitaabu .
PFX WW 0 ezitaalu .
PFX WW 0 ezitaaku .
PFX WW 0 ezitaatu .
PFX WW 0 tekiin [^lmn]
PFX WW l tekiind l.[^mn]
PFX WW l tekiinn l.[mn]
PFX WW w tekiimp [w]
PFX WW 0 tekiimu .
PFX WW 0 tekiiba .
PFX WW 0 tekiigu .
PFX WW 0 tekiigi .
PFX WW 0 tekiizi .
PFX WW 0 tekiiki .
PFX WW 0 tekiibi .
PFX WW 0 tekiili .
PFX WW 0 tekiiga .
PFX WW 0 tekiika .
PFX WW 0 tekiibu .
PFX WW 0 tekiilu .
PFX WW 0 tekiiku .
PFX WW 0 tekiitu .
PFX WW 0 ekitaan [^lmn]
PFX WW l ekitaand l.[^mn]
PFX WW l ekitaann l.[mn]
PFX WW w ekitaamp [w]
PFX WW 0 ekitaamu .
PFX WW 0 ekitaaba .
PFX WW 0 ekitaagu .
PFX WW 0 ekitaagi .
PFX WW 0 ekitaazi .
PFX WW 0 ekitaaki .
PFX WW 0 ekitaabi .
PFX WW 0 ekitaali .
PFX WW 0 ekitaaga .
PFX WW 0 ekitaaka .
PFX WW 0 ekitaabu .
PFX WW 0 ekitaalu .
PFX WW 0 ekitaaku .
PFX WW 0 ekitaatu .
PFX WW 0 tebiin [^lmn]
PFX WW l tebiind l.[^mn]
PFX WW l tebiinn l.[mn]
PFX WW w tebiimp [w]
PFX WW 0 tebiimu .
PFX WW 0 tebiiba .
PFX WW 0 tebiigu .
PFX WW 0 tebiigi .
PFX WW 0 tebiizi .
PFX WW 0 tebiiki .
PFX WW 0 tebiibi .
PFX WW 0 tebiili .
PFX WW 0 tebiiga .
PFX WW 0 tebiika .
PFX WW 0 tebiibu .
PFX WW 0 tebiilu .
PFX WW 0 tebiiku .
PFX WW 0 tebiitu .
PFX WW 0 ebitaan [^lmn]
PFX WW l ebitaand l.[^mn]
PFX WW l ebitaann l.[mn]
PFX WW w ebitaamp [w]
PFX WW 0 ebitaamu .
PFX WW 0 ebitaaba .
PFX WW 0 ebitaagu .
PFX WW 0 ebitaagi .
PFX WW 0 ebitaazi .
PFX WW 0 ebitaaki .
PFX WW 0 ebitaabi .
PFX WW 0 ebitaali .
PFX WW 0 ebitaaga .
PFX WW 0 ebitaaka .
PFX WW 0 ebitaabu .
PFX WW 0 ebitaalu .
PFX WW 0 ebitaaku .
PFX WW 0 ebitaatu .
PFX WW 0 teliin [^lmn]
PFX WW l teliind l.[^mn]
PFX WW l teliinn l.[mn]
PFX WW w teliimp [w]
PFX WW 0 teliimu .
PFX WW 0 teliiba .
PFX WW 0 teliigu .
PFX WW 0 teliigi .
PFX WW 0 teliizi .
PFX WW 0 teliiki .
PFX WW 0 teliibi .
PFX WW 0 teliili .
PFX WW 0 teliiga .
PFX WW 0 teliika .
PFX WW 0 teliibu .
PFX WW 0 teliilu .
PFX WW 0 teliiku .
PFX WW 0 teliitu .
PFX WW 0 elitaan [^lmn]
PFX WW l elitaand l.[^mn]
PFX WW l elitaann l.[mn]
PFX WW w elitaamp [w]
PFX WW 0 elitaamu .
PFX WW 0 elitaaba .
PFX WW 0 elitaagu .
PFX WW 0 elitaagi .
PFX WW 0 elitaazi .
PFX WW 0 elitaaki .
PFX WW 0 elitaabi .
PFX WW 0 elitaali .
PFX WW 0 elitaaga .
PFX WW 0 elitaaka .
PFX WW 0 elitaabu .
PFX WW 0 elitaalu .
PFX WW 0 elitaaku .
PFX WW 0 elitaatu .
PFX WW 0 tegaan [^lmn]
PFX WW l tegaand l.[^mn]
PFX WW l tegaann l.[mn]
PFX WW w tegaamp [w]
PFX WW 0 tegaamu .
PFX WW 0 tegaaba .
PFX WW 0 tegaagu .
PFX WW 0 tegaagi .
PFX WW 0 tegaazi .
PFX WW 0 tegaaki .
PFX WW 0 tegaabi .
PFX WW 0 tegaali .
PFX WW 0 tegaaga .
PFX WW 0 tegaaka .
PFX WW 0 tegaabu .
PFX WW 0 tegaalu .
PFX WW 0 tegaaku .
PFX WW 0 tegaatu .
PFX WW 0 agataan [^lmn]
PFX WW l agataand l.[^mn]
PFX WW l agataann l.[mn]
PFX WW w agataamp [w]
PFX WW 0 agataamu .
PFX WW 0 agataaba .
PFX WW 0 agataagu .
PFX WW 0 agataagi .
PFX WW 0 agataazi .
PFX WW 0 agataaki .
PFX WW 0 agataabi .
PFX WW 0 agataali .
PFX WW 0 agataaga .
PFX WW 0 agataaka .
PFX WW 0 agataabu .
PFX WW 0 agataalu .
PFX WW 0 agataaku .
PFX WW 0 agataatu .
PFX WW 0 tekaan [^lmn]
PFX WW l tekaand l.[^mn]
PFX WW l tekaann l.[mn]
PFX WW w tekaamp [w]
PFX WW 0 tekaamu .
PFX WW 0 tekaaba .
PFX WW 0 tekaagu .
PFX WW 0 tekaagi .
PFX WW 0 tekaazi .
PFX WW 0 tekaaki .
PFX WW 0 tekaabi .
PFX WW 0 tekaali .
PFX WW 0 tekaaga .
PFX WW 0 tekaaka .
PFX WW 0 tekaabu .
PFX WW 0 tekaalu .
PFX WW 0 tekaaku .
PFX WW 0 tekaatu .
PFX WW 0 akataan [^lmn]
PFX WW l akataand l.[^mn]
PFX WW l akataann l.[mn]
PFX WW w akataamp [w]
PFX WW 0 akataamu .
PFX WW 0 akataaba .
PFX WW 0 akataagu .
PFX WW 0 akataagi .
PFX WW 0 akataazi .
PFX WW 0 akataaki .
PFX WW 0 akataabi .
PFX WW 0 akataali .
PFX WW 0 akataaga .
PFX WW 0 akataaka .
PFX WW 0 akataabu .
PFX WW 0 akataalu .
PFX WW 0 akataaku .
PFX WW 0 akataatu .
PFX WW 0 tebuun [^lmn]
PFX WW l tebuund l.[^mn]
PFX WW l tebuunn l.[mn]
PFX WW w tebuump [w]
PFX WW 0 tebuumu .
PFX WW 0 tebuuba .
PFX WW 0 tebuugu .
PFX WW 0 tebuugi .
PFX WW 0 tebuuzi .
PFX WW 0 tebuuki .
PFX WW 0 tebuubi .
PFX WW 0 tebuuli .
PFX WW 0 tebuuga .
PFX WW 0 tebuuka .
PFX WW 0 tebuubu .
PFX WW 0 tebuulu .
PFX WW 0 tebuuku .
PFX WW 0 tebuutu .
PFX WW 0 obutaan [^lmn]
PFX WW l obutaand l.[^mn]
PFX WW l obutaann l.[mn]
PFX WW w obutaamp [w]
PFX WW 0 obutaamu .
PFX WW 0 obutaaba .
PFX WW 0 obutaagu .
PFX WW 0 obutaagi .
PFX WW 0 obutaazi .
PFX WW 0 obutaaki .
PFX WW 0 obutaabi .
PFX WW 0 obutaali .
PFX WW 0 obutaaga .
PFX WW 0 obutaaka .
PFX WW 0 obutaabu .
PFX WW 0 obutaalu .
PFX WW 0 obutaaku .
PFX WW 0 obutaatu .
PFX WW 0 teluun [^lmn]
PFX WW l teluund l.[^mn]
PFX WW l teluunn l.[mn]
PFX WW w teluump [w]
PFX WW 0 teluumu .
PFX WW 0 teluuba .
PFX WW 0 teluugu .
PFX WW 0 teluugi .
PFX WW 0 teluuzi .
PFX WW 0 teluuki .
PFX WW 0 teluubi .
PFX WW 0 teluuli .
PFX WW 0 teluuga .
PFX WW 0 teluuka .
PFX WW 0 teluubu .
PFX WW 0 teluulu .
PFX WW 0 teluuku .
PFX WW 0 teluutu .
PFX WW 0 olutaan [^lmn]
PFX WW l olutaand l.[^mn]
PFX WW l olutaann l.[mn]
PFX WW w olutaamp [w]
PFX WW 0 olutaamu .
PFX WW 0 olutaaba .
PFX WW 0 olutaagu .
PFX WW 0 olutaagi .
PFX WW 0 olutaazi .
PFX WW 0 olutaaki .
PFX WW 0 olutaabi .
PFX WW 0 olutaali .
PFX WW 0 olutaaga .
PFX WW 0 olutaaka .
PFX WW 0 olutaabu .
PFX WW 0 olutaalu .
PFX WW 0 olutaaku .
PFX WW 0 olutaatu .
PFX WW 0 teziin [^lmn]
PFX WW l teziind l.[^mn]
PFX WW l teziinn l.[mn]
PFX WW w teziimp [w]
PFX WW 0 teziimu .
PFX WW 0 teziiba .
PFX WW 0 teziigu .
PFX WW 0 teziigi .
PFX WW 0 teziizi .
PFX WW 0 teziiki .
PFX WW 0 teziibi .
PFX WW 0 teziili .
PFX WW 0 teziiga .
PFX WW 0 teziika .
PFX WW 0 teziibu .
PFX WW 0 teziilu .
PFX WW 0 teziiku .
PFX WW 0 teziitu .
PFX WW 0 ezitaan [^lmn]
PFX WW l ezitaand l.[^mn]
PFX WW l ezitaann l.[mn]
PFX WW w ezitaamp [w]
PFX WW 0 ezitaamu .
PFX WW 0 ezitaaba .
PFX WW 0 ezitaagu .
PFX WW 0 ezitaagi .
PFX WW 0 ezitaazi .
PFX WW 0 ezitaaki .
PFX WW 0 ezitaabi .
PFX WW 0 ezitaali .
PFX WW 0 ezitaaga .
PFX WW 0 ezitaaka .
PFX WW 0 ezitaabu .
PFX WW 0 ezitaalu .
PFX WW 0 ezitaaku .
PFX WW 0 ezitaatu .
PFX WW 0 tekuun [^lmn]
PFX WW l tekuund l.[^mn]
PFX WW l tekuunn l.[mn]
PFX WW w tekuump [w]
PFX WW 0 tekuumu .
PFX WW 0 tekuuba .
PFX WW 0 tekuugu .
PFX WW 0 tekuugi .
PFX WW 0 tekuuzi .
PFX WW 0 tekuuki .
PFX WW 0 tekuubi .
PFX WW 0 tekuuli .
PFX WW 0 tekuuga .
PFX WW 0 tekuuka .
PFX WW 0 tekuubu .
PFX WW 0 tekuulu .
PFX WW 0 tekuuku .
PFX WW 0 tekuutu .
PFX WW 0 okutaan [^lmn]
PFX WW l okutaand l.[^mn]
PFX WW l okutaann l.[mn]
PFX WW w okutaamp [w]
PFX WW 0 okutaamu .
PFX WW 0 okutaaba .
PFX WW 0 okutaagu .
PFX WW 0 okutaagi .
PFX WW 0 okutaazi .
PFX WW 0 okutaaki .
PFX WW 0 okutaabi .
PFX WW 0 okutaali .
PFX WW 0 okutaaga .
PFX WW 0 okutaaka .
PFX WW 0 okutaabu .
PFX WW 0 okutaalu .
PFX WW 0 okutaaku .
PFX WW 0 okutaatu .
PFX WW 0 teguun [^lmn]
PFX WW l teguund l.[^mn]
PFX WW l teguunn l.[mn]
PFX WW w teguump [w]
PFX WW 0 teguumu .
PFX WW 0 teguuba .
PFX WW 0 teguugu .
PFX WW 0 teguugi .
PFX WW 0 teguuzi .
PFX WW 0 teguuki .
PFX WW 0 teguubi .
PFX WW 0 teguuli .
PFX WW 0 teguuga .
PFX WW 0 teguuka .
PFX WW 0 teguubu .
PFX WW 0 teguulu .
PFX WW 0 teguuku .
PFX WW 0 teguutu .
PFX WW 0 ogutaan [^lmn]
PFX WW l ogutaand l.[^mn]
PFX WW l ogutaann l.[mn]
PFX WW w ogutaamp [w]
PFX WW 0 ogutaamu .
PFX WW 0 ogutaaba .
PFX WW 0 ogutaagu .
PFX WW 0 ogutaagi .
PFX WW 0 ogutaazi .
PFX WW 0 ogutaaki .
PFX WW 0 ogutaabi .
PFX WW 0 ogutaali .
PFX WW 0 ogutaaga .
PFX WW 0 ogutaaka .
PFX WW 0 ogutaabu .
PFX WW 0 ogutaalu .
PFX WW 0 ogutaaku .
PFX WW 0 ogutaatu .
PFX WW 0 tetuun [^lmn]
PFX WW l tetuund l.[^mn]
PFX WW l tetuunn l.[mn]
PFX WW w tetuump [w]
PFX WW 0 tetuumu .
PFX WW 0 tetuuba .
PFX WW 0 tetuugu .
PFX WW 0 tetuugi .
PFX WW 0 tetuuzi .
PFX WW 0 tetuuki .
PFX WW 0 tetuubi .
PFX WW 0 tetuuli .
PFX WW 0 tetuuga .
PFX WW 0 tetuuka .
PFX WW 0 tetuubu .
PFX WW 0 tetuulu .
PFX WW 0 tetuuku .
PFX WW 0 tetuutu .
PFX WW 0 otutaan [^lmn]
PFX WW l otutaand l.[^mn]
PFX WW l otutaann l.[mn]
PFX WW w otutaamp [w]
PFX WW 0 otutaamu .
PFX WW 0 otutaaba .
PFX WW 0 otutaagu .
PFX WW 0 otutaagi .
PFX WW 0 otutaazi .
PFX WW 0 otutaaki .
PFX WW 0 otutaabi .
PFX WW 0 otutaali .
PFX WW 0 otutaaga .
PFX WW 0 otutaaka .
PFX WW 0 otutaabu .
PFX WW 0 otutaalu .
PFX WW 0 otutaaku .
PFX WW 0 otutaatu ."""

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
    "WW": "WW",
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

    out_flag = "JA"
    left_desc = FLAG_DESCRIPTIONS.get("WW", "WW")
    right_desc = FLAG_DESCRIPTIONS.get("Ob", "Ob")
    comment_line = "# Cross product of {} ({}) and {} ({}) to {}".format(
        "WW", left_desc, "Ob", right_desc, out_flag
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
