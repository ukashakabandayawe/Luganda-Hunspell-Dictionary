import re
import os
from pathlib import Path

# Cross product generator: EB x Ob => GY
# Description:
# - Left block `EB`: EB
# - Right block `Ob`: Object markers
# - Output flag `GY`: Cross-product prefixes for EB x Ob

REPO_ROOT = Path(__file__).resolve().parents[1]
AFF_FILE = REPO_ROOT / "Luganda.aff"

# If set to a flag name (e.g. "HB"), the generated cross-product block will be inserted
# immediately before the first "PFX <flag>" line when the output flag block doesn't
# already exist in the .aff.
INSERT_BEFORE_FLAG = "".strip() or None

rule_left_raw = """
PFX EB Y 608
PFX EB 0 nkyaba .
PFX EB 0 nkyagu .
PFX EB 0 nkyagi .
PFX EB 0 nkyazi .
PFX EB 0 nkyaki .
PFX EB 0 nkyabi .
PFX EB 0 nkyali .
PFX EB 0 nkyaga .
PFX EB 0 nkyaka .
PFX EB 0 nkyabu .
PFX EB 0 nkyalu .
PFX EB 0 nkyaku .
PFX EB 0 nkyatu .
PFX EB 0 nkyamu .
PFX EB 0 okyan [^lmnb]
PFX EB l okyand l.[^mn][^u]
PFX EB l okyann l.[mn]
PFX EB w okyamp [w]
PFX EB 0 okyamu .
PFX EB 0 okyaba .
PFX EB 0 okyagu .
PFX EB 0 okyagi .
PFX EB 0 okyazi .
PFX EB 0 okyaki .
PFX EB 0 okyabi .
PFX EB 0 okyali .
PFX EB 0 okyaga .
PFX EB 0 okyaka .
PFX EB 0 okyabu .
PFX EB 0 okyalu .
PFX EB 0 okyaku .
PFX EB 0 okyatu .
PFX EB 0 akyan [^lmnb]
PFX EB l akyand l.[^mn][^u]
PFX EB l akyann l.[mn]
PFX EB w akyamp [w]
PFX EB 0 akyamu .
PFX EB 0 akyaba .
PFX EB 0 akyagu .
PFX EB 0 akyagi .
PFX EB 0 akyazi .
PFX EB 0 akyaki .
PFX EB 0 akyabi .
PFX EB 0 akyali .
PFX EB 0 akyaga .
PFX EB 0 akyaka .
PFX EB 0 akyabu .
PFX EB 0 akyalu .
PFX EB 0 akyaku .
PFX EB 0 akyatu .
PFX EB 0 tukyan [^lmnb]
PFX EB l tukyand l.[^mn][^u]
PFX EB l tukyann l.[mn]
PFX EB w tukyamp [w]
PFX EB 0 tukyamu .
PFX EB 0 tukyaba .
PFX EB 0 tukyagu .
PFX EB 0 tukyagi .
PFX EB 0 tukyazi .
PFX EB 0 tukyaki .
PFX EB 0 tukyabi .
PFX EB 0 tukyali .
PFX EB 0 tukyaga .
PFX EB 0 tukyaka .
PFX EB 0 tukyabu .
PFX EB 0 tukyalu .
PFX EB 0 tukyaku .
PFX EB 0 tukyatu .
PFX EB 0 mukyan [^lmnb]
PFX EB l mukyand l.[^mn][^u]
PFX EB l mukyann l.[mn]
PFX EB w mukyamp [w]
PFX EB 0 mukyamu .
PFX EB 0 mukyaba .
PFX EB 0 mukyagu .
PFX EB 0 mukyagi .
PFX EB 0 mukyazi .
PFX EB 0 mukyaki .
PFX EB 0 mukyabi .
PFX EB 0 mukyali .
PFX EB 0 mukyaga .
PFX EB 0 mukyaka .
PFX EB 0 mukyabu .
PFX EB 0 mukyalu .
PFX EB 0 mukyaku .
PFX EB 0 mukyatu .
PFX EB 0 bakyan [^lmnb]
PFX EB l bakyand l.[^mn][^u]
PFX EB l bakyann l.[mn]
PFX EB w bakyamp [w]
PFX EB 0 bakyamu .
PFX EB 0 bakyaba .
PFX EB 0 bakyagu .
PFX EB 0 bakyagi .
PFX EB 0 bakyazi .
PFX EB 0 bakyaki .
PFX EB 0 bakyabi .
PFX EB 0 bakyali .
PFX EB 0 bakyaga .
PFX EB 0 bakyaka .
PFX EB 0 bakyabu .
PFX EB 0 bakyalu .
PFX EB 0 bakyaku .
PFX EB 0 bakyatu .
PFX EB 0 akyan [^lmnb]
PFX EB l akyand l.[^mn][^u]
PFX EB l akyann l.[mn]
PFX EB w akyamp [w]
PFX EB 0 akyamu .
PFX EB 0 akyaba .
PFX EB 0 akyagu .
PFX EB 0 akyagi .
PFX EB 0 akyazi .
PFX EB 0 akyaki .
PFX EB 0 akyabi .
PFX EB 0 akyali .
PFX EB 0 akyaga .
PFX EB 0 akyaka .
PFX EB 0 akyabu .
PFX EB 0 akyalu .
PFX EB 0 akyaku .
PFX EB 0 akyatu .
PFX EB 0 bakyan [^lmnb]
PFX EB l bakyand l.[^mn][^u]
PFX EB l bakyann l.[mn]
PFX EB w bakyamp [w]
PFX EB 0 bakyamu .
PFX EB 0 bakyaba .
PFX EB 0 bakyagu .
PFX EB 0 bakyagi .
PFX EB 0 bakyazi .
PFX EB 0 bakyaki .
PFX EB 0 bakyabi .
PFX EB 0 bakyali .
PFX EB 0 bakyaga .
PFX EB 0 bakyaka .
PFX EB 0 bakyabu .
PFX EB 0 bakyalu .
PFX EB 0 bakyaku .
PFX EB 0 bakyatu .
PFX EB 0 abakyan [^lmnb]
PFX EB l abakyand l.[^mn][^u]
PFX EB l abakyann l.[mn]
PFX EB w abakyamp [w]
PFX EB 0 abakyamu .
PFX EB 0 abakyaba .
PFX EB 0 abakyagu .
PFX EB 0 abakyagi .
PFX EB 0 abakyazi .
PFX EB 0 abakyaki .
PFX EB 0 abakyabi .
PFX EB 0 abakyali .
PFX EB 0 abakyaga .
PFX EB 0 abakyaka .
PFX EB 0 abakyabu .
PFX EB 0 abakyalu .
PFX EB 0 abakyaku .
PFX EB 0 abakyatu .
PFX EB 0 gukyan [^lmnb]
PFX EB l gukyand l.[^mn][^u]
PFX EB l gukyann l.[mn]
PFX EB w gukyamp [w]
PFX EB 0 gukyamu .
PFX EB 0 gukyaba .
PFX EB 0 gukyagu .
PFX EB 0 gukyagi .
PFX EB 0 gukyazi .
PFX EB 0 gukyaki .
PFX EB 0 gukyabi .
PFX EB 0 gukyali .
PFX EB 0 gukyaga .
PFX EB 0 gukyaka .
PFX EB 0 gukyabu .
PFX EB 0 gukyalu .
PFX EB 0 gukyaku .
PFX EB 0 gukyatu .
PFX EB 0 ogukyan [^lmnb]
PFX EB l ogukyand l.[^mn][^u]
PFX EB l ogukyann l.[mn]
PFX EB w ogukyamp [w]
PFX EB 0 ogukyamu .
PFX EB 0 ogukyaba .
PFX EB 0 ogukyagu .
PFX EB 0 ogukyagi .
PFX EB 0 ogukyazi .
PFX EB 0 ogukyaki .
PFX EB 0 ogukyabi .
PFX EB 0 ogukyali .
PFX EB 0 ogukyaga .
PFX EB 0 ogukyaka .
PFX EB 0 ogukyabu .
PFX EB 0 ogukyalu .
PFX EB 0 ogukyaku .
PFX EB 0 ogukyatu .
PFX EB 0 gikyan [^lmnb]
PFX EB l gikyand l.[^mn][^u]
PFX EB l gikyann l.[mn]
PFX EB w gikyamp [w]
PFX EB 0 gikyamu .
PFX EB 0 gikyaba .
PFX EB 0 gikyagu .
PFX EB 0 gikyagi .
PFX EB 0 gikyazi .
PFX EB 0 gikyaki .
PFX EB 0 gikyabi .
PFX EB 0 gikyali .
PFX EB 0 gikyaga .
PFX EB 0 gikyaka .
PFX EB 0 gikyabu .
PFX EB 0 gikyalu .
PFX EB 0 gikyaku .
PFX EB 0 gikyatu .
PFX EB 0 egikyan [^lmnb]
PFX EB l egikyand l.[^mn][^u]
PFX EB l egikyann l.[mn]
PFX EB w egikyamp [w]
PFX EB 0 egikyamu .
PFX EB 0 egikyaba .
PFX EB 0 egikyagu .
PFX EB 0 egikyagi .
PFX EB 0 egikyazi .
PFX EB 0 egikyaki .
PFX EB 0 egikyabi .
PFX EB 0 egikyali .
PFX EB 0 egikyaga .
PFX EB 0 egikyaka .
PFX EB 0 egikyabu .
PFX EB 0 egikyalu .
PFX EB 0 egikyaku .
PFX EB 0 egikyatu .
PFX EB 0 ekyan [^lmnb]
PFX EB l ekyand l.[^mn][^u]
PFX EB l ekyann l.[mn]
PFX EB w ekyamp [w]
PFX EB 0 ekyamu .
PFX EB 0 ekyaba .
PFX EB 0 ekyagu .
PFX EB 0 ekyagi .
PFX EB 0 ekyazi .
PFX EB 0 ekyaki .
PFX EB 0 ekyabi .
PFX EB 0 ekyali .
PFX EB 0 ekyaga .
PFX EB 0 ekyaka .
PFX EB 0 ekyabu .
PFX EB 0 ekyalu .
PFX EB 0 ekyaku .
PFX EB 0 ekyatu .
PFX EB 0 zikyan [^lmnb]
PFX EB l zikyand l.[^mn][^u]
PFX EB l zikyann l.[mn]
PFX EB w zikyamp [w]
PFX EB 0 zikyamu .
PFX EB 0 zikyaba .
PFX EB 0 zikyagu .
PFX EB 0 zikyagi .
PFX EB 0 zikyazi .
PFX EB 0 zikyaki .
PFX EB 0 zikyabi .
PFX EB 0 zikyali .
PFX EB 0 zikyaga .
PFX EB 0 zikyaka .
PFX EB 0 zikyabu .
PFX EB 0 zikyalu .
PFX EB 0 zikyaku .
PFX EB 0 zikyatu .
PFX EB 0 ezikyan [^lmnb]
PFX EB l ezikyand l.[^mn][^u]
PFX EB l ezikyann l.[mn]
PFX EB w ezikyamp [w]
PFX EB 0 ezikyamu .
PFX EB 0 ezikyaba .
PFX EB 0 ezikyagu .
PFX EB 0 ezikyagi .
PFX EB 0 ezikyazi .
PFX EB 0 ezikyaki .
PFX EB 0 ezikyabi .
PFX EB 0 ezikyali .
PFX EB 0 ezikyaga .
PFX EB 0 ezikyaka .
PFX EB 0 ezikyabu .
PFX EB 0 ezikyalu .
PFX EB 0 ezikyaku .
PFX EB 0 ezikyatu .
PFX EB 0 kikyan [^lmnb]
PFX EB l kikyand l.[^mn][^u]
PFX EB l kikyann l.[mn]
PFX EB w kikyamp [w]
PFX EB 0 kikyamu .
PFX EB 0 kikyaba .
PFX EB 0 kikyagu .
PFX EB 0 kikyagi .
PFX EB 0 kikyazi .
PFX EB 0 kikyaki .
PFX EB 0 kikyabi .
PFX EB 0 kikyali .
PFX EB 0 kikyaga .
PFX EB 0 kikyaka .
PFX EB 0 kikyabu .
PFX EB 0 kikyalu .
PFX EB 0 kikyaku .
PFX EB 0 kikyatu .
PFX EB 0 ekikyan [^lmnb]
PFX EB l ekikyand l.[^mn][^u]
PFX EB l ekikyann l.[mn]
PFX EB w ekikyamp [w]
PFX EB 0 ekikyamu .
PFX EB 0 ekikyaba .
PFX EB 0 ekikyagu .
PFX EB 0 ekikyagi .
PFX EB 0 ekikyazi .
PFX EB 0 ekikyaki .
PFX EB 0 ekikyabi .
PFX EB 0 ekikyali .
PFX EB 0 ekikyaga .
PFX EB 0 ekikyaka .
PFX EB 0 ekikyabu .
PFX EB 0 ekikyalu .
PFX EB 0 ekikyaku .
PFX EB 0 ekikyatu .
PFX EB 0 bikyan [^lmnb]
PFX EB l bikyand l.[^mn][^u]
PFX EB l bikyann l.[mn]
PFX EB w bikyamp [w]
PFX EB 0 bikyamu .
PFX EB 0 bikyaba .
PFX EB 0 bikyagu .
PFX EB 0 bikyagi .
PFX EB 0 bikyazi .
PFX EB 0 bikyaki .
PFX EB 0 bikyabi .
PFX EB 0 bikyali .
PFX EB 0 bikyaga .
PFX EB 0 bikyaka .
PFX EB 0 bikyabu .
PFX EB 0 bikyalu .
PFX EB 0 bikyaku .
PFX EB 0 bikyatu .
PFX EB 0 ebikyan [^lmnb]
PFX EB l ebikyand l.[^mn][^u]
PFX EB l ebikyann l.[mn]
PFX EB w ebikyamp [w]
PFX EB 0 ebikyamu .
PFX EB 0 ebikyaba .
PFX EB 0 ebikyagu .
PFX EB 0 ebikyagi .
PFX EB 0 ebikyazi .
PFX EB 0 ebikyaki .
PFX EB 0 ebikyabi .
PFX EB 0 ebikyali .
PFX EB 0 ebikyaga .
PFX EB 0 ebikyaka .
PFX EB 0 ebikyabu .
PFX EB 0 ebikyalu .
PFX EB 0 ebikyaku .
PFX EB 0 ebikyatu .
PFX EB 0 likyan [^lmnb]
PFX EB l likyand l.[^mn][^u]
PFX EB l likyann l.[mn]
PFX EB w likyamp [w]
PFX EB 0 likyamu .
PFX EB 0 likyaba .
PFX EB 0 likyagu .
PFX EB 0 likyagi .
PFX EB 0 likyazi .
PFX EB 0 likyaki .
PFX EB 0 likyabi .
PFX EB 0 likyali .
PFX EB 0 likyaga .
PFX EB 0 likyaka .
PFX EB 0 likyabu .
PFX EB 0 likyalu .
PFX EB 0 likyaku .
PFX EB 0 likyatu .
PFX EB 0 elikyan [^lmnb]
PFX EB l elikyand l.[^mn][^u]
PFX EB l elikyann l.[mn]
PFX EB w elikyamp [w]
PFX EB 0 elikyamu .
PFX EB 0 elikyaba .
PFX EB 0 elikyagu .
PFX EB 0 elikyagi .
PFX EB 0 elikyazi .
PFX EB 0 elikyaki .
PFX EB 0 elikyabi .
PFX EB 0 elikyali .
PFX EB 0 elikyaga .
PFX EB 0 elikyaka .
PFX EB 0 elikyabu .
PFX EB 0 elikyalu .
PFX EB 0 elikyaku .
PFX EB 0 elikyatu .
PFX EB 0 gakyan [^lmnb]
PFX EB l gakyand l.[^mn][^u]
PFX EB l gakyann l.[mn]
PFX EB w gakyamp [w]
PFX EB 0 gakyamu .
PFX EB 0 gakyaba .
PFX EB 0 gakyagu .
PFX EB 0 gakyagi .
PFX EB 0 gakyazi .
PFX EB 0 gakyaki .
PFX EB 0 gakyabi .
PFX EB 0 gakyali .
PFX EB 0 gakyaga .
PFX EB 0 gakyaka .
PFX EB 0 gakyabu .
PFX EB 0 gakyalu .
PFX EB 0 gakyaku .
PFX EB 0 gakyatu .
PFX EB 0 agakyan [^lmnb]
PFX EB l agakyand l.[^mn][^u]
PFX EB l agakyann l.[mn]
PFX EB w agakyamp [w]
PFX EB 0 agakyamu .
PFX EB 0 agakyaba .
PFX EB 0 agakyagu .
PFX EB 0 agakyagi .
PFX EB 0 agakyazi .
PFX EB 0 agakyaki .
PFX EB 0 agakyabi .
PFX EB 0 agakyali .
PFX EB 0 agakyaga .
PFX EB 0 agakyaka .
PFX EB 0 agakyabu .
PFX EB 0 agakyalu .
PFX EB 0 agakyaku .
PFX EB 0 agakyatu .
PFX EB 0 kakyan [^lmnb]
PFX EB l kakyand l.[^mn][^u]
PFX EB l kakyann l.[mn]
PFX EB w kakyamp [w]
PFX EB 0 kakyamu .
PFX EB 0 kakyaba .
PFX EB 0 kakyagu .
PFX EB 0 kakyagi .
PFX EB 0 kakyazi .
PFX EB 0 kakyaki .
PFX EB 0 kakyabi .
PFX EB 0 kakyali .
PFX EB 0 kakyaga .
PFX EB 0 kakyaka .
PFX EB 0 kakyabu .
PFX EB 0 kakyalu .
PFX EB 0 kakyaku .
PFX EB 0 kakyatu .
PFX EB 0 akakyan [^lmnb]
PFX EB l akakyand l.[^mn][^u]
PFX EB l akakyann l.[mn]
PFX EB w akakyamp [w]
PFX EB 0 akakyamu .
PFX EB 0 akakyaba .
PFX EB 0 akakyagu .
PFX EB 0 akakyagi .
PFX EB 0 akakyazi .
PFX EB 0 akakyaki .
PFX EB 0 akakyabi .
PFX EB 0 akakyali .
PFX EB 0 akakyaga .
PFX EB 0 akakyaka .
PFX EB 0 akakyabu .
PFX EB 0 akakyalu .
PFX EB 0 akakyaku .
PFX EB 0 akakyatu .
PFX EB 0 bukyan [^lmnb]
PFX EB l bukyand l.[^mn][^u]
PFX EB l bukyann l.[mn]
PFX EB w bukyamp [w]
PFX EB 0 bukyamu .
PFX EB 0 bukyaba .
PFX EB 0 bukyagu .
PFX EB 0 bukyagi .
PFX EB 0 bukyazi .
PFX EB 0 bukyaki .
PFX EB 0 bukyabi .
PFX EB 0 bukyali .
PFX EB 0 bukyaga .
PFX EB 0 bukyaka .
PFX EB 0 bukyabu .
PFX EB 0 bukyalu .
PFX EB 0 bukyaku .
PFX EB 0 bukyatu .
PFX EB 0 obukyan [^lmnb]
PFX EB l obukyand l.[^mn][^u]
PFX EB l obukyann l.[mn]
PFX EB w obukyamp [w]
PFX EB 0 obukyamu .
PFX EB 0 obukyaba .
PFX EB 0 obukyagu .
PFX EB 0 obukyagi .
PFX EB 0 obukyazi .
PFX EB 0 obukyaki .
PFX EB 0 obukyabi .
PFX EB 0 obukyali .
PFX EB 0 obukyaga .
PFX EB 0 obukyaka .
PFX EB 0 obukyabu .
PFX EB 0 obukyalu .
PFX EB 0 obukyaku .
PFX EB 0 obukyatu .
PFX EB 0 lukyan [^lmnb]
PFX EB l lukyand l.[^mn][^u]
PFX EB l lukyann l.[mn]
PFX EB w lukyamp [w]
PFX EB 0 lukyamu .
PFX EB 0 lukyaba .
PFX EB 0 lukyagu .
PFX EB 0 lukyagi .
PFX EB 0 lukyazi .
PFX EB 0 lukyaki .
PFX EB 0 lukyabi .
PFX EB 0 lukyali .
PFX EB 0 lukyaga .
PFX EB 0 lukyaka .
PFX EB 0 lukyabu .
PFX EB 0 lukyalu .
PFX EB 0 lukyaku .
PFX EB 0 lukyatu .
PFX EB 0 olukyan [^lmnb]
PFX EB l olukyand l.[^mn][^u]
PFX EB l olukyann l.[mn]
PFX EB w olukyamp [w]
PFX EB 0 olukyamu .
PFX EB 0 olukyaba .
PFX EB 0 olukyagu .
PFX EB 0 olukyagi .
PFX EB 0 olukyazi .
PFX EB 0 olukyaki .
PFX EB 0 olukyabi .
PFX EB 0 olukyali .
PFX EB 0 olukyaga .
PFX EB 0 olukyaka .
PFX EB 0 olukyabu .
PFX EB 0 olukyalu .
PFX EB 0 olukyaku .
PFX EB 0 olukyatu .
PFX EB 0 kukyan [^lmnb]
PFX EB l kukyand l.[^mn][^u]
PFX EB l kukyann l.[mn]
PFX EB w kukyamp [w]
PFX EB 0 kukyamu .
PFX EB 0 kukyaba .
PFX EB 0 kukyagu .
PFX EB 0 kukyagi .
PFX EB 0 kukyazi .
PFX EB 0 kukyaki .
PFX EB 0 kukyabi .
PFX EB 0 kukyali .
PFX EB 0 kukyaga .
PFX EB 0 kukyaka .
PFX EB 0 kukyabu .
PFX EB 0 kukyalu .
PFX EB 0 kukyaku .
PFX EB 0 kukyatu .
PFX EB 0 okukyan [^lmnb]
PFX EB l okukyand l.[^mn][^u]
PFX EB l okukyann l.[mn]
PFX EB w okukyamp [w]
PFX EB 0 okukyamu .
PFX EB 0 okukyaba .
PFX EB 0 okukyagu .
PFX EB 0 okukyagi .
PFX EB 0 okukyazi .
PFX EB 0 okukyaki .
PFX EB 0 okukyabi .
PFX EB 0 okukyali .
PFX EB 0 okukyaga .
PFX EB 0 okukyaka .
PFX EB 0 okukyabu .
PFX EB 0 okukyalu .
PFX EB 0 okukyaku .
PFX EB 0 okukyatu .
PFX EB 0 tukyan [^lmnb]
PFX EB l tukyand l.[^mn][^u]
PFX EB l tukyann l.[mn]
PFX EB w tukyamp [w]
PFX EB 0 tukyamu .
PFX EB 0 tukyaba .
PFX EB 0 tukyagu .
PFX EB 0 tukyagi .
PFX EB 0 tukyazi .
PFX EB 0 tukyaki .
PFX EB 0 tukyabi .
PFX EB 0 tukyali .
PFX EB 0 tukyaga .
PFX EB 0 tukyaka .
PFX EB 0 tukyabu .
PFX EB 0 tukyalu .
PFX EB 0 tukyaku .
PFX EB 0 tukyatu .
PFX EB 0 otukyan [^lmnb]
PFX EB l otukyand l.[^mn][^u]
PFX EB l otukyann l.[mn]
PFX EB w otukyamp [w]
PFX EB 0 otukyamu .
PFX EB 0 otukyaba .
PFX EB 0 otukyagu .
PFX EB 0 otukyagi .
PFX EB 0 otukyazi .
PFX EB 0 otukyaki .
PFX EB 0 otukyabi .
PFX EB 0 otukyali .
PFX EB 0 otukyaga .
PFX EB 0 otukyaka .
PFX EB 0 otukyabu .
PFX EB 0 otukyalu .
PFX EB 0 otukyaku .
PFX EB 0 otukyatu ."""

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
    "EB": "EB",
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

    out_flag = "GY"
    left_desc = FLAG_DESCRIPTIONS.get("EB", "EB")
    right_desc = FLAG_DESCRIPTIONS.get("Ob", "Ob")
    comment_line = "# Cross product of {} ({}) and {} ({}) to {}".format(
        "EB", left_desc, "Ob", right_desc, out_flag
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
