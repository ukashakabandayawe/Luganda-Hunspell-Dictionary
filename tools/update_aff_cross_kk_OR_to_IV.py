import re
import os
from pathlib import Path

# Cross product generator: kk x OR => IV
# Description:
# - Left block `kk`: kk
# - Right block `OR`: Special reflexive object markers
# - Output flag `IV`: Cross-product prefixes for kk x OR

REPO_ROOT = Path(__file__).resolve().parents[1]
AFF_FILE = REPO_ROOT / "Luganda.aff"

# If set to a flag name (e.g. "HB"), the generated cross-product block will be inserted
# immediately before the first "PFX <flag>" line when the output flag block doesn't
# already exist in the .aff.
INSERT_BEFORE_FLAG = "".strip() or None

rule_left_raw = """
PFX kk Y 698
PFX kk 0 silimukumu .
PFX kk 0 silimukuba .
PFX kk 0 silimukugu .
PFX kk 0 silimukugi .
PFX kk 0 silimukuzi .
PFX kk 0 silimukuki .
PFX kk 0 silimukubi .
PFX kk 0 silimukuli .
PFX kk 0 silimukuga .
PFX kk 0 silimukuka .
PFX kk 0 silimukubu .
PFX kk 0 silimukulu .
PFX kk 0 silimukuku .
PFX kk 0 silimukutu .
PFX kk 0 tolimukun [^lmn]
PFX kk l tolimukund l.[^mn]
PFX kk l tolimukunn l.[mn]
PFX kk w tolimukump [w]
PFX kk 0 tolimukumu .
PFX kk 0 tolimukuba .
PFX kk 0 tolimukugu .
PFX kk 0 tolimukugi .
PFX kk 0 tolimukuzi .
PFX kk 0 tolimukuki .
PFX kk 0 tolimukubi .
PFX kk 0 tolimukuli .
PFX kk 0 tolimukuga .
PFX kk 0 tolimukuka .
PFX kk 0 tolimukubu .
PFX kk 0 tolimukulu .
PFX kk 0 tolimukuku .
PFX kk 0 tolimukutu .
PFX kk 0 talimukun [^lmn]
PFX kk l talimukund l.[^mn]
PFX kk l talimukunn l.[mn]
PFX kk w talimukump [w]
PFX kk 0 talimukumu .
PFX kk 0 talimukuba .
PFX kk 0 talimukugu .
PFX kk 0 talimukugi .
PFX kk 0 talimukuzi .
PFX kk 0 talimukuki .
PFX kk 0 talimukubi .
PFX kk 0 talimukuli .
PFX kk 0 talimukuga .
PFX kk 0 talimukuka .
PFX kk 0 talimukubu .
PFX kk 0 talimukulu .
PFX kk 0 talimukuku .
PFX kk 0 talimukutu .
PFX kk 0 tetulimukun [^lmn]
PFX kk l tetulimukund l.[^mn]
PFX kk l tetulimukunn l.[mn]
PFX kk w tetulimukump [w]
PFX kk 0 tetulimukumu .
PFX kk 0 tetulimukuba .
PFX kk 0 tetulimukugu .
PFX kk 0 tetulimukugi .
PFX kk 0 tetulimukuzi .
PFX kk 0 tetulimukuki .
PFX kk 0 tetulimukubi .
PFX kk 0 tetulimukuli .
PFX kk 0 tetulimukuga .
PFX kk 0 tetulimukuka .
PFX kk 0 tetulimukubu .
PFX kk 0 tetulimukulu .
PFX kk 0 tetulimukuku .
PFX kk 0 tetulimukutu .
PFX kk 0 temulimukun [^lmn]
PFX kk l temulimukund l.[^mn]
PFX kk l temulimukunn l.[mn]
PFX kk w temulimukump [w]
PFX kk 0 temulimukumu .
PFX kk 0 temulimukuba .
PFX kk 0 temulimukugu .
PFX kk 0 temulimukugi .
PFX kk 0 temulimukuzi .
PFX kk 0 temulimukuki .
PFX kk 0 temulimukubi .
PFX kk 0 temulimukuli .
PFX kk 0 temulimukuga .
PFX kk 0 temulimukuka .
PFX kk 0 temulimukubu .
PFX kk 0 temulimukulu .
PFX kk 0 temulimukuku .
PFX kk 0 temulimukutu .
PFX kk 0 tebalimukun [^lmn]
PFX kk l tebalimukund l.[^mn]
PFX kk l tebalimukunn l.[mn]
PFX kk w tebalimukump [w]
PFX kk 0 tebalimukumu .
PFX kk 0 tebalimukuba .
PFX kk 0 tebalimukugu .
PFX kk 0 tebalimukugi .
PFX kk 0 tebalimukuzi .
PFX kk 0 tebalimukuki .
PFX kk 0 tebalimukubi .
PFX kk 0 tebalimukuli .
PFX kk 0 tebalimukuga .
PFX kk 0 tebalimukuka .
PFX kk 0 tebalimukubu .
PFX kk 0 tebalimukulu .
PFX kk 0 tebalimukuku .
PFX kk 0 tebalimukutu .
PFX kk 0 abatalimukun [^lmn]
PFX kk l abatalimukund l.[^mn]
PFX kk l abatalimukunn l.[mn]
PFX kk w abatalimukump [w]
PFX kk 0 abatalimukumu .
PFX kk 0 abatalimukuba .
PFX kk 0 abatalimukugu .
PFX kk 0 abatalimukugi .
PFX kk 0 abatalimukuzi .
PFX kk 0 abatalimukuki .
PFX kk 0 abatalimukubi .
PFX kk 0 abatalimukuli .
PFX kk 0 abatalimukuga .
PFX kk 0 abatalimukuka .
PFX kk 0 abatalimukubu .
PFX kk 0 abatalimukulu .
PFX kk 0 abatalimukuku .
PFX kk 0 abatalimukutu .
PFX kk 0 atalimukun [^lmn]
PFX kk l atalimukund l.[^mn]
PFX kk l atalimukunn l.[mn]
PFX kk w atalimukump [w]
PFX kk 0 atalimukumu .
PFX kk 0 atalimukuba .
PFX kk 0 atalimukugu .
PFX kk 0 atalimukugi .
PFX kk 0 atalimukuzi .
PFX kk 0 atalimukuki .
PFX kk 0 atalimukubi .
PFX kk 0 atalimukuli .
PFX kk 0 atalimukuga .
PFX kk 0 atalimukuka .
PFX kk 0 atalimukubu .
PFX kk 0 atalimukulu .
PFX kk 0 atalimukuku .
PFX kk 0 atalimukutu .
PFX kk 0 tebalimukun [^lmn]
PFX kk l tebalimukund l.[^mn]
PFX kk l tebalimukunn l.[mn]
PFX kk w tebalimukump [w]
PFX kk 0 tebalimukumu .
PFX kk 0 tebalimukuba .
PFX kk 0 tebalimukugu .
PFX kk 0 tebalimukugi .
PFX kk 0 tebalimukuzi .
PFX kk 0 tebalimukuki .
PFX kk 0 tebalimukubi .
PFX kk 0 tebalimukuli .
PFX kk 0 tebalimukuga .
PFX kk 0 tebalimukuka .
PFX kk 0 tebalimukubu .
PFX kk 0 tebalimukulu .
PFX kk 0 tebalimukuku .
PFX kk 0 tebalimukutu .
PFX kk 0 abatalimukun [^lmn]
PFX kk l abatalimukund l.[^mn]
PFX kk l abatalimukunn l.[mn]
PFX kk w abatalimukump [w]
PFX kk 0 abatalimukumu .
PFX kk 0 abatalimukuba .
PFX kk 0 abatalimukugu .
PFX kk 0 abatalimukugi .
PFX kk 0 abatalimukuzi .
PFX kk 0 abatalimukuki .
PFX kk 0 abatalimukubi .
PFX kk 0 abatalimukuli .
PFX kk 0 abatalimukuga .
PFX kk 0 abatalimukuka .
PFX kk 0 abatalimukubu .
PFX kk 0 abatalimukulu .
PFX kk 0 abatalimukuku .
PFX kk 0 abatalimukutu .
PFX kk 0 tegulimukun [^lmn]
PFX kk l tegulimukund l.[^mn]
PFX kk l tegulimukunn l.[mn]
PFX kk w tegulimukump [w]
PFX kk 0 tegulimukumu .
PFX kk 0 tegulimukuba .
PFX kk 0 tegulimukugu .
PFX kk 0 tegulimukugi .
PFX kk 0 tegulimukuzi .
PFX kk 0 tegulimukuki .
PFX kk 0 tegulimukubi .
PFX kk 0 tegulimukuli .
PFX kk 0 tegulimukuga .
PFX kk 0 tegulimukuka .
PFX kk 0 tegulimukubu .
PFX kk 0 tegulimukulu .
PFX kk 0 tegulimukuku .
PFX kk 0 tegulimukutu .
PFX kk 0 ogutalimukun [^lmn]
PFX kk l ogutalimukund l.[^mn]
PFX kk l ogutalimukunn l.[mn]
PFX kk w ogutalimukump [w]
PFX kk 0 ogutalimukumu .
PFX kk 0 ogutalimukuba .
PFX kk 0 ogutalimukugu .
PFX kk 0 ogutalimukugi .
PFX kk 0 ogutalimukuzi .
PFX kk 0 ogutalimukuki .
PFX kk 0 ogutalimukubi .
PFX kk 0 ogutalimukuli .
PFX kk 0 ogutalimukuga .
PFX kk 0 ogutalimukuka .
PFX kk 0 ogutalimukubu .
PFX kk 0 ogutalimukulu .
PFX kk 0 ogutalimukuku .
PFX kk 0 ogutalimukutu .
PFX kk 0 tegilimukun [^lmn]
PFX kk l tegilimukund l.[^mn]
PFX kk l tegilimukunn l.[mn]
PFX kk w tegilimukump [w]
PFX kk 0 tegilimukumu .
PFX kk 0 tegilimukuba .
PFX kk 0 tegilimukugu .
PFX kk 0 tegilimukugi .
PFX kk 0 tegilimukuzi .
PFX kk 0 tegilimukuki .
PFX kk 0 tegilimukubi .
PFX kk 0 tegilimukuli .
PFX kk 0 tegilimukuga .
PFX kk 0 tegilimukuka .
PFX kk 0 tegilimukubu .
PFX kk 0 tegilimukulu .
PFX kk 0 tegilimukuku .
PFX kk 0 tegilimukutu .
PFX kk 0 egitalimukun [^lmn]
PFX kk l egitalimukund l.[^mn]
PFX kk l egitalimukunn l.[mn]
PFX kk w egitalimukump [w]
PFX kk 0 egitalimukumu .
PFX kk 0 egitalimukuba .
PFX kk 0 egitalimukugu .
PFX kk 0 egitalimukugi .
PFX kk 0 egitalimukuzi .
PFX kk 0 egitalimukuki .
PFX kk 0 egitalimukubi .
PFX kk 0 egitalimukuli .
PFX kk 0 egitalimukuga .
PFX kk 0 egitalimukuka .
PFX kk 0 egitalimukubu .
PFX kk 0 egitalimukulu .
PFX kk 0 egitalimukuku .
PFX kk 0 egitalimukutu .
PFX kk 0 telimukun [^lmn]
PFX kk l telimukund l.[^mn]
PFX kk l telimukunn l.[mn]
PFX kk w telimukump [w]
PFX kk 0 telimukumu .
PFX kk 0 telimukuba .
PFX kk 0 telimukugu .
PFX kk 0 telimukugi .
PFX kk 0 telimukuzi .
PFX kk 0 telimukuki .
PFX kk 0 telimukubi .
PFX kk 0 telimukuli .
PFX kk 0 telimukuga .
PFX kk 0 telimukuka .
PFX kk 0 telimukubu .
PFX kk 0 telimukulu .
PFX kk 0 telimukuku .
PFX kk 0 telimukutu .
PFX kk 0 tezilimukun [^lmn]
PFX kk l tezilimukund l.[^mn]
PFX kk l tezilimukunn l.[mn]
PFX kk w tezilimukump [w]
PFX kk 0 tezilimukumu .
PFX kk 0 tezilimukuba .
PFX kk 0 tezilimukugu .
PFX kk 0 tezilimukugi .
PFX kk 0 tezilimukuzi .
PFX kk 0 tezilimukuki .
PFX kk 0 tezilimukubi .
PFX kk 0 tezilimukuli .
PFX kk 0 tezilimukuga .
PFX kk 0 tezilimukuka .
PFX kk 0 tezilimukubu .
PFX kk 0 tezilimukulu .
PFX kk 0 tezilimukuku .
PFX kk 0 tezilimukutu .
PFX kk 0 ezitalimukun [^lmn]
PFX kk l ezitalimukund l.[^mn]
PFX kk l ezitalimukunn l.[mn]
PFX kk w ezitalimukump [w]
PFX kk 0 ezitalimukumu .
PFX kk 0 ezitalimukuba .
PFX kk 0 ezitalimukugu .
PFX kk 0 ezitalimukugi .
PFX kk 0 ezitalimukuzi .
PFX kk 0 ezitalimukuki .
PFX kk 0 ezitalimukubi .
PFX kk 0 ezitalimukuli .
PFX kk 0 ezitalimukuga .
PFX kk 0 ezitalimukuka .
PFX kk 0 ezitalimukubu .
PFX kk 0 ezitalimukulu .
PFX kk 0 ezitalimukuku .
PFX kk 0 ezitalimukutu .
PFX kk 0 tekilimukun [^lmn]
PFX kk l tekilimukund l.[^mn]
PFX kk l tekilimukunn l.[mn]
PFX kk w tekilimukump [w]
PFX kk 0 tekilimukumu .
PFX kk 0 tekilimukuba .
PFX kk 0 tekilimukugu .
PFX kk 0 tekilimukugi .
PFX kk 0 tekilimukuzi .
PFX kk 0 tekilimukuki .
PFX kk 0 tekilimukubi .
PFX kk 0 tekilimukuli .
PFX kk 0 tekilimukuga .
PFX kk 0 tekilimukuka .
PFX kk 0 tekilimukubu .
PFX kk 0 tekilimukulu .
PFX kk 0 tekilimukuku .
PFX kk 0 tekilimukutu .
PFX kk 0 ekitalimukun [^lmn]
PFX kk l ekitalimukund l.[^mn]
PFX kk l ekitalimukunn l.[mn]
PFX kk w ekitalimukump [w]
PFX kk 0 ekitalimukumu .
PFX kk 0 ekitalimukuba .
PFX kk 0 ekitalimukugu .
PFX kk 0 ekitalimukugi .
PFX kk 0 ekitalimukuzi .
PFX kk 0 ekitalimukuki .
PFX kk 0 ekitalimukubi .
PFX kk 0 ekitalimukuli .
PFX kk 0 ekitalimukuga .
PFX kk 0 ekitalimukuka .
PFX kk 0 ekitalimukubu .
PFX kk 0 ekitalimukulu .
PFX kk 0 ekitalimukuku .
PFX kk 0 ekitalimukutu .
PFX kk 0 tebilimukun [^lmn]
PFX kk l tebilimukund l.[^mn]
PFX kk l tebilimukunn l.[mn]
PFX kk w tebilimukump [w]
PFX kk 0 tebilimukumu .
PFX kk 0 tebilimukuba .
PFX kk 0 tebilimukugu .
PFX kk 0 tebilimukugi .
PFX kk 0 tebilimukuzi .
PFX kk 0 tebilimukuki .
PFX kk 0 tebilimukubi .
PFX kk 0 tebilimukuli .
PFX kk 0 tebilimukuga .
PFX kk 0 tebilimukuka .
PFX kk 0 tebilimukubu .
PFX kk 0 tebilimukulu .
PFX kk 0 tebilimukuku .
PFX kk 0 tebilimukutu .
PFX kk 0 ebitalimukun [^lmn]
PFX kk l ebitalimukund l.[^mn]
PFX kk l ebitalimukunn l.[mn]
PFX kk w ebitalimukump [w]
PFX kk 0 ebitalimukumu .
PFX kk 0 ebitalimukuba .
PFX kk 0 ebitalimukugu .
PFX kk 0 ebitalimukugi .
PFX kk 0 ebitalimukuzi .
PFX kk 0 ebitalimukuki .
PFX kk 0 ebitalimukubi .
PFX kk 0 ebitalimukuli .
PFX kk 0 ebitalimukuga .
PFX kk 0 ebitalimukuka .
PFX kk 0 ebitalimukubu .
PFX kk 0 ebitalimukulu .
PFX kk 0 ebitalimukuku .
PFX kk 0 ebitalimukutu .
PFX kk 0 telilimukun [^lmn]
PFX kk l telilimukund l.[^mn]
PFX kk l telilimukunn l.[mn]
PFX kk w telilimukump [w]
PFX kk 0 telilimukumu .
PFX kk 0 telilimukuba .
PFX kk 0 telilimukugu .
PFX kk 0 telilimukugi .
PFX kk 0 telilimukuzi .
PFX kk 0 telilimukuki .
PFX kk 0 telilimukubi .
PFX kk 0 telilimukuli .
PFX kk 0 telilimukuga .
PFX kk 0 telilimukuka .
PFX kk 0 telilimukubu .
PFX kk 0 telilimukulu .
PFX kk 0 telilimukuku .
PFX kk 0 telilimukutu .
PFX kk 0 elitalimukun [^lmn]
PFX kk l elitalimukund l.[^mn]
PFX kk l elitalimukunn l.[mn]
PFX kk w elitalimukump [w]
PFX kk 0 elitalimukumu .
PFX kk 0 elitalimukuba .
PFX kk 0 elitalimukugu .
PFX kk 0 elitalimukugi .
PFX kk 0 elitalimukuzi .
PFX kk 0 elitalimukuki .
PFX kk 0 elitalimukubi .
PFX kk 0 elitalimukuli .
PFX kk 0 elitalimukuga .
PFX kk 0 elitalimukuka .
PFX kk 0 elitalimukubu .
PFX kk 0 elitalimukulu .
PFX kk 0 elitalimukuku .
PFX kk 0 elitalimukutu .
PFX kk 0 tegalimukun [^lmn]
PFX kk l tegalimukund l.[^mn]
PFX kk l tegalimukunn l.[mn]
PFX kk w tegalimukump [w]
PFX kk 0 tegalimukumu .
PFX kk 0 tegalimukuba .
PFX kk 0 tegalimukugu .
PFX kk 0 tegalimukugi .
PFX kk 0 tegalimukuzi .
PFX kk 0 tegalimukuki .
PFX kk 0 tegalimukubi .
PFX kk 0 tegalimukuli .
PFX kk 0 tegalimukuga .
PFX kk 0 tegalimukuka .
PFX kk 0 tegalimukubu .
PFX kk 0 tegalimukulu .
PFX kk 0 tegalimukuku .
PFX kk 0 tegalimukutu .
PFX kk 0 agatalimukun [^lmn]
PFX kk l agatalimukund l.[^mn]
PFX kk l agatalimukunn l.[mn]
PFX kk w agatalimukump [w]
PFX kk 0 agatalimukumu .
PFX kk 0 agatalimukuba .
PFX kk 0 agatalimukugu .
PFX kk 0 agatalimukugi .
PFX kk 0 agatalimukuzi .
PFX kk 0 agatalimukuki .
PFX kk 0 agatalimukubi .
PFX kk 0 agatalimukuli .
PFX kk 0 agatalimukuga .
PFX kk 0 agatalimukuka .
PFX kk 0 agatalimukubu .
PFX kk 0 agatalimukulu .
PFX kk 0 agatalimukuku .
PFX kk 0 agatalimukutu .
PFX kk 0 tekalimukun [^lmn]
PFX kk l tekalimukund l.[^mn]
PFX kk l tekalimukunn l.[mn]
PFX kk w tekalimukump [w]
PFX kk 0 tekalimukumu .
PFX kk 0 tekalimukuba .
PFX kk 0 tekalimukugu .
PFX kk 0 tekalimukugi .
PFX kk 0 tekalimukuzi .
PFX kk 0 tekalimukuki .
PFX kk 0 tekalimukubi .
PFX kk 0 tekalimukuli .
PFX kk 0 tekalimukuga .
PFX kk 0 tekalimukuka .
PFX kk 0 tekalimukubu .
PFX kk 0 tekalimukulu .
PFX kk 0 tekalimukuku .
PFX kk 0 tekalimukutu .
PFX kk 0 akatalimukun [^lmn]
PFX kk l akatalimukund l.[^mn]
PFX kk l akatalimukunn l.[mn]
PFX kk w akatalimukump [w]
PFX kk 0 akatalimukumu .
PFX kk 0 akatalimukuba .
PFX kk 0 akatalimukugu .
PFX kk 0 akatalimukugi .
PFX kk 0 akatalimukuzi .
PFX kk 0 akatalimukuki .
PFX kk 0 akatalimukubi .
PFX kk 0 akatalimukuli .
PFX kk 0 akatalimukuga .
PFX kk 0 akatalimukuka .
PFX kk 0 akatalimukubu .
PFX kk 0 akatalimukulu .
PFX kk 0 akatalimukuku .
PFX kk 0 akatalimukutu .
PFX kk 0 tebulimukun [^lmn]
PFX kk l tebulimukund l.[^mn]
PFX kk l tebulimukunn l.[mn]
PFX kk w tebulimukump [w]
PFX kk 0 tebulimukumu .
PFX kk 0 tebulimukuba .
PFX kk 0 tebulimukugu .
PFX kk 0 tebulimukugi .
PFX kk 0 tebulimukuzi .
PFX kk 0 tebulimukuki .
PFX kk 0 tebulimukubi .
PFX kk 0 tebulimukuli .
PFX kk 0 tebulimukuga .
PFX kk 0 tebulimukuka .
PFX kk 0 tebulimukubu .
PFX kk 0 tebulimukulu .
PFX kk 0 tebulimukuku .
PFX kk 0 tebulimukutu .
PFX kk 0 obutalimukun [^lmn]
PFX kk l obutalimukund l.[^mn]
PFX kk l obutalimukunn l.[mn]
PFX kk w obutalimukump [w]
PFX kk 0 obutalimukumu .
PFX kk 0 obutalimukuba .
PFX kk 0 obutalimukugu .
PFX kk 0 obutalimukugi .
PFX kk 0 obutalimukuzi .
PFX kk 0 obutalimukuki .
PFX kk 0 obutalimukubi .
PFX kk 0 obutalimukuli .
PFX kk 0 obutalimukuga .
PFX kk 0 obutalimukuka .
PFX kk 0 obutalimukubu .
PFX kk 0 obutalimukulu .
PFX kk 0 obutalimukuku .
PFX kk 0 obutalimukutu .
PFX kk 0 telulimukun [^lmn]
PFX kk l telulimukund l.[^mn]
PFX kk l telulimukunn l.[mn]
PFX kk w telulimukump [w]
PFX kk 0 telulimukumu .
PFX kk 0 telulimukuba .
PFX kk 0 telulimukugu .
PFX kk 0 telulimukugi .
PFX kk 0 telulimukuzi .
PFX kk 0 telulimukuki .
PFX kk 0 telulimukubi .
PFX kk 0 telulimukuli .
PFX kk 0 telulimukuga .
PFX kk 0 telulimukuka .
PFX kk 0 telulimukubu .
PFX kk 0 telulimukulu .
PFX kk 0 telulimukuku .
PFX kk 0 telulimukutu .
PFX kk 0 olutalimukun [^lmn]
PFX kk l olutalimukund l.[^mn]
PFX kk l olutalimukunn l.[mn]
PFX kk w olutalimukump [w]
PFX kk 0 olutalimukumu .
PFX kk 0 olutalimukuba .
PFX kk 0 olutalimukugu .
PFX kk 0 olutalimukugi .
PFX kk 0 olutalimukuzi .
PFX kk 0 olutalimukuki .
PFX kk 0 olutalimukubi .
PFX kk 0 olutalimukuli .
PFX kk 0 olutalimukuga .
PFX kk 0 olutalimukuka .
PFX kk 0 olutalimukubu .
PFX kk 0 olutalimukulu .
PFX kk 0 olutalimukuku .
PFX kk 0 olutalimukutu .
PFX kk 0 tezilimukun [^lmn]
PFX kk l tezilimukund l.[^mn]
PFX kk l tezilimukunn l.[mn]
PFX kk w tezilimukump [w]
PFX kk 0 tezilimukumu .
PFX kk 0 tezilimukuba .
PFX kk 0 tezilimukugu .
PFX kk 0 tezilimukugi .
PFX kk 0 tezilimukuzi .
PFX kk 0 tezilimukuki .
PFX kk 0 tezilimukubi .
PFX kk 0 tezilimukuli .
PFX kk 0 tezilimukuga .
PFX kk 0 tezilimukuka .
PFX kk 0 tezilimukubu .
PFX kk 0 tezilimukulu .
PFX kk 0 tezilimukuku .
PFX kk 0 tezilimukutu .
PFX kk 0 ezitalimukun [^lmn]
PFX kk l ezitalimukund l.[^mn]
PFX kk l ezitalimukunn l.[mn]
PFX kk w ezitalimukump [w]
PFX kk 0 ezitalimukumu .
PFX kk 0 ezitalimukuba .
PFX kk 0 ezitalimukugu .
PFX kk 0 ezitalimukugi .
PFX kk 0 ezitalimukuzi .
PFX kk 0 ezitalimukuki .
PFX kk 0 ezitalimukubi .
PFX kk 0 ezitalimukuli .
PFX kk 0 ezitalimukuga .
PFX kk 0 ezitalimukuka .
PFX kk 0 ezitalimukubu .
PFX kk 0 ezitalimukulu .
PFX kk 0 ezitalimukuku .
PFX kk 0 ezitalimukutu .
PFX kk 0 tekulimukun [^lmn]
PFX kk l tekulimukund l.[^mn]
PFX kk l tekulimukunn l.[mn]
PFX kk w tekulimukump [w]
PFX kk 0 tekulimukumu .
PFX kk 0 tekulimukuba .
PFX kk 0 tekulimukugu .
PFX kk 0 tekulimukugi .
PFX kk 0 tekulimukuzi .
PFX kk 0 tekulimukuki .
PFX kk 0 tekulimukubi .
PFX kk 0 tekulimukuli .
PFX kk 0 tekulimukuga .
PFX kk 0 tekulimukuka .
PFX kk 0 tekulimukubu .
PFX kk 0 tekulimukulu .
PFX kk 0 tekulimukuku .
PFX kk 0 tekulimukutu .
PFX kk 0 okutalimukun [^lmn]
PFX kk l okutalimukund l.[^mn]
PFX kk l okutalimukunn l.[mn]
PFX kk w okutalimukump [w]
PFX kk 0 okutalimukumu .
PFX kk 0 okutalimukuba .
PFX kk 0 okutalimukugu .
PFX kk 0 okutalimukugi .
PFX kk 0 okutalimukuzi .
PFX kk 0 okutalimukuki .
PFX kk 0 okutalimukubi .
PFX kk 0 okutalimukuli .
PFX kk 0 okutalimukuga .
PFX kk 0 okutalimukuka .
PFX kk 0 okutalimukubu .
PFX kk 0 okutalimukulu .
PFX kk 0 okutalimukuku .
PFX kk 0 okutalimukutu .
PFX kk 0 tegalimukun [^lmn]
PFX kk l tegalimukund l.[^mn]
PFX kk l tegalimukunn l.[mn]
PFX kk w tegalimukump [w]
PFX kk 0 tegalimukumu .
PFX kk 0 tegalimukuba .
PFX kk 0 tegalimukugu .
PFX kk 0 tegalimukugi .
PFX kk 0 tegalimukuzi .
PFX kk 0 tegalimukuki .
PFX kk 0 tegalimukubi .
PFX kk 0 tegalimukuli .
PFX kk 0 tegalimukuga .
PFX kk 0 tegalimukuka .
PFX kk 0 tegalimukubu .
PFX kk 0 tegalimukulu .
PFX kk 0 tegalimukuku .
PFX kk 0 tegalimukutu .
PFX kk 0 agatalimukun [^lmn]
PFX kk l agatalimukund l.[^mn]
PFX kk l agatalimukunn l.[mn]
PFX kk w agatalimukump [w]
PFX kk 0 agatalimukumu .
PFX kk 0 agatalimukuba .
PFX kk 0 agatalimukugu .
PFX kk 0 agatalimukugi .
PFX kk 0 agatalimukuzi .
PFX kk 0 agatalimukuki .
PFX kk 0 agatalimukubi .
PFX kk 0 agatalimukuli .
PFX kk 0 agatalimukuga .
PFX kk 0 agatalimukuka .
PFX kk 0 agatalimukubu .
PFX kk 0 agatalimukulu .
PFX kk 0 agatalimukuku .
PFX kk 0 agatalimukutu .
PFX kk 0 tetulimukun [^lmn]
PFX kk l tetulimukund l.[^mn]
PFX kk l tetulimukunn l.[mn]
PFX kk w tetulimukump [w]
PFX kk 0 tetulimukumu .
PFX kk 0 tetulimukuba .
PFX kk 0 tetulimukugu .
PFX kk 0 tetulimukugi .
PFX kk 0 tetulimukuzi .
PFX kk 0 tetulimukuki .
PFX kk 0 tetulimukubi .
PFX kk 0 tetulimukuli .
PFX kk 0 tetulimukuga .
PFX kk 0 tetulimukuka .
PFX kk 0 tetulimukubu .
PFX kk 0 tetulimukulu .
PFX kk 0 tetulimukuku .
PFX kk 0 tetulimukutu .
PFX kk 0 otutalimukun [^lmn]
PFX kk l otutalimukund l.[^mn]
PFX kk l otutalimukunn l.[mn]
PFX kk w otutalimukump [w]
PFX kk 0 otutalimukumu .
PFX kk 0 otutalimukuba .
PFX kk 0 otutalimukugu .
PFX kk 0 otutalimukugi .
PFX kk 0 otutalimukuzi .
PFX kk 0 otutalimukuki .
PFX kk 0 otutalimukubi .
PFX kk 0 otutalimukuli .
PFX kk 0 otutalimukuga .
PFX kk 0 otutalimukuka .
PFX kk 0 otutalimukubu .
PFX kk 0 otutalimukulu .
PFX kk 0 otutalimukuku .
PFX kk 0 otutalimukutu ."""

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
    "kk": "kk",
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

    out_flag = "IV"
    left_desc = FLAG_DESCRIPTIONS.get("kk", "kk")
    right_desc = FLAG_DESCRIPTIONS.get("OR", "OR")
    comment_line = "# Cross product of {} ({}) and {} ({}) to {}".format(
        "kk", left_desc, "OR", right_desc, out_flag
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
