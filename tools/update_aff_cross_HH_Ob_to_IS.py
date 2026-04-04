import re
import os
from pathlib import Path

# Cross product generator: HH x Ob => IS
# Description:
# - Left block `HH`: HH
# - Right block `Ob`: Object markers
# - Output flag `IS`: Cross-product prefixes for HH x Ob

REPO_ROOT = Path(__file__).resolve().parents[1]
AFF_FILE = REPO_ROOT / "Luganda.aff"

# If set to a flag name (e.g. "HB"), the generated cross-product block will be inserted
# immediately before the first "PFX <flag>" line when the output flag block doesn't
# already exist in the .aff.
INSERT_BEFORE_FLAG = "".strip() or None

rule_left_raw = """
PFX HH Y 644
PFX HH 0 nnalimukumu .
PFX HH 0 nnalimukuba .
PFX HH 0 nnalimukugu .
PFX HH 0 nnalimukugi .
PFX HH 0 nnalimukuzi .
PFX HH 0 nnalimukuki .
PFX HH 0 nnalimukubi .
PFX HH 0 nnalimukuli .
PFX HH 0 nnalimukuga .
PFX HH 0 nnalimukuka .
PFX HH 0 nnalimukubu .
PFX HH 0 nnalimukulu .
PFX HH 0 nnalimukuku .
PFX HH 0 nnalimukutu .
PFX HH 0 walimukun [^lmn]
PFX HH l walimukund l.[^mn]
PFX HH l walimukunn l.[mn]
PFX HH w walimukump [w]
PFX HH 0 walimukumu .
PFX HH 0 walimukuba .
PFX HH 0 walimukugu .
PFX HH 0 walimukugi .
PFX HH 0 walimukuzi .
PFX HH 0 walimukuki .
PFX HH 0 walimukubi .
PFX HH 0 walimukuli .
PFX HH 0 walimukuga .
PFX HH 0 walimukuka .
PFX HH 0 walimukubu .
PFX HH 0 walimukulu .
PFX HH 0 walimukuku .
PFX HH 0 walimukutu .
PFX HH 0 yalimukun [^lmn]
PFX HH l yalimukund l.[^mn]
PFX HH l yalimukunn l.[mn]
PFX HH w yalimukump [w]
PFX HH 0 yalimukumu .
PFX HH 0 yalimukuba .
PFX HH 0 yalimukugu .
PFX HH 0 yalimukugi .
PFX HH 0 yalimukuzi .
PFX HH 0 yalimukuki .
PFX HH 0 yalimukubi .
PFX HH 0 yalimukuli .
PFX HH 0 yalimukuga .
PFX HH 0 yalimukuka .
PFX HH 0 yalimukubu .
PFX HH 0 yalimukulu .
PFX HH 0 yalimukuku .
PFX HH 0 yalimukutu .
PFX HH 0 eyalimukun [^lmn]
PFX HH l eyalimukund l.[^mn]
PFX HH l eyalimukunn l.[mn]
PFX HH w eyalimukump [w]
PFX HH 0 eyalimukumu .
PFX HH 0 eyalimukuba .
PFX HH 0 eyalimukugu .
PFX HH 0 eyalimukugi .
PFX HH 0 eyalimukuzi .
PFX HH 0 eyalimukuki .
PFX HH 0 eyalimukubi .
PFX HH 0 eyalimukuli .
PFX HH 0 eyalimukuga .
PFX HH 0 eyalimukuka .
PFX HH 0 eyalimukubu .
PFX HH 0 eyalimukulu .
PFX HH 0 eyalimukuku .
PFX HH 0 eyalimukutu .
PFX HH 0 twalimukun [^lmn]
PFX HH l twalimukund l.[^mn]
PFX HH l twalimukunn l.[mn]
PFX HH w twalimukump [w]
PFX HH 0 twalimukumu .
PFX HH 0 twalimukuba .
PFX HH 0 twalimukugu .
PFX HH 0 twalimukugi .
PFX HH 0 twalimukuzi .
PFX HH 0 twalimukuki .
PFX HH 0 twalimukubi .
PFX HH 0 twalimukuli .
PFX HH 0 twalimukuga .
PFX HH 0 twalimukuka .
PFX HH 0 twalimukubu .
PFX HH 0 twalimukulu .
PFX HH 0 twalimukuku .
PFX HH 0 twalimukutu .
PFX HH 0 mwalimukun [^lmn]
PFX HH l mwalimukund l.[^mn]
PFX HH l mwalimukunn l.[mn]
PFX HH w mwalimukump [w]
PFX HH 0 mwalimukumu .
PFX HH 0 mwalimukuba .
PFX HH 0 mwalimukugu .
PFX HH 0 mwalimukugi .
PFX HH 0 mwalimukuzi .
PFX HH 0 mwalimukuki .
PFX HH 0 mwalimukubi .
PFX HH 0 mwalimukuli .
PFX HH 0 mwalimukuga .
PFX HH 0 mwalimukuka .
PFX HH 0 mwalimukubu .
PFX HH 0 mwalimukulu .
PFX HH 0 mwalimukuku .
PFX HH 0 mwalimukutu .
PFX HH 0 baalimukun [^lmn]
PFX HH l baalimukund l.[^mn]
PFX HH l baalimukunn l.[mn]
PFX HH w baalimukump [w]
PFX HH 0 baalimukumu .
PFX HH 0 baalimukuba .
PFX HH 0 baalimukugu .
PFX HH 0 baalimukugi .
PFX HH 0 baalimukuzi .
PFX HH 0 baalimukuki .
PFX HH 0 baalimukubi .
PFX HH 0 baalimukuli .
PFX HH 0 baalimukuga .
PFX HH 0 baalimukuka .
PFX HH 0 baalimukubu .
PFX HH 0 baalimukulu .
PFX HH 0 baalimukuku .
PFX HH 0 baalimukutu .
PFX HH 0 abaalimukun [^lmn]
PFX HH l abaalimukund l.[^mn]
PFX HH l abaalimukunn l.[mn]
PFX HH w abaalimukump [w]
PFX HH 0 abaalimukumu .
PFX HH 0 abaalimukuba .
PFX HH 0 abaalimukugu .
PFX HH 0 abaalimukugi .
PFX HH 0 abaalimukuzi .
PFX HH 0 abaalimukuki .
PFX HH 0 abaalimukubi .
PFX HH 0 abaalimukuli .
PFX HH 0 abaalimukuga .
PFX HH 0 abaalimukuka .
PFX HH 0 abaalimukubu .
PFX HH 0 abaalimukulu .
PFX HH 0 abaalimukuku .
PFX HH 0 abaalimukutu .
PFX HH 0 gwalimukun [^lmn]
PFX HH l gwalimukund l.[^mn]
PFX HH l gwalimukunn l.[mn]
PFX HH w gwalimukump [w]
PFX HH 0 gwalimukumu .
PFX HH 0 gwalimukuba .
PFX HH 0 gwalimukugu .
PFX HH 0 gwalimukugi .
PFX HH 0 gwalimukuzi .
PFX HH 0 gwalimukuki .
PFX HH 0 gwalimukubi .
PFX HH 0 gwalimukuli .
PFX HH 0 gwalimukuga .
PFX HH 0 gwalimukuka .
PFX HH 0 gwalimukubu .
PFX HH 0 gwalimukulu .
PFX HH 0 gwalimukuku .
PFX HH 0 gwalimukutu .
PFX HH 0 ogwalimukun [^lmn]
PFX HH l ogwalimukund l.[^mn]
PFX HH l ogwalimukunn l.[mn]
PFX HH w ogwalimukump [w]
PFX HH 0 ogwalimukumu .
PFX HH 0 ogwalimukuba .
PFX HH 0 ogwalimukugu .
PFX HH 0 ogwalimukugi .
PFX HH 0 ogwalimukuzi .
PFX HH 0 ogwalimukuki .
PFX HH 0 ogwalimukubi .
PFX HH 0 ogwalimukuli .
PFX HH 0 ogwalimukuga .
PFX HH 0 ogwalimukuka .
PFX HH 0 ogwalimukubu .
PFX HH 0 ogwalimukulu .
PFX HH 0 ogwalimukuku .
PFX HH 0 ogwalimukutu .
PFX HH 0 gyalimukun [^lmn]
PFX HH l gyalimukund l.[^mn]
PFX HH l gyalimukunn l.[mn]
PFX HH w gyalimukump [w]
PFX HH 0 gyalimukumu .
PFX HH 0 gyalimukuba .
PFX HH 0 gyalimukugu .
PFX HH 0 gyalimukugi .
PFX HH 0 gyalimukuzi .
PFX HH 0 gyalimukuki .
PFX HH 0 gyalimukubi .
PFX HH 0 gyalimukuli .
PFX HH 0 gyalimukuga .
PFX HH 0 gyalimukuka .
PFX HH 0 gyalimukubu .
PFX HH 0 gyalimukulu .
PFX HH 0 gyalimukuku .
PFX HH 0 gyalimukutu .
PFX HH 0 egyalimukun [^lmn]
PFX HH l egyalimukund l.[^mn]
PFX HH l egyalimukunn l.[mn]
PFX HH w egyalimukump [w]
PFX HH 0 egyalimukumu .
PFX HH 0 egyalimukuba .
PFX HH 0 egyalimukugu .
PFX HH 0 egyalimukugi .
PFX HH 0 egyalimukuzi .
PFX HH 0 egyalimukuki .
PFX HH 0 egyalimukubi .
PFX HH 0 egyalimukuli .
PFX HH 0 egyalimukuga .
PFX HH 0 egyalimukuka .
PFX HH 0 egyalimukubu .
PFX HH 0 egyalimukulu .
PFX HH 0 egyalimukuku .
PFX HH 0 egyalimukutu .
PFX HH 0 zaalimukun [^lmn]
PFX HH l zaalimukund l.[^mn]
PFX HH l zaalimukunn l.[mn]
PFX HH w zaalimukump [w]
PFX HH 0 zaalimukumu .
PFX HH 0 zaalimukuba .
PFX HH 0 zaalimukugu .
PFX HH 0 zaalimukugi .
PFX HH 0 zaalimukuzi .
PFX HH 0 zaalimukuki .
PFX HH 0 zaalimukubi .
PFX HH 0 zaalimukuli .
PFX HH 0 zaalimukuga .
PFX HH 0 zaalimukuka .
PFX HH 0 zaalimukubu .
PFX HH 0 zaalimukulu .
PFX HH 0 zaalimukuku .
PFX HH 0 zaalimukutu .
PFX HH 0 ezaalimukun [^lmn]
PFX HH l ezaalimukund l.[^mn]
PFX HH l ezaalimukunn l.[mn]
PFX HH w ezaalimukump [w]
PFX HH 0 ezaalimukumu .
PFX HH 0 ezaalimukuba .
PFX HH 0 ezaalimukugu .
PFX HH 0 ezaalimukugi .
PFX HH 0 ezaalimukuzi .
PFX HH 0 ezaalimukuki .
PFX HH 0 ezaalimukubi .
PFX HH 0 ezaalimukuli .
PFX HH 0 ezaalimukuga .
PFX HH 0 ezaalimukuka .
PFX HH 0 ezaalimukubu .
PFX HH 0 ezaalimukulu .
PFX HH 0 ezaalimukuku .
PFX HH 0 ezaalimukutu .
PFX HH 0 kyalimukun [^lmn]
PFX HH l kyalimukund l.[^mn]
PFX HH l kyalimukunn l.[mn]
PFX HH w kyalimukump [w]
PFX HH 0 kyalimukumu .
PFX HH 0 kyalimukuba .
PFX HH 0 kyalimukugu .
PFX HH 0 kyalimukugi .
PFX HH 0 kyalimukuzi .
PFX HH 0 kyalimukuki .
PFX HH 0 kyalimukubi .
PFX HH 0 kyalimukuli .
PFX HH 0 kyalimukuga .
PFX HH 0 kyalimukuka .
PFX HH 0 kyalimukubu .
PFX HH 0 kyalimukulu .
PFX HH 0 kyalimukuku .
PFX HH 0 kyalimukutu .
PFX HH 0 ekyalimukun [^lmn]
PFX HH l ekyalimukund l.[^mn]
PFX HH l ekyalimukunn l.[mn]
PFX HH w ekyalimukump [w]
PFX HH 0 ekyalimukumu .
PFX HH 0 ekyalimukuba .
PFX HH 0 ekyalimukugu .
PFX HH 0 ekyalimukugi .
PFX HH 0 ekyalimukuzi .
PFX HH 0 ekyalimukuki .
PFX HH 0 ekyalimukubi .
PFX HH 0 ekyalimukuli .
PFX HH 0 ekyalimukuga .
PFX HH 0 ekyalimukuka .
PFX HH 0 ekyalimukubu .
PFX HH 0 ekyalimukulu .
PFX HH 0 ekyalimukuku .
PFX HH 0 ekyalimukutu .
PFX HH 0 byalimukun [^lmn]
PFX HH l byalimukund l.[^mn]
PFX HH l byalimukunn l.[mn]
PFX HH w byalimukump [w]
PFX HH 0 byalimukumu .
PFX HH 0 byalimukuba .
PFX HH 0 byalimukugu .
PFX HH 0 byalimukugi .
PFX HH 0 byalimukuzi .
PFX HH 0 byalimukuki .
PFX HH 0 byalimukubi .
PFX HH 0 byalimukuli .
PFX HH 0 byalimukuga .
PFX HH 0 byalimukuka .
PFX HH 0 byalimukubu .
PFX HH 0 byalimukulu .
PFX HH 0 byalimukuku .
PFX HH 0 byalimukutu .
PFX HH 0 ebyalimukun [^lmn]
PFX HH l ebyalimukund l.[^mn]
PFX HH l ebyalimukunn l.[mn]
PFX HH w ebyalimukump [w]
PFX HH 0 ebyalimukumu .
PFX HH 0 ebyalimukuba .
PFX HH 0 ebyalimukugu .
PFX HH 0 ebyalimukugi .
PFX HH 0 ebyalimukuzi .
PFX HH 0 ebyalimukuki .
PFX HH 0 ebyalimukubi .
PFX HH 0 ebyalimukuli .
PFX HH 0 ebyalimukuga .
PFX HH 0 ebyalimukuka .
PFX HH 0 ebyalimukubu .
PFX HH 0 ebyalimukulu .
PFX HH 0 ebyalimukuku .
PFX HH 0 ebyalimukutu .
PFX HH 0 lyalimukun [^lmn]
PFX HH l lyalimukund l.[^mn]
PFX HH l lyalimukunn l.[mn]
PFX HH w lyalimukump [w]
PFX HH 0 lyalimukumu .
PFX HH 0 lyalimukuba .
PFX HH 0 lyalimukugu .
PFX HH 0 lyalimukugi .
PFX HH 0 lyalimukuzi .
PFX HH 0 lyalimukuki .
PFX HH 0 lyalimukubi .
PFX HH 0 lyalimukuli .
PFX HH 0 lyalimukuga .
PFX HH 0 lyalimukuka .
PFX HH 0 lyalimukubu .
PFX HH 0 lyalimukulu .
PFX HH 0 lyalimukuku .
PFX HH 0 lyalimukutu .
PFX HH 0 elyalimukun [^lmn]
PFX HH l elyalimukund l.[^mn]
PFX HH l elyalimukunn l.[mn]
PFX HH w elyalimukump [w]
PFX HH 0 elyalimukumu .
PFX HH 0 elyalimukuba .
PFX HH 0 elyalimukugu .
PFX HH 0 elyalimukugi .
PFX HH 0 elyalimukuzi .
PFX HH 0 elyalimukuki .
PFX HH 0 elyalimukubi .
PFX HH 0 elyalimukuli .
PFX HH 0 elyalimukuga .
PFX HH 0 elyalimukuka .
PFX HH 0 elyalimukubu .
PFX HH 0 elyalimukulu .
PFX HH 0 elyalimukuku .
PFX HH 0 elyalimukutu .
PFX HH 0 gaalimukun [^lmn]
PFX HH l gaalimukund l.[^mn]
PFX HH l gaalimukunn l.[mn]
PFX HH w gaalimukump [w]
PFX HH 0 gaalimukumu .
PFX HH 0 gaalimukuba .
PFX HH 0 gaalimukugu .
PFX HH 0 gaalimukugi .
PFX HH 0 gaalimukuzi .
PFX HH 0 gaalimukuki .
PFX HH 0 gaalimukubi .
PFX HH 0 gaalimukuli .
PFX HH 0 gaalimukuga .
PFX HH 0 gaalimukuka .
PFX HH 0 gaalimukubu .
PFX HH 0 gaalimukulu .
PFX HH 0 gaalimukuku .
PFX HH 0 gaalimukutu .
PFX HH 0 ogwalimukun [^lmn]
PFX HH l ogwalimukund l.[^mn]
PFX HH l ogwalimukunn l.[mn]
PFX HH w ogwalimukump [w]
PFX HH 0 ogwalimukumu .
PFX HH 0 ogwalimukuba .
PFX HH 0 ogwalimukugu .
PFX HH 0 ogwalimukugi .
PFX HH 0 ogwalimukuzi .
PFX HH 0 ogwalimukuki .
PFX HH 0 ogwalimukubi .
PFX HH 0 ogwalimukuli .
PFX HH 0 ogwalimukuga .
PFX HH 0 ogwalimukuka .
PFX HH 0 ogwalimukubu .
PFX HH 0 ogwalimukulu .
PFX HH 0 ogwalimukuku .
PFX HH 0 ogwalimukutu .
PFX HH 0 kaalimukun [^lmn]
PFX HH l kaalimukund l.[^mn]
PFX HH l kaalimukunn l.[mn]
PFX HH w kaalimukump [w]
PFX HH 0 kaalimukumu .
PFX HH 0 kaalimukuba .
PFX HH 0 kaalimukugu .
PFX HH 0 kaalimukugi .
PFX HH 0 kaalimukuzi .
PFX HH 0 kaalimukuki .
PFX HH 0 kaalimukubi .
PFX HH 0 kaalimukuli .
PFX HH 0 kaalimukuga .
PFX HH 0 kaalimukuka .
PFX HH 0 kaalimukubu .
PFX HH 0 kaalimukulu .
PFX HH 0 kaalimukuku .
PFX HH 0 kaalimukutu .
PFX HH 0 akaalimukun [^lmn]
PFX HH l akaalimukund l.[^mn]
PFX HH l akaalimukunn l.[mn]
PFX HH w akaalimukump [w]
PFX HH 0 akaalimukumu .
PFX HH 0 akaalimukuba .
PFX HH 0 akaalimukugu .
PFX HH 0 akaalimukugi .
PFX HH 0 akaalimukuzi .
PFX HH 0 akaalimukuki .
PFX HH 0 akaalimukubi .
PFX HH 0 akaalimukuli .
PFX HH 0 akaalimukuga .
PFX HH 0 akaalimukuka .
PFX HH 0 akaalimukubu .
PFX HH 0 akaalimukulu .
PFX HH 0 akaalimukuku .
PFX HH 0 akaalimukutu .
PFX HH 0 bwalimukun [^lmn]
PFX HH l bwalimukund l.[^mn]
PFX HH l bwalimukunn l.[mn]
PFX HH w bwalimukump [w]
PFX HH 0 bwalimukumu .
PFX HH 0 bwalimukuba .
PFX HH 0 bwalimukugu .
PFX HH 0 bwalimukugi .
PFX HH 0 bwalimukuzi .
PFX HH 0 bwalimukuki .
PFX HH 0 bwalimukubi .
PFX HH 0 bwalimukuli .
PFX HH 0 bwalimukuga .
PFX HH 0 bwalimukuka .
PFX HH 0 bwalimukubu .
PFX HH 0 bwalimukulu .
PFX HH 0 bwalimukuku .
PFX HH 0 bwalimukutu .
PFX HH 0 obwalimukun [^lmn]
PFX HH l obwalimukund l.[^mn]
PFX HH l obwalimukunn l.[mn]
PFX HH w obwalimukump [w]
PFX HH 0 obwalimukumu .
PFX HH 0 obwalimukuba .
PFX HH 0 obwalimukugu .
PFX HH 0 obwalimukugi .
PFX HH 0 obwalimukuzi .
PFX HH 0 obwalimukuki .
PFX HH 0 obwalimukubi .
PFX HH 0 obwalimukuli .
PFX HH 0 obwalimukuga .
PFX HH 0 obwalimukuka .
PFX HH 0 obwalimukubu .
PFX HH 0 obwalimukulu .
PFX HH 0 obwalimukuku .
PFX HH 0 obwalimukutu .
PFX HH 0 lwaalimukun [^lmn]
PFX HH l lwaalimukund l.[^mn]
PFX HH l lwaalimukunn l.[mn]
PFX HH w lwaalimukump [w]
PFX HH 0 lwaalimukumu .
PFX HH 0 lwaalimukuba .
PFX HH 0 lwaalimukugu .
PFX HH 0 lwaalimukugi .
PFX HH 0 lwaalimukuzi .
PFX HH 0 lwaalimukuki .
PFX HH 0 lwaalimukubi .
PFX HH 0 lwaalimukuli .
PFX HH 0 lwaalimukuga .
PFX HH 0 lwaalimukuka .
PFX HH 0 lwaalimukubu .
PFX HH 0 lwaalimukulu .
PFX HH 0 lwaalimukuku .
PFX HH 0 lwaalimukutu .
PFX HH 0 olwaalimukun [^lmn]
PFX HH l olwaalimukund l.[^mn]
PFX HH l olwaalimukunn l.[mn]
PFX HH w olwaalimukump [w]
PFX HH 0 olwaalimukumu .
PFX HH 0 olwaalimukuba .
PFX HH 0 olwaalimukugu .
PFX HH 0 olwaalimukugi .
PFX HH 0 olwaalimukuzi .
PFX HH 0 olwaalimukuki .
PFX HH 0 olwaalimukubi .
PFX HH 0 olwaalimukuli .
PFX HH 0 olwaalimukuga .
PFX HH 0 olwaalimukuka .
PFX HH 0 olwaalimukubu .
PFX HH 0 olwaalimukulu .
PFX HH 0 olwaalimukuku .
PFX HH 0 olwaalimukutu .
PFX HH 0 zaalimukun [^lmn]
PFX HH l zaalimukund l.[^mn]
PFX HH l zaalimukunn l.[mn]
PFX HH w zaalimukump [w]
PFX HH 0 zaalimukumu .
PFX HH 0 zaalimukuba .
PFX HH 0 zaalimukugu .
PFX HH 0 zaalimukugi .
PFX HH 0 zaalimukuzi .
PFX HH 0 zaalimukuki .
PFX HH 0 zaalimukubi .
PFX HH 0 zaalimukuli .
PFX HH 0 zaalimukuga .
PFX HH 0 zaalimukuka .
PFX HH 0 zaalimukubu .
PFX HH 0 zaalimukulu .
PFX HH 0 zaalimukuku .
PFX HH 0 zaalimukutu .
PFX HH 0 ezaalimukun [^lmn]
PFX HH l ezaalimukund l.[^mn]
PFX HH l ezaalimukunn l.[mn]
PFX HH w ezaalimukump [w]
PFX HH 0 ezaalimukumu .
PFX HH 0 ezaalimukuba .
PFX HH 0 ezaalimukugu .
PFX HH 0 ezaalimukugi .
PFX HH 0 ezaalimukuzi .
PFX HH 0 ezaalimukuki .
PFX HH 0 ezaalimukubi .
PFX HH 0 ezaalimukuli .
PFX HH 0 ezaalimukuga .
PFX HH 0 ezaalimukuka .
PFX HH 0 ezaalimukubu .
PFX HH 0 ezaalimukulu .
PFX HH 0 ezaalimukuku .
PFX HH 0 ezaalimukutu .
PFX HH 0 kwaalimukun [^lmn]
PFX HH l kwaalimukund l.[^mn]
PFX HH l kwaalimukunn l.[mn]
PFX HH w kwaalimukump [w]
PFX HH 0 kwaalimukumu .
PFX HH 0 kwaalimukuba .
PFX HH 0 kwaalimukugu .
PFX HH 0 kwaalimukugi .
PFX HH 0 kwaalimukuzi .
PFX HH 0 kwaalimukuki .
PFX HH 0 kwaalimukubi .
PFX HH 0 kwaalimukuli .
PFX HH 0 kwaalimukuga .
PFX HH 0 kwaalimukuka .
PFX HH 0 kwaalimukubu .
PFX HH 0 kwaalimukulu .
PFX HH 0 kwaalimukuku .
PFX HH 0 kwaalimukutu .
PFX HH 0 okwaalimukun [^lmn]
PFX HH l okwaalimukund l.[^mn]
PFX HH l okwaalimukunn l.[mn]
PFX HH w okwaalimukump [w]
PFX HH 0 okwaalimukumu .
PFX HH 0 okwaalimukuba .
PFX HH 0 okwaalimukugu .
PFX HH 0 okwaalimukugi .
PFX HH 0 okwaalimukuzi .
PFX HH 0 okwaalimukuki .
PFX HH 0 okwaalimukubi .
PFX HH 0 okwaalimukuli .
PFX HH 0 okwaalimukuga .
PFX HH 0 okwaalimukuka .
PFX HH 0 okwaalimukubu .
PFX HH 0 okwaalimukulu .
PFX HH 0 okwaalimukuku .
PFX HH 0 okwaalimukutu .
PFX HH 0 gaalimukun [^lmn]
PFX HH l gaalimukund l.[^mn]
PFX HH l gaalimukunn l.[mn]
PFX HH w gaalimukump [w]
PFX HH 0 gaalimukumu .
PFX HH 0 gaalimukuba .
PFX HH 0 gaalimukugu .
PFX HH 0 gaalimukugi .
PFX HH 0 gaalimukuzi .
PFX HH 0 gaalimukuki .
PFX HH 0 gaalimukubi .
PFX HH 0 gaalimukuli .
PFX HH 0 gaalimukuga .
PFX HH 0 gaalimukuka .
PFX HH 0 gaalimukubu .
PFX HH 0 gaalimukulu .
PFX HH 0 gaalimukuku .
PFX HH 0 gaalimukutu .
PFX HH 0 agaalimukun [^lmn]
PFX HH l agaalimukund l.[^mn]
PFX HH l agaalimukunn l.[mn]
PFX HH w agaalimukump [w]
PFX HH 0 agaalimukumu .
PFX HH 0 agaalimukuba .
PFX HH 0 agaalimukugu .
PFX HH 0 agaalimukugi .
PFX HH 0 agaalimukuzi .
PFX HH 0 agaalimukuki .
PFX HH 0 agaalimukubi .
PFX HH 0 agaalimukuli .
PFX HH 0 agaalimukuga .
PFX HH 0 agaalimukuka .
PFX HH 0 agaalimukubu .
PFX HH 0 agaalimukulu .
PFX HH 0 agaalimukuku .
PFX HH 0 agaalimukutu .
PFX HH 0 twalimukun [^lmn]
PFX HH l twalimukund l.[^mn]
PFX HH l twalimukunn l.[mn]
PFX HH w twalimukump [w]
PFX HH 0 twalimukumu .
PFX HH 0 twalimukuba .
PFX HH 0 twalimukugu .
PFX HH 0 twalimukugi .
PFX HH 0 twalimukuzi .
PFX HH 0 twalimukuki .
PFX HH 0 twalimukubi .
PFX HH 0 twalimukuli .
PFX HH 0 twalimukuga .
PFX HH 0 twalimukuka .
PFX HH 0 twalimukubu .
PFX HH 0 twalimukulu .
PFX HH 0 twalimukuku .
PFX HH 0 twalimukutu .
PFX HH 0 otwalimukun [^lmn]
PFX HH l otwalimukund l.[^mn]
PFX HH l otwalimukunn l.[mn]
PFX HH w otwalimukump [w]
PFX HH 0 otwalimukumu .
PFX HH 0 otwalimukuba .
PFX HH 0 otwalimukugu .
PFX HH 0 otwalimukugi .
PFX HH 0 otwalimukuzi .
PFX HH 0 otwalimukuki .
PFX HH 0 otwalimukubi .
PFX HH 0 otwalimukuli .
PFX HH 0 otwalimukuga .
PFX HH 0 otwalimukuka .
PFX HH 0 otwalimukubu .
PFX HH 0 otwalimukulu .
PFX HH 0 otwalimukuku .
PFX HH 0 otwalimukutu ."""

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
    "HH": "HH",
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

    out_flag = "IS"
    left_desc = FLAG_DESCRIPTIONS.get("HH", "HH")
    right_desc = FLAG_DESCRIPTIONS.get("Ob", "Ob")
    comment_line = "# Cross product of {} ({}) and {} ({}) to {}".format(
        "HH", left_desc, "Ob", right_desc, out_flag
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
