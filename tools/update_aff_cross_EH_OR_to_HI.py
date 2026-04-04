import re
import os
from pathlib import Path

# Cross product generator: EH x OR => HI
# Description:
# - Left block `EH`: EH
# - Right block `OR`: Special reflexive object markers
# - Output flag `HI`: Cross-product prefixes for EH x OR

REPO_ROOT = Path(__file__).resolve().parents[1]
AFF_FILE = REPO_ROOT / "Luganda.aff"

# If set to a flag name (e.g. "HB"), the generated cross-product block will be inserted
# immediately before the first "PFX <flag>" line when the output flag block doesn't
# already exist in the .aff.
INSERT_BEFORE_FLAG = "".strip() or None

rule_left_raw = """
PFX EH Y 654
PFX EH 0 bwengu .
PFX EH 0 bwengi .
PFX EH 0 bwenzi .
PFX EH 0 bwenki .
PFX EH 0 bwenga .
PFX EH 0 bwenka .
PFX EH 0 bwenku .
PFX EH 0 bwentu .
PFX EH 0 bwemba .
PFX EH 0 bwembi .
PFX EH 0 bwembu .
PFX EH 0 on [^lmnb]
PFX EH l ond l.[^mn]
PFX EH l onn l.[mn]
PFX EH w omp w
PFX EH 0 omu .
PFX EH 0 oba .
PFX EH 0 ogu .
PFX EH 0 ogi .
PFX EH 0 ozi .
PFX EH 0 oki .
PFX EH 0 obi .
PFX EH 0 oli .
PFX EH 0 oga .
PFX EH 0 oka .
PFX EH 0 obu .
PFX EH 0 olu .
PFX EH 0 oku .
PFX EH 0 otu .
PFX EH 0 bwendi .
PFX EH 0 an [^lmnb]
PFX EH l and l.[^mn]
PFX EH l ann l.[mn]
PFX EH w amp w
PFX EH 0 amu .
PFX EH 0 aba .
PFX EH 0 agu .
PFX EH 0 agi .
PFX EH 0 azi .
PFX EH 0 aki .
PFX EH 0 abi .
PFX EH 0 ali .
PFX EH 0 aga .
PFX EH 0 aka .
PFX EH 0 abu .
PFX EH 0 alu .
PFX EH 0 aku .
PFX EH 0 atu .
PFX EH 0 bwetun [^lmnb]
PFX EH l bwetund l.[^mn]
PFX EH l bwetunn l.[mn]
PFX EH w bwetump w
PFX EH 0 bwetumu .
PFX EH 0 bwetuba .
PFX EH 0 bwetugu .
PFX EH 0 bwetugi .
PFX EH 0 bwetuzi .
PFX EH 0 bwetuki .
PFX EH 0 bwetubi .
PFX EH 0 bwetuli .
PFX EH 0 bwetuga .
PFX EH 0 bwetuka .
PFX EH 0 bwetubu .
PFX EH 0 bwetulu .
PFX EH 0 bwetuku .
PFX EH 0 bwetutu .
PFX EH 0 bwemun [^lmnb]
PFX EH l bwemund l.[^mn]
PFX EH l bwemunn l.[mn]
PFX EH w bwemump w
PFX EH 0 bwemumu .
PFX EH 0 bwemuba .
PFX EH 0 bwemugu .
PFX EH 0 bwemugi .
PFX EH 0 bwemuzi .
PFX EH 0 bwemuki .
PFX EH 0 bwemubi .
PFX EH 0 bwemuli .
PFX EH 0 bwemuga .
PFX EH 0 bwemuka .
PFX EH 0 bwemubu .
PFX EH 0 bwemulu .
PFX EH 0 bwemuku .
PFX EH 0 bwemutu .
PFX EH 0 bweban [^lmnb]
PFX EH l bweband l.[^mn]
PFX EH l bwebann l.[mn]
PFX EH w bwebamp w
PFX EH 0 bwebamu .
PFX EH 0 bwebaba .
PFX EH 0 bwebagu .
PFX EH 0 bwebagi .
PFX EH 0 bwebazi .
PFX EH 0 bwebaki .
PFX EH 0 bwebabi .
PFX EH 0 bwebali .
PFX EH 0 bwebaga .
PFX EH 0 bwebaka .
PFX EH 0 bwebabu .
PFX EH 0 bwebalu .
PFX EH 0 bwebaku .
PFX EH 0 bwebatu .
PFX EH 0 bweban [^lmnb]
PFX EH l bweband l.[^mn]
PFX EH l bwebann l.[mn]
PFX EH w bwebamp w
PFX EH 0 bwebamu .
PFX EH 0 bwebaba .
PFX EH 0 bwebagu .
PFX EH 0 bwebagi .
PFX EH 0 bwebazi .
PFX EH 0 bwebaki .
PFX EH 0 bwebabi .
PFX EH 0 bwebali .
PFX EH 0 bwebaga .
PFX EH 0 bwebaka .
PFX EH 0 bwebabu .
PFX EH 0 bwebalu .
PFX EH 0 bwebaku .
PFX EH 0 bwebatu .
PFX EH 0 bwegun [^lmnb]
PFX EH l bwegund l.[^mn]
PFX EH l bwegunn l.[mn]
PFX EH w bwegump w
PFX EH 0 bwegumu .
PFX EH 0 bweguba .
PFX EH 0 bwegugu .
PFX EH 0 bwegugi .
PFX EH 0 bweguzi .
PFX EH 0 bweguki .
PFX EH 0 bwegubi .
PFX EH 0 bweguli .
PFX EH 0 bweguga .
PFX EH 0 bweguka .
PFX EH 0 bwegubu .
PFX EH 0 bwegulu .
PFX EH 0 bweguku .
PFX EH 0 bwegutu .
PFX EH 0 bwegin [^lmnb]
PFX EH l bwegind l.[^mn]
PFX EH l bweginn l.[mn]
PFX EH w bwegimp w
PFX EH 0 bwegimu .
PFX EH 0 bwegiba .
PFX EH 0 bwegigu .
PFX EH 0 bwegigi .
PFX EH 0 bwegizi .
PFX EH 0 bwegiki .
PFX EH 0 bwegibi .
PFX EH 0 bwegili .
PFX EH 0 bwegiga .
PFX EH 0 bwegika .
PFX EH 0 bwegibu .
PFX EH 0 bwegilu .
PFX EH 0 bwegiku .
PFX EH 0 bwegitu .
PFX EH 0 en [^lmnb]
PFX EH l end l.[^mn]
PFX EH l enn l.[mn]
PFX EH w emp w
PFX EH 0 emu .
PFX EH 0 eba .
PFX EH 0 egu .
PFX EH 0 egi .
PFX EH 0 ezi .
PFX EH 0 eki .
PFX EH 0 ebi .
PFX EH 0 eli .
PFX EH 0 ega .
PFX EH 0 eka .
PFX EH 0 ebu .
PFX EH 0 elu .
PFX EH 0 eku .
PFX EH 0 etu .
PFX EH 0 bwezin [^lmnb]
PFX EH l bwezind l.[^mn]
PFX EH l bwezinn l.[mn]
PFX EH w bwezimp w
PFX EH 0 bwezimu .
PFX EH 0 bweziba .
PFX EH 0 bwezigu .
PFX EH 0 bwezigi .
PFX EH 0 bwezizi .
PFX EH 0 bweziki .
PFX EH 0 bwezibi .
PFX EH 0 bwezili .
PFX EH 0 bweziga .
PFX EH 0 bwezika .
PFX EH 0 bwezibu .
PFX EH 0 bwezilu .
PFX EH 0 bweziku .
PFX EH 0 bwezitu .
PFX EH 0 bwekin [^lmnb]
PFX EH l bwekind l.[^mn]
PFX EH l bwekinn l.[mn]
PFX EH w bwekimp w
PFX EH 0 bwekimu .
PFX EH 0 bwekiba .
PFX EH 0 bwekigu .
PFX EH 0 bwekigi .
PFX EH 0 bwekizi .
PFX EH 0 bwekiki .
PFX EH 0 bwekibi .
PFX EH 0 bwekili .
PFX EH 0 bwekiga .
PFX EH 0 bwekika .
PFX EH 0 bwekibu .
PFX EH 0 bwekilu .
PFX EH 0 bwekiku .
PFX EH 0 bwekitu .
PFX EH 0 bwebin [^lmnb]
PFX EH l bwebind l.[^mn]
PFX EH l bwebinn l.[mn]
PFX EH w bwebimp w
PFX EH 0 bwebimu .
PFX EH 0 bwebiba .
PFX EH 0 bwebigu .
PFX EH 0 bwebigi .
PFX EH 0 bwebizi .
PFX EH 0 bwebiki .
PFX EH 0 bwebibi .
PFX EH 0 bwebili .
PFX EH 0 bwebiga .
PFX EH 0 bwebika .
PFX EH 0 bwebibu .
PFX EH 0 bwebilu .
PFX EH 0 bwebiku .
PFX EH 0 bwebitu .
PFX EH 0 bwelin [^lmnb]
PFX EH l bwelind l.[^mn]
PFX EH l bwelinn l.[mn]
PFX EH w bwelimp w
PFX EH 0 bwelimu .
PFX EH 0 bweliba .
PFX EH 0 bweligu .
PFX EH 0 bweligi .
PFX EH 0 bwelizi .
PFX EH 0 bweliki .
PFX EH 0 bwelibi .
PFX EH 0 bwelili .
PFX EH 0 bweliga .
PFX EH 0 bwelika .
PFX EH 0 bwelibu .
PFX EH 0 bwelilu .
PFX EH 0 bweliku .
PFX EH 0 bwelitu .
PFX EH 0 bwegan [^lmnb]
PFX EH l bwegand l.[^mn]
PFX EH l bwegann l.[mn]
PFX EH w bwegamp w
PFX EH 0 bwegamu .
PFX EH 0 bwegaba .
PFX EH 0 bwegagu .
PFX EH 0 bwegagi .
PFX EH 0 bwegazi .
PFX EH 0 bwegaki .
PFX EH 0 bwegabi .
PFX EH 0 bwegali .
PFX EH 0 bwegaga .
PFX EH 0 bwegaka .
PFX EH 0 bwegabu .
PFX EH 0 bwegalu .
PFX EH 0 bwegaku .
PFX EH 0 bwegatu .
PFX EH 0 bwekan [^lmnb]
PFX EH l bwekand l.[^mn]
PFX EH l bwekann l.[mn]
PFX EH w bwekamp w
PFX EH 0 bwekamu .
PFX EH 0 bwekaba .
PFX EH 0 bwekagu .
PFX EH 0 bwekagi .
PFX EH 0 bwekazi .
PFX EH 0 bwekaki .
PFX EH 0 bwekabi .
PFX EH 0 bwekali .
PFX EH 0 bwekaga .
PFX EH 0 bwekaka .
PFX EH 0 bwekabu .
PFX EH 0 bwekalu .
PFX EH 0 bwekaku .
PFX EH 0 bwekatu .
PFX EH 0 bwebun [^lmnb]
PFX EH l bwebund l.[^mn]
PFX EH l bwebunn l.[mn]
PFX EH w bwebump w
PFX EH 0 bwebumu .
PFX EH 0 bwebuba .
PFX EH 0 bwebugu .
PFX EH 0 bwebugi .
PFX EH 0 bwebuzi .
PFX EH 0 bwebuki .
PFX EH 0 bwebubi .
PFX EH 0 bwebuli .
PFX EH 0 bwebuga .
PFX EH 0 bwebuka .
PFX EH 0 bwebubu .
PFX EH 0 bwebulu .
PFX EH 0 bwebuku .
PFX EH 0 bwebutu .
PFX EH 0 bwelun [^lmnb]
PFX EH l bwelund l.[^mn]
PFX EH l bwelunn l.[mn]
PFX EH w bwelump w
PFX EH 0 bwelumu .
PFX EH 0 bweluba .
PFX EH 0 bwelugu .
PFX EH 0 bwelugi .
PFX EH 0 bweluzi .
PFX EH 0 bweluki .
PFX EH 0 bwelubi .
PFX EH 0 bweluli .
PFX EH 0 bweluga .
PFX EH 0 bweluka .
PFX EH 0 bwelubu .
PFX EH 0 bwelulu .
PFX EH 0 bweluku .
PFX EH 0 bwelutu .
PFX EH 0 bwekun [^lmnb]
PFX EH l bwekund l.[^mn]
PFX EH l bwekunn l.[mn]
PFX EH w bwekump w
PFX EH 0 bwekumu .
PFX EH 0 bwekuba .
PFX EH 0 bwekugu .
PFX EH 0 bwekugi .
PFX EH 0 bwekuzi .
PFX EH 0 bwekuki .
PFX EH 0 bwekubi .
PFX EH 0 bwekuli .
PFX EH 0 bwekuga .
PFX EH 0 bwekuka .
PFX EH 0 bwekubu .
PFX EH 0 bwekulu .
PFX EH 0 bwekuku .
PFX EH 0 bwekutu .
PFX EH 0 bwetun [^lmnb]
PFX EH l bwetund l.[^mn]
PFX EH l bwetunn l.[mn]
PFX EH w bwetump w
PFX EH 0 bwetumu .
PFX EH 0 bwetuba .
PFX EH 0 bwetugu .
PFX EH 0 bwetugi .
PFX EH 0 bwetuzi .
PFX EH 0 bwetuki .
PFX EH 0 bwetubi .
PFX EH 0 bwetuli .
PFX EH 0 bwetuga .
PFX EH 0 bwetuka .
PFX EH 0 bwetubu .
PFX EH 0 bwetulu .
PFX EH 0 bwetuku .
PFX EH 0 bwetutu .
PFX EH 0 wengu .
PFX EH 0 wengi .
PFX EH 0 wenzi .
PFX EH 0 wenki .
PFX EH 0 wenga .
PFX EH 0 wenka .
PFX EH 0 wenku .
PFX EH 0 wentu .
PFX EH 0 wemba .
PFX EH 0 wembi .
PFX EH 0 wembu .
PFX EH 0 wendi .
PFX EH 0 wetun [^lmnb]
PFX EH l wetund l.[^mn]
PFX EH l wetunn l.[mn]
PFX EH w wetump w
PFX EH 0 wetumu .
PFX EH 0 wetuba .
PFX EH 0 wetugu .
PFX EH 0 wetugi .
PFX EH 0 wetuzi .
PFX EH 0 wetuki .
PFX EH 0 wetubi .
PFX EH 0 wetuli .
PFX EH 0 wetuga .
PFX EH 0 wetuka .
PFX EH 0 wetubu .
PFX EH 0 wetulu .
PFX EH 0 wetuku .
PFX EH 0 wetutu .
PFX EH 0 wemun [^lmnb]
PFX EH l wemund l.[^mn]
PFX EH l wemunn l.[mn]
PFX EH w wemump w
PFX EH 0 wemumu .
PFX EH 0 wemuba .
PFX EH 0 wemugu .
PFX EH 0 wemugi .
PFX EH 0 wemuzi .
PFX EH 0 wemuki .
PFX EH 0 wemubi .
PFX EH 0 wemuli .
PFX EH 0 wemuga .
PFX EH 0 wemuka .
PFX EH 0 wemubu .
PFX EH 0 wemulu .
PFX EH 0 wemuku .
PFX EH 0 wemutu .
PFX EH 0 weban [^lmnb]
PFX EH l weband l.[^mn]
PFX EH l webann l.[mn]
PFX EH w webamp w
PFX EH 0 webamu .
PFX EH 0 webaba .
PFX EH 0 webagu .
PFX EH 0 webagi .
PFX EH 0 webazi .
PFX EH 0 webaki .
PFX EH 0 webabi .
PFX EH 0 webali .
PFX EH 0 webaga .
PFX EH 0 webaka .
PFX EH 0 webabu .
PFX EH 0 webalu .
PFX EH 0 webaku .
PFX EH 0 webatu .
PFX EH 0 weban [^lmnb]
PFX EH l weband l.[^mn]
PFX EH l webann l.[mn]
PFX EH w webamp w
PFX EH 0 webamu .
PFX EH 0 webaba .
PFX EH 0 webagu .
PFX EH 0 webagi .
PFX EH 0 webazi .
PFX EH 0 webaki .
PFX EH 0 webabi .
PFX EH 0 webali .
PFX EH 0 webaga .
PFX EH 0 webaka .
PFX EH 0 webabu .
PFX EH 0 webalu .
PFX EH 0 webaku .
PFX EH 0 webatu .
PFX EH 0 wegun [^lmnb]
PFX EH l wegund l.[^mn]
PFX EH l wegunn l.[mn]
PFX EH w wegump w
PFX EH 0 wegumu .
PFX EH 0 weguba .
PFX EH 0 wegugu .
PFX EH 0 wegugi .
PFX EH 0 weguzi .
PFX EH 0 weguki .
PFX EH 0 wegubi .
PFX EH 0 weguli .
PFX EH 0 weguga .
PFX EH 0 weguka .
PFX EH 0 wegubu .
PFX EH 0 wegulu .
PFX EH 0 weguku .
PFX EH 0 wegutu .
PFX EH 0 wegin [^lmnb]
PFX EH l wegind l.[^mn]
PFX EH l weginn l.[mn]
PFX EH w wegimp w
PFX EH 0 wegimu .
PFX EH 0 wegiba .
PFX EH 0 wegigu .
PFX EH 0 wegigi .
PFX EH 0 wegizi .
PFX EH 0 wegiki .
PFX EH 0 wegibi .
PFX EH 0 wegili .
PFX EH 0 wegiga .
PFX EH 0 wegika .
PFX EH 0 wegibu .
PFX EH 0 wegilu .
PFX EH 0 wegiku .
PFX EH 0 wegitu .
PFX EH 0 wezin [^lmnb]
PFX EH l wezind l.[^mn]
PFX EH l wezinn l.[mn]
PFX EH w wezimp w
PFX EH 0 wezimu .
PFX EH 0 weziba .
PFX EH 0 wezigu .
PFX EH 0 wezigi .
PFX EH 0 wezizi .
PFX EH 0 weziki .
PFX EH 0 wezibi .
PFX EH 0 wezili .
PFX EH 0 weziga .
PFX EH 0 wezika .
PFX EH 0 wezibu .
PFX EH 0 wezilu .
PFX EH 0 weziku .
PFX EH 0 wezitu .
PFX EH 0 wekin [^lmnb]
PFX EH l wekind l.[^mn]
PFX EH l wekinn l.[mn]
PFX EH w wekimp w
PFX EH 0 wekimu .
PFX EH 0 wekiba .
PFX EH 0 wekigu .
PFX EH 0 wekigi .
PFX EH 0 wekizi .
PFX EH 0 wekiki .
PFX EH 0 wekibi .
PFX EH 0 wekili .
PFX EH 0 wekiga .
PFX EH 0 wekika .
PFX EH 0 wekibu .
PFX EH 0 wekilu .
PFX EH 0 wekiku .
PFX EH 0 wekitu .
PFX EH 0 webin [^lmnb]
PFX EH l webind l.[^mn]
PFX EH l webinn l.[mn]
PFX EH w webimp w
PFX EH 0 webimu .
PFX EH 0 webiba .
PFX EH 0 webigu .
PFX EH 0 webigi .
PFX EH 0 webizi .
PFX EH 0 webiki .
PFX EH 0 webibi .
PFX EH 0 webili .
PFX EH 0 webiga .
PFX EH 0 webika .
PFX EH 0 webibu .
PFX EH 0 webilu .
PFX EH 0 webiku .
PFX EH 0 webitu .
PFX EH 0 welin [^lmnb]
PFX EH l welind l.[^mn]
PFX EH l welinn l.[mn]
PFX EH w welimp w
PFX EH 0 welimu .
PFX EH 0 weliba .
PFX EH 0 weligu .
PFX EH 0 weligi .
PFX EH 0 welizi .
PFX EH 0 weliki .
PFX EH 0 welibi .
PFX EH 0 welili .
PFX EH 0 weliga .
PFX EH 0 welika .
PFX EH 0 welibu .
PFX EH 0 welilu .
PFX EH 0 weliku .
PFX EH 0 welitu .
PFX EH 0 wegan [^lmnb]
PFX EH l wegand l.[^mn]
PFX EH l wegann l.[mn]
PFX EH w wegamp w
PFX EH 0 wegamu .
PFX EH 0 wegaba .
PFX EH 0 wegagu .
PFX EH 0 wegagi .
PFX EH 0 wegazi .
PFX EH 0 wegaki .
PFX EH 0 wegabi .
PFX EH 0 wegali .
PFX EH 0 wegaga .
PFX EH 0 wegaka .
PFX EH 0 wegabu .
PFX EH 0 wegalu .
PFX EH 0 wegaku .
PFX EH 0 wegatu .
PFX EH 0 wekan [^lmnb]
PFX EH l wekand l.[^mn]
PFX EH l wekann l.[mn]
PFX EH w wekamp w
PFX EH 0 wekamu .
PFX EH 0 wekaba .
PFX EH 0 wekagu .
PFX EH 0 wekagi .
PFX EH 0 wekazi .
PFX EH 0 wekaki .
PFX EH 0 wekabi .
PFX EH 0 wekali .
PFX EH 0 wekaga .
PFX EH 0 wekaka .
PFX EH 0 wekabu .
PFX EH 0 wekalu .
PFX EH 0 wekaku .
PFX EH 0 wekatu .
PFX EH 0 webun [^lmnb]
PFX EH l webund l.[^mn]
PFX EH l webunn l.[mn]
PFX EH w webump w
PFX EH 0 webumu .
PFX EH 0 webuba .
PFX EH 0 webugu .
PFX EH 0 webugi .
PFX EH 0 webuzi .
PFX EH 0 webuki .
PFX EH 0 webubi .
PFX EH 0 webuli .
PFX EH 0 webuga .
PFX EH 0 webuka .
PFX EH 0 webubu .
PFX EH 0 webulu .
PFX EH 0 webuku .
PFX EH 0 webutu .
PFX EH 0 welun [^lmnb]
PFX EH l welund l.[^mn]
PFX EH l welunn l.[mn]
PFX EH w welump w
PFX EH 0 welumu .
PFX EH 0 weluba .
PFX EH 0 welugu .
PFX EH 0 welugi .
PFX EH 0 weluzi .
PFX EH 0 weluki .
PFX EH 0 welubi .
PFX EH 0 weluli .
PFX EH 0 weluga .
PFX EH 0 weluka .
PFX EH 0 welubu .
PFX EH 0 welulu .
PFX EH 0 weluku .
PFX EH 0 welutu .
PFX EH 0 wekun [^lmnb]
PFX EH l wekund l.[^mn]
PFX EH l wekunn l.[mn]
PFX EH w wekump w
PFX EH 0 wekumu .
PFX EH 0 wekuba .
PFX EH 0 wekugu .
PFX EH 0 wekugi .
PFX EH 0 wekuzi .
PFX EH 0 wekuki .
PFX EH 0 wekubi .
PFX EH 0 wekuli .
PFX EH 0 wekuga .
PFX EH 0 wekuka .
PFX EH 0 wekubu .
PFX EH 0 wekulu .
PFX EH 0 wekuku .
PFX EH 0 wekutu .
PFX EH 0 wetun [^lmnb]
PFX EH l wetund l.[^mn]
PFX EH l wetunn l.[mn]
PFX EH w wetump w
PFX EH 0 wetumu .
PFX EH 0 wetuba .
PFX EH 0 wetugu .
PFX EH 0 wetugi .
PFX EH 0 wetuzi .
PFX EH 0 wetuki .
PFX EH 0 wetubi .
PFX EH 0 wetuli .
PFX EH 0 wetuga .
PFX EH 0 wetuka .
PFX EH 0 wetubu .
PFX EH 0 wetulu .
PFX EH 0 wetuku .
PFX EH 0 wetutu ."""

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
    "EH": "EH",
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

    out_flag = "HI"
    left_desc = FLAG_DESCRIPTIONS.get("EH", "EH")
    right_desc = FLAG_DESCRIPTIONS.get("OR", "OR")
    comment_line = "# Cross product of {} ({}) and {} ({}) to {}".format(
        "EH", left_desc, "OR", right_desc, out_flag
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
