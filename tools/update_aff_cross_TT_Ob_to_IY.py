import re
import os
from pathlib import Path

# Cross product generator: TT x Ob => IY
# Description:
# - Left block `TT`: TT
# - Right block `Ob`: Object markers
# - Output flag `IY`: Cross-product prefixes for TT x Ob

REPO_ROOT = Path(__file__).resolve().parents[1]
AFF_FILE = REPO_ROOT / "Luganda.aff"

# If set to a flag name (e.g. "HB"), the generated cross-product block will be inserted
# immediately before the first "PFX <flag>" line when the output flag block doesn't
# already exist in the .aff.
INSERT_BEFORE_FLAG = "".strip() or None

rule_left_raw = """
PFX TT Y 698
PFX TT 0 silimu .
PFX TT 0 siliba .
PFX TT 0 siligu .
PFX TT 0 siligi .
PFX TT 0 silizi .
PFX TT 0 siliki .
PFX TT 0 silibi .
PFX TT 0 silili .
PFX TT 0 siliga .
PFX TT 0 silika .
PFX TT 0 silibu .
PFX TT 0 sililu .
PFX TT 0 siliku .
PFX TT 0 silitu .
PFX TT 0 tolin [^lmn]
PFX TT l tolind l.[^mn]
PFX TT l tolinn l.[mn]
PFX TT w tolimp [w]
PFX TT 0 tolimu .
PFX TT 0 toliba .
PFX TT 0 toligu .
PFX TT 0 toligi .
PFX TT 0 tolizi .
PFX TT 0 toliki .
PFX TT 0 tolibi .
PFX TT 0 tolili .
PFX TT 0 toliga .
PFX TT 0 tolika .
PFX TT 0 tolibu .
PFX TT 0 tolilu .
PFX TT 0 toliku .
PFX TT 0 tolitu .
PFX TT 0 talin [^lmn]
PFX TT l talind l.[^mn]
PFX TT l talinn l.[mn]
PFX TT w talimp [w]
PFX TT 0 talimu .
PFX TT 0 taliba .
PFX TT 0 taligu .
PFX TT 0 taligi .
PFX TT 0 talizi .
PFX TT 0 taliki .
PFX TT 0 talibi .
PFX TT 0 talili .
PFX TT 0 taliga .
PFX TT 0 talika .
PFX TT 0 talibu .
PFX TT 0 talilu .
PFX TT 0 taliku .
PFX TT 0 talitu .
PFX TT 0 tetulin [^lmn]
PFX TT l tetulind l.[^mn]
PFX TT l tetulinn l.[mn]
PFX TT w tetulimp [w]
PFX TT 0 tetulimu .
PFX TT 0 tetuliba .
PFX TT 0 tetuligu .
PFX TT 0 tetuligi .
PFX TT 0 tetulizi .
PFX TT 0 tetuliki .
PFX TT 0 tetulibi .
PFX TT 0 tetulili .
PFX TT 0 tetuliga .
PFX TT 0 tetulika .
PFX TT 0 tetulibu .
PFX TT 0 tetulilu .
PFX TT 0 tetuliku .
PFX TT 0 tetulitu .
PFX TT 0 temulin [^lmn]
PFX TT l temulind l.[^mn]
PFX TT l temulinn l.[mn]
PFX TT w temulimp [w]
PFX TT 0 temulimu .
PFX TT 0 temuliba .
PFX TT 0 temuligu .
PFX TT 0 temuligi .
PFX TT 0 temulizi .
PFX TT 0 temuliki .
PFX TT 0 temulibi .
PFX TT 0 temulili .
PFX TT 0 temuliga .
PFX TT 0 temulika .
PFX TT 0 temulibu .
PFX TT 0 temulilu .
PFX TT 0 temuliku .
PFX TT 0 temulitu .
PFX TT 0 tebalin [^lmn]
PFX TT l tebalind l.[^mn]
PFX TT l tebalinn l.[mn]
PFX TT w tebalimp [w]
PFX TT 0 tebalimu .
PFX TT 0 tebaliba .
PFX TT 0 tebaligu .
PFX TT 0 tebaligi .
PFX TT 0 tebalizi .
PFX TT 0 tebaliki .
PFX TT 0 tebalibi .
PFX TT 0 tebalili .
PFX TT 0 tebaliga .
PFX TT 0 tebalika .
PFX TT 0 tebalibu .
PFX TT 0 tebalilu .
PFX TT 0 tebaliku .
PFX TT 0 tebalitu .
PFX TT 0 abatalin [^lmn]
PFX TT l abatalind l.[^mn]
PFX TT l abatalinn l.[mn]
PFX TT w abatalimp [w]
PFX TT 0 abatalimu .
PFX TT 0 abataliba .
PFX TT 0 abataligu .
PFX TT 0 abataligi .
PFX TT 0 abatalizi .
PFX TT 0 abataliki .
PFX TT 0 abatalibi .
PFX TT 0 abatalili .
PFX TT 0 abataliga .
PFX TT 0 abatalika .
PFX TT 0 abatalibu .
PFX TT 0 abatalilu .
PFX TT 0 abataliku .
PFX TT 0 abatalitu .
PFX TT 0 atalin [^lmn]
PFX TT l atalind l.[^mn]
PFX TT l atalinn l.[mn]
PFX TT w atalimp [w]
PFX TT 0 atalimu .
PFX TT 0 ataliba .
PFX TT 0 ataligu .
PFX TT 0 ataligi .
PFX TT 0 atalizi .
PFX TT 0 ataliki .
PFX TT 0 atalibi .
PFX TT 0 atalili .
PFX TT 0 ataliga .
PFX TT 0 atalika .
PFX TT 0 atalibu .
PFX TT 0 atalilu .
PFX TT 0 ataliku .
PFX TT 0 atalitu .
PFX TT 0 tebalin [^lmn]
PFX TT l tebalind l.[^mn]
PFX TT l tebalinn l.[mn]
PFX TT w tebalimp [w]
PFX TT 0 tebalimu .
PFX TT 0 tebaliba .
PFX TT 0 tebaligu .
PFX TT 0 tebaligi .
PFX TT 0 tebalizi .
PFX TT 0 tebaliki .
PFX TT 0 tebalibi .
PFX TT 0 tebalili .
PFX TT 0 tebaliga .
PFX TT 0 tebalika .
PFX TT 0 tebalibu .
PFX TT 0 tebalilu .
PFX TT 0 tebaliku .
PFX TT 0 tebalitu .
PFX TT 0 abatalin [^lmn]
PFX TT l abatalind l.[^mn]
PFX TT l abatalinn l.[mn]
PFX TT w abatalimp [w]
PFX TT 0 abatalimu .
PFX TT 0 abataliba .
PFX TT 0 abataligu .
PFX TT 0 abataligi .
PFX TT 0 abatalizi .
PFX TT 0 abataliki .
PFX TT 0 abatalibi .
PFX TT 0 abatalili .
PFX TT 0 abataliga .
PFX TT 0 abatalika .
PFX TT 0 abatalibu .
PFX TT 0 abatalilu .
PFX TT 0 abataliku .
PFX TT 0 abatalitu .
PFX TT 0 tegulin [^lmn]
PFX TT l tegulind l.[^mn]
PFX TT l tegulinn l.[mn]
PFX TT w tegulimp [w]
PFX TT 0 tegulimu .
PFX TT 0 teguliba .
PFX TT 0 teguligu .
PFX TT 0 teguligi .
PFX TT 0 tegulizi .
PFX TT 0 teguliki .
PFX TT 0 tegulibi .
PFX TT 0 tegulili .
PFX TT 0 teguliga .
PFX TT 0 tegulika .
PFX TT 0 tegulibu .
PFX TT 0 tegulilu .
PFX TT 0 teguliku .
PFX TT 0 tegulitu .
PFX TT 0 ogutalin [^lmn]
PFX TT l ogutalind l.[^mn]
PFX TT l ogutalinn l.[mn]
PFX TT w ogutalimp [w]
PFX TT 0 ogutalimu .
PFX TT 0 ogutaliba .
PFX TT 0 ogutaligu .
PFX TT 0 ogutaligi .
PFX TT 0 ogutalizi .
PFX TT 0 ogutaliki .
PFX TT 0 ogutalibi .
PFX TT 0 ogutalili .
PFX TT 0 ogutaliga .
PFX TT 0 ogutalika .
PFX TT 0 ogutalibu .
PFX TT 0 ogutalilu .
PFX TT 0 ogutaliku .
PFX TT 0 ogutalitu .
PFX TT 0 tegilin [^lmn]
PFX TT l tegilind l.[^mn]
PFX TT l tegilinn l.[mn]
PFX TT w tegilimp [w]
PFX TT 0 tegilimu .
PFX TT 0 tegiliba .
PFX TT 0 tegiligu .
PFX TT 0 tegiligi .
PFX TT 0 tegilizi .
PFX TT 0 tegiliki .
PFX TT 0 tegilibi .
PFX TT 0 tegilili .
PFX TT 0 tegiliga .
PFX TT 0 tegilika .
PFX TT 0 tegilibu .
PFX TT 0 tegililu .
PFX TT 0 tegiliku .
PFX TT 0 tegilitu .
PFX TT 0 egitalin [^lmn]
PFX TT l egitalind l.[^mn]
PFX TT l egitalinn l.[mn]
PFX TT w egitalimp [w]
PFX TT 0 egitalimu .
PFX TT 0 egitaliba .
PFX TT 0 egitaligu .
PFX TT 0 egitaligi .
PFX TT 0 egitalizi .
PFX TT 0 egitaliki .
PFX TT 0 egitalibi .
PFX TT 0 egitalili .
PFX TT 0 egitaliga .
PFX TT 0 egitalika .
PFX TT 0 egitalibu .
PFX TT 0 egitalilu .
PFX TT 0 egitaliku .
PFX TT 0 egitalitu .
PFX TT 0 telin [^lmn]
PFX TT l telind l.[^mn]
PFX TT l telinn l.[mn]
PFX TT w telimp [w]
PFX TT 0 telimu .
PFX TT 0 teliba .
PFX TT 0 teligu .
PFX TT 0 teligi .
PFX TT 0 telizi .
PFX TT 0 teliki .
PFX TT 0 telibi .
PFX TT 0 telili .
PFX TT 0 teliga .
PFX TT 0 telika .
PFX TT 0 telibu .
PFX TT 0 telilu .
PFX TT 0 teliku .
PFX TT 0 telitu .
PFX TT 0 tezilin [^lmn]
PFX TT l tezilind l.[^mn]
PFX TT l tezilinn l.[mn]
PFX TT w tezilimp [w]
PFX TT 0 tezilimu .
PFX TT 0 teziliba .
PFX TT 0 teziligu .
PFX TT 0 teziligi .
PFX TT 0 tezilizi .
PFX TT 0 teziliki .
PFX TT 0 tezilibi .
PFX TT 0 tezilili .
PFX TT 0 teziliga .
PFX TT 0 tezilika .
PFX TT 0 tezilibu .
PFX TT 0 tezililu .
PFX TT 0 teziliku .
PFX TT 0 tezilitu .
PFX TT 0 ezitalin [^lmn]
PFX TT l ezitalind l.[^mn]
PFX TT l ezitalinn l.[mn]
PFX TT w ezitalimp [w]
PFX TT 0 ezitalimu .
PFX TT 0 ezitaliba .
PFX TT 0 ezitaligu .
PFX TT 0 ezitaligi .
PFX TT 0 ezitalizi .
PFX TT 0 ezitaliki .
PFX TT 0 ezitalibi .
PFX TT 0 ezitalili .
PFX TT 0 ezitaliga .
PFX TT 0 ezitalika .
PFX TT 0 ezitalibu .
PFX TT 0 ezitalilu .
PFX TT 0 ezitaliku .
PFX TT 0 ezitalitu .
PFX TT 0 tekilin [^lmn]
PFX TT l tekilind l.[^mn]
PFX TT l tekilinn l.[mn]
PFX TT w tekilimp [w]
PFX TT 0 tekilimu .
PFX TT 0 tekiliba .
PFX TT 0 tekiligu .
PFX TT 0 tekiligi .
PFX TT 0 tekilizi .
PFX TT 0 tekiliki .
PFX TT 0 tekilibi .
PFX TT 0 tekilili .
PFX TT 0 tekiliga .
PFX TT 0 tekilika .
PFX TT 0 tekilibu .
PFX TT 0 tekililu .
PFX TT 0 tekiliku .
PFX TT 0 tekilitu .
PFX TT 0 ekitalin [^lmn]
PFX TT l ekitalind l.[^mn]
PFX TT l ekitalinn l.[mn]
PFX TT w ekitalimp [w]
PFX TT 0 ekitalimu .
PFX TT 0 ekitaliba .
PFX TT 0 ekitaligu .
PFX TT 0 ekitaligi .
PFX TT 0 ekitalizi .
PFX TT 0 ekitaliki .
PFX TT 0 ekitalibi .
PFX TT 0 ekitalili .
PFX TT 0 ekitaliga .
PFX TT 0 ekitalika .
PFX TT 0 ekitalibu .
PFX TT 0 ekitalilu .
PFX TT 0 ekitaliku .
PFX TT 0 ekitalitu .
PFX TT 0 tebilin [^lmn]
PFX TT l tebilind l.[^mn]
PFX TT l tebilinn l.[mn]
PFX TT w tebilimp [w]
PFX TT 0 tebilimu .
PFX TT 0 tebiliba .
PFX TT 0 tebiligu .
PFX TT 0 tebiligi .
PFX TT 0 tebilizi .
PFX TT 0 tebiliki .
PFX TT 0 tebilibi .
PFX TT 0 tebilili .
PFX TT 0 tebiliga .
PFX TT 0 tebilika .
PFX TT 0 tebilibu .
PFX TT 0 tebililu .
PFX TT 0 tebiliku .
PFX TT 0 tebilitu .
PFX TT 0 ebitalin [^lmn]
PFX TT l ebitalind l.[^mn]
PFX TT l ebitalinn l.[mn]
PFX TT w ebitalimp [w]
PFX TT 0 ebitalimu .
PFX TT 0 ebitaliba .
PFX TT 0 ebitaligu .
PFX TT 0 ebitaligi .
PFX TT 0 ebitalizi .
PFX TT 0 ebitaliki .
PFX TT 0 ebitalibi .
PFX TT 0 ebitalili .
PFX TT 0 ebitaliga .
PFX TT 0 ebitalika .
PFX TT 0 ebitalibu .
PFX TT 0 ebitalilu .
PFX TT 0 ebitaliku .
PFX TT 0 ebitalitu .
PFX TT 0 telilin [^lmn]
PFX TT l telilind l.[^mn]
PFX TT l telilinn l.[mn]
PFX TT w telilimp [w]
PFX TT 0 telilimu .
PFX TT 0 teliliba .
PFX TT 0 teliligu .
PFX TT 0 teliligi .
PFX TT 0 telilizi .
PFX TT 0 teliliki .
PFX TT 0 telilibi .
PFX TT 0 telilili .
PFX TT 0 teliliga .
PFX TT 0 telilika .
PFX TT 0 telilibu .
PFX TT 0 telililu .
PFX TT 0 teliliku .
PFX TT 0 telilitu .
PFX TT 0 elitalin [^lmn]
PFX TT l elitalind l.[^mn]
PFX TT l elitalinn l.[mn]
PFX TT w elitalimp [w]
PFX TT 0 elitalimu .
PFX TT 0 elitaliba .
PFX TT 0 elitaligu .
PFX TT 0 elitaligi .
PFX TT 0 elitalizi .
PFX TT 0 elitaliki .
PFX TT 0 elitalibi .
PFX TT 0 elitalili .
PFX TT 0 elitaliga .
PFX TT 0 elitalika .
PFX TT 0 elitalibu .
PFX TT 0 elitalilu .
PFX TT 0 elitaliku .
PFX TT 0 elitalitu .
PFX TT 0 tegalin [^lmn]
PFX TT l tegalind l.[^mn]
PFX TT l tegalinn l.[mn]
PFX TT w tegalimp [w]
PFX TT 0 tegalimu .
PFX TT 0 tegaliba .
PFX TT 0 tegaligu .
PFX TT 0 tegaligi .
PFX TT 0 tegalizi .
PFX TT 0 tegaliki .
PFX TT 0 tegalibi .
PFX TT 0 tegalili .
PFX TT 0 tegaliga .
PFX TT 0 tegalika .
PFX TT 0 tegalibu .
PFX TT 0 tegalilu .
PFX TT 0 tegaliku .
PFX TT 0 tegalitu .
PFX TT 0 agatalin [^lmn]
PFX TT l agatalind l.[^mn]
PFX TT l agatalinn l.[mn]
PFX TT w agatalimp [w]
PFX TT 0 agatalimu .
PFX TT 0 agataliba .
PFX TT 0 agataligu .
PFX TT 0 agataligi .
PFX TT 0 agatalizi .
PFX TT 0 agataliki .
PFX TT 0 agatalibi .
PFX TT 0 agatalili .
PFX TT 0 agataliga .
PFX TT 0 agatalika .
PFX TT 0 agatalibu .
PFX TT 0 agatalilu .
PFX TT 0 agataliku .
PFX TT 0 agatalitu .
PFX TT 0 tekalin [^lmn]
PFX TT l tekalind l.[^mn]
PFX TT l tekalinn l.[mn]
PFX TT w tekalimp [w]
PFX TT 0 tekalimu .
PFX TT 0 tekaliba .
PFX TT 0 tekaligu .
PFX TT 0 tekaligi .
PFX TT 0 tekalizi .
PFX TT 0 tekaliki .
PFX TT 0 tekalibi .
PFX TT 0 tekalili .
PFX TT 0 tekaliga .
PFX TT 0 tekalika .
PFX TT 0 tekalibu .
PFX TT 0 tekalilu .
PFX TT 0 tekaliku .
PFX TT 0 tekalitu .
PFX TT 0 akatalin [^lmn]
PFX TT l akatalind l.[^mn]
PFX TT l akatalinn l.[mn]
PFX TT w akatalimp [w]
PFX TT 0 akatalimu .
PFX TT 0 akataliba .
PFX TT 0 akataligu .
PFX TT 0 akataligi .
PFX TT 0 akatalizi .
PFX TT 0 akataliki .
PFX TT 0 akatalibi .
PFX TT 0 akatalili .
PFX TT 0 akataliga .
PFX TT 0 akatalika .
PFX TT 0 akatalibu .
PFX TT 0 akatalilu .
PFX TT 0 akataliku .
PFX TT 0 akatalitu .
PFX TT 0 tebulin [^lmn]
PFX TT l tebulind l.[^mn]
PFX TT l tebulinn l.[mn]
PFX TT w tebulimp [w]
PFX TT 0 tebulimu .
PFX TT 0 tebuliba .
PFX TT 0 tebuligu .
PFX TT 0 tebuligi .
PFX TT 0 tebulizi .
PFX TT 0 tebuliki .
PFX TT 0 tebulibi .
PFX TT 0 tebulili .
PFX TT 0 tebuliga .
PFX TT 0 tebulika .
PFX TT 0 tebulibu .
PFX TT 0 tebulilu .
PFX TT 0 tebuliku .
PFX TT 0 tebulitu .
PFX TT 0 obutalin [^lmn]
PFX TT l obutalind l.[^mn]
PFX TT l obutalinn l.[mn]
PFX TT w obutalimp [w]
PFX TT 0 obutalimu .
PFX TT 0 obutaliba .
PFX TT 0 obutaligu .
PFX TT 0 obutaligi .
PFX TT 0 obutalizi .
PFX TT 0 obutaliki .
PFX TT 0 obutalibi .
PFX TT 0 obutalili .
PFX TT 0 obutaliga .
PFX TT 0 obutalika .
PFX TT 0 obutalibu .
PFX TT 0 obutalilu .
PFX TT 0 obutaliku .
PFX TT 0 obutalitu .
PFX TT 0 telulin [^lmn]
PFX TT l telulind l.[^mn]
PFX TT l telulinn l.[mn]
PFX TT w telulimp [w]
PFX TT 0 telulimu .
PFX TT 0 teluliba .
PFX TT 0 teluligu .
PFX TT 0 teluligi .
PFX TT 0 telulizi .
PFX TT 0 teluliki .
PFX TT 0 telulibi .
PFX TT 0 telulili .
PFX TT 0 teluliga .
PFX TT 0 telulika .
PFX TT 0 telulibu .
PFX TT 0 telulilu .
PFX TT 0 teluliku .
PFX TT 0 telulitu .
PFX TT 0 olutalin [^lmn]
PFX TT l olutalind l.[^mn]
PFX TT l olutalinn l.[mn]
PFX TT w olutalimp [w]
PFX TT 0 olutalimu .
PFX TT 0 olutaliba .
PFX TT 0 olutaligu .
PFX TT 0 olutaligi .
PFX TT 0 olutalizi .
PFX TT 0 olutaliki .
PFX TT 0 olutalibi .
PFX TT 0 olutalili .
PFX TT 0 olutaliga .
PFX TT 0 olutalika .
PFX TT 0 olutalibu .
PFX TT 0 olutalilu .
PFX TT 0 olutaliku .
PFX TT 0 olutalitu .
PFX TT 0 tezilin [^lmn]
PFX TT l tezilind l.[^mn]
PFX TT l tezilinn l.[mn]
PFX TT w tezilimp [w]
PFX TT 0 tezilimu .
PFX TT 0 teziliba .
PFX TT 0 teziligu .
PFX TT 0 teziligi .
PFX TT 0 tezilizi .
PFX TT 0 teziliki .
PFX TT 0 tezilibi .
PFX TT 0 tezilili .
PFX TT 0 teziliga .
PFX TT 0 tezilika .
PFX TT 0 tezilibu .
PFX TT 0 tezililu .
PFX TT 0 teziliku .
PFX TT 0 tezilitu .
PFX TT 0 ezitalin [^lmn]
PFX TT l ezitalind l.[^mn]
PFX TT l ezitalinn l.[mn]
PFX TT w ezitalimp [w]
PFX TT 0 ezitalimu .
PFX TT 0 ezitaliba .
PFX TT 0 ezitaligu .
PFX TT 0 ezitaligi .
PFX TT 0 ezitalizi .
PFX TT 0 ezitaliki .
PFX TT 0 ezitalibi .
PFX TT 0 ezitalili .
PFX TT 0 ezitaliga .
PFX TT 0 ezitalika .
PFX TT 0 ezitalibu .
PFX TT 0 ezitalilu .
PFX TT 0 ezitaliku .
PFX TT 0 ezitalitu .
PFX TT 0 tekulin [^lmn]
PFX TT l tekulind l.[^mn]
PFX TT l tekulinn l.[mn]
PFX TT w tekulimp [w]
PFX TT 0 tekulimu .
PFX TT 0 tekuliba .
PFX TT 0 tekuligu .
PFX TT 0 tekuligi .
PFX TT 0 tekulizi .
PFX TT 0 tekuliki .
PFX TT 0 tekulibi .
PFX TT 0 tekulili .
PFX TT 0 tekuliga .
PFX TT 0 tekulika .
PFX TT 0 tekulibu .
PFX TT 0 tekulilu .
PFX TT 0 tekuliku .
PFX TT 0 tekulitu .
PFX TT 0 okutalin [^lmn]
PFX TT l okutalind l.[^mn]
PFX TT l okutalinn l.[mn]
PFX TT w okutalimp [w]
PFX TT 0 okutalimu .
PFX TT 0 okutaliba .
PFX TT 0 okutaligu .
PFX TT 0 okutaligi .
PFX TT 0 okutalizi .
PFX TT 0 okutaliki .
PFX TT 0 okutalibi .
PFX TT 0 okutalili .
PFX TT 0 okutaliga .
PFX TT 0 okutalika .
PFX TT 0 okutalibu .
PFX TT 0 okutalilu .
PFX TT 0 okutaliku .
PFX TT 0 okutalitu .
PFX TT 0 tegalin [^lmn]
PFX TT l tegalind l.[^mn]
PFX TT l tegalinn l.[mn]
PFX TT w tegalimp [w]
PFX TT 0 tegalimu .
PFX TT 0 tegaliba .
PFX TT 0 tegaligu .
PFX TT 0 tegaligi .
PFX TT 0 tegalizi .
PFX TT 0 tegaliki .
PFX TT 0 tegalibi .
PFX TT 0 tegalili .
PFX TT 0 tegaliga .
PFX TT 0 tegalika .
PFX TT 0 tegalibu .
PFX TT 0 tegalilu .
PFX TT 0 tegaliku .
PFX TT 0 tegalitu .
PFX TT 0 agatalin [^lmn]
PFX TT l agatalind l.[^mn]
PFX TT l agatalinn l.[mn]
PFX TT w agatalimp [w]
PFX TT 0 agatalimu .
PFX TT 0 agataliba .
PFX TT 0 agataligu .
PFX TT 0 agataligi .
PFX TT 0 agatalizi .
PFX TT 0 agataliki .
PFX TT 0 agatalibi .
PFX TT 0 agatalili .
PFX TT 0 agataliga .
PFX TT 0 agatalika .
PFX TT 0 agatalibu .
PFX TT 0 agatalilu .
PFX TT 0 agataliku .
PFX TT 0 agatalitu .
PFX TT 0 tetulin [^lmn]
PFX TT l tetulind l.[^mn]
PFX TT l tetulinn l.[mn]
PFX TT w tetulimp [w]
PFX TT 0 tetulimu .
PFX TT 0 tetuliba .
PFX TT 0 tetuligu .
PFX TT 0 tetuligi .
PFX TT 0 tetulizi .
PFX TT 0 tetuliki .
PFX TT 0 tetulibi .
PFX TT 0 tetulili .
PFX TT 0 tetuliga .
PFX TT 0 tetulika .
PFX TT 0 tetulibu .
PFX TT 0 tetulilu .
PFX TT 0 tetuliku .
PFX TT 0 tetulitu .
PFX TT 0 otutalin [^lmn]
PFX TT l otutalind l.[^mn]
PFX TT l otutalinn l.[mn]
PFX TT w otutalimp [w]
PFX TT 0 otutalimu .
PFX TT 0 otutaliba .
PFX TT 0 otutaligu .
PFX TT 0 otutaligi .
PFX TT 0 otutalizi .
PFX TT 0 otutaliki .
PFX TT 0 otutalibi .
PFX TT 0 otutalili .
PFX TT 0 otutaliga .
PFX TT 0 otutalika .
PFX TT 0 otutalibu .
PFX TT 0 otutalilu .
PFX TT 0 otutaliku .
PFX TT 0 otutalitu ."""

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
    "TT": "TT",
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

    out_flag = "IY"
    left_desc = FLAG_DESCRIPTIONS.get("TT", "TT")
    right_desc = FLAG_DESCRIPTIONS.get("Ob", "Ob")
    comment_line = "# Cross product of {} ({}) and {} ({}) to {}".format(
        "TT", left_desc, "Ob", right_desc, out_flag
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
