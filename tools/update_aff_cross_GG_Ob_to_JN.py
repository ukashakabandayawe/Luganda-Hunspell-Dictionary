import re
import os
from pathlib import Path

# Cross product generator: GG x Ob => JN
# Description:
# - Left block `GG`: GG
# - Right block `Ob`: Object markers
# - Output flag `JN`: Cross-product prefixes for GG x Ob

REPO_ROOT = Path(__file__).resolve().parents[1]
AFF_FILE = REPO_ROOT / "Luganda.aff"

# If set to a flag name (e.g. "HB"), the generated cross-product block will be inserted
# immediately before the first "PFX <flag>" line when the output flag block doesn't
# already exist in the .aff.
INSERT_BEFORE_FLAG = "".strip() or None

rule_left_raw = """
PFX GG Y 608
PFX GG 0 nnaba .
PFX GG 0 nnagu .
PFX GG 0 nnagi .
PFX GG 0 nnazi .
PFX GG 0 nnaki .
PFX GG 0 nnabi .
PFX GG 0 nnali .
PFX GG 0 nnaga .
PFX GG 0 nnaka .
PFX GG 0 nnabu .
PFX GG 0 nnalu .
PFX GG 0 nnaku .
PFX GG 0 nnatu .
PFX GG 0 nnamu .
PFX GG 0 wan [^lmnb]
PFX GG l wand l.[^mn]
PFX GG l wann l.[mn]
PFX GG w wamp [w]
PFX GG 0 wamu .
PFX GG 0 waba .
PFX GG 0 wagu .
PFX GG 0 wagi .
PFX GG 0 wazi .
PFX GG 0 waki .
PFX GG 0 wabi .
PFX GG 0 wali .
PFX GG 0 waga .
PFX GG 0 waka .
PFX GG 0 wabu .
PFX GG 0 walu .
PFX GG 0 waku .
PFX GG 0 watu .
PFX GG 0 yan [^lmnb]
PFX GG l yand l.[^mn]
PFX GG l yann l.[mn]
PFX GG w yamp [w]
PFX GG 0 yamu .
PFX GG 0 yaba .
PFX GG 0 yagu .
PFX GG 0 yagi .
PFX GG 0 yazi .
PFX GG 0 yaki .
PFX GG 0 yabi .
PFX GG 0 yali .
PFX GG 0 yaga .
PFX GG 0 yaka .
PFX GG 0 yabu .
PFX GG 0 yalu .
PFX GG 0 yaku .
PFX GG 0 yatu .
PFX GG 0 eyan [^lmnb]
PFX GG l eyand l.[^mn]
PFX GG l eyann l.[mn]
PFX GG w eyamp [w]
PFX GG 0 eyamu .
PFX GG 0 eyaba .
PFX GG 0 eyagu .
PFX GG 0 eyagi .
PFX GG 0 eyazi .
PFX GG 0 eyaki .
PFX GG 0 eyabi .
PFX GG 0 eyali .
PFX GG 0 eyaga .
PFX GG 0 eyaka .
PFX GG 0 eyabu .
PFX GG 0 eyalu .
PFX GG 0 eyaku .
PFX GG 0 eyatu .
PFX GG 0 twan [^lmnb]
PFX GG l twand l.[^mn]
PFX GG l twann l.[mn]
PFX GG w twamp [w]
PFX GG 0 twamu .
PFX GG 0 twaba .
PFX GG 0 twagu .
PFX GG 0 twagi .
PFX GG 0 twazi .
PFX GG 0 twaki .
PFX GG 0 twabi .
PFX GG 0 twali .
PFX GG 0 twaga .
PFX GG 0 twaka .
PFX GG 0 twabu .
PFX GG 0 twalu .
PFX GG 0 twaku .
PFX GG 0 twatu .
PFX GG 0 mwan [^lmnb]
PFX GG l mwand l.[^mn]
PFX GG l mwann l.[mn]
PFX GG w mwamp [w]
PFX GG 0 mwamu .
PFX GG 0 mwaba .
PFX GG 0 mwagu .
PFX GG 0 mwagi .
PFX GG 0 mwazi .
PFX GG 0 mwaki .
PFX GG 0 mwabi .
PFX GG 0 mwali .
PFX GG 0 mwaga .
PFX GG 0 mwaka .
PFX GG 0 mwabu .
PFX GG 0 mwalu .
PFX GG 0 mwaku .
PFX GG 0 mwatu .
PFX GG 0 baan [^lmnb]
PFX GG l baand l.[^mn]
PFX GG l baann l.[mn]
PFX GG w baamp [w]
PFX GG 0 baamu .
PFX GG 0 baaba .
PFX GG 0 baagu .
PFX GG 0 baagi .
PFX GG 0 baazi .
PFX GG 0 baaki .
PFX GG 0 baabi .
PFX GG 0 baali .
PFX GG 0 baaga .
PFX GG 0 baaka .
PFX GG 0 baabu .
PFX GG 0 baalu .
PFX GG 0 baaku .
PFX GG 0 baatu .
PFX GG 0 abaan [^lmnb]
PFX GG l abaand l.[^mn]
PFX GG l abaann l.[mn]
PFX GG w abaamp [w]
PFX GG 0 abaamu .
PFX GG 0 abaaba .
PFX GG 0 abaagu .
PFX GG 0 abaagi .
PFX GG 0 abaazi .
PFX GG 0 abaaki .
PFX GG 0 abaabi .
PFX GG 0 abaali .
PFX GG 0 abaaga .
PFX GG 0 abaaka .
PFX GG 0 abaabu .
PFX GG 0 abaalu .
PFX GG 0 abaaku .
PFX GG 0 abaatu .
PFX GG 0 gwan [^lmnb]
PFX GG l gwand l.[^mn]
PFX GG l gwann l.[mn]
PFX GG w gwamp [w]
PFX GG 0 gwamu .
PFX GG 0 gwaba .
PFX GG 0 gwagu .
PFX GG 0 gwagi .
PFX GG 0 gwazi .
PFX GG 0 gwaki .
PFX GG 0 gwabi .
PFX GG 0 gwali .
PFX GG 0 gwaga .
PFX GG 0 gwaka .
PFX GG 0 gwabu .
PFX GG 0 gwalu .
PFX GG 0 gwaku .
PFX GG 0 gwatu .
PFX GG 0 ogwan [^lmnb]
PFX GG l ogwand l.[^mn]
PFX GG l ogwann l.[mn]
PFX GG w ogwamp [w]
PFX GG 0 ogwamu .
PFX GG 0 ogwaba .
PFX GG 0 ogwagu .
PFX GG 0 ogwagi .
PFX GG 0 ogwazi .
PFX GG 0 ogwaki .
PFX GG 0 ogwabi .
PFX GG 0 ogwali .
PFX GG 0 ogwaga .
PFX GG 0 ogwaka .
PFX GG 0 ogwabu .
PFX GG 0 ogwalu .
PFX GG 0 ogwaku .
PFX GG 0 ogwatu .
PFX GG 0 gyan [^lmnb]
PFX GG l gyand l.[^mn]
PFX GG l gyann l.[mn]
PFX GG w gyamp [w]
PFX GG 0 gyamu .
PFX GG 0 gyaba .
PFX GG 0 gyagu .
PFX GG 0 gyagi .
PFX GG 0 gyazi .
PFX GG 0 gyaki .
PFX GG 0 gyabi .
PFX GG 0 gyali .
PFX GG 0 gyaga .
PFX GG 0 gyaka .
PFX GG 0 gyabu .
PFX GG 0 gyalu .
PFX GG 0 gyaku .
PFX GG 0 gyatu .
PFX GG 0 egyan [^lmnb]
PFX GG l egyand l.[^mn]
PFX GG l egyann l.[mn]
PFX GG w egyamp [w]
PFX GG 0 egyamu .
PFX GG 0 egyaba .
PFX GG 0 egyagu .
PFX GG 0 egyagi .
PFX GG 0 egyazi .
PFX GG 0 egyaki .
PFX GG 0 egyabi .
PFX GG 0 egyali .
PFX GG 0 egyaga .
PFX GG 0 egyaka .
PFX GG 0 egyabu .
PFX GG 0 egyalu .
PFX GG 0 egyaku .
PFX GG 0 egyatu .
PFX GG 0 zaan [^lmnb]
PFX GG l zaand l.[^mn]
PFX GG l zaann l.[mn]
PFX GG w zaamp [w]
PFX GG 0 zaamu .
PFX GG 0 zaaba .
PFX GG 0 zaagu .
PFX GG 0 zaagi .
PFX GG 0 zaazi .
PFX GG 0 zaaki .
PFX GG 0 zaabi .
PFX GG 0 zaali .
PFX GG 0 zaaga .
PFX GG 0 zaaka .
PFX GG 0 zaabu .
PFX GG 0 zaalu .
PFX GG 0 zaaku .
PFX GG 0 zaatu .
PFX GG 0 ezaan [^lmnb]
PFX GG l ezaand l.[^mn]
PFX GG l ezaann l.[mn]
PFX GG w ezaamp [w]
PFX GG 0 ezaamu .
PFX GG 0 ezaaba .
PFX GG 0 ezaagu .
PFX GG 0 ezaagi .
PFX GG 0 ezaazi .
PFX GG 0 ezaaki .
PFX GG 0 ezaabi .
PFX GG 0 ezaali .
PFX GG 0 ezaaga .
PFX GG 0 ezaaka .
PFX GG 0 ezaabu .
PFX GG 0 ezaalu .
PFX GG 0 ezaaku .
PFX GG 0 ezaatu .
PFX GG 0 kyaan [^lmnb]
PFX GG l kyaand l.[^mn]
PFX GG l kyaann l.[mn]
PFX GG w kyaamp [w]
PFX GG 0 kyaamu .
PFX GG 0 kyaaba .
PFX GG 0 kyaagu .
PFX GG 0 kyaagi .
PFX GG 0 kyaazi .
PFX GG 0 kyaaki .
PFX GG 0 kyaabi .
PFX GG 0 kyaali .
PFX GG 0 kyaaga .
PFX GG 0 kyaaka .
PFX GG 0 kyaabu .
PFX GG 0 kyaalu .
PFX GG 0 kyaaku .
PFX GG 0 kyaatu .
PFX GG 0 ekyaan [^lmnb]
PFX GG l ekyaand l.[^mn]
PFX GG l ekyaann l.[mn]
PFX GG w ekyaamp [w]
PFX GG 0 ekyaamu .
PFX GG 0 ekyaaba .
PFX GG 0 ekyaagu .
PFX GG 0 ekyaagi .
PFX GG 0 ekyaazi .
PFX GG 0 ekyaaki .
PFX GG 0 ekyaabi .
PFX GG 0 ekyaali .
PFX GG 0 ekyaaga .
PFX GG 0 ekyaaka .
PFX GG 0 ekyaabu .
PFX GG 0 ekyaalu .
PFX GG 0 ekyaaku .
PFX GG 0 ekyaatu .
PFX GG 0 byaan [^lmnb]
PFX GG l byaand l.[^mn]
PFX GG l byaann l.[mn]
PFX GG w byaamp [w]
PFX GG 0 byaamu .
PFX GG 0 byaaba .
PFX GG 0 byaagu .
PFX GG 0 byaagi .
PFX GG 0 byaazi .
PFX GG 0 byaaki .
PFX GG 0 byaabi .
PFX GG 0 byaali .
PFX GG 0 byaaga .
PFX GG 0 byaaka .
PFX GG 0 byaabu .
PFX GG 0 byaalu .
PFX GG 0 byaaku .
PFX GG 0 byaatu .
PFX GG 0 ebyaan [^lmnb]
PFX GG l ebyaand l.[^mn]
PFX GG l ebyaann l.[mn]
PFX GG w ebyaamp [w]
PFX GG 0 ebyaamu .
PFX GG 0 ebyaaba .
PFX GG 0 ebyaagu .
PFX GG 0 ebyaagi .
PFX GG 0 ebyaazi .
PFX GG 0 ebyaaki .
PFX GG 0 ebyaabi .
PFX GG 0 ebyaali .
PFX GG 0 ebyaaga .
PFX GG 0 ebyaaka .
PFX GG 0 ebyaabu .
PFX GG 0 ebyaalu .
PFX GG 0 ebyaaku .
PFX GG 0 ebyaatu .
PFX GG 0 lyaan [^lmnb]
PFX GG l lyaand l.[^mn]
PFX GG l lyaann l.[mn]
PFX GG w lyaamp [w]
PFX GG 0 lyaamu .
PFX GG 0 lyaaba .
PFX GG 0 lyaagu .
PFX GG 0 lyaagi .
PFX GG 0 lyaazi .
PFX GG 0 lyaaki .
PFX GG 0 lyaabi .
PFX GG 0 lyaali .
PFX GG 0 lyaaga .
PFX GG 0 lyaaka .
PFX GG 0 lyaabu .
PFX GG 0 lyaalu .
PFX GG 0 lyaaku .
PFX GG 0 lyaatu .
PFX GG 0 elyaan [^lmnb]
PFX GG l elyaand l.[^mn]
PFX GG l elyaann l.[mn]
PFX GG w elyaamp [w]
PFX GG 0 elyaamu .
PFX GG 0 elyaaba .
PFX GG 0 elyaagu .
PFX GG 0 elyaagi .
PFX GG 0 elyaazi .
PFX GG 0 elyaaki .
PFX GG 0 elyaabi .
PFX GG 0 elyaali .
PFX GG 0 elyaaga .
PFX GG 0 elyaaka .
PFX GG 0 elyaabu .
PFX GG 0 elyaalu .
PFX GG 0 elyaaku .
PFX GG 0 elyaatu .
PFX GG 0 gaan [^lmnb]
PFX GG l gaand l.[^mn]
PFX GG l gaann l.[mn]
PFX GG w gaamp [w]
PFX GG 0 gaamu .
PFX GG 0 gaaba .
PFX GG 0 gaagu .
PFX GG 0 gaagi .
PFX GG 0 gaazi .
PFX GG 0 gaaki .
PFX GG 0 gaabi .
PFX GG 0 gaali .
PFX GG 0 gaaga .
PFX GG 0 gaaka .
PFX GG 0 gaabu .
PFX GG 0 gaalu .
PFX GG 0 gaaku .
PFX GG 0 gaatu .
PFX GG 0 agaan [^lmnb]
PFX GG l agaand l.[^mn]
PFX GG l agaann l.[mn]
PFX GG w agaamp [w]
PFX GG 0 agaamu .
PFX GG 0 agaaba .
PFX GG 0 agaagu .
PFX GG 0 agaagi .
PFX GG 0 agaazi .
PFX GG 0 agaaki .
PFX GG 0 agaabi .
PFX GG 0 agaali .
PFX GG 0 agaaga .
PFX GG 0 agaaka .
PFX GG 0 agaabu .
PFX GG 0 agaalu .
PFX GG 0 agaaku .
PFX GG 0 agaatu .
PFX GG 0 kaan [^lmnb]
PFX GG l kaand l.[^mn]
PFX GG l kaann l.[mn]
PFX GG w kaamp [w]
PFX GG 0 kaamu .
PFX GG 0 kaaba .
PFX GG 0 kaagu .
PFX GG 0 kaagi .
PFX GG 0 kaazi .
PFX GG 0 kaaki .
PFX GG 0 kaabi .
PFX GG 0 kaali .
PFX GG 0 kaaga .
PFX GG 0 kaaka .
PFX GG 0 kaabu .
PFX GG 0 kaalu .
PFX GG 0 kaaku .
PFX GG 0 kaatu .
PFX GG 0 akaan [^lmnb]
PFX GG l akaand l.[^mn]
PFX GG l akaann l.[mn]
PFX GG w akaamp [w]
PFX GG 0 akaamu .
PFX GG 0 akaaba .
PFX GG 0 akaagu .
PFX GG 0 akaagi .
PFX GG 0 akaazi .
PFX GG 0 akaaki .
PFX GG 0 akaabi .
PFX GG 0 akaali .
PFX GG 0 akaaga .
PFX GG 0 akaaka .
PFX GG 0 akaabu .
PFX GG 0 akaalu .
PFX GG 0 akaaku .
PFX GG 0 akaatu .
PFX GG 0 bwan [^lmnb]
PFX GG l bwand l.[^mn]
PFX GG l bwann l.[mn]
PFX GG w bwamp [w]
PFX GG 0 bwamu .
PFX GG 0 bwaba .
PFX GG 0 bwagu .
PFX GG 0 bwagi .
PFX GG 0 bwazi .
PFX GG 0 bwaki .
PFX GG 0 bwabi .
PFX GG 0 bwali .
PFX GG 0 bwaga .
PFX GG 0 bwaka .
PFX GG 0 bwabu .
PFX GG 0 bwalu .
PFX GG 0 bwaku .
PFX GG 0 bwatu .
PFX GG 0 obwan [^lmnb]
PFX GG l obwand l.[^mn]
PFX GG l obwann l.[mn]
PFX GG w obwamp [w]
PFX GG 0 obwamu .
PFX GG 0 obwaba .
PFX GG 0 obwagu .
PFX GG 0 obwagi .
PFX GG 0 obwazi .
PFX GG 0 obwaki .
PFX GG 0 obwabi .
PFX GG 0 obwali .
PFX GG 0 obwaga .
PFX GG 0 obwaka .
PFX GG 0 obwabu .
PFX GG 0 obwalu .
PFX GG 0 obwaku .
PFX GG 0 obwatu .
PFX GG 0 lwan [^lmnb]
PFX GG l lwand l.[^mn]
PFX GG l lwann l.[mn]
PFX GG w lwamp [w]
PFX GG 0 lwamu .
PFX GG 0 lwaba .
PFX GG 0 lwagu .
PFX GG 0 lwagi .
PFX GG 0 lwazi .
PFX GG 0 lwaki .
PFX GG 0 lwabi .
PFX GG 0 lwali .
PFX GG 0 lwaga .
PFX GG 0 lwaka .
PFX GG 0 lwabu .
PFX GG 0 lwalu .
PFX GG 0 lwaku .
PFX GG 0 lwatu .
PFX GG 0 olwan [^lmnb]
PFX GG l olwand l.[^mn]
PFX GG l olwann l.[mn]
PFX GG w olwamp [w]
PFX GG 0 olwamu .
PFX GG 0 olwaba .
PFX GG 0 olwagu .
PFX GG 0 olwagi .
PFX GG 0 olwazi .
PFX GG 0 olwaki .
PFX GG 0 olwabi .
PFX GG 0 olwali .
PFX GG 0 olwaga .
PFX GG 0 olwaka .
PFX GG 0 olwabu .
PFX GG 0 olwalu .
PFX GG 0 olwaku .
PFX GG 0 olwatu .
PFX GG 0 kwaan [^lmnb]
PFX GG l kwaand l.[^mn]
PFX GG l kwaann l.[mn]
PFX GG w kwaamp [w]
PFX GG 0 kwaamu .
PFX GG 0 kwaaba .
PFX GG 0 kwaagu .
PFX GG 0 kwaagi .
PFX GG 0 kwaazi .
PFX GG 0 kwaaki .
PFX GG 0 kwaabi .
PFX GG 0 kwaali .
PFX GG 0 kwaaga .
PFX GG 0 kwaaka .
PFX GG 0 kwaabu .
PFX GG 0 kwaalu .
PFX GG 0 kwaaku .
PFX GG 0 kwaatu .
PFX GG 0 okwaan [^lmnb]
PFX GG l okwaand l.[^mn]
PFX GG l okwaann l.[mn]
PFX GG w okwaamp [w]
PFX GG 0 okwaamu .
PFX GG 0 okwaaba .
PFX GG 0 okwaagu .
PFX GG 0 okwaagi .
PFX GG 0 okwaazi .
PFX GG 0 okwaaki .
PFX GG 0 okwaabi .
PFX GG 0 okwaali .
PFX GG 0 okwaaga .
PFX GG 0 okwaaka .
PFX GG 0 okwaabu .
PFX GG 0 okwaalu .
PFX GG 0 okwaaku .
PFX GG 0 okwaatu .
PFX GG 0 gaan [^lmnb]
PFX GG l gaand l.[^mn]
PFX GG l gaann l.[mn]
PFX GG w gaamp [w]
PFX GG 0 gaamu .
PFX GG 0 gaaba .
PFX GG 0 gaagu .
PFX GG 0 gaagi .
PFX GG 0 gaazi .
PFX GG 0 gaaki .
PFX GG 0 gaabi .
PFX GG 0 gaali .
PFX GG 0 gaaga .
PFX GG 0 gaaka .
PFX GG 0 gaabu .
PFX GG 0 gaalu .
PFX GG 0 gaaku .
PFX GG 0 gaatu .
PFX GG 0 agaan [^lmnb]
PFX GG l agaand l.[^mn]
PFX GG l agaann l.[mn]
PFX GG w agaamp [w]
PFX GG 0 agaamu .
PFX GG 0 agaaba .
PFX GG 0 agaagu .
PFX GG 0 agaagi .
PFX GG 0 agaazi .
PFX GG 0 agaaki .
PFX GG 0 agaabi .
PFX GG 0 agaali .
PFX GG 0 agaaga .
PFX GG 0 agaaka .
PFX GG 0 agaabu .
PFX GG 0 agaalu .
PFX GG 0 agaaku .
PFX GG 0 agaatu .
PFX GG 0 twaan [^lmnb]
PFX GG l twaand l.[^mn]
PFX GG l twaann l.[mn]
PFX GG w twaamp [w]
PFX GG 0 twaamu .
PFX GG 0 twaaba .
PFX GG 0 twaagu .
PFX GG 0 twaagi .
PFX GG 0 twaazi .
PFX GG 0 twaaki .
PFX GG 0 twaabi .
PFX GG 0 twaali .
PFX GG 0 twaaga .
PFX GG 0 twaaka .
PFX GG 0 twaabu .
PFX GG 0 twaalu .
PFX GG 0 twaaku .
PFX GG 0 twaatu .
PFX GG 0 otwaan [^lmnb]
PFX GG l otwaand l.[^mn]
PFX GG l otwaann l.[mn]
PFX GG w otwaamp [w]
PFX GG 0 otwaamu .
PFX GG 0 otwaaba .
PFX GG 0 otwaagu .
PFX GG 0 otwaagi .
PFX GG 0 otwaazi .
PFX GG 0 otwaaki .
PFX GG 0 otwaabi .
PFX GG 0 otwaali .
PFX GG 0 otwaaga .
PFX GG 0 otwaaka .
PFX GG 0 otwaabu .
PFX GG 0 otwaalu .
PFX GG 0 otwaaku .
PFX GG 0 otwaatu ."""

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
    "GG": "GG",
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

    out_flag = "JN"
    left_desc = FLAG_DESCRIPTIONS.get("GG", "GG")
    right_desc = FLAG_DESCRIPTIONS.get("Ob", "Ob")
    comment_line = "# Cross product of {} ({}) and {} ({}) to {}".format(
        "GG", left_desc, "Ob", right_desc, out_flag
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
