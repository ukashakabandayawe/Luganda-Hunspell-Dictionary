import re
import os
from pathlib import Path

# Cross product generator: FA x Ob => GA
# Description:
# - Left block `FA`: FA
# - Right block `Ob`: Object markers
# - Output flag `GA`: Cross-product prefixes for FA x Ob

REPO_ROOT = Path(__file__).resolve().parents[1]
AFF_FILE = REPO_ROOT / "Luganda.aff"

# If set to a flag name (e.g. "HB"), the generated cross-product block will be inserted
# immediately before the first "PFX <flag>" line when the output flag block doesn't
# already exist in the .aff.
INSERT_BEFORE_FLAG = "".strip() or None

rule_left_raw = """
PFX FA Y 662
PFX FA 0 sinnaba .
PFX FA 0 sinnagu .
PFX FA 0 sinnagi .
PFX FA 0 sinnazi .
PFX FA 0 sinnaki .
PFX FA 0 sinnabi .
PFX FA 0 sinnali .
PFX FA 0 sinnaga .
PFX FA 0 sinnaka .
PFX FA 0 sinnabu .
PFX FA 0 sinnalu .
PFX FA 0 sinnaku .
PFX FA 0 sinnatu .
PFX FA 0 sinnamu .
PFX FA 0 tonnan [^lmnb]
PFX FA l tonnand l.[^mn]
PFX FA l tonnann l.[mn]
PFX FA w tonnamp [w]
PFX FA 0 tonnamu .
PFX FA 0 tonnaba .
PFX FA 0 tonnagu .
PFX FA 0 tonnagi .
PFX FA 0 tonnazi .
PFX FA 0 tonnaki .
PFX FA 0 tonnabi .
PFX FA 0 tonnali .
PFX FA 0 tonnaga .
PFX FA 0 tonnaka .
PFX FA 0 tonnabu .
PFX FA 0 tonnalu .
PFX FA 0 tonnaku .
PFX FA 0 tonnatu .
PFX FA 0 tannan [^lmnb]
PFX FA l tannand l.[^mn]
PFX FA l tannann l.[mn]
PFX FA w tannamp [w]
PFX FA 0 tannamu .
PFX FA 0 tannaba .
PFX FA 0 tannagu .
PFX FA 0 tannagi .
PFX FA 0 tannazi .
PFX FA 0 tannaki .
PFX FA 0 tannabi .
PFX FA 0 tannali .
PFX FA 0 tannaga .
PFX FA 0 tannaka .
PFX FA 0 tannabu .
PFX FA 0 tannalu .
PFX FA 0 tannaku .
PFX FA 0 tannatu .
PFX FA 0 tetunnan [^lmnb]
PFX FA l tetunnand l.[^mn]
PFX FA l tetunnann l.[mn]
PFX FA w tetunnamp [w]
PFX FA 0 tetunnamu .
PFX FA 0 tetunnaba .
PFX FA 0 tetunnagu .
PFX FA 0 tetunnagi .
PFX FA 0 tetunnazi .
PFX FA 0 tetunnaki .
PFX FA 0 tetunnabi .
PFX FA 0 tetunnali .
PFX FA 0 tetunnaga .
PFX FA 0 tetunnaka .
PFX FA 0 tetunnabu .
PFX FA 0 tetunnalu .
PFX FA 0 tetunnaku .
PFX FA 0 tetunnatu .
PFX FA 0 temunnan [^lmnb]
PFX FA l temunnand l.[^mn]
PFX FA l temunnann l.[mn]
PFX FA w temunnamp [w]
PFX FA 0 temunnamu .
PFX FA 0 temunnaba .
PFX FA 0 temunnagu .
PFX FA 0 temunnagi .
PFX FA 0 temunnazi .
PFX FA 0 temunnaki .
PFX FA 0 temunnabi .
PFX FA 0 temunnali .
PFX FA 0 temunnaga .
PFX FA 0 temunnaka .
PFX FA 0 temunnabu .
PFX FA 0 temunnalu .
PFX FA 0 temunnaku .
PFX FA 0 temunnatu .
PFX FA 0 tebannan [^lmnb]
PFX FA l tebannand l.[^mn]
PFX FA l tebannann l.[mn]
PFX FA w tebannamp [w]
PFX FA 0 tebannamu .
PFX FA 0 tebannaba .
PFX FA 0 tebannagu .
PFX FA 0 tebannagi .
PFX FA 0 tebannazi .
PFX FA 0 tebannaki .
PFX FA 0 tebannabi .
PFX FA 0 tebannali .
PFX FA 0 tebannaga .
PFX FA 0 tebannaka .
PFX FA 0 tebannabu .
PFX FA 0 tebannalu .
PFX FA 0 tebannaku .
PFX FA 0 tebannatu .
PFX FA 0 abatannan [^lmnb]
PFX FA l abatannand l.[^mn]
PFX FA l abatannann l.[mn]
PFX FA w abatannamp [w]
PFX FA 0 abatannamu .
PFX FA 0 abatannaba .
PFX FA 0 abatannagu .
PFX FA 0 abatannagi .
PFX FA 0 abatannazi .
PFX FA 0 abatannaki .
PFX FA 0 abatannabi .
PFX FA 0 abatannali .
PFX FA 0 abatannaga .
PFX FA 0 abatannaka .
PFX FA 0 abatannabu .
PFX FA 0 abatannalu .
PFX FA 0 abatannaku .
PFX FA 0 abatannatu .
PFX FA 0 atannan [^lmnb]
PFX FA l atannand l.[^mn]
PFX FA l atannann l.[mn]
PFX FA w atannamp [w]
PFX FA 0 atannamu .
PFX FA 0 atannaba .
PFX FA 0 atannagu .
PFX FA 0 atannagi .
PFX FA 0 atannazi .
PFX FA 0 atannaki .
PFX FA 0 atannabi .
PFX FA 0 atannali .
PFX FA 0 atannaga .
PFX FA 0 atannaka .
PFX FA 0 atannabu .
PFX FA 0 atannalu .
PFX FA 0 atannaku .
PFX FA 0 atannatu .
PFX FA 0 tegunnan [^lmnb]
PFX FA l tegunnand l.[^mn]
PFX FA l tegunnann l.[mn]
PFX FA w tegunnamp [w]
PFX FA 0 tegunnamu .
PFX FA 0 tegunnaba .
PFX FA 0 tegunnagu .
PFX FA 0 tegunnagi .
PFX FA 0 tegunnazi .
PFX FA 0 tegunnaki .
PFX FA 0 tegunnabi .
PFX FA 0 tegunnali .
PFX FA 0 tegunnaga .
PFX FA 0 tegunnaka .
PFX FA 0 tegunnabu .
PFX FA 0 tegunnalu .
PFX FA 0 tegunnaku .
PFX FA 0 tegunnatu .
PFX FA 0 ogutannan [^lmnb]
PFX FA l ogutannand l.[^mn]
PFX FA l ogutannann l.[mn]
PFX FA w ogutannamp [w]
PFX FA 0 ogutannamu .
PFX FA 0 ogutannaba .
PFX FA 0 ogutannagu .
PFX FA 0 ogutannagi .
PFX FA 0 ogutannazi .
PFX FA 0 ogutannaki .
PFX FA 0 ogutannabi .
PFX FA 0 ogutannali .
PFX FA 0 ogutannaga .
PFX FA 0 ogutannaka .
PFX FA 0 ogutannabu .
PFX FA 0 ogutannalu .
PFX FA 0 ogutannaku .
PFX FA 0 ogutannatu .
PFX FA 0 teginnan [^lmnb]
PFX FA l teginnand l.[^mn]
PFX FA l teginnann l.[mn]
PFX FA w teginnamp [w]
PFX FA 0 teginnamu .
PFX FA 0 teginnaba .
PFX FA 0 teginnagu .
PFX FA 0 teginnagi .
PFX FA 0 teginnazi .
PFX FA 0 teginnaki .
PFX FA 0 teginnabi .
PFX FA 0 teginnali .
PFX FA 0 teginnaga .
PFX FA 0 teginnaka .
PFX FA 0 teginnabu .
PFX FA 0 teginnalu .
PFX FA 0 teginnaku .
PFX FA 0 teginnatu .
PFX FA 0 egitannan [^lmnb]
PFX FA l egitannand l.[^mn]
PFX FA l egitannann l.[mn]
PFX FA w egitannamp [w]
PFX FA 0 egitannamu .
PFX FA 0 egitannaba .
PFX FA 0 egitannagu .
PFX FA 0 egitannagi .
PFX FA 0 egitannazi .
PFX FA 0 egitannaki .
PFX FA 0 egitannabi .
PFX FA 0 egitannali .
PFX FA 0 egitannaga .
PFX FA 0 egitannaka .
PFX FA 0 egitannabu .
PFX FA 0 egitannalu .
PFX FA 0 egitannaku .
PFX FA 0 egitannatu .
PFX FA 0 tennan [^lmnb]
PFX FA l tennand l.[^mn]
PFX FA l tennann l.[mn]
PFX FA w tennamp [w]
PFX FA 0 tennamu .
PFX FA 0 tennaba .
PFX FA 0 tennagu .
PFX FA 0 tennagi .
PFX FA 0 tennazi .
PFX FA 0 tennaki .
PFX FA 0 tennabi .
PFX FA 0 tennali .
PFX FA 0 tennaga .
PFX FA 0 tennaka .
PFX FA 0 tennabu .
PFX FA 0 tennalu .
PFX FA 0 tennaku .
PFX FA 0 tennatu .
PFX FA 0 tezinnan [^lmnb]
PFX FA l tezinnand l.[^mn]
PFX FA l tezinnann l.[mn]
PFX FA w tezinnamp [w]
PFX FA 0 tezinnamu .
PFX FA 0 tezinnaba .
PFX FA 0 tezinnagu .
PFX FA 0 tezinnagi .
PFX FA 0 tezinnazi .
PFX FA 0 tezinnaki .
PFX FA 0 tezinnabi .
PFX FA 0 tezinnali .
PFX FA 0 tezinnaga .
PFX FA 0 tezinnaka .
PFX FA 0 tezinnabu .
PFX FA 0 tezinnalu .
PFX FA 0 tezinnaku .
PFX FA 0 tezinnatu .
PFX FA 0 ezitannan [^lmnb]
PFX FA l ezitannand l.[^mn]
PFX FA l ezitannann l.[mn]
PFX FA w ezitannamp [w]
PFX FA 0 ezitannamu .
PFX FA 0 ezitannaba .
PFX FA 0 ezitannagu .
PFX FA 0 ezitannagi .
PFX FA 0 ezitannazi .
PFX FA 0 ezitannaki .
PFX FA 0 ezitannabi .
PFX FA 0 ezitannali .
PFX FA 0 ezitannaga .
PFX FA 0 ezitannaka .
PFX FA 0 ezitannabu .
PFX FA 0 ezitannalu .
PFX FA 0 ezitannaku .
PFX FA 0 ezitannatu .
PFX FA 0 tekinnan [^lmnb]
PFX FA l tekinnand l.[^mn]
PFX FA l tekinnann l.[mn]
PFX FA w tekinnamp [w]
PFX FA 0 tekinnamu .
PFX FA 0 tekinnaba .
PFX FA 0 tekinnagu .
PFX FA 0 tekinnagi .
PFX FA 0 tekinnazi .
PFX FA 0 tekinnaki .
PFX FA 0 tekinnabi .
PFX FA 0 tekinnali .
PFX FA 0 tekinnaga .
PFX FA 0 tekinnaka .
PFX FA 0 tekinnabu .
PFX FA 0 tekinnalu .
PFX FA 0 tekinnaku .
PFX FA 0 tekinnatu .
PFX FA 0 ekitannan [^lmnb]
PFX FA l ekitannand l.[^mn]
PFX FA l ekitannann l.[mn]
PFX FA w ekitannamp [w]
PFX FA 0 ekitannamu .
PFX FA 0 ekitannaba .
PFX FA 0 ekitannagu .
PFX FA 0 ekitannagi .
PFX FA 0 ekitannazi .
PFX FA 0 ekitannaki .
PFX FA 0 ekitannabi .
PFX FA 0 ekitannali .
PFX FA 0 ekitannaga .
PFX FA 0 ekitannaka .
PFX FA 0 ekitannabu .
PFX FA 0 ekitannalu .
PFX FA 0 ekitannaku .
PFX FA 0 ekitannatu .
PFX FA 0 tebinnan [^lmnb]
PFX FA l tebinnand l.[^mn]
PFX FA l tebinnann l.[mn]
PFX FA w tebinnamp [w]
PFX FA 0 tebinnamu .
PFX FA 0 tebinnaba .
PFX FA 0 tebinnagu .
PFX FA 0 tebinnagi .
PFX FA 0 tebinnazi .
PFX FA 0 tebinnaki .
PFX FA 0 tebinnabi .
PFX FA 0 tebinnali .
PFX FA 0 tebinnaga .
PFX FA 0 tebinnaka .
PFX FA 0 tebinnabu .
PFX FA 0 tebinnalu .
PFX FA 0 tebinnaku .
PFX FA 0 tebinnatu .
PFX FA 0 ebitannan [^lmnb]
PFX FA l ebitannand l.[^mn]
PFX FA l ebitannann l.[mn]
PFX FA w ebitannamp [w]
PFX FA 0 ebitannamu .
PFX FA 0 ebitannaba .
PFX FA 0 ebitannagu .
PFX FA 0 ebitannagi .
PFX FA 0 ebitannazi .
PFX FA 0 ebitannaki .
PFX FA 0 ebitannabi .
PFX FA 0 ebitannali .
PFX FA 0 ebitannaga .
PFX FA 0 ebitannaka .
PFX FA 0 ebitannabu .
PFX FA 0 ebitannalu .
PFX FA 0 ebitannaku .
PFX FA 0 ebitannatu .
PFX FA 0 telinnan [^lmnb]
PFX FA l telinnand l.[^mn]
PFX FA l telinnann l.[mn]
PFX FA w telinnamp [w]
PFX FA 0 telinnamu .
PFX FA 0 telinnaba .
PFX FA 0 telinnagu .
PFX FA 0 telinnagi .
PFX FA 0 telinnazi .
PFX FA 0 telinnaki .
PFX FA 0 telinnabi .
PFX FA 0 telinnali .
PFX FA 0 telinnaga .
PFX FA 0 telinnaka .
PFX FA 0 telinnabu .
PFX FA 0 telinnalu .
PFX FA 0 telinnaku .
PFX FA 0 telinnatu .
PFX FA 0 elitannan [^lmnb]
PFX FA l elitannand l.[^mn]
PFX FA l elitannann l.[mn]
PFX FA w elitannamp [w]
PFX FA 0 elitannamu .
PFX FA 0 elitannaba .
PFX FA 0 elitannagu .
PFX FA 0 elitannagi .
PFX FA 0 elitannazi .
PFX FA 0 elitannaki .
PFX FA 0 elitannabi .
PFX FA 0 elitannali .
PFX FA 0 elitannaga .
PFX FA 0 elitannaka .
PFX FA 0 elitannabu .
PFX FA 0 elitannalu .
PFX FA 0 elitannaku .
PFX FA 0 elitannatu .
PFX FA 0 tegannan [^lmnb]
PFX FA l tegannand l.[^mn]
PFX FA l tegannann l.[mn]
PFX FA w tegannamp [w]
PFX FA 0 tegannamu .
PFX FA 0 tegannaba .
PFX FA 0 tegannagu .
PFX FA 0 tegannagi .
PFX FA 0 tegannazi .
PFX FA 0 tegannaki .
PFX FA 0 tegannabi .
PFX FA 0 tegannali .
PFX FA 0 tegannaga .
PFX FA 0 tegannaka .
PFX FA 0 tegannabu .
PFX FA 0 tegannalu .
PFX FA 0 tegannaku .
PFX FA 0 tegannatu .
PFX FA 0 agatannan [^lmnb]
PFX FA l agatannand l.[^mn]
PFX FA l agatannann l.[mn]
PFX FA w agatannamp [w]
PFX FA 0 agatannamu .
PFX FA 0 agatannaba .
PFX FA 0 agatannagu .
PFX FA 0 agatannagi .
PFX FA 0 agatannazi .
PFX FA 0 agatannaki .
PFX FA 0 agatannabi .
PFX FA 0 agatannali .
PFX FA 0 agatannaga .
PFX FA 0 agatannaka .
PFX FA 0 agatannabu .
PFX FA 0 agatannalu .
PFX FA 0 agatannaku .
PFX FA 0 agatannatu .
PFX FA 0 tekannan [^lmnb]
PFX FA l tekannand l.[^mn]
PFX FA l tekannann l.[mn]
PFX FA w tekannamp [w]
PFX FA 0 tekannamu .
PFX FA 0 tekannaba .
PFX FA 0 tekannagu .
PFX FA 0 tekannagi .
PFX FA 0 tekannazi .
PFX FA 0 tekannaki .
PFX FA 0 tekannabi .
PFX FA 0 tekannali .
PFX FA 0 tekannaga .
PFX FA 0 tekannaka .
PFX FA 0 tekannabu .
PFX FA 0 tekannalu .
PFX FA 0 tekannaku .
PFX FA 0 tekannatu .
PFX FA 0 akatannan [^lmnb]
PFX FA l akatannand l.[^mn]
PFX FA l akatannann l.[mn]
PFX FA w akatannamp [w]
PFX FA 0 akatannamu .
PFX FA 0 akatannaba .
PFX FA 0 akatannagu .
PFX FA 0 akatannagi .
PFX FA 0 akatannazi .
PFX FA 0 akatannaki .
PFX FA 0 akatannabi .
PFX FA 0 akatannali .
PFX FA 0 akatannaga .
PFX FA 0 akatannaka .
PFX FA 0 akatannabu .
PFX FA 0 akatannalu .
PFX FA 0 akatannaku .
PFX FA 0 akatannatu .
PFX FA 0 tebunnan [^lmnb]
PFX FA l tebunnand l.[^mn]
PFX FA l tebunnann l.[mn]
PFX FA w tebunnamp [w]
PFX FA 0 tebunnamu .
PFX FA 0 tebunnaba .
PFX FA 0 tebunnagu .
PFX FA 0 tebunnagi .
PFX FA 0 tebunnazi .
PFX FA 0 tebunnaki .
PFX FA 0 tebunnabi .
PFX FA 0 tebunnali .
PFX FA 0 tebunnaga .
PFX FA 0 tebunnaka .
PFX FA 0 tebunnabu .
PFX FA 0 tebunnalu .
PFX FA 0 tebunnaku .
PFX FA 0 tebunnatu .
PFX FA 0 obutannan [^lmnb]
PFX FA l obutannand l.[^mn]
PFX FA l obutannann l.[mn]
PFX FA w obutannamp [w]
PFX FA 0 obutannamu .
PFX FA 0 obutannaba .
PFX FA 0 obutannagu .
PFX FA 0 obutannagi .
PFX FA 0 obutannazi .
PFX FA 0 obutannaki .
PFX FA 0 obutannabi .
PFX FA 0 obutannali .
PFX FA 0 obutannaga .
PFX FA 0 obutannaka .
PFX FA 0 obutannabu .
PFX FA 0 obutannalu .
PFX FA 0 obutannaku .
PFX FA 0 obutannatu .
PFX FA 0 telunnan [^lmnb]
PFX FA l telunnand l.[^mn]
PFX FA l telunnann l.[mn]
PFX FA w telunnamp [w]
PFX FA 0 telunnamu .
PFX FA 0 telunnaba .
PFX FA 0 telunnagu .
PFX FA 0 telunnagi .
PFX FA 0 telunnazi .
PFX FA 0 telunnaki .
PFX FA 0 telunnabi .
PFX FA 0 telunnali .
PFX FA 0 telunnaga .
PFX FA 0 telunnaka .
PFX FA 0 telunnabu .
PFX FA 0 telunnalu .
PFX FA 0 telunnaku .
PFX FA 0 telunnatu .
PFX FA 0 olutannan [^lmnb]
PFX FA l olutannand l.[^mn]
PFX FA l olutannann l.[mn]
PFX FA w olutannamp [w]
PFX FA 0 olutannamu .
PFX FA 0 olutannaba .
PFX FA 0 olutannagu .
PFX FA 0 olutannagi .
PFX FA 0 olutannazi .
PFX FA 0 olutannaki .
PFX FA 0 olutannabi .
PFX FA 0 olutannali .
PFX FA 0 olutannaga .
PFX FA 0 olutannaka .
PFX FA 0 olutannabu .
PFX FA 0 olutannalu .
PFX FA 0 olutannaku .
PFX FA 0 olutannatu .
PFX FA 0 tezinnan [^lmnb]
PFX FA l tezinnand l.[^mn]
PFX FA l tezinnann l.[mn]
PFX FA w tezinnamp [w]
PFX FA 0 tezinnamu .
PFX FA 0 tezinnaba .
PFX FA 0 tezinnagu .
PFX FA 0 tezinnagi .
PFX FA 0 tezinnazi .
PFX FA 0 tezinnaki .
PFX FA 0 tezinnabi .
PFX FA 0 tezinnali .
PFX FA 0 tezinnaga .
PFX FA 0 tezinnaka .
PFX FA 0 tezinnabu .
PFX FA 0 tezinnalu .
PFX FA 0 tezinnaku .
PFX FA 0 tezinnatu .
PFX FA 0 ezitannan [^lmnb]
PFX FA l ezitannand l.[^mn]
PFX FA l ezitannann l.[mn]
PFX FA w ezitannamp [w]
PFX FA 0 ezitannamu .
PFX FA 0 ezitannaba .
PFX FA 0 ezitannagu .
PFX FA 0 ezitannagi .
PFX FA 0 ezitannazi .
PFX FA 0 ezitannaki .
PFX FA 0 ezitannabi .
PFX FA 0 ezitannali .
PFX FA 0 ezitannaga .
PFX FA 0 ezitannaka .
PFX FA 0 ezitannabu .
PFX FA 0 ezitannalu .
PFX FA 0 ezitannaku .
PFX FA 0 ezitannatu .
PFX FA 0 tekunnan [^lmnb]
PFX FA l tekunnand l.[^mn]
PFX FA l tekunnann l.[mn]
PFX FA w tekunnamp [w]
PFX FA 0 tekunnamu .
PFX FA 0 tekunnaba .
PFX FA 0 tekunnagu .
PFX FA 0 tekunnagi .
PFX FA 0 tekunnazi .
PFX FA 0 tekunnaki .
PFX FA 0 tekunnabi .
PFX FA 0 tekunnali .
PFX FA 0 tekunnaga .
PFX FA 0 tekunnaka .
PFX FA 0 tekunnabu .
PFX FA 0 tekunnalu .
PFX FA 0 tekunnaku .
PFX FA 0 tekunnatu .
PFX FA 0 okutannan [^lmnb]
PFX FA l okutannand l.[^mn]
PFX FA l okutannann l.[mn]
PFX FA w okutannamp [w]
PFX FA 0 okutannamu .
PFX FA 0 okutannaba .
PFX FA 0 okutannagu .
PFX FA 0 okutannagi .
PFX FA 0 okutannazi .
PFX FA 0 okutannaki .
PFX FA 0 okutannabi .
PFX FA 0 okutannali .
PFX FA 0 okutannaga .
PFX FA 0 okutannaka .
PFX FA 0 okutannabu .
PFX FA 0 okutannalu .
PFX FA 0 okutannaku .
PFX FA 0 okutannatu .
PFX FA 0 tegannan [^lmnb]
PFX FA l tegannand l.[^mn]
PFX FA l tegannann l.[mn]
PFX FA w tegannamp [w]
PFX FA 0 tegannamu .
PFX FA 0 tegannaba .
PFX FA 0 tegannagu .
PFX FA 0 tegannagi .
PFX FA 0 tegannazi .
PFX FA 0 tegannaki .
PFX FA 0 tegannabi .
PFX FA 0 tegannali .
PFX FA 0 tegannaga .
PFX FA 0 tegannaka .
PFX FA 0 tegannabu .
PFX FA 0 tegannalu .
PFX FA 0 tegannaku .
PFX FA 0 tegannatu .
PFX FA 0 agatannan [^lmnb]
PFX FA l agatannand l.[^mn]
PFX FA l agatannann l.[mn]
PFX FA w agatannamp [w]
PFX FA 0 agatannamu .
PFX FA 0 agatannaba .
PFX FA 0 agatannagu .
PFX FA 0 agatannagi .
PFX FA 0 agatannazi .
PFX FA 0 agatannaki .
PFX FA 0 agatannabi .
PFX FA 0 agatannali .
PFX FA 0 agatannaga .
PFX FA 0 agatannaka .
PFX FA 0 agatannabu .
PFX FA 0 agatannalu .
PFX FA 0 agatannaku .
PFX FA 0 agatannatu .
PFX FA 0 tetunnan [^lmnb]
PFX FA l tetunnand l.[^mn]
PFX FA l tetunnann l.[mn]
PFX FA w tetunnamp [w]
PFX FA 0 tetunnamu .
PFX FA 0 tetunnaba .
PFX FA 0 tetunnagu .
PFX FA 0 tetunnagi .
PFX FA 0 tetunnazi .
PFX FA 0 tetunnaki .
PFX FA 0 tetunnabi .
PFX FA 0 tetunnali .
PFX FA 0 tetunnaga .
PFX FA 0 tetunnaka .
PFX FA 0 tetunnabu .
PFX FA 0 tetunnalu .
PFX FA 0 tetunnaku .
PFX FA 0 tetunnatu .
PFX FA 0 otutannan [^lmnb]
PFX FA l otutannand l.[^mn]
PFX FA l otutannann l.[mn]
PFX FA w otutannamp [w]
PFX FA 0 otutannamu .
PFX FA 0 otutannaba .
PFX FA 0 otutannagu .
PFX FA 0 otutannagi .
PFX FA 0 otutannazi .
PFX FA 0 otutannaki .
PFX FA 0 otutannabi .
PFX FA 0 otutannali .
PFX FA 0 otutannaga .
PFX FA 0 otutannaka .
PFX FA 0 otutannabu .
PFX FA 0 otutannalu .
PFX FA 0 otutannaku .
PFX FA 0 otutannatu ."""

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
    "FA": "FA",
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

    out_flag = "GA"
    left_desc = FLAG_DESCRIPTIONS.get("FA", "FA")
    right_desc = FLAG_DESCRIPTIONS.get("Ob", "Ob")
    comment_line = "# Cross product of {} ({}) and {} ({}) to {}".format(
        "FA", left_desc, "Ob", right_desc, out_flag
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
