import re
import os
from pathlib import Path

# Cross product generator: tt x Ob => IQ
# Description:
# - Left block `tt`: tt
# - Right block `Ob`: Object markers
# - Output flag `IQ`: Cross-product prefixes for tt x Ob

REPO_ROOT = Path(__file__).resolve().parents[1]
AFF_FILE = REPO_ROOT / "Luganda.aff"

# If set to a flag name (e.g. "HB"), the generated cross-product block will be inserted
# immediately before the first "PFX <flag>" line when the output flag block doesn't
# already exist in the .aff.
INSERT_BEFORE_FLAG = "".strip() or None

rule_left_raw = """
PFX tt Y 590
PFX tt 0 saalimukumu .
PFX tt 0 saalimukuba .
PFX tt 0 saalimukugu .
PFX tt 0 saalimukugi .
PFX tt 0 saalimukuzi .
PFX tt 0 saalimukuki .
PFX tt 0 saalimukubi .
PFX tt 0 saalimukuli .
PFX tt 0 saalimukuga .
PFX tt 0 saalimukuka .
PFX tt 0 saalimukubu .
PFX tt 0 saalimukulu .
PFX tt 0 saalimukuku .
PFX tt 0 saalimukutu .
PFX tt 0 tewalimukun [^lmn]
PFX tt l tewalimukund l.[^mn]
PFX tt l tewalimukunn l.[mn]
PFX tt w tewalimukump [w]
PFX tt 0 tewalimukumu .
PFX tt 0 tewalimukuba .
PFX tt 0 tewalimukugu .
PFX tt 0 tewalimukugi .
PFX tt 0 tewalimukuzi .
PFX tt 0 tewalimukuki .
PFX tt 0 tewalimukubi .
PFX tt 0 tewalimukuli .
PFX tt 0 tewalimukuga .
PFX tt 0 tewalimukuka .
PFX tt 0 tewalimukubu .
PFX tt 0 tewalimukulu .
PFX tt 0 tewalimukuku .
PFX tt 0 tewalimukutu .
PFX tt 0 teyalimukun [^lmn]
PFX tt l teyalimukund l.[^mn]
PFX tt l teyalimukunn l.[mn]
PFX tt w teyalimukump [w]
PFX tt 0 teyalimukumu .
PFX tt 0 teyalimukuba .
PFX tt 0 teyalimukugu .
PFX tt 0 teyalimukugi .
PFX tt 0 teyalimukuzi .
PFX tt 0 teyalimukuki .
PFX tt 0 teyalimukubi .
PFX tt 0 teyalimukuli .
PFX tt 0 teyalimukuga .
PFX tt 0 teyalimukuka .
PFX tt 0 teyalimukubu .
PFX tt 0 teyalimukulu .
PFX tt 0 teyalimukuku .
PFX tt 0 teyalimukutu .
PFX tt 0 tetwalimukun [^lmn]
PFX tt l tetwalimukund l.[^mn]
PFX tt l tetwalimukunn l.[mn]
PFX tt w tetwalimukump [w]
PFX tt 0 tetwalimukumu .
PFX tt 0 tetwalimukuba .
PFX tt 0 tetwalimukugu .
PFX tt 0 tetwalimukugi .
PFX tt 0 tetwalimukuzi .
PFX tt 0 tetwalimukuki .
PFX tt 0 tetwalimukubi .
PFX tt 0 tetwalimukuli .
PFX tt 0 tetwalimukuga .
PFX tt 0 tetwalimukuka .
PFX tt 0 tetwalimukubu .
PFX tt 0 tetwalimukulu .
PFX tt 0 tetwalimukuku .
PFX tt 0 tetwalimukutu .
PFX tt 0 temwalimukun [^lmn]
PFX tt l temwalimukund l.[^mn]
PFX tt l temwalimukunn l.[mn]
PFX tt w temwalimukump [w]
PFX tt 0 temwalimukumu .
PFX tt 0 temwalimukuba .
PFX tt 0 temwalimukugu .
PFX tt 0 temwalimukugi .
PFX tt 0 temwalimukuzi .
PFX tt 0 temwalimukuki .
PFX tt 0 temwalimukubi .
PFX tt 0 temwalimukuli .
PFX tt 0 temwalimukuga .
PFX tt 0 temwalimukuka .
PFX tt 0 temwalimukubu .
PFX tt 0 temwalimukulu .
PFX tt 0 temwalimukuku .
PFX tt 0 temwalimukutu .
PFX tt 0 tebaalimukun [^lmn]
PFX tt l tebaalimukund l.[^mn]
PFX tt l tebaalimukunn l.[mn]
PFX tt w tebaalimukump [w]
PFX tt 0 tebaalimukumu .
PFX tt 0 tebaalimukuba .
PFX tt 0 tebaalimukugu .
PFX tt 0 tebaalimukugi .
PFX tt 0 tebaalimukuzi .
PFX tt 0 tebaalimukuki .
PFX tt 0 tebaalimukubi .
PFX tt 0 tebaalimukuli .
PFX tt 0 tebaalimukuga .
PFX tt 0 tebaalimukuka .
PFX tt 0 tebaalimukubu .
PFX tt 0 tebaalimukulu .
PFX tt 0 tebaalimukuku .
PFX tt 0 tebaalimukutu .
PFX tt 0 abataalimukun [^lmn]
PFX tt l abataalimukund l.[^mn]
PFX tt l abataalimukunn l.[mn]
PFX tt w abataalimukump [w]
PFX tt 0 abataalimukumu .
PFX tt 0 abataalimukuba .
PFX tt 0 abataalimukugu .
PFX tt 0 abataalimukugi .
PFX tt 0 abataalimukuzi .
PFX tt 0 abataalimukuki .
PFX tt 0 abataalimukubi .
PFX tt 0 abataalimukuli .
PFX tt 0 abataalimukuga .
PFX tt 0 abataalimukuka .
PFX tt 0 abataalimukubu .
PFX tt 0 abataalimukulu .
PFX tt 0 abataalimukuku .
PFX tt 0 abataalimukutu .
PFX tt 0 tegwalimukun [^lmn]
PFX tt l tegwalimukund l.[^mn]
PFX tt l tegwalimukunn l.[mn]
PFX tt w tegwalimukump [w]
PFX tt 0 tegwalimukumu .
PFX tt 0 tegwalimukuba .
PFX tt 0 tegwalimukugu .
PFX tt 0 tegwalimukugi .
PFX tt 0 tegwalimukuzi .
PFX tt 0 tegwalimukuki .
PFX tt 0 tegwalimukubi .
PFX tt 0 tegwalimukuli .
PFX tt 0 tegwalimukuga .
PFX tt 0 tegwalimukuka .
PFX tt 0 tegwalimukubu .
PFX tt 0 tegwalimukulu .
PFX tt 0 tegwalimukuku .
PFX tt 0 tegwalimukutu .
PFX tt 0 ogutaalimukun [^lmn]
PFX tt l ogutaalimukund l.[^mn]
PFX tt l ogutaalimukunn l.[mn]
PFX tt w ogutaalimukump [w]
PFX tt 0 ogutaalimukumu .
PFX tt 0 ogutaalimukuba .
PFX tt 0 ogutaalimukugu .
PFX tt 0 ogutaalimukugi .
PFX tt 0 ogutaalimukuzi .
PFX tt 0 ogutaalimukuki .
PFX tt 0 ogutaalimukubi .
PFX tt 0 ogutaalimukuli .
PFX tt 0 ogutaalimukuga .
PFX tt 0 ogutaalimukuka .
PFX tt 0 ogutaalimukubu .
PFX tt 0 ogutaalimukulu .
PFX tt 0 ogutaalimukuku .
PFX tt 0 ogutaalimukutu .
PFX tt 0 tegyalimukun [^lmn]
PFX tt l tegyalimukund l.[^mn]
PFX tt l tegyalimukunn l.[mn]
PFX tt w tegyalimukump [w]
PFX tt 0 tegyalimukumu .
PFX tt 0 tegyalimukuba .
PFX tt 0 tegyalimukugu .
PFX tt 0 tegyalimukugi .
PFX tt 0 tegyalimukuzi .
PFX tt 0 tegyalimukuki .
PFX tt 0 tegyalimukubi .
PFX tt 0 tegyalimukuli .
PFX tt 0 tegyalimukuga .
PFX tt 0 tegyalimukuka .
PFX tt 0 tegyalimukubu .
PFX tt 0 tegyalimukulu .
PFX tt 0 tegyalimukuku .
PFX tt 0 tegyalimukutu .
PFX tt 0 egitaalimukun [^lmn]
PFX tt l egitaalimukund l.[^mn]
PFX tt l egitaalimukunn l.[mn]
PFX tt w egitaalimukump [w]
PFX tt 0 egitaalimukumu .
PFX tt 0 egitaalimukuba .
PFX tt 0 egitaalimukugu .
PFX tt 0 egitaalimukugi .
PFX tt 0 egitaalimukuzi .
PFX tt 0 egitaalimukuki .
PFX tt 0 egitaalimukubi .
PFX tt 0 egitaalimukuli .
PFX tt 0 egitaalimukuga .
PFX tt 0 egitaalimukuka .
PFX tt 0 egitaalimukubu .
PFX tt 0 egitaalimukulu .
PFX tt 0 egitaalimukuku .
PFX tt 0 egitaalimukutu .
PFX tt 0 teyalimukun [^lmn]
PFX tt l teyalimukund l.[^mn]
PFX tt l teyalimukunn l.[mn]
PFX tt w teyalimukump [w]
PFX tt 0 teyalimukumu .
PFX tt 0 teyalimukuba .
PFX tt 0 teyalimukugu .
PFX tt 0 teyalimukugi .
PFX tt 0 teyalimukuzi .
PFX tt 0 teyalimukuki .
PFX tt 0 teyalimukubi .
PFX tt 0 teyalimukuli .
PFX tt 0 teyalimukuga .
PFX tt 0 teyalimukuka .
PFX tt 0 teyalimukubu .
PFX tt 0 teyalimukulu .
PFX tt 0 teyalimukuku .
PFX tt 0 teyalimukutu .
PFX tt 0 etaalimukun [^lmn]
PFX tt l etaalimukund l.[^mn]
PFX tt l etaalimukunn l.[mn]
PFX tt w etaalimukump [w]
PFX tt 0 etaalimukumu .
PFX tt 0 etaalimukuba .
PFX tt 0 etaalimukugu .
PFX tt 0 etaalimukugi .
PFX tt 0 etaalimukuzi .
PFX tt 0 etaalimukuki .
PFX tt 0 etaalimukubi .
PFX tt 0 etaalimukuli .
PFX tt 0 etaalimukuga .
PFX tt 0 etaalimukuka .
PFX tt 0 etaalimukubu .
PFX tt 0 etaalimukulu .
PFX tt 0 etaalimukuku .
PFX tt 0 etaalimukutu .
PFX tt 0 tezaalimukun [^lmn]
PFX tt l tezaalimukund l.[^mn]
PFX tt l tezaalimukunn l.[mn]
PFX tt w tezaalimukump [w]
PFX tt 0 tezaalimukumu .
PFX tt 0 tezaalimukuba .
PFX tt 0 tezaalimukugu .
PFX tt 0 tezaalimukugi .
PFX tt 0 tezaalimukuzi .
PFX tt 0 tezaalimukuki .
PFX tt 0 tezaalimukubi .
PFX tt 0 tezaalimukuli .
PFX tt 0 tezaalimukuga .
PFX tt 0 tezaalimukuka .
PFX tt 0 tezaalimukubu .
PFX tt 0 tezaalimukulu .
PFX tt 0 tezaalimukuku .
PFX tt 0 tezaalimukutu .
PFX tt 0 ezitalimukun [^lmn]
PFX tt l ezitalimukund l.[^mn]
PFX tt l ezitalimukunn l.[mn]
PFX tt w ezitalimukump [w]
PFX tt 0 ezitalimukumu .
PFX tt 0 ezitalimukuba .
PFX tt 0 ezitalimukugu .
PFX tt 0 ezitalimukugi .
PFX tt 0 ezitalimukuzi .
PFX tt 0 ezitalimukuki .
PFX tt 0 ezitalimukubi .
PFX tt 0 ezitalimukuli .
PFX tt 0 ezitalimukuga .
PFX tt 0 ezitalimukuka .
PFX tt 0 ezitalimukubu .
PFX tt 0 ezitalimukulu .
PFX tt 0 ezitalimukuku .
PFX tt 0 ezitalimukutu .
PFX tt 0 tekyalimukun [^lmn]
PFX tt l tekyalimukund l.[^mn]
PFX tt l tekyalimukunn l.[mn]
PFX tt w tekyalimukump [w]
PFX tt 0 tekyalimukumu .
PFX tt 0 tekyalimukuba .
PFX tt 0 tekyalimukugu .
PFX tt 0 tekyalimukugi .
PFX tt 0 tekyalimukuzi .
PFX tt 0 tekyalimukuki .
PFX tt 0 tekyalimukubi .
PFX tt 0 tekyalimukuli .
PFX tt 0 tekyalimukuga .
PFX tt 0 tekyalimukuka .
PFX tt 0 tekyalimukubu .
PFX tt 0 tekyalimukulu .
PFX tt 0 tekyalimukuku .
PFX tt 0 tekyalimukutu .
PFX tt 0 ekitaalimukun [^lmn]
PFX tt l ekitaalimukund l.[^mn]
PFX tt l ekitaalimukunn l.[mn]
PFX tt w ekitaalimukump [w]
PFX tt 0 ekitaalimukumu .
PFX tt 0 ekitaalimukuba .
PFX tt 0 ekitaalimukugu .
PFX tt 0 ekitaalimukugi .
PFX tt 0 ekitaalimukuzi .
PFX tt 0 ekitaalimukuki .
PFX tt 0 ekitaalimukubi .
PFX tt 0 ekitaalimukuli .
PFX tt 0 ekitaalimukuga .
PFX tt 0 ekitaalimukuka .
PFX tt 0 ekitaalimukubu .
PFX tt 0 ekitaalimukulu .
PFX tt 0 ekitaalimukuku .
PFX tt 0 ekitaalimukutu .
PFX tt 0 tebyalimukun [^lmn]
PFX tt l tebyalimukund l.[^mn]
PFX tt l tebyalimukunn l.[mn]
PFX tt w tebyalimukump [w]
PFX tt 0 tebyalimukumu .
PFX tt 0 tebyalimukuba .
PFX tt 0 tebyalimukugu .
PFX tt 0 tebyalimukugi .
PFX tt 0 tebyalimukuzi .
PFX tt 0 tebyalimukuki .
PFX tt 0 tebyalimukubi .
PFX tt 0 tebyalimukuli .
PFX tt 0 tebyalimukuga .
PFX tt 0 tebyalimukuka .
PFX tt 0 tebyalimukubu .
PFX tt 0 tebyalimukulu .
PFX tt 0 tebyalimukuku .
PFX tt 0 tebyalimukutu .
PFX tt 0 ebitaalimukun [^lmn]
PFX tt l ebitaalimukund l.[^mn]
PFX tt l ebitaalimukunn l.[mn]
PFX tt w ebitaalimukump [w]
PFX tt 0 ebitaalimukumu .
PFX tt 0 ebitaalimukuba .
PFX tt 0 ebitaalimukugu .
PFX tt 0 ebitaalimukugi .
PFX tt 0 ebitaalimukuzi .
PFX tt 0 ebitaalimukuki .
PFX tt 0 ebitaalimukubi .
PFX tt 0 ebitaalimukuli .
PFX tt 0 ebitaalimukuga .
PFX tt 0 ebitaalimukuka .
PFX tt 0 ebitaalimukubu .
PFX tt 0 ebitaalimukulu .
PFX tt 0 ebitaalimukuku .
PFX tt 0 ebitaalimukutu .
PFX tt 0 telyalimukun [^lmn]
PFX tt l telyalimukund l.[^mn]
PFX tt l telyalimukunn l.[mn]
PFX tt w telyalimukump [w]
PFX tt 0 telyalimukumu .
PFX tt 0 telyalimukuba .
PFX tt 0 telyalimukugu .
PFX tt 0 telyalimukugi .
PFX tt 0 telyalimukuzi .
PFX tt 0 telyalimukuki .
PFX tt 0 telyalimukubi .
PFX tt 0 telyalimukuli .
PFX tt 0 telyalimukuga .
PFX tt 0 telyalimukuka .
PFX tt 0 telyalimukubu .
PFX tt 0 telyalimukulu .
PFX tt 0 telyalimukuku .
PFX tt 0 telyalimukutu .
PFX tt 0 elitaalimukun [^lmn]
PFX tt l elitaalimukund l.[^mn]
PFX tt l elitaalimukunn l.[mn]
PFX tt w elitaalimukump [w]
PFX tt 0 elitaalimukumu .
PFX tt 0 elitaalimukuba .
PFX tt 0 elitaalimukugu .
PFX tt 0 elitaalimukugi .
PFX tt 0 elitaalimukuzi .
PFX tt 0 elitaalimukuki .
PFX tt 0 elitaalimukubi .
PFX tt 0 elitaalimukuli .
PFX tt 0 elitaalimukuga .
PFX tt 0 elitaalimukuka .
PFX tt 0 elitaalimukubu .
PFX tt 0 elitaalimukulu .
PFX tt 0 elitaalimukuku .
PFX tt 0 elitaalimukutu .
PFX tt 0 tegaalimukun [^lmn]
PFX tt l tegaalimukund l.[^mn]
PFX tt l tegaalimukunn l.[mn]
PFX tt w tegaalimukump [w]
PFX tt 0 tegaalimukumu .
PFX tt 0 tegaalimukuba .
PFX tt 0 tegaalimukugu .
PFX tt 0 tegaalimukugi .
PFX tt 0 tegaalimukuzi .
PFX tt 0 tegaalimukuki .
PFX tt 0 tegaalimukubi .
PFX tt 0 tegaalimukuli .
PFX tt 0 tegaalimukuga .
PFX tt 0 tegaalimukuka .
PFX tt 0 tegaalimukubu .
PFX tt 0 tegaalimukulu .
PFX tt 0 tegaalimukuku .
PFX tt 0 tegaalimukutu .
PFX tt 0 agataalimukun [^lmn]
PFX tt l agataalimukund l.[^mn]
PFX tt l agataalimukunn l.[mn]
PFX tt w agataalimukump [w]
PFX tt 0 agataalimukumu .
PFX tt 0 agataalimukuba .
PFX tt 0 agataalimukugu .
PFX tt 0 agataalimukugi .
PFX tt 0 agataalimukuzi .
PFX tt 0 agataalimukuki .
PFX tt 0 agataalimukubi .
PFX tt 0 agataalimukuli .
PFX tt 0 agataalimukuga .
PFX tt 0 agataalimukuka .
PFX tt 0 agataalimukubu .
PFX tt 0 agataalimukulu .
PFX tt 0 agataalimukuku .
PFX tt 0 agataalimukutu .
PFX tt 0 tekaalimukun [^lmn]
PFX tt l tekaalimukund l.[^mn]
PFX tt l tekaalimukunn l.[mn]
PFX tt w tekaalimukump [w]
PFX tt 0 tekaalimukumu .
PFX tt 0 tekaalimukuba .
PFX tt 0 tekaalimukugu .
PFX tt 0 tekaalimukugi .
PFX tt 0 tekaalimukuzi .
PFX tt 0 tekaalimukuki .
PFX tt 0 tekaalimukubi .
PFX tt 0 tekaalimukuli .
PFX tt 0 tekaalimukuga .
PFX tt 0 tekaalimukuka .
PFX tt 0 tekaalimukubu .
PFX tt 0 tekaalimukulu .
PFX tt 0 tekaalimukuku .
PFX tt 0 tekaalimukutu .
PFX tt 0 akataalimukun [^lmn]
PFX tt l akataalimukund l.[^mn]
PFX tt l akataalimukunn l.[mn]
PFX tt w akataalimukump [w]
PFX tt 0 akataalimukumu .
PFX tt 0 akataalimukuba .
PFX tt 0 akataalimukugu .
PFX tt 0 akataalimukugi .
PFX tt 0 akataalimukuzi .
PFX tt 0 akataalimukuki .
PFX tt 0 akataalimukubi .
PFX tt 0 akataalimukuli .
PFX tt 0 akataalimukuga .
PFX tt 0 akataalimukuka .
PFX tt 0 akataalimukubu .
PFX tt 0 akataalimukulu .
PFX tt 0 akataalimukuku .
PFX tt 0 akataalimukutu .
PFX tt 0 tebwalimukun [^lmn]
PFX tt l tebwalimukund l.[^mn]
PFX tt l tebwalimukunn l.[mn]
PFX tt w tebwalimukump [w]
PFX tt 0 tebwalimukumu .
PFX tt 0 tebwalimukuba .
PFX tt 0 tebwalimukugu .
PFX tt 0 tebwalimukugi .
PFX tt 0 tebwalimukuzi .
PFX tt 0 tebwalimukuki .
PFX tt 0 tebwalimukubi .
PFX tt 0 tebwalimukuli .
PFX tt 0 tebwalimukuga .
PFX tt 0 tebwalimukuka .
PFX tt 0 tebwalimukubu .
PFX tt 0 tebwalimukulu .
PFX tt 0 tebwalimukuku .
PFX tt 0 tebwalimukutu .
PFX tt 0 obutaalimukun [^lmn]
PFX tt l obutaalimukund l.[^mn]
PFX tt l obutaalimukunn l.[mn]
PFX tt w obutaalimukump [w]
PFX tt 0 obutaalimukumu .
PFX tt 0 obutaalimukuba .
PFX tt 0 obutaalimukugu .
PFX tt 0 obutaalimukugi .
PFX tt 0 obutaalimukuzi .
PFX tt 0 obutaalimukuki .
PFX tt 0 obutaalimukubi .
PFX tt 0 obutaalimukuli .
PFX tt 0 obutaalimukuga .
PFX tt 0 obutaalimukuka .
PFX tt 0 obutaalimukubu .
PFX tt 0 obutaalimukulu .
PFX tt 0 obutaalimukuku .
PFX tt 0 obutaalimukutu .
PFX tt 0 telwalimukun [^lmn]
PFX tt l telwalimukund l.[^mn]
PFX tt l telwalimukunn l.[mn]
PFX tt w telwalimukump [w]
PFX tt 0 telwalimukumu .
PFX tt 0 telwalimukuba .
PFX tt 0 telwalimukugu .
PFX tt 0 telwalimukugi .
PFX tt 0 telwalimukuzi .
PFX tt 0 telwalimukuki .
PFX tt 0 telwalimukubi .
PFX tt 0 telwalimukuli .
PFX tt 0 telwalimukuga .
PFX tt 0 telwalimukuka .
PFX tt 0 telwalimukubu .
PFX tt 0 telwalimukulu .
PFX tt 0 telwalimukuku .
PFX tt 0 telwalimukutu .
PFX tt 0 olutaalimukun [^lmn]
PFX tt l olutaalimukund l.[^mn]
PFX tt l olutaalimukunn l.[mn]
PFX tt w olutaalimukump [w]
PFX tt 0 olutaalimukumu .
PFX tt 0 olutaalimukuba .
PFX tt 0 olutaalimukugu .
PFX tt 0 olutaalimukugi .
PFX tt 0 olutaalimukuzi .
PFX tt 0 olutaalimukuki .
PFX tt 0 olutaalimukubi .
PFX tt 0 olutaalimukuli .
PFX tt 0 olutaalimukuga .
PFX tt 0 olutaalimukuka .
PFX tt 0 olutaalimukubu .
PFX tt 0 olutaalimukulu .
PFX tt 0 olutaalimukuku .
PFX tt 0 olutaalimukutu .
PFX tt 0 tekwalimukun [^lmn]
PFX tt l tekwalimukund l.[^mn]
PFX tt l tekwalimukunn l.[mn]
PFX tt w tekwalimukump [w]
PFX tt 0 tekwalimukumu .
PFX tt 0 tekwalimukuba .
PFX tt 0 tekwalimukugu .
PFX tt 0 tekwalimukugi .
PFX tt 0 tekwalimukuzi .
PFX tt 0 tekwalimukuki .
PFX tt 0 tekwalimukubi .
PFX tt 0 tekwalimukuli .
PFX tt 0 tekwalimukuga .
PFX tt 0 tekwalimukuka .
PFX tt 0 tekwalimukubu .
PFX tt 0 tekwalimukulu .
PFX tt 0 tekwalimukuku .
PFX tt 0 tekwalimukutu .
PFX tt 0 okutaalimukun [^lmn]
PFX tt l okutaalimukund l.[^mn]
PFX tt l okutaalimukunn l.[mn]
PFX tt w okutaalimukump [w]
PFX tt 0 okutaalimukumu .
PFX tt 0 okutaalimukuba .
PFX tt 0 okutaalimukugu .
PFX tt 0 okutaalimukugi .
PFX tt 0 okutaalimukuzi .
PFX tt 0 okutaalimukuki .
PFX tt 0 okutaalimukubi .
PFX tt 0 okutaalimukuli .
PFX tt 0 okutaalimukuga .
PFX tt 0 okutaalimukuka .
PFX tt 0 okutaalimukubu .
PFX tt 0 okutaalimukulu .
PFX tt 0 okutaalimukuku .
PFX tt 0 okutaalimukutu .
PFX tt 0 tetwalimukun [^lmn]
PFX tt l tetwalimukund l.[^mn]
PFX tt l tetwalimukunn l.[mn]
PFX tt w tetwalimukump [w]
PFX tt 0 tetwalimukumu .
PFX tt 0 tetwalimukuba .
PFX tt 0 tetwalimukugu .
PFX tt 0 tetwalimukugi .
PFX tt 0 tetwalimukuzi .
PFX tt 0 tetwalimukuki .
PFX tt 0 tetwalimukubi .
PFX tt 0 tetwalimukuli .
PFX tt 0 tetwalimukuga .
PFX tt 0 tetwalimukuka .
PFX tt 0 tetwalimukubu .
PFX tt 0 tetwalimukulu .
PFX tt 0 tetwalimukuku .
PFX tt 0 tetwalimukutu .
PFX tt 0 otutaalimukun [^lmn]
PFX tt l otutaalimukund l.[^mn]
PFX tt l otutaalimukunn l.[mn]
PFX tt w otutaalimukump [w]
PFX tt 0 otutaalimukumu .
PFX tt 0 otutaalimukuba .
PFX tt 0 otutaalimukugu .
PFX tt 0 otutaalimukugi .
PFX tt 0 otutaalimukuzi .
PFX tt 0 otutaalimukuki .
PFX tt 0 otutaalimukubi .
PFX tt 0 otutaalimukuli .
PFX tt 0 otutaalimukuga .
PFX tt 0 otutaalimukuka .
PFX tt 0 otutaalimukubu .
PFX tt 0 otutaalimukulu .
PFX tt 0 otutaalimukuku .
PFX tt 0 otutaalimukutu ."""

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
    "tt": "tt",
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

    out_flag = "IQ"
    left_desc = FLAG_DESCRIPTIONS.get("tt", "tt")
    right_desc = FLAG_DESCRIPTIONS.get("Ob", "Ob")
    comment_line = "# Cross product of {} ({}) and {} ({}) to {}".format(
        "tt", left_desc, "Ob", right_desc, out_flag
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
