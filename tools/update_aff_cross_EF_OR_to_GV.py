import re
import os
from pathlib import Path

# Cross product generator: EF x OR => GV
# Description:
# - Left block `EF`: EF
# - Right block `OR`: Special reflexive object markers
# - Output flag `GV`: Cross-product prefixes for EF x OR

REPO_ROOT = Path(__file__).resolve().parents[1]
AFF_FILE = REPO_ROOT / "Luganda.aff"

# If set to a flag name (e.g. "HB"), the generated cross-product block will be inserted
# immediately before the first "PFX <flag>" line when the output flag block doesn't
# already exist in the .aff.
INSERT_BEFORE_FLAG = "".strip() or None

rule_left_raw = """
PFX EF Y 608
PFX EF 0 sikyaba .
PFX EF 0 sikyagu .
PFX EF 0 sikyagi .
PFX EF 0 sikyazi .
PFX EF 0 sikyaki .
PFX EF 0 sikyabi .
PFX EF 0 sikyali .
PFX EF 0 sikyaga .
PFX EF 0 sikyaka .
PFX EF 0 sikyabu .
PFX EF 0 sikyalu .
PFX EF 0 sikyaku .
PFX EF 0 sikyatu .
PFX EF 0 sikyamu .
PFX EF 0 tokyan .
PFX EF 0 tokyand .
PFX EF 0 tokyann .
PFX EF 0 tokyamp .
PFX EF 0 tokyamu .
PFX EF 0 tokyaba .
PFX EF 0 tokyagu .
PFX EF 0 tokyagi .
PFX EF 0 tokyazi .
PFX EF 0 tokyaki .
PFX EF 0 tokyabi .
PFX EF 0 tokyali .
PFX EF 0 tokyaga .
PFX EF 0 tokyaka .
PFX EF 0 tokyabu .
PFX EF 0 tokyalu .
PFX EF 0 tokyaku .
PFX EF 0 tokyatu .
PFX EF 0 takyan .
PFX EF 0 takyand .
PFX EF 0 takyann .
PFX EF 0 takyamp .
PFX EF 0 takyamu .
PFX EF 0 takyaba .
PFX EF 0 takyagu .
PFX EF 0 takyagi .
PFX EF 0 takyazi .
PFX EF 0 takyaki .
PFX EF 0 takyabi .
PFX EF 0 takyali .
PFX EF 0 takyaga .
PFX EF 0 takyaka .
PFX EF 0 takyabu .
PFX EF 0 takyalu .
PFX EF 0 takyaku .
PFX EF 0 takyatu .
PFX EF 0 atakyan .
PFX EF 0 atakyand .
PFX EF 0 atakyann .
PFX EF 0 atakyamp .
PFX EF 0 atakyamu .
PFX EF 0 atakyaba .
PFX EF 0 atakyagu .
PFX EF 0 atakyagi .
PFX EF 0 atakyazi .
PFX EF 0 atakyaki .
PFX EF 0 atakyabi .
PFX EF 0 atakyali .
PFX EF 0 atakyaga .
PFX EF 0 atakyaka .
PFX EF 0 atakyabu .
PFX EF 0 atakyalu .
PFX EF 0 atakyaku .
PFX EF 0 atakyatu .
PFX EF 0 tetukyan .
PFX EF 0 tetukyand .
PFX EF 0 tetukyann .
PFX EF 0 tetukyamp .
PFX EF 0 tetukyamu .
PFX EF 0 tetukyaba .
PFX EF 0 tetukyagu .
PFX EF 0 tetukyagi .
PFX EF 0 tetukyazi .
PFX EF 0 tetukyaki .
PFX EF 0 tetukyabi .
PFX EF 0 tetukyali .
PFX EF 0 tetukyaga .
PFX EF 0 tetukyaka .
PFX EF 0 tetukyabu .
PFX EF 0 tetukyalu .
PFX EF 0 tetukyaku .
PFX EF 0 tetukyatu .
PFX EF 0 temukyan .
PFX EF 0 temukyand .
PFX EF 0 temukyann .
PFX EF 0 temukyamp .
PFX EF 0 temukyamu .
PFX EF 0 temukyaba .
PFX EF 0 temukyagu .
PFX EF 0 temukyagi .
PFX EF 0 temukyazi .
PFX EF 0 temukyaki .
PFX EF 0 temukyabi .
PFX EF 0 temukyali .
PFX EF 0 temukyaga .
PFX EF 0 temukyaka .
PFX EF 0 temukyabu .
PFX EF 0 temukyalu .
PFX EF 0 temukyaku .
PFX EF 0 temukyatu .
PFX EF 0 tebakyan .
PFX EF 0 tebakyand .
PFX EF 0 tebakyann .
PFX EF 0 tebakyamp .
PFX EF 0 tebakyamu .
PFX EF 0 tebakyaba .
PFX EF 0 tebakyagu .
PFX EF 0 tebakyagi .
PFX EF 0 tebakyazi .
PFX EF 0 tebakyaki .
PFX EF 0 tebakyabi .
PFX EF 0 tebakyali .
PFX EF 0 tebakyaga .
PFX EF 0 tebakyaka .
PFX EF 0 tebakyabu .
PFX EF 0 tebakyalu .
PFX EF 0 tebakyaku .
PFX EF 0 tebakyatu .
PFX EF 0 abatakyan .
PFX EF 0 abatakyand .
PFX EF 0 abatakyann .
PFX EF 0 abatakyamp .
PFX EF 0 abatakyamu .
PFX EF 0 abatakyaba .
PFX EF 0 abatakyagu .
PFX EF 0 abatakyagi .
PFX EF 0 abatakyazi .
PFX EF 0 abatakyaki .
PFX EF 0 abatakyabi .
PFX EF 0 abatakyali .
PFX EF 0 abatakyaga .
PFX EF 0 abatakyaka .
PFX EF 0 abatakyabu .
PFX EF 0 abatakyalu .
PFX EF 0 abatakyaku .
PFX EF 0 abatakyatu .
PFX EF 0 tegukyan .
PFX EF 0 tegukyand .
PFX EF 0 tegukyann .
PFX EF 0 tegukyamp .
PFX EF 0 tegukyamu .
PFX EF 0 tegukyaba .
PFX EF 0 tegukyagu .
PFX EF 0 tegukyagi .
PFX EF 0 tegukyazi .
PFX EF 0 tegukyaki .
PFX EF 0 tegukyabi .
PFX EF 0 tegukyali .
PFX EF 0 tegukyaga .
PFX EF 0 tegukyaka .
PFX EF 0 tegukyabu .
PFX EF 0 tegukyalu .
PFX EF 0 tegukyaku .
PFX EF 0 tegukyatu .
PFX EF 0 ogutakyan .
PFX EF 0 ogutakyand .
PFX EF 0 ogutakyann .
PFX EF 0 ogutakyamp .
PFX EF 0 ogutakyamu .
PFX EF 0 ogutakyaba .
PFX EF 0 ogutakyagu .
PFX EF 0 ogutakyagi .
PFX EF 0 ogutakyazi .
PFX EF 0 ogutakyaki .
PFX EF 0 ogutakyabi .
PFX EF 0 ogutakyali .
PFX EF 0 ogutakyaga .
PFX EF 0 ogutakyaka .
PFX EF 0 ogutakyabu .
PFX EF 0 ogutakyalu .
PFX EF 0 ogutakyaku .
PFX EF 0 ogutakyatu .
PFX EF 0 tegikyan .
PFX EF 0 tegikyand .
PFX EF 0 tegikyann .
PFX EF 0 tegikyamp .
PFX EF 0 tegikyamu .
PFX EF 0 tegikyaba .
PFX EF 0 tegikyagu .
PFX EF 0 tegikyagi .
PFX EF 0 tegikyazi .
PFX EF 0 tegikyaki .
PFX EF 0 tegikyabi .
PFX EF 0 tegikyali .
PFX EF 0 tegikyaga .
PFX EF 0 tegikyaka .
PFX EF 0 tegikyabu .
PFX EF 0 tegikyalu .
PFX EF 0 tegikyaku .
PFX EF 0 tegikyatu .
PFX EF 0 egitakyan .
PFX EF 0 egitakyand .
PFX EF 0 egitakyann .
PFX EF 0 egitakyamp .
PFX EF 0 egitakyamu .
PFX EF 0 egitakyaba .
PFX EF 0 egitakyagu .
PFX EF 0 egitakyagi .
PFX EF 0 egitakyazi .
PFX EF 0 egitakyaki .
PFX EF 0 egitakyabi .
PFX EF 0 egitakyali .
PFX EF 0 egitakyaga .
PFX EF 0 egitakyaka .
PFX EF 0 egitakyabu .
PFX EF 0 egitakyalu .
PFX EF 0 egitakyaku .
PFX EF 0 egitakyatu .
PFX EF 0 tekyan .
PFX EF 0 tekyand .
PFX EF 0 tekyann .
PFX EF 0 tekyamp .
PFX EF 0 tekyamu .
PFX EF 0 tekyaba .
PFX EF 0 tekyagu .
PFX EF 0 tekyagi .
PFX EF 0 tekyazi .
PFX EF 0 tekyaki .
PFX EF 0 tekyabi .
PFX EF 0 tekyali .
PFX EF 0 tekyaga .
PFX EF 0 tekyaka .
PFX EF 0 tekyabu .
PFX EF 0 tekyalu .
PFX EF 0 tekyaku .
PFX EF 0 tekyatu .
PFX EF 0 etekyan .
PFX EF 0 etekyand .
PFX EF 0 etekyann .
PFX EF 0 etekyamp .
PFX EF 0 etekyamu .
PFX EF 0 etekyaba .
PFX EF 0 etekyagu .
PFX EF 0 etekyagi .
PFX EF 0 etekyazi .
PFX EF 0 etekyaki .
PFX EF 0 etekyabi .
PFX EF 0 etekyali .
PFX EF 0 etekyaga .
PFX EF 0 etekyaka .
PFX EF 0 etekyabu .
PFX EF 0 etekyalu .
PFX EF 0 etekyaku .
PFX EF 0 etekyatu .
PFX EF 0 tezikyan .
PFX EF 0 tezikyand .
PFX EF 0 tezikyann .
PFX EF 0 tezikyamp .
PFX EF 0 tezikyamu .
PFX EF 0 tezikyaba .
PFX EF 0 tezikyagu .
PFX EF 0 tezikyagi .
PFX EF 0 tezikyazi .
PFX EF 0 tezikyaki .
PFX EF 0 tezikyabi .
PFX EF 0 tezikyali .
PFX EF 0 tezikyaga .
PFX EF 0 tezikyaka .
PFX EF 0 tezikyabu .
PFX EF 0 tezikyalu .
PFX EF 0 tezikyaku .
PFX EF 0 tezikyatu .
PFX EF 0 ezitakyan .
PFX EF 0 ezitakyand .
PFX EF 0 ezitakyann .
PFX EF 0 ezitakyamp .
PFX EF 0 ezitakyamu .
PFX EF 0 ezitakyaba .
PFX EF 0 ezitakyagu .
PFX EF 0 ezitakyagi .
PFX EF 0 ezitakyazi .
PFX EF 0 ezitakyaki .
PFX EF 0 ezitakyabi .
PFX EF 0 ezitakyali .
PFX EF 0 ezitakyaga .
PFX EF 0 ezitakyaka .
PFX EF 0 ezitakyabu .
PFX EF 0 ezitakyalu .
PFX EF 0 ezitakyaku .
PFX EF 0 ezitakyatu .
PFX EF 0 tekikyan .
PFX EF 0 tekikyand .
PFX EF 0 tekikyann .
PFX EF 0 tekikyamp .
PFX EF 0 tekikyamu .
PFX EF 0 tekikyaba .
PFX EF 0 tekikyagu .
PFX EF 0 tekikyagi .
PFX EF 0 tekikyazi .
PFX EF 0 tekikyaki .
PFX EF 0 tekikyabi .
PFX EF 0 tekikyali .
PFX EF 0 tekikyaga .
PFX EF 0 tekikyaka .
PFX EF 0 tekikyabu .
PFX EF 0 tekikyalu .
PFX EF 0 tekikyaku .
PFX EF 0 tekikyatu .
PFX EF 0 ekitakyan .
PFX EF 0 ekitakyand .
PFX EF 0 ekitakyann .
PFX EF 0 ekitakyamp .
PFX EF 0 ekitakyamu .
PFX EF 0 ekitakyaba .
PFX EF 0 ekitakyagu .
PFX EF 0 ekitakyagi .
PFX EF 0 ekitakyazi .
PFX EF 0 ekitakyaki .
PFX EF 0 ekitakyabi .
PFX EF 0 ekitakyali .
PFX EF 0 ekitakyaga .
PFX EF 0 ekitakyaka .
PFX EF 0 ekitakyabu .
PFX EF 0 ekitakyalu .
PFX EF 0 ekitakyaku .
PFX EF 0 ekitakyatu .
PFX EF 0 tebikyan .
PFX EF 0 tebikyand .
PFX EF 0 tebikyann .
PFX EF 0 tebikyamp .
PFX EF 0 tebikyamu .
PFX EF 0 tebikyaba .
PFX EF 0 tebikyagu .
PFX EF 0 tebikyagi .
PFX EF 0 tebikyazi .
PFX EF 0 tebikyaki .
PFX EF 0 tebikyabi .
PFX EF 0 tebikyali .
PFX EF 0 tebikyaga .
PFX EF 0 tebikyaka .
PFX EF 0 tebikyabu .
PFX EF 0 tebikyalu .
PFX EF 0 tebikyaku .
PFX EF 0 tebikyatu .
PFX EF 0 ebitakyan .
PFX EF 0 ebitakyand .
PFX EF 0 ebitakyann .
PFX EF 0 ebitakyamp .
PFX EF 0 ebitakyamu .
PFX EF 0 ebitakyaba .
PFX EF 0 ebitakyagu .
PFX EF 0 ebitakyagi .
PFX EF 0 ebitakyazi .
PFX EF 0 ebitakyaki .
PFX EF 0 ebitakyabi .
PFX EF 0 ebitakyali .
PFX EF 0 ebitakyaga .
PFX EF 0 ebitakyaka .
PFX EF 0 ebitakyabu .
PFX EF 0 ebitakyalu .
PFX EF 0 ebitakyaku .
PFX EF 0 ebitakyatu .
PFX EF 0 telikyan .
PFX EF 0 telikyand .
PFX EF 0 telikyann .
PFX EF 0 telikyamp .
PFX EF 0 telikyamu .
PFX EF 0 telikyaba .
PFX EF 0 telikyagu .
PFX EF 0 telikyagi .
PFX EF 0 telikyazi .
PFX EF 0 telikyaki .
PFX EF 0 telikyabi .
PFX EF 0 telikyali .
PFX EF 0 telikyaga .
PFX EF 0 telikyaka .
PFX EF 0 telikyabu .
PFX EF 0 telikyalu .
PFX EF 0 telikyaku .
PFX EF 0 telikyatu .
PFX EF 0 elitakyan .
PFX EF 0 elitakyand .
PFX EF 0 elitakyann .
PFX EF 0 elitakyamp .
PFX EF 0 elitakyamu .
PFX EF 0 elitakyaba .
PFX EF 0 elitakyagu .
PFX EF 0 elitakyagi .
PFX EF 0 elitakyazi .
PFX EF 0 elitakyaki .
PFX EF 0 elitakyabi .
PFX EF 0 elitakyali .
PFX EF 0 elitakyaga .
PFX EF 0 elitakyaka .
PFX EF 0 elitakyabu .
PFX EF 0 elitakyalu .
PFX EF 0 elitakyaku .
PFX EF 0 elitakyatu .
PFX EF 0 tegakyan .
PFX EF 0 tegakyand .
PFX EF 0 tegakyann .
PFX EF 0 tegakyamp .
PFX EF 0 tegakyamu .
PFX EF 0 tegakyaba .
PFX EF 0 tegakyagu .
PFX EF 0 tegakyagi .
PFX EF 0 tegakyazi .
PFX EF 0 tegakyaki .
PFX EF 0 tegakyabi .
PFX EF 0 tegakyali .
PFX EF 0 tegakyaga .
PFX EF 0 tegakyaka .
PFX EF 0 tegakyabu .
PFX EF 0 tegakyalu .
PFX EF 0 tegakyaku .
PFX EF 0 tegakyatu .
PFX EF 0 agatakyan .
PFX EF 0 agatakyand .
PFX EF 0 agatakyann .
PFX EF 0 agatakyamp .
PFX EF 0 agatakyamu .
PFX EF 0 agatakyaba .
PFX EF 0 agatakyagu .
PFX EF 0 agatakyagi .
PFX EF 0 agatakyazi .
PFX EF 0 agatakyaki .
PFX EF 0 agatakyabi .
PFX EF 0 agatakyali .
PFX EF 0 agatakyaga .
PFX EF 0 agatakyaka .
PFX EF 0 agatakyabu .
PFX EF 0 agatakyalu .
PFX EF 0 agatakyaku .
PFX EF 0 agatakyatu .
PFX EF 0 tekakyan .
PFX EF 0 tekakyand .
PFX EF 0 tekakyann .
PFX EF 0 tekakyamp .
PFX EF 0 tekakyamu .
PFX EF 0 tekakyaba .
PFX EF 0 tekakyagu .
PFX EF 0 tekakyagi .
PFX EF 0 tekakyazi .
PFX EF 0 tekakyaki .
PFX EF 0 tekakyabi .
PFX EF 0 tekakyali .
PFX EF 0 tekakyaga .
PFX EF 0 tekakyaka .
PFX EF 0 tekakyabu .
PFX EF 0 tekakyalu .
PFX EF 0 tekakyaku .
PFX EF 0 tekakyatu .
PFX EF 0 akatakyan .
PFX EF 0 akatakyand .
PFX EF 0 akatakyann .
PFX EF 0 akatakyamp .
PFX EF 0 akatakyamu .
PFX EF 0 akatakyaba .
PFX EF 0 akatakyagu .
PFX EF 0 akatakyagi .
PFX EF 0 akatakyazi .
PFX EF 0 akatakyaki .
PFX EF 0 akatakyabi .
PFX EF 0 akatakyali .
PFX EF 0 akatakyaga .
PFX EF 0 akatakyaka .
PFX EF 0 akatakyabu .
PFX EF 0 akatakyalu .
PFX EF 0 akatakyaku .
PFX EF 0 akatakyatu .
PFX EF 0 tebukyan .
PFX EF 0 tebukyand .
PFX EF 0 tebukyann .
PFX EF 0 tebukyamp .
PFX EF 0 tebukyamu .
PFX EF 0 tebukyaba .
PFX EF 0 tebukyagu .
PFX EF 0 tebukyagi .
PFX EF 0 tebukyazi .
PFX EF 0 tebukyaki .
PFX EF 0 tebukyabi .
PFX EF 0 tebukyali .
PFX EF 0 tebukyaga .
PFX EF 0 tebukyaka .
PFX EF 0 tebukyabu .
PFX EF 0 tebukyalu .
PFX EF 0 tebukyaku .
PFX EF 0 tebukyatu .
PFX EF 0 obutakyan .
PFX EF 0 obutakyand .
PFX EF 0 obutakyann .
PFX EF 0 obutakyamp .
PFX EF 0 obutakyamu .
PFX EF 0 obutakyaba .
PFX EF 0 obutakyagu .
PFX EF 0 obutakyagi .
PFX EF 0 obutakyazi .
PFX EF 0 obutakyaki .
PFX EF 0 obutakyabi .
PFX EF 0 obutakyali .
PFX EF 0 obutakyaga .
PFX EF 0 obutakyaka .
PFX EF 0 obutakyabu .
PFX EF 0 obutakyalu .
PFX EF 0 obutakyaku .
PFX EF 0 obutakyatu .
PFX EF 0 telukyan .
PFX EF 0 telukyand .
PFX EF 0 telukyann .
PFX EF 0 telukyamp .
PFX EF 0 telukyamu .
PFX EF 0 telukyaba .
PFX EF 0 telukyagu .
PFX EF 0 telukyagi .
PFX EF 0 telukyazi .
PFX EF 0 telukyaki .
PFX EF 0 telukyabi .
PFX EF 0 telukyali .
PFX EF 0 telukyaga .
PFX EF 0 telukyaka .
PFX EF 0 telukyabu .
PFX EF 0 telukyalu .
PFX EF 0 telukyaku .
PFX EF 0 telukyatu .
PFX EF 0 olutakyan .
PFX EF 0 olutakyand .
PFX EF 0 olutakyann .
PFX EF 0 olutakyamp .
PFX EF 0 olutakyamu .
PFX EF 0 olutakyaba .
PFX EF 0 olutakyagu .
PFX EF 0 olutakyagi .
PFX EF 0 olutakyazi .
PFX EF 0 olutakyaki .
PFX EF 0 olutakyabi .
PFX EF 0 olutakyali .
PFX EF 0 olutakyaga .
PFX EF 0 olutakyaka .
PFX EF 0 olutakyabu .
PFX EF 0 olutakyalu .
PFX EF 0 olutakyaku .
PFX EF 0 olutakyatu .
PFX EF 0 tekukyan .
PFX EF 0 tekukyand .
PFX EF 0 tekukyann .
PFX EF 0 tekukyamp .
PFX EF 0 tekukyamu .
PFX EF 0 tekukyaba .
PFX EF 0 tekukyagu .
PFX EF 0 tekukyagi .
PFX EF 0 tekukyazi .
PFX EF 0 tekukyaki .
PFX EF 0 tekukyabi .
PFX EF 0 tekukyali .
PFX EF 0 tekukyaga .
PFX EF 0 tekukyaka .
PFX EF 0 tekukyabu .
PFX EF 0 tekukyalu .
PFX EF 0 tekukyaku .
PFX EF 0 tekukyatu .
PFX EF 0 okutakyan .
PFX EF 0 okutakyand .
PFX EF 0 okutakyann .
PFX EF 0 okutakyamp .
PFX EF 0 okutakyamu .
PFX EF 0 okutakyaba .
PFX EF 0 okutakyagu .
PFX EF 0 okutakyagi .
PFX EF 0 okutakyazi .
PFX EF 0 okutakyaki .
PFX EF 0 okutakyabi .
PFX EF 0 okutakyali .
PFX EF 0 okutakyaga .
PFX EF 0 okutakyaka .
PFX EF 0 okutakyabu .
PFX EF 0 okutakyalu .
PFX EF 0 okutakyaku .
PFX EF 0 okutakyatu .
PFX EF 0 tetukyan .
PFX EF 0 tetukyand .
PFX EF 0 tetukyann .
PFX EF 0 tetukyamp .
PFX EF 0 tetukyamu .
PFX EF 0 tetukyaba .
PFX EF 0 tetukyagu .
PFX EF 0 tetukyagi .
PFX EF 0 tetukyazi .
PFX EF 0 tetukyaki .
PFX EF 0 tetukyabi .
PFX EF 0 tetukyali .
PFX EF 0 tetukyaga .
PFX EF 0 tetukyaka .
PFX EF 0 tetukyabu .
PFX EF 0 tetukyalu .
PFX EF 0 tetukyaku .
PFX EF 0 tetukyatu .
PFX EF 0 otutakyan .
PFX EF 0 otutakyand .
PFX EF 0 otutakyann .
PFX EF 0 otutakyamp .
PFX EF 0 otutakyamu .
PFX EF 0 otutakyaba .
PFX EF 0 otutakyagu .
PFX EF 0 otutakyagi .
PFX EF 0 otutakyazi .
PFX EF 0 otutakyaki .
PFX EF 0 otutakyabi .
PFX EF 0 otutakyali .
PFX EF 0 otutakyaga .
PFX EF 0 otutakyaka .
PFX EF 0 otutakyabu .
PFX EF 0 otutakyalu .
PFX EF 0 otutakyaku .
PFX EF 0 otutakyatu ."""

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
    "EF": "EF",
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

    out_flag = "GV"
    left_desc = FLAG_DESCRIPTIONS.get("EF", "EF")
    right_desc = FLAG_DESCRIPTIONS.get("OR", "OR")
    comment_line = "# Cross product of {} ({}) and {} ({}) to {}".format(
        "EF", left_desc, "OR", right_desc, out_flag
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
