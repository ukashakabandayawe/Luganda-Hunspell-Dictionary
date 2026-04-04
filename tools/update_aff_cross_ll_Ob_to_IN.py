import re
import os
from pathlib import Path

# Cross product generator: ll x Ob => IN
# Description:
# - Left block `ll`: ll
# - Right block `Ob`: Object markers
# - Output flag `IN`: Cross-product prefixes for ll x Ob

REPO_ROOT = Path(__file__).resolve().parents[1]
AFF_FILE = REPO_ROOT / "Luganda.aff"

# If set to a flag name (e.g. "HB"), the generated cross-product block will be inserted
# immediately before the first "PFX <flag>" line when the output flag block doesn't
# already exist in the .aff.
INSERT_BEFORE_FLAG = "".strip() or None

rule_left_raw = """
PFX ll Y 698
PFX ll 0 ndimukumu .
PFX ll 0 ndimukuba .
PFX ll 0 ndimukugu .
PFX ll 0 ndimukugi .
PFX ll 0 ndimukuzi .
PFX ll 0 ndimukuki .
PFX ll 0 ndimukubi .
PFX ll 0 ndimukuli .
PFX ll 0 ndimukuga .
PFX ll 0 ndimukuka .
PFX ll 0 ndimukubu .
PFX ll 0 ndimukulu .
PFX ll 0 ndimukuku .
PFX ll 0 ndimukutu .
PFX ll 0 olimukun [^lmn]
PFX ll l olimukund l.[^mn]
PFX ll l olimukunn l.[mn]
PFX ll w olimukump [w]
PFX ll 0 olimukumu .
PFX ll 0 olimukuba .
PFX ll 0 olimukugu .
PFX ll 0 olimukugi .
PFX ll 0 olimukuzi .
PFX ll 0 olimukuki .
PFX ll 0 olimukubi .
PFX ll 0 olimukuli .
PFX ll 0 olimukuga .
PFX ll 0 olimukuka .
PFX ll 0 olimukubu .
PFX ll 0 olimukulu .
PFX ll 0 olimukuku .
PFX ll 0 olimukutu .
PFX ll 0 alimukun [^lmn]
PFX ll l alimukund l.[^mn]
PFX ll l alimukunn l.[mn]
PFX ll w alimukump [w]
PFX ll 0 alimukumu .
PFX ll 0 alimukuba .
PFX ll 0 alimukugu .
PFX ll 0 alimukugi .
PFX ll 0 alimukuzi .
PFX ll 0 alimukuki .
PFX ll 0 alimukubi .
PFX ll 0 alimukuli .
PFX ll 0 alimukuga .
PFX ll 0 alimukuka .
PFX ll 0 alimukubu .
PFX ll 0 alimukulu .
PFX ll 0 alimukuku .
PFX ll 0 alimukutu .
PFX ll 0 tulimukun [^lmn]
PFX ll l tulimukund l.[^mn]
PFX ll l tulimukunn l.[mn]
PFX ll w tulimukump [w]
PFX ll 0 tulimukumu .
PFX ll 0 tulimukuba .
PFX ll 0 tulimukugu .
PFX ll 0 tulimukugi .
PFX ll 0 tulimukuzi .
PFX ll 0 tulimukuki .
PFX ll 0 tulimukubi .
PFX ll 0 tulimukuli .
PFX ll 0 tulimukuga .
PFX ll 0 tulimukuka .
PFX ll 0 tulimukubu .
PFX ll 0 tulimukulu .
PFX ll 0 tulimukuku .
PFX ll 0 tulimukutu .
PFX ll 0 mulimukun [^lmn]
PFX ll l mulimukund l.[^mn]
PFX ll l mulimukunn l.[mn]
PFX ll w mulimukump [w]
PFX ll 0 mulimukumu .
PFX ll 0 mulimukuba .
PFX ll 0 mulimukugu .
PFX ll 0 mulimukugi .
PFX ll 0 mulimukuzi .
PFX ll 0 mulimukuki .
PFX ll 0 mulimukubi .
PFX ll 0 mulimukuli .
PFX ll 0 mulimukuga .
PFX ll 0 mulimukuka .
PFX ll 0 mulimukubu .
PFX ll 0 mulimukulu .
PFX ll 0 mulimukuku .
PFX ll 0 mulimukutu .
PFX ll 0 balimukun [^lmn]
PFX ll l balimukund l.[^mn]
PFX ll l balimukunn l.[mn]
PFX ll w balimukump [w]
PFX ll 0 balimukumu .
PFX ll 0 balimukuba .
PFX ll 0 balimukugu .
PFX ll 0 balimukugi .
PFX ll 0 balimukuzi .
PFX ll 0 balimukuki .
PFX ll 0 balimukubi .
PFX ll 0 balimukuli .
PFX ll 0 balimukuga .
PFX ll 0 balimukuka .
PFX ll 0 balimukubu .
PFX ll 0 balimukulu .
PFX ll 0 balimukuku .
PFX ll 0 balimukutu .
PFX ll 0 abalimukun [^lmn]
PFX ll l abalimukund l.[^mn]
PFX ll l abalimukunn l.[mn]
PFX ll w abalimukump [w]
PFX ll 0 abalimukumu .
PFX ll 0 abalimukuba .
PFX ll 0 abalimukugu .
PFX ll 0 abalimukugi .
PFX ll 0 abalimukuzi .
PFX ll 0 abalimukuki .
PFX ll 0 abalimukubi .
PFX ll 0 abalimukuli .
PFX ll 0 abalimukuga .
PFX ll 0 abalimukuka .
PFX ll 0 abalimukubu .
PFX ll 0 abalimukulu .
PFX ll 0 abalimukuku .
PFX ll 0 abalimukutu .
PFX ll 0 alimukun [^lmn]
PFX ll l alimukund l.[^mn]
PFX ll l alimukunn l.[mn]
PFX ll w alimukump [w]
PFX ll 0 alimukumu .
PFX ll 0 alimukuba .
PFX ll 0 alimukugu .
PFX ll 0 alimukugi .
PFX ll 0 alimukuzi .
PFX ll 0 alimukuki .
PFX ll 0 alimukubi .
PFX ll 0 alimukuli .
PFX ll 0 alimukuga .
PFX ll 0 alimukuka .
PFX ll 0 alimukubu .
PFX ll 0 alimukulu .
PFX ll 0 alimukuku .
PFX ll 0 alimukutu .
PFX ll 0 balimukun [^lmn]
PFX ll l balimukund l.[^mn]
PFX ll l balimukunn l.[mn]
PFX ll w balimukump [w]
PFX ll 0 balimukumu .
PFX ll 0 balimukuba .
PFX ll 0 balimukugu .
PFX ll 0 balimukugi .
PFX ll 0 balimukuzi .
PFX ll 0 balimukuki .
PFX ll 0 balimukubi .
PFX ll 0 balimukuli .
PFX ll 0 balimukuga .
PFX ll 0 balimukuka .
PFX ll 0 balimukubu .
PFX ll 0 balimukulu .
PFX ll 0 balimukuku .
PFX ll 0 balimukutu .
PFX ll 0 abalimukun [^lmn]
PFX ll l abalimukund l.[^mn]
PFX ll l abalimukunn l.[mn]
PFX ll w abalimukump [w]
PFX ll 0 abalimukumu .
PFX ll 0 abalimukuba .
PFX ll 0 abalimukugu .
PFX ll 0 abalimukugi .
PFX ll 0 abalimukuzi .
PFX ll 0 abalimukuki .
PFX ll 0 abalimukubi .
PFX ll 0 abalimukuli .
PFX ll 0 abalimukuga .
PFX ll 0 abalimukuka .
PFX ll 0 abalimukubu .
PFX ll 0 abalimukulu .
PFX ll 0 abalimukuku .
PFX ll 0 abalimukutu .
PFX ll 0 gulimukun [^lmn]
PFX ll l gulimukund l.[^mn]
PFX ll l gulimukunn l.[mn]
PFX ll w gulimukump [w]
PFX ll 0 gulimukumu .
PFX ll 0 gulimukuba .
PFX ll 0 gulimukugu .
PFX ll 0 gulimukugi .
PFX ll 0 gulimukuzi .
PFX ll 0 gulimukuki .
PFX ll 0 gulimukubi .
PFX ll 0 gulimukuli .
PFX ll 0 gulimukuga .
PFX ll 0 gulimukuka .
PFX ll 0 gulimukubu .
PFX ll 0 gulimukulu .
PFX ll 0 gulimukuku .
PFX ll 0 gulimukutu .
PFX ll 0 ogulimukun [^lmn]
PFX ll l ogulimukund l.[^mn]
PFX ll l ogulimukunn l.[mn]
PFX ll w ogulimukump [w]
PFX ll 0 ogulimukumu .
PFX ll 0 ogulimukuba .
PFX ll 0 ogulimukugu .
PFX ll 0 ogulimukugi .
PFX ll 0 ogulimukuzi .
PFX ll 0 ogulimukuki .
PFX ll 0 ogulimukubi .
PFX ll 0 ogulimukuli .
PFX ll 0 ogulimukuga .
PFX ll 0 ogulimukuka .
PFX ll 0 ogulimukubu .
PFX ll 0 ogulimukulu .
PFX ll 0 ogulimukuku .
PFX ll 0 ogulimukutu .
PFX ll 0 gilimukun [^lmn]
PFX ll l gilimukund l.[^mn]
PFX ll l gilimukunn l.[mn]
PFX ll w gilimukump [w]
PFX ll 0 gilimukumu .
PFX ll 0 gilimukuba .
PFX ll 0 gilimukugu .
PFX ll 0 gilimukugi .
PFX ll 0 gilimukuzi .
PFX ll 0 gilimukuki .
PFX ll 0 gilimukubi .
PFX ll 0 gilimukuli .
PFX ll 0 gilimukuga .
PFX ll 0 gilimukuka .
PFX ll 0 gilimukubu .
PFX ll 0 gilimukulu .
PFX ll 0 gilimukuku .
PFX ll 0 gilimukutu .
PFX ll 0 egilimukun [^lmn]
PFX ll l egilimukund l.[^mn]
PFX ll l egilimukunn l.[mn]
PFX ll w egilimukump [w]
PFX ll 0 egilimukumu .
PFX ll 0 egilimukuba .
PFX ll 0 egilimukugu .
PFX ll 0 egilimukugi .
PFX ll 0 egilimukuzi .
PFX ll 0 egilimukuki .
PFX ll 0 egilimukubi .
PFX ll 0 egilimukuli .
PFX ll 0 egilimukuga .
PFX ll 0 egilimukuka .
PFX ll 0 egilimukubu .
PFX ll 0 egilimukulu .
PFX ll 0 egilimukuku .
PFX ll 0 egilimukutu .
PFX ll 0 elimukun [^lmn]
PFX ll l elimukund l.[^mn]
PFX ll l elimukunn l.[mn]
PFX ll w elimukump [w]
PFX ll 0 elimukumu .
PFX ll 0 elimukuba .
PFX ll 0 elimukugu .
PFX ll 0 elimukugi .
PFX ll 0 elimukuzi .
PFX ll 0 elimukuki .
PFX ll 0 elimukubi .
PFX ll 0 elimukuli .
PFX ll 0 elimukuga .
PFX ll 0 elimukuka .
PFX ll 0 elimukubu .
PFX ll 0 elimukulu .
PFX ll 0 elimukuku .
PFX ll 0 elimukutu .
PFX ll 0 zilimukun [^lmn]
PFX ll l zilimukund l.[^mn]
PFX ll l zilimukunn l.[mn]
PFX ll w zilimukump [w]
PFX ll 0 zilimukumu .
PFX ll 0 zilimukuba .
PFX ll 0 zilimukugu .
PFX ll 0 zilimukugi .
PFX ll 0 zilimukuzi .
PFX ll 0 zilimukuki .
PFX ll 0 zilimukubi .
PFX ll 0 zilimukuli .
PFX ll 0 zilimukuga .
PFX ll 0 zilimukuka .
PFX ll 0 zilimukubu .
PFX ll 0 zilimukulu .
PFX ll 0 zilimukuku .
PFX ll 0 zilimukutu .
PFX ll 0 ezilimukun [^lmn]
PFX ll l ezilimukund l.[^mn]
PFX ll l ezilimukunn l.[mn]
PFX ll w ezilimukump [w]
PFX ll 0 ezilimukumu .
PFX ll 0 ezilimukuba .
PFX ll 0 ezilimukugu .
PFX ll 0 ezilimukugi .
PFX ll 0 ezilimukuzi .
PFX ll 0 ezilimukuki .
PFX ll 0 ezilimukubi .
PFX ll 0 ezilimukuli .
PFX ll 0 ezilimukuga .
PFX ll 0 ezilimukuka .
PFX ll 0 ezilimukubu .
PFX ll 0 ezilimukulu .
PFX ll 0 ezilimukuku .
PFX ll 0 ezilimukutu .
PFX ll 0 kilimukun [^lmn]
PFX ll l kilimukund l.[^mn]
PFX ll l kilimukunn l.[mn]
PFX ll w kilimukump [w]
PFX ll 0 kilimukumu .
PFX ll 0 kilimukuba .
PFX ll 0 kilimukugu .
PFX ll 0 kilimukugi .
PFX ll 0 kilimukuzi .
PFX ll 0 kilimukuki .
PFX ll 0 kilimukubi .
PFX ll 0 kilimukuli .
PFX ll 0 kilimukuga .
PFX ll 0 kilimukuka .
PFX ll 0 kilimukubu .
PFX ll 0 kilimukulu .
PFX ll 0 kilimukuku .
PFX ll 0 kilimukutu .
PFX ll 0 ekilimukun [^lmn]
PFX ll l ekilimukund l.[^mn]
PFX ll l ekilimukunn l.[mn]
PFX ll w ekilimukump [w]
PFX ll 0 ekilimukumu .
PFX ll 0 ekilimukuba .
PFX ll 0 ekilimukugu .
PFX ll 0 ekilimukugi .
PFX ll 0 ekilimukuzi .
PFX ll 0 ekilimukuki .
PFX ll 0 ekilimukubi .
PFX ll 0 ekilimukuli .
PFX ll 0 ekilimukuga .
PFX ll 0 ekilimukuka .
PFX ll 0 ekilimukubu .
PFX ll 0 ekilimukulu .
PFX ll 0 ekilimukuku .
PFX ll 0 ekilimukutu .
PFX ll 0 bilimukun [^lmn]
PFX ll l bilimukund l.[^mn]
PFX ll l bilimukunn l.[mn]
PFX ll w bilimukump [w]
PFX ll 0 bilimukumu .
PFX ll 0 bilimukuba .
PFX ll 0 bilimukugu .
PFX ll 0 bilimukugi .
PFX ll 0 bilimukuzi .
PFX ll 0 bilimukuki .
PFX ll 0 bilimukubi .
PFX ll 0 bilimukuli .
PFX ll 0 bilimukuga .
PFX ll 0 bilimukuka .
PFX ll 0 bilimukubu .
PFX ll 0 bilimukulu .
PFX ll 0 bilimukuku .
PFX ll 0 bilimukutu .
PFX ll 0 ebilimukun [^lmn]
PFX ll l ebilimukund l.[^mn]
PFX ll l ebilimukunn l.[mn]
PFX ll w ebilimukump [w]
PFX ll 0 ebilimukumu .
PFX ll 0 ebilimukuba .
PFX ll 0 ebilimukugu .
PFX ll 0 ebilimukugi .
PFX ll 0 ebilimukuzi .
PFX ll 0 ebilimukuki .
PFX ll 0 ebilimukubi .
PFX ll 0 ebilimukuli .
PFX ll 0 ebilimukuga .
PFX ll 0 ebilimukuka .
PFX ll 0 ebilimukubu .
PFX ll 0 ebilimukulu .
PFX ll 0 ebilimukuku .
PFX ll 0 ebilimukutu .
PFX ll 0 lilimukun [^lmn]
PFX ll l lilimukund l.[^mn]
PFX ll l lilimukunn l.[mn]
PFX ll w lilimukump [w]
PFX ll 0 lilimukumu .
PFX ll 0 lilimukuba .
PFX ll 0 lilimukugu .
PFX ll 0 lilimukugi .
PFX ll 0 lilimukuzi .
PFX ll 0 lilimukuki .
PFX ll 0 lilimukubi .
PFX ll 0 lilimukuli .
PFX ll 0 lilimukuga .
PFX ll 0 lilimukuka .
PFX ll 0 lilimukubu .
PFX ll 0 lilimukulu .
PFX ll 0 lilimukuku .
PFX ll 0 lilimukutu .
PFX ll 0 elilimukun [^lmn]
PFX ll l elilimukund l.[^mn]
PFX ll l elilimukunn l.[mn]
PFX ll w elilimukump [w]
PFX ll 0 elilimukumu .
PFX ll 0 elilimukuba .
PFX ll 0 elilimukugu .
PFX ll 0 elilimukugi .
PFX ll 0 elilimukuzi .
PFX ll 0 elilimukuki .
PFX ll 0 elilimukubi .
PFX ll 0 elilimukuli .
PFX ll 0 elilimukuga .
PFX ll 0 elilimukuka .
PFX ll 0 elilimukubu .
PFX ll 0 elilimukulu .
PFX ll 0 elilimukuku .
PFX ll 0 elilimukutu .
PFX ll 0 galimukun [^lmn]
PFX ll l galimukund l.[^mn]
PFX ll l galimukunn l.[mn]
PFX ll w galimukump [w]
PFX ll 0 galimukumu .
PFX ll 0 galimukuba .
PFX ll 0 galimukugu .
PFX ll 0 galimukugi .
PFX ll 0 galimukuzi .
PFX ll 0 galimukuki .
PFX ll 0 galimukubi .
PFX ll 0 galimukuli .
PFX ll 0 galimukuga .
PFX ll 0 galimukuka .
PFX ll 0 galimukubu .
PFX ll 0 galimukulu .
PFX ll 0 galimukuku .
PFX ll 0 galimukutu .
PFX ll 0 agalimukun [^lmn]
PFX ll l agalimukund l.[^mn]
PFX ll l agalimukunn l.[mn]
PFX ll w agalimukump [w]
PFX ll 0 agalimukumu .
PFX ll 0 agalimukuba .
PFX ll 0 agalimukugu .
PFX ll 0 agalimukugi .
PFX ll 0 agalimukuzi .
PFX ll 0 agalimukuki .
PFX ll 0 agalimukubi .
PFX ll 0 agalimukuli .
PFX ll 0 agalimukuga .
PFX ll 0 agalimukuka .
PFX ll 0 agalimukubu .
PFX ll 0 agalimukulu .
PFX ll 0 agalimukuku .
PFX ll 0 agalimukutu .
PFX ll 0 kalimukun [^lmn]
PFX ll l kalimukund l.[^mn]
PFX ll l kalimukunn l.[mn]
PFX ll w kalimukump [w]
PFX ll 0 kalimukumu .
PFX ll 0 kalimukuba .
PFX ll 0 kalimukugu .
PFX ll 0 kalimukugi .
PFX ll 0 kalimukuzi .
PFX ll 0 kalimukuki .
PFX ll 0 kalimukubi .
PFX ll 0 kalimukuli .
PFX ll 0 kalimukuga .
PFX ll 0 kalimukuka .
PFX ll 0 kalimukubu .
PFX ll 0 kalimukulu .
PFX ll 0 kalimukuku .
PFX ll 0 kalimukutu .
PFX ll 0 akalimukun [^lmn]
PFX ll l akalimukund l.[^mn]
PFX ll l akalimukunn l.[mn]
PFX ll w akalimukump [w]
PFX ll 0 akalimukumu .
PFX ll 0 akalimukuba .
PFX ll 0 akalimukugu .
PFX ll 0 akalimukugi .
PFX ll 0 akalimukuzi .
PFX ll 0 akalimukuki .
PFX ll 0 akalimukubi .
PFX ll 0 akalimukuli .
PFX ll 0 akalimukuga .
PFX ll 0 akalimukuka .
PFX ll 0 akalimukubu .
PFX ll 0 akalimukulu .
PFX ll 0 akalimukuku .
PFX ll 0 akalimukutu .
PFX ll 0 bulimukun [^lmn]
PFX ll l bulimukund l.[^mn]
PFX ll l bulimukunn l.[mn]
PFX ll w bulimukump [w]
PFX ll 0 bulimukumu .
PFX ll 0 bulimukuba .
PFX ll 0 bulimukugu .
PFX ll 0 bulimukugi .
PFX ll 0 bulimukuzi .
PFX ll 0 bulimukuki .
PFX ll 0 bulimukubi .
PFX ll 0 bulimukuli .
PFX ll 0 bulimukuga .
PFX ll 0 bulimukuka .
PFX ll 0 bulimukubu .
PFX ll 0 bulimukulu .
PFX ll 0 bulimukuku .
PFX ll 0 bulimukutu .
PFX ll 0 obulimukun [^lmn]
PFX ll l obulimukund l.[^mn]
PFX ll l obulimukunn l.[mn]
PFX ll w obulimukump [w]
PFX ll 0 obulimukumu .
PFX ll 0 obulimukuba .
PFX ll 0 obulimukugu .
PFX ll 0 obulimukugi .
PFX ll 0 obulimukuzi .
PFX ll 0 obulimukuki .
PFX ll 0 obulimukubi .
PFX ll 0 obulimukuli .
PFX ll 0 obulimukuga .
PFX ll 0 obulimukuka .
PFX ll 0 obulimukubu .
PFX ll 0 obulimukulu .
PFX ll 0 obulimukuku .
PFX ll 0 obulimukutu .
PFX ll 0 lulimukun [^lmn]
PFX ll l lulimukund l.[^mn]
PFX ll l lulimukunn l.[mn]
PFX ll w lulimukump [w]
PFX ll 0 lulimukumu .
PFX ll 0 lulimukuba .
PFX ll 0 lulimukugu .
PFX ll 0 lulimukugi .
PFX ll 0 lulimukuzi .
PFX ll 0 lulimukuki .
PFX ll 0 lulimukubi .
PFX ll 0 lulimukuli .
PFX ll 0 lulimukuga .
PFX ll 0 lulimukuka .
PFX ll 0 lulimukubu .
PFX ll 0 lulimukulu .
PFX ll 0 lulimukuku .
PFX ll 0 lulimukutu .
PFX ll 0 olulimukun [^lmn]
PFX ll l olulimukund l.[^mn]
PFX ll l olulimukunn l.[mn]
PFX ll w olulimukump [w]
PFX ll 0 olulimukumu .
PFX ll 0 olulimukuba .
PFX ll 0 olulimukugu .
PFX ll 0 olulimukugi .
PFX ll 0 olulimukuzi .
PFX ll 0 olulimukuki .
PFX ll 0 olulimukubi .
PFX ll 0 olulimukuli .
PFX ll 0 olulimukuga .
PFX ll 0 olulimukuka .
PFX ll 0 olulimukubu .
PFX ll 0 olulimukulu .
PFX ll 0 olulimukuku .
PFX ll 0 olulimukutu .
PFX ll 0 zilimukun [^lmn]
PFX ll l zilimukund l.[^mn]
PFX ll l zilimukunn l.[mn]
PFX ll w zilimukump [w]
PFX ll 0 zilimukumu .
PFX ll 0 zilimukuba .
PFX ll 0 zilimukugu .
PFX ll 0 zilimukugi .
PFX ll 0 zilimukuzi .
PFX ll 0 zilimukuki .
PFX ll 0 zilimukubi .
PFX ll 0 zilimukuli .
PFX ll 0 zilimukuga .
PFX ll 0 zilimukuka .
PFX ll 0 zilimukubu .
PFX ll 0 zilimukulu .
PFX ll 0 zilimukuku .
PFX ll 0 zilimukutu .
PFX ll 0 ezilimukun [^lmn]
PFX ll l ezilimukund l.[^mn]
PFX ll l ezilimukunn l.[mn]
PFX ll w ezilimukump [w]
PFX ll 0 ezilimukumu .
PFX ll 0 ezilimukuba .
PFX ll 0 ezilimukugu .
PFX ll 0 ezilimukugi .
PFX ll 0 ezilimukuzi .
PFX ll 0 ezilimukuki .
PFX ll 0 ezilimukubi .
PFX ll 0 ezilimukuli .
PFX ll 0 ezilimukuga .
PFX ll 0 ezilimukuka .
PFX ll 0 ezilimukubu .
PFX ll 0 ezilimukulu .
PFX ll 0 ezilimukuku .
PFX ll 0 ezilimukutu .
PFX ll 0 kulimukun [^lmn]
PFX ll l kulimukund l.[^mn]
PFX ll l kulimukunn l.[mn]
PFX ll w kulimukump [w]
PFX ll 0 kulimukumu .
PFX ll 0 kulimukuba .
PFX ll 0 kulimukugu .
PFX ll 0 kulimukugi .
PFX ll 0 kulimukuzi .
PFX ll 0 kulimukuki .
PFX ll 0 kulimukubi .
PFX ll 0 kulimukuli .
PFX ll 0 kulimukuga .
PFX ll 0 kulimukuka .
PFX ll 0 kulimukubu .
PFX ll 0 kulimukulu .
PFX ll 0 kulimukuku .
PFX ll 0 kulimukutu .
PFX ll 0 okulimukun [^lmn]
PFX ll l okulimukund l.[^mn]
PFX ll l okulimukunn l.[mn]
PFX ll w okulimukump [w]
PFX ll 0 okulimukumu .
PFX ll 0 okulimukuba .
PFX ll 0 okulimukugu .
PFX ll 0 okulimukugi .
PFX ll 0 okulimukuzi .
PFX ll 0 okulimukuki .
PFX ll 0 okulimukubi .
PFX ll 0 okulimukuli .
PFX ll 0 okulimukuga .
PFX ll 0 okulimukuka .
PFX ll 0 okulimukubu .
PFX ll 0 okulimukulu .
PFX ll 0 okulimukuku .
PFX ll 0 okulimukutu .
PFX ll 0 galimukun [^lmn]
PFX ll l galimukund l.[^mn]
PFX ll l galimukunn l.[mn]
PFX ll w galimukump [w]
PFX ll 0 galimukumu .
PFX ll 0 galimukuba .
PFX ll 0 galimukugu .
PFX ll 0 galimukugi .
PFX ll 0 galimukuzi .
PFX ll 0 galimukuki .
PFX ll 0 galimukubi .
PFX ll 0 galimukuli .
PFX ll 0 galimukuga .
PFX ll 0 galimukuka .
PFX ll 0 galimukubu .
PFX ll 0 galimukulu .
PFX ll 0 galimukuku .
PFX ll 0 galimukutu .
PFX ll 0 galimukun [^lmn]
PFX ll l galimukund l.[^mn]
PFX ll l galimukunn l.[mn]
PFX ll w galimukump [w]
PFX ll 0 galimukumu .
PFX ll 0 galimukuba .
PFX ll 0 galimukugu .
PFX ll 0 galimukugi .
PFX ll 0 galimukuzi .
PFX ll 0 galimukuki .
PFX ll 0 galimukubi .
PFX ll 0 galimukuli .
PFX ll 0 galimukuga .
PFX ll 0 galimukuka .
PFX ll 0 galimukubu .
PFX ll 0 galimukulu .
PFX ll 0 galimukuku .
PFX ll 0 galimukutu .
PFX ll 0 tulimukun [^lmn]
PFX ll l tulimukund l.[^mn]
PFX ll l tulimukunn l.[mn]
PFX ll w tulimukump [w]
PFX ll 0 tulimukumu .
PFX ll 0 tulimukuba .
PFX ll 0 tulimukugu .
PFX ll 0 tulimukugi .
PFX ll 0 tulimukuzi .
PFX ll 0 tulimukuki .
PFX ll 0 tulimukubi .
PFX ll 0 tulimukuli .
PFX ll 0 tulimukuga .
PFX ll 0 tulimukuka .
PFX ll 0 tulimukubu .
PFX ll 0 tulimukulu .
PFX ll 0 tulimukuku .
PFX ll 0 tulimukutu .
PFX ll 0 otulimukun [^lmn]
PFX ll l otulimukund l.[^mn]
PFX ll l otulimukunn l.[mn]
PFX ll w otulimukump [w]
PFX ll 0 otulimukumu .
PFX ll 0 otulimukuba .
PFX ll 0 otulimukugu .
PFX ll 0 otulimukugi .
PFX ll 0 otulimukuzi .
PFX ll 0 otulimukuki .
PFX ll 0 otulimukubi .
PFX ll 0 otulimukuli .
PFX ll 0 otulimukuga .
PFX ll 0 otulimukuka .
PFX ll 0 otulimukubu .
PFX ll 0 otulimukulu .
PFX ll 0 otulimukuku .
PFX ll 0 otulimukutu ."""

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
    "ll": "ll",
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

    out_flag = "IN"
    left_desc = FLAG_DESCRIPTIONS.get("ll", "ll")
    right_desc = FLAG_DESCRIPTIONS.get("Ob", "Ob")
    comment_line = "# Cross product of {} ({}) and {} ({}) to {}".format(
        "ll", left_desc, "Ob", right_desc, out_flag
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
