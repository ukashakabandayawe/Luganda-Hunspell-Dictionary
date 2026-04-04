import re
import os
from pathlib import Path

# Cross product generator: vv x OR => IT
# Description:
# - Left block `vv`: vv
# - Right block `OR`: Special reflexive object markers
# - Output flag `IT`: Cross-product prefixes for vv x OR

REPO_ROOT = Path(__file__).resolve().parents[1]
AFF_FILE = REPO_ROOT / "Luganda.aff"

# If set to a flag name (e.g. "HB"), the generated cross-product block will be inserted
# immediately before the first "PFX <flag>" line when the output flag block doesn't
# already exist in the .aff.
INSERT_BEFORE_FLAG = "".strip() or None

rule_left_raw = """
PFX vv Y 644
PFX vv 0 nnaakamu .
PFX vv 0 nnaakaba .
PFX vv 0 nnaakagu .
PFX vv 0 nnaakagi .
PFX vv 0 nnaakazi .
PFX vv 0 nnaakaki .
PFX vv 0 nnaakabi .
PFX vv 0 nnaakali .
PFX vv 0 nnaakaga .
PFX vv 0 nnaakaka .
PFX vv 0 nnaakabu .
PFX vv 0 nnaakalu .
PFX vv 0 nnaakaku .
PFX vv 0 nnaakatu .
PFX vv 0 waakan [^lmn]
PFX vv l waakand l.[^mn]
PFX vv l waakann l.[mn]
PFX vv w waakamp [w]
PFX vv 0 waakamu .
PFX vv 0 waakaba .
PFX vv 0 waakagu .
PFX vv 0 waakagi .
PFX vv 0 waakazi .
PFX vv 0 waakaki .
PFX vv 0 waakabi .
PFX vv 0 waakali .
PFX vv 0 waakaga .
PFX vv 0 waakaka .
PFX vv 0 waakabu .
PFX vv 0 waakalu .
PFX vv 0 waakaku .
PFX vv 0 waakatu .
PFX vv 0 yaakan [^lmn]
PFX vv l yaakand l.[^mn]
PFX vv l yaakann l.[mn]
PFX vv w yaakamp [w]
PFX vv 0 yaakamu .
PFX vv 0 yaakaba .
PFX vv 0 yaakagu .
PFX vv 0 yaakagi .
PFX vv 0 yaakazi .
PFX vv 0 yaakaki .
PFX vv 0 yaakabi .
PFX vv 0 yaakali .
PFX vv 0 yaakaga .
PFX vv 0 yaakaka .
PFX vv 0 yaakabu .
PFX vv 0 yaakalu .
PFX vv 0 yaakaku .
PFX vv 0 yaakatu .
PFX vv 0 eyaakan [^lmn]
PFX vv l eyaakand l.[^mn]
PFX vv l eyaakann l.[mn]
PFX vv w eyaakamp [w]
PFX vv 0 eyaakamu .
PFX vv 0 eyaakaba .
PFX vv 0 eyaakagu .
PFX vv 0 eyaakagi .
PFX vv 0 eyaakazi .
PFX vv 0 eyaakaki .
PFX vv 0 eyaakabi .
PFX vv 0 eyaakali .
PFX vv 0 eyaakaga .
PFX vv 0 eyaakaka .
PFX vv 0 eyaakabu .
PFX vv 0 eyaakalu .
PFX vv 0 eyaakaku .
PFX vv 0 eyaakatu .
PFX vv 0 twakan [^lmn]
PFX vv l twakand l.[^mn]
PFX vv l twakann l.[mn]
PFX vv w twakamp [w]
PFX vv 0 twakamu .
PFX vv 0 twakaba .
PFX vv 0 twakagu .
PFX vv 0 twakagi .
PFX vv 0 twakazi .
PFX vv 0 twakaki .
PFX vv 0 twakabi .
PFX vv 0 twakali .
PFX vv 0 twakaga .
PFX vv 0 twakaka .
PFX vv 0 twakabu .
PFX vv 0 twakalu .
PFX vv 0 twakaku .
PFX vv 0 twakatu .
PFX vv 0 mwakan [^lmn]
PFX vv l mwakand l.[^mn]
PFX vv l mwakann l.[mn]
PFX vv w mwakamp [w]
PFX vv 0 mwakamu .
PFX vv 0 mwakaba .
PFX vv 0 mwakagu .
PFX vv 0 mwakagi .
PFX vv 0 mwakazi .
PFX vv 0 mwakaki .
PFX vv 0 mwakabi .
PFX vv 0 mwakali .
PFX vv 0 mwakaga .
PFX vv 0 mwakaka .
PFX vv 0 mwakabu .
PFX vv 0 mwakalu .
PFX vv 0 mwakaku .
PFX vv 0 mwakatu .
PFX vv 0 baakan [^lmn]
PFX vv l baakand l.[^mn]
PFX vv l baakann l.[mn]
PFX vv w baakamp [w]
PFX vv 0 baakamu .
PFX vv 0 baakaba .
PFX vv 0 baakagu .
PFX vv 0 baakagi .
PFX vv 0 baakazi .
PFX vv 0 baakaki .
PFX vv 0 baakabi .
PFX vv 0 baakali .
PFX vv 0 baakaga .
PFX vv 0 baakaka .
PFX vv 0 baakabu .
PFX vv 0 baakalu .
PFX vv 0 baakaku .
PFX vv 0 baakatu .
PFX vv 0 abaakan [^lmn]
PFX vv l abaakand l.[^mn]
PFX vv l abaakann l.[mn]
PFX vv w abaakamp [w]
PFX vv 0 abaakamu .
PFX vv 0 abaakaba .
PFX vv 0 abaakagu .
PFX vv 0 abaakagi .
PFX vv 0 abaakazi .
PFX vv 0 abaakaki .
PFX vv 0 abaakabi .
PFX vv 0 abaakali .
PFX vv 0 abaakaga .
PFX vv 0 abaakaka .
PFX vv 0 abaakabu .
PFX vv 0 abaakalu .
PFX vv 0 abaakaku .
PFX vv 0 abaakatu .
PFX vv 0 gwakan [^lmn]
PFX vv l gwakand l.[^mn]
PFX vv l gwakann l.[mn]
PFX vv w gwakamp [w]
PFX vv 0 gwakamu .
PFX vv 0 gwakaba .
PFX vv 0 gwakagu .
PFX vv 0 gwakagi .
PFX vv 0 gwakazi .
PFX vv 0 gwakaki .
PFX vv 0 gwakabi .
PFX vv 0 gwakali .
PFX vv 0 gwakaga .
PFX vv 0 gwakaka .
PFX vv 0 gwakabu .
PFX vv 0 gwakalu .
PFX vv 0 gwakaku .
PFX vv 0 gwakatu .
PFX vv 0 ogwakan [^lmn]
PFX vv l ogwakand l.[^mn]
PFX vv l ogwakann l.[mn]
PFX vv w ogwakamp [w]
PFX vv 0 ogwakamu .
PFX vv 0 ogwakaba .
PFX vv 0 ogwakagu .
PFX vv 0 ogwakagi .
PFX vv 0 ogwakazi .
PFX vv 0 ogwakaki .
PFX vv 0 ogwakabi .
PFX vv 0 ogwakali .
PFX vv 0 ogwakaga .
PFX vv 0 ogwakaka .
PFX vv 0 ogwakabu .
PFX vv 0 ogwakalu .
PFX vv 0 ogwakaku .
PFX vv 0 ogwakatu .
PFX vv 0 gyakan [^lmn]
PFX vv l gyakand l.[^mn]
PFX vv l gyakann l.[mn]
PFX vv w gyakamp [w]
PFX vv 0 gyakamu .
PFX vv 0 gyakaba .
PFX vv 0 gyakagu .
PFX vv 0 gyakagi .
PFX vv 0 gyakazi .
PFX vv 0 gyakaki .
PFX vv 0 gyakabi .
PFX vv 0 gyakali .
PFX vv 0 gyakaga .
PFX vv 0 gyakaka .
PFX vv 0 gyakabu .
PFX vv 0 gyakalu .
PFX vv 0 gyakaku .
PFX vv 0 gyakatu .
PFX vv 0 egyakan [^lmn]
PFX vv l egyakand l.[^mn]
PFX vv l egyakann l.[mn]
PFX vv w egyakamp [w]
PFX vv 0 egyakamu .
PFX vv 0 egyakaba .
PFX vv 0 egyakagu .
PFX vv 0 egyakagi .
PFX vv 0 egyakazi .
PFX vv 0 egyakaki .
PFX vv 0 egyakabi .
PFX vv 0 egyakali .
PFX vv 0 egyakaga .
PFX vv 0 egyakaka .
PFX vv 0 egyakabu .
PFX vv 0 egyakalu .
PFX vv 0 egyakaku .
PFX vv 0 egyakatu .
PFX vv 0 zaakan [^lmn]
PFX vv l zaakand l.[^mn]
PFX vv l zaakann l.[mn]
PFX vv w zaakamp [w]
PFX vv 0 zaakamu .
PFX vv 0 zaakaba .
PFX vv 0 zaakagu .
PFX vv 0 zaakagi .
PFX vv 0 zaakazi .
PFX vv 0 zaakaki .
PFX vv 0 zaakabi .
PFX vv 0 zaakali .
PFX vv 0 zaakaga .
PFX vv 0 zaakaka .
PFX vv 0 zaakabu .
PFX vv 0 zaakalu .
PFX vv 0 zaakaku .
PFX vv 0 zaakatu .
PFX vv 0 ezaakan [^lmn]
PFX vv l ezaakand l.[^mn]
PFX vv l ezaakann l.[mn]
PFX vv w ezaakamp [w]
PFX vv 0 ezaakamu .
PFX vv 0 ezaakaba .
PFX vv 0 ezaakagu .
PFX vv 0 ezaakagi .
PFX vv 0 ezaakazi .
PFX vv 0 ezaakaki .
PFX vv 0 ezaakabi .
PFX vv 0 ezaakali .
PFX vv 0 ezaakaga .
PFX vv 0 ezaakaka .
PFX vv 0 ezaakabu .
PFX vv 0 ezaakalu .
PFX vv 0 ezaakaku .
PFX vv 0 ezaakatu .
PFX vv 0 kyakan [^lmn]
PFX vv l kyakand l.[^mn]
PFX vv l kyakann l.[mn]
PFX vv w kyakamp [w]
PFX vv 0 kyakamu .
PFX vv 0 kyakaba .
PFX vv 0 kyakagu .
PFX vv 0 kyakagi .
PFX vv 0 kyakazi .
PFX vv 0 kyakaki .
PFX vv 0 kyakabi .
PFX vv 0 kyakali .
PFX vv 0 kyakaga .
PFX vv 0 kyakaka .
PFX vv 0 kyakabu .
PFX vv 0 kyakalu .
PFX vv 0 kyakaku .
PFX vv 0 kyakatu .
PFX vv 0 ekyakan [^lmn]
PFX vv l ekyakand l.[^mn]
PFX vv l ekyakann l.[mn]
PFX vv w ekyakamp [w]
PFX vv 0 ekyakamu .
PFX vv 0 ekyakaba .
PFX vv 0 ekyakagu .
PFX vv 0 ekyakagi .
PFX vv 0 ekyakazi .
PFX vv 0 ekyakaki .
PFX vv 0 ekyakabi .
PFX vv 0 ekyakali .
PFX vv 0 ekyakaga .
PFX vv 0 ekyakaka .
PFX vv 0 ekyakabu .
PFX vv 0 ekyakalu .
PFX vv 0 ekyakaku .
PFX vv 0 ekyakatu .
PFX vv 0 byakan [^lmn]
PFX vv l byakand l.[^mn]
PFX vv l byakann l.[mn]
PFX vv w byakamp [w]
PFX vv 0 byakamu .
PFX vv 0 byakaba .
PFX vv 0 byakagu .
PFX vv 0 byakagi .
PFX vv 0 byakazi .
PFX vv 0 byakaki .
PFX vv 0 byakabi .
PFX vv 0 byakali .
PFX vv 0 byakaga .
PFX vv 0 byakaka .
PFX vv 0 byakabu .
PFX vv 0 byakalu .
PFX vv 0 byakaku .
PFX vv 0 byakatu .
PFX vv 0 ebyakan [^lmn]
PFX vv l ebyakand l.[^mn]
PFX vv l ebyakann l.[mn]
PFX vv w ebyakamp [w]
PFX vv 0 ebyakamu .
PFX vv 0 ebyakaba .
PFX vv 0 ebyakagu .
PFX vv 0 ebyakagi .
PFX vv 0 ebyakazi .
PFX vv 0 ebyakaki .
PFX vv 0 ebyakabi .
PFX vv 0 ebyakali .
PFX vv 0 ebyakaga .
PFX vv 0 ebyakaka .
PFX vv 0 ebyakabu .
PFX vv 0 ebyakalu .
PFX vv 0 ebyakaku .
PFX vv 0 ebyakatu .
PFX vv 0 lyakan [^lmn]
PFX vv l lyakand l.[^mn]
PFX vv l lyakann l.[mn]
PFX vv w lyakamp [w]
PFX vv 0 lyakamu .
PFX vv 0 lyakaba .
PFX vv 0 lyakagu .
PFX vv 0 lyakagi .
PFX vv 0 lyakazi .
PFX vv 0 lyakaki .
PFX vv 0 lyakabi .
PFX vv 0 lyakali .
PFX vv 0 lyakaga .
PFX vv 0 lyakaka .
PFX vv 0 lyakabu .
PFX vv 0 lyakalu .
PFX vv 0 lyakaku .
PFX vv 0 lyakatu .
PFX vv 0 elyakan [^lmn]
PFX vv l elyakand l.[^mn]
PFX vv l elyakann l.[mn]
PFX vv w elyakamp [w]
PFX vv 0 elyakamu .
PFX vv 0 elyakaba .
PFX vv 0 elyakagu .
PFX vv 0 elyakagi .
PFX vv 0 elyakazi .
PFX vv 0 elyakaki .
PFX vv 0 elyakabi .
PFX vv 0 elyakali .
PFX vv 0 elyakaga .
PFX vv 0 elyakaka .
PFX vv 0 elyakabu .
PFX vv 0 elyakalu .
PFX vv 0 elyakaku .
PFX vv 0 elyakatu .
PFX vv 0 gaakan [^lmn]
PFX vv l gaakand l.[^mn]
PFX vv l gaakann l.[mn]
PFX vv w gaakamp [w]
PFX vv 0 gaakamu .
PFX vv 0 gaakaba .
PFX vv 0 gaakagu .
PFX vv 0 gaakagi .
PFX vv 0 gaakazi .
PFX vv 0 gaakaki .
PFX vv 0 gaakabi .
PFX vv 0 gaakali .
PFX vv 0 gaakaga .
PFX vv 0 gaakaka .
PFX vv 0 gaakabu .
PFX vv 0 gaakalu .
PFX vv 0 gaakaku .
PFX vv 0 gaakatu .
PFX vv 0 ogwakan [^lmn]
PFX vv l ogwakand l.[^mn]
PFX vv l ogwakann l.[mn]
PFX vv w ogwakamp [w]
PFX vv 0 ogwakamu .
PFX vv 0 ogwakaba .
PFX vv 0 ogwakagu .
PFX vv 0 ogwakagi .
PFX vv 0 ogwakazi .
PFX vv 0 ogwakaki .
PFX vv 0 ogwakabi .
PFX vv 0 ogwakali .
PFX vv 0 ogwakaga .
PFX vv 0 ogwakaka .
PFX vv 0 ogwakabu .
PFX vv 0 ogwakalu .
PFX vv 0 ogwakaku .
PFX vv 0 ogwakatu .
PFX vv 0 kaakan [^lmn]
PFX vv l kaakand l.[^mn]
PFX vv l kaakann l.[mn]
PFX vv w kaakamp [w]
PFX vv 0 kaakamu .
PFX vv 0 kaakaba .
PFX vv 0 kaakagu .
PFX vv 0 kaakagi .
PFX vv 0 kaakazi .
PFX vv 0 kaakaki .
PFX vv 0 kaakabi .
PFX vv 0 kaakali .
PFX vv 0 kaakaga .
PFX vv 0 kaakaka .
PFX vv 0 kaakabu .
PFX vv 0 kaakalu .
PFX vv 0 kaakaku .
PFX vv 0 kaakatu .
PFX vv 0 akaakan [^lmn]
PFX vv l akaakand l.[^mn]
PFX vv l akaakann l.[mn]
PFX vv w akaakamp [w]
PFX vv 0 akaakamu .
PFX vv 0 akaakaba .
PFX vv 0 akaakagu .
PFX vv 0 akaakagi .
PFX vv 0 akaakazi .
PFX vv 0 akaakaki .
PFX vv 0 akaakabi .
PFX vv 0 akaakali .
PFX vv 0 akaakaga .
PFX vv 0 akaakaka .
PFX vv 0 akaakabu .
PFX vv 0 akaakalu .
PFX vv 0 akaakaku .
PFX vv 0 akaakatu .
PFX vv 0 bwakan [^lmn]
PFX vv l bwakand l.[^mn]
PFX vv l bwakann l.[mn]
PFX vv w bwakamp [w]
PFX vv 0 bwakamu .
PFX vv 0 bwakaba .
PFX vv 0 bwakagu .
PFX vv 0 bwakagi .
PFX vv 0 bwakazi .
PFX vv 0 bwakaki .
PFX vv 0 bwakabi .
PFX vv 0 bwakali .
PFX vv 0 bwakaga .
PFX vv 0 bwakaka .
PFX vv 0 bwakabu .
PFX vv 0 bwakalu .
PFX vv 0 bwakaku .
PFX vv 0 bwakatu .
PFX vv 0 obwakan [^lmn]
PFX vv l obwakand l.[^mn]
PFX vv l obwakann l.[mn]
PFX vv w obwakamp [w]
PFX vv 0 obwakamu .
PFX vv 0 obwakaba .
PFX vv 0 obwakagu .
PFX vv 0 obwakagi .
PFX vv 0 obwakazi .
PFX vv 0 obwakaki .
PFX vv 0 obwakabi .
PFX vv 0 obwakali .
PFX vv 0 obwakaga .
PFX vv 0 obwakaka .
PFX vv 0 obwakabu .
PFX vv 0 obwakalu .
PFX vv 0 obwakaku .
PFX vv 0 obwakatu .
PFX vv 0 lwaakan [^lmn]
PFX vv l lwaakand l.[^mn]
PFX vv l lwaakann l.[mn]
PFX vv w lwaakamp [w]
PFX vv 0 lwaakamu .
PFX vv 0 lwaakaba .
PFX vv 0 lwaakagu .
PFX vv 0 lwaakagi .
PFX vv 0 lwaakazi .
PFX vv 0 lwaakaki .
PFX vv 0 lwaakabi .
PFX vv 0 lwaakali .
PFX vv 0 lwaakaga .
PFX vv 0 lwaakaka .
PFX vv 0 lwaakabu .
PFX vv 0 lwaakalu .
PFX vv 0 lwaakaku .
PFX vv 0 lwaakatu .
PFX vv 0 olwaakan [^lmn]
PFX vv l olwaakand l.[^mn]
PFX vv l olwaakann l.[mn]
PFX vv w olwaakamp [w]
PFX vv 0 olwaakamu .
PFX vv 0 olwaakaba .
PFX vv 0 olwaakagu .
PFX vv 0 olwaakagi .
PFX vv 0 olwaakazi .
PFX vv 0 olwaakaki .
PFX vv 0 olwaakabi .
PFX vv 0 olwaakali .
PFX vv 0 olwaakaga .
PFX vv 0 olwaakaka .
PFX vv 0 olwaakabu .
PFX vv 0 olwaakalu .
PFX vv 0 olwaakaku .
PFX vv 0 olwaakatu .
PFX vv 0 zaakan [^lmn]
PFX vv l zaakand l.[^mn]
PFX vv l zaakann l.[mn]
PFX vv w zaakamp [w]
PFX vv 0 zaakamu .
PFX vv 0 zaakaba .
PFX vv 0 zaakagu .
PFX vv 0 zaakagi .
PFX vv 0 zaakazi .
PFX vv 0 zaakaki .
PFX vv 0 zaakabi .
PFX vv 0 zaakali .
PFX vv 0 zaakaga .
PFX vv 0 zaakaka .
PFX vv 0 zaakabu .
PFX vv 0 zaakalu .
PFX vv 0 zaakaku .
PFX vv 0 zaakatu .
PFX vv 0 ezaakan [^lmn]
PFX vv l ezaakand l.[^mn]
PFX vv l ezaakann l.[mn]
PFX vv w ezaakamp [w]
PFX vv 0 ezaakamu .
PFX vv 0 ezaakaba .
PFX vv 0 ezaakagu .
PFX vv 0 ezaakagi .
PFX vv 0 ezaakazi .
PFX vv 0 ezaakaki .
PFX vv 0 ezaakabi .
PFX vv 0 ezaakali .
PFX vv 0 ezaakaga .
PFX vv 0 ezaakaka .
PFX vv 0 ezaakabu .
PFX vv 0 ezaakalu .
PFX vv 0 ezaakaku .
PFX vv 0 ezaakatu .
PFX vv 0 kwaakan [^lmn]
PFX vv l kwaakand l.[^mn]
PFX vv l kwaakann l.[mn]
PFX vv w kwaakamp [w]
PFX vv 0 kwaakamu .
PFX vv 0 kwaakaba .
PFX vv 0 kwaakagu .
PFX vv 0 kwaakagi .
PFX vv 0 kwaakazi .
PFX vv 0 kwaakaki .
PFX vv 0 kwaakabi .
PFX vv 0 kwaakali .
PFX vv 0 kwaakaga .
PFX vv 0 kwaakaka .
PFX vv 0 kwaakabu .
PFX vv 0 kwaakalu .
PFX vv 0 kwaakaku .
PFX vv 0 kwaakatu .
PFX vv 0 okwaakan [^lmn]
PFX vv l okwaakand l.[^mn]
PFX vv l okwaakann l.[mn]
PFX vv w okwaakamp [w]
PFX vv 0 okwaakamu .
PFX vv 0 okwaakaba .
PFX vv 0 okwaakagu .
PFX vv 0 okwaakagi .
PFX vv 0 okwaakazi .
PFX vv 0 okwaakaki .
PFX vv 0 okwaakabi .
PFX vv 0 okwaakali .
PFX vv 0 okwaakaga .
PFX vv 0 okwaakaka .
PFX vv 0 okwaakabu .
PFX vv 0 okwaakalu .
PFX vv 0 okwaakaku .
PFX vv 0 okwaakatu .
PFX vv 0 gaakan [^lmn]
PFX vv l gaakand l.[^mn]
PFX vv l gaakann l.[mn]
PFX vv w gaakamp [w]
PFX vv 0 gaakamu .
PFX vv 0 gaakaba .
PFX vv 0 gaakagu .
PFX vv 0 gaakagi .
PFX vv 0 gaakazi .
PFX vv 0 gaakaki .
PFX vv 0 gaakabi .
PFX vv 0 gaakali .
PFX vv 0 gaakaga .
PFX vv 0 gaakaka .
PFX vv 0 gaakabu .
PFX vv 0 gaakalu .
PFX vv 0 gaakaku .
PFX vv 0 gaakatu .
PFX vv 0 agaakan [^lmn]
PFX vv l agaakand l.[^mn]
PFX vv l agaakann l.[mn]
PFX vv w agaakamp [w]
PFX vv 0 agaakamu .
PFX vv 0 agaakaba .
PFX vv 0 agaakagu .
PFX vv 0 agaakagi .
PFX vv 0 agaakazi .
PFX vv 0 agaakaki .
PFX vv 0 agaakabi .
PFX vv 0 agaakali .
PFX vv 0 agaakaga .
PFX vv 0 agaakaka .
PFX vv 0 agaakabu .
PFX vv 0 agaakalu .
PFX vv 0 agaakaku .
PFX vv 0 agaakatu .
PFX vv 0 twakan [^lmn]
PFX vv l twakand l.[^mn]
PFX vv l twakann l.[mn]
PFX vv w twakamp [w]
PFX vv 0 twakamu .
PFX vv 0 twakaba .
PFX vv 0 twakagu .
PFX vv 0 twakagi .
PFX vv 0 twakazi .
PFX vv 0 twakaki .
PFX vv 0 twakabi .
PFX vv 0 twakali .
PFX vv 0 twakaga .
PFX vv 0 twakaka .
PFX vv 0 twakabu .
PFX vv 0 twakalu .
PFX vv 0 twakaku .
PFX vv 0 twakatu .
PFX vv 0 otwakan [^lmn]
PFX vv l otwakand l.[^mn]
PFX vv l otwakann l.[mn]
PFX vv w otwakamp [w]
PFX vv 0 otwakamu .
PFX vv 0 otwakaba .
PFX vv 0 otwakagu .
PFX vv 0 otwakagi .
PFX vv 0 otwakazi .
PFX vv 0 otwakaki .
PFX vv 0 otwakabi .
PFX vv 0 otwakali .
PFX vv 0 otwakaga .
PFX vv 0 otwakaka .
PFX vv 0 otwakabu .
PFX vv 0 otwakalu .
PFX vv 0 otwakaku .
PFX vv 0 otwakatu ."""

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
    "vv": "vv",
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

    out_flag = "IT"
    left_desc = FLAG_DESCRIPTIONS.get("vv", "vv")
    right_desc = FLAG_DESCRIPTIONS.get("OR", "OR")
    comment_line = "# Cross product of {} ({}) and {} ({}) to {}".format(
        "vv", left_desc, "OR", right_desc, out_flag
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
