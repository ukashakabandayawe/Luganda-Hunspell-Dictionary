import re
import os
from pathlib import Path

# Cross product generator: QQ x Ob => JL
# Description:
# - Left block `QQ`: QQ
# - Right block `Ob`: Object markers
# - Output flag `JL`: Cross-product prefixes for QQ x Ob

REPO_ROOT = Path(__file__).resolve().parents[1]
AFF_FILE = REPO_ROOT / "Luganda.aff"

# If set to a flag name (e.g. "HB"), the generated cross-product block will be inserted
# immediately before the first "PFX <flag>" line when the output flag block doesn't
# already exist in the .aff.
INSERT_BEFORE_FLAG = "".strip() or None

rule_left_raw = """
PFX QQ Y 680
PFX QQ 0 naaba .
PFX QQ 0 naagu .
PFX QQ 0 naagi .
PFX QQ 0 naazi .
PFX QQ 0 naaki .
PFX QQ 0 naabi .
PFX QQ 0 naali .
PFX QQ 0 naaga .
PFX QQ 0 naaka .
PFX QQ 0 naabu .
PFX QQ 0 naalu .
PFX QQ 0 naaku .
PFX QQ 0 naatu .
PFX QQ 0 naamu .
PFX QQ 0 munaan [^lmnb]
PFX QQ l munaand l.[^mn]
PFX QQ l munaann l.[mn]
PFX QQ w munaamp [w]
PFX QQ 0 munaamu .
PFX QQ 0 munaaba .
PFX QQ 0 munaagu .
PFX QQ 0 munaagi .
PFX QQ 0 munaazi .
PFX QQ 0 munaaki .
PFX QQ 0 munaabi .
PFX QQ 0 munaali .
PFX QQ 0 munaaga .
PFX QQ 0 munaaka .
PFX QQ 0 munaabu .
PFX QQ 0 munaalu .
PFX QQ 0 munaaku .
PFX QQ 0 munaatu .
PFX QQ 0 onoon [^lmnb]
PFX QQ l onoond l.[^mn]
PFX QQ l onoonn l.[mn]
PFX QQ w onoomp [w]
PFX QQ 0 onoomu .
PFX QQ 0 onooba .
PFX QQ 0 onoogu .
PFX QQ 0 onoogi .
PFX QQ 0 onoozi .
PFX QQ 0 onooki .
PFX QQ 0 onoobi .
PFX QQ 0 onooli .
PFX QQ 0 onooga .
PFX QQ 0 onooka .
PFX QQ 0 onoobu .
PFX QQ 0 onoolu .
PFX QQ 0 onooku .
PFX QQ 0 onootu .
PFX QQ 0 onaan [^lmnb]
PFX QQ l onaand l.[^mn]
PFX QQ l onaann l.[mn]
PFX QQ w onaamp [w]
PFX QQ 0 onaamu .
PFX QQ 0 onaaba .
PFX QQ 0 onaagu .
PFX QQ 0 onaagi .
PFX QQ 0 onaazi .
PFX QQ 0 onaaki .
PFX QQ 0 onaabi .
PFX QQ 0 onaali .
PFX QQ 0 onaaga .
PFX QQ 0 onaaka .
PFX QQ 0 onaabu .
PFX QQ 0 onaalu .
PFX QQ 0 onaaku .
PFX QQ 0 onaatu .
PFX QQ 0 anaan [^lmnb]
PFX QQ l anaand l.[^mn]
PFX QQ l anaann l.[mn]
PFX QQ w anaamp [w]
PFX QQ 0 anaamu .
PFX QQ 0 anaaba .
PFX QQ 0 anaagu .
PFX QQ 0 anaagi .
PFX QQ 0 anaazi .
PFX QQ 0 anaaki .
PFX QQ 0 anaabi .
PFX QQ 0 anaali .
PFX QQ 0 anaaga .
PFX QQ 0 anaaka .
PFX QQ 0 anaabu .
PFX QQ 0 anaalu .
PFX QQ 0 anaaku .
PFX QQ 0 anaatu .
PFX QQ 0 tunaan [^lmnb]
PFX QQ l tunaand l.[^mn]
PFX QQ l tunaann l.[mn]
PFX QQ w tunaamp [w]
PFX QQ 0 tunaamu .
PFX QQ 0 tunaaba .
PFX QQ 0 tunaagu .
PFX QQ 0 tunaagi .
PFX QQ 0 tunaazi .
PFX QQ 0 tunaaki .
PFX QQ 0 tunaabi .
PFX QQ 0 tunaali .
PFX QQ 0 tunaaga .
PFX QQ 0 tunaaka .
PFX QQ 0 tunaabu .
PFX QQ 0 tunaalu .
PFX QQ 0 tunaaku .
PFX QQ 0 tunaatu .
PFX QQ 0 munaan [^lmnb]
PFX QQ l munaand l.[^mn]
PFX QQ l munaann l.[mn]
PFX QQ w munaamp [w]
PFX QQ 0 munaamu .
PFX QQ 0 munaaba .
PFX QQ 0 munaagu .
PFX QQ 0 munaagi .
PFX QQ 0 munaazi .
PFX QQ 0 munaaki .
PFX QQ 0 munaabi .
PFX QQ 0 munaali .
PFX QQ 0 munaaga .
PFX QQ 0 munaaka .
PFX QQ 0 munaabu .
PFX QQ 0 munaalu .
PFX QQ 0 munaaku .
PFX QQ 0 munaatu .
PFX QQ 0 banaan [^lmnb]
PFX QQ l banaand l.[^mn]
PFX QQ l banaann l.[mn]
PFX QQ w banaamp [w]
PFX QQ 0 banaamu .
PFX QQ 0 banaaba .
PFX QQ 0 banaagu .
PFX QQ 0 banaagi .
PFX QQ 0 banaazi .
PFX QQ 0 banaaki .
PFX QQ 0 banaabi .
PFX QQ 0 banaali .
PFX QQ 0 banaaga .
PFX QQ 0 banaaka .
PFX QQ 0 banaabu .
PFX QQ 0 banaalu .
PFX QQ 0 banaaku .
PFX QQ 0 banaatu .
PFX QQ 0 abanaan [^lmnb]
PFX QQ l abanaand l.[^mn]
PFX QQ l abanaann l.[mn]
PFX QQ w abanaamp [w]
PFX QQ 0 abanaamu .
PFX QQ 0 abanaaba .
PFX QQ 0 abanaagu .
PFX QQ 0 abanaagi .
PFX QQ 0 abanaazi .
PFX QQ 0 abanaaki .
PFX QQ 0 abanaabi .
PFX QQ 0 abanaali .
PFX QQ 0 abanaaga .
PFX QQ 0 abanaaka .
PFX QQ 0 abanaabu .
PFX QQ 0 abanaalu .
PFX QQ 0 abanaaku .
PFX QQ 0 abanaatu .
PFX QQ 0 gunaan [^lmnb]
PFX QQ l gunaand l.[^mn]
PFX QQ l gunaann l.[mn]
PFX QQ w gunaamp [w]
PFX QQ 0 gunaamu .
PFX QQ 0 gunaaba .
PFX QQ 0 gunaagu .
PFX QQ 0 gunaagi .
PFX QQ 0 gunaazi .
PFX QQ 0 gunaaki .
PFX QQ 0 gunaabi .
PFX QQ 0 gunaali .
PFX QQ 0 gunaaga .
PFX QQ 0 gunaaka .
PFX QQ 0 gunaabu .
PFX QQ 0 gunaalu .
PFX QQ 0 gunaaku .
PFX QQ 0 gunaatu .
PFX QQ 0 ogunaan [^lmnb]
PFX QQ l ogunaand l.[^mn]
PFX QQ l ogunaann l.[mn]
PFX QQ w ogunaamp [w]
PFX QQ 0 ogunaamu .
PFX QQ 0 ogunaaba .
PFX QQ 0 ogunaagu .
PFX QQ 0 ogunaagi .
PFX QQ 0 ogunaazi .
PFX QQ 0 ogunaaki .
PFX QQ 0 ogunaabi .
PFX QQ 0 ogunaali .
PFX QQ 0 ogunaaga .
PFX QQ 0 ogunaaka .
PFX QQ 0 ogunaabu .
PFX QQ 0 ogunaalu .
PFX QQ 0 ogunaaku .
PFX QQ 0 ogunaatu .
PFX QQ 0 ginaan [^lmnb]
PFX QQ l ginaand l.[^mn]
PFX QQ l ginaann l.[mn]
PFX QQ w ginaamp [w]
PFX QQ 0 ginaamu .
PFX QQ 0 ginaaba .
PFX QQ 0 ginaagu .
PFX QQ 0 ginaagi .
PFX QQ 0 ginaazi .
PFX QQ 0 ginaaki .
PFX QQ 0 ginaabi .
PFX QQ 0 ginaali .
PFX QQ 0 ginaaga .
PFX QQ 0 ginaaka .
PFX QQ 0 ginaabu .
PFX QQ 0 ginaalu .
PFX QQ 0 ginaaku .
PFX QQ 0 ginaatu .
PFX QQ 0 eginaan [^lmnb]
PFX QQ l eginaand l.[^mn]
PFX QQ l eginaann l.[mn]
PFX QQ w eginaamp [w]
PFX QQ 0 eginaamu .
PFX QQ 0 eginaaba .
PFX QQ 0 eginaagu .
PFX QQ 0 eginaagi .
PFX QQ 0 eginaazi .
PFX QQ 0 eginaaki .
PFX QQ 0 eginaabi .
PFX QQ 0 eginaali .
PFX QQ 0 eginaaga .
PFX QQ 0 eginaaka .
PFX QQ 0 eginaabu .
PFX QQ 0 eginaalu .
PFX QQ 0 eginaaku .
PFX QQ 0 eginaatu .
PFX QQ 0 enaan [^lmnb]
PFX QQ l enaand l.[^mn]
PFX QQ l enaann l.[mn]
PFX QQ w enaamp [w]
PFX QQ 0 enaamu .
PFX QQ 0 enaaba .
PFX QQ 0 enaagu .
PFX QQ 0 enaagi .
PFX QQ 0 enaazi .
PFX QQ 0 enaaki .
PFX QQ 0 enaabi .
PFX QQ 0 enaali .
PFX QQ 0 enaaga .
PFX QQ 0 enaaka .
PFX QQ 0 enaabu .
PFX QQ 0 enaalu .
PFX QQ 0 enaaku .
PFX QQ 0 enaatu .
PFX QQ 0 zinaan [^lmnb]
PFX QQ l zinaand l.[^mn]
PFX QQ l zinaann l.[mn]
PFX QQ w zinaamp [w]
PFX QQ 0 zinaamu .
PFX QQ 0 zinaaba .
PFX QQ 0 zinaagu .
PFX QQ 0 zinaagi .
PFX QQ 0 zinaazi .
PFX QQ 0 zinaaki .
PFX QQ 0 zinaabi .
PFX QQ 0 zinaali .
PFX QQ 0 zinaaga .
PFX QQ 0 zinaaka .
PFX QQ 0 zinaabu .
PFX QQ 0 zinaalu .
PFX QQ 0 zinaaku .
PFX QQ 0 zinaatu .
PFX QQ 0 ezinaan [^lmnb]
PFX QQ l ezinaand l.[^mn]
PFX QQ l ezinaann l.[mn]
PFX QQ w ezinaamp [w]
PFX QQ 0 ezinaamu .
PFX QQ 0 ezinaaba .
PFX QQ 0 ezinaagu .
PFX QQ 0 ezinaagi .
PFX QQ 0 ezinaazi .
PFX QQ 0 ezinaaki .
PFX QQ 0 ezinaabi .
PFX QQ 0 ezinaali .
PFX QQ 0 ezinaaga .
PFX QQ 0 ezinaaka .
PFX QQ 0 ezinaabu .
PFX QQ 0 ezinaalu .
PFX QQ 0 ezinaaku .
PFX QQ 0 ezinaatu .
PFX QQ 0 kinaan [^lmnb]
PFX QQ l kinaand l.[^mn]
PFX QQ l kinaann l.[mn]
PFX QQ w kinaamp [w]
PFX QQ 0 kinaamu .
PFX QQ 0 kinaaba .
PFX QQ 0 kinaagu .
PFX QQ 0 kinaagi .
PFX QQ 0 kinaazi .
PFX QQ 0 kinaaki .
PFX QQ 0 kinaabi .
PFX QQ 0 kinaali .
PFX QQ 0 kinaaga .
PFX QQ 0 kinaaka .
PFX QQ 0 kinaabu .
PFX QQ 0 kinaalu .
PFX QQ 0 kinaaku .
PFX QQ 0 kinaatu .
PFX QQ 0 ekinaan [^lmnb]
PFX QQ l ekinaand l.[^mn]
PFX QQ l ekinaann l.[mn]
PFX QQ w ekinaamp [w]
PFX QQ 0 ekinaamu .
PFX QQ 0 ekinaaba .
PFX QQ 0 ekinaagu .
PFX QQ 0 ekinaagi .
PFX QQ 0 ekinaazi .
PFX QQ 0 ekinaaki .
PFX QQ 0 ekinaabi .
PFX QQ 0 ekinaali .
PFX QQ 0 ekinaaga .
PFX QQ 0 ekinaaka .
PFX QQ 0 ekinaabu .
PFX QQ 0 ekinaalu .
PFX QQ 0 ekinaaku .
PFX QQ 0 ekinaatu .
PFX QQ 0 binaan [^lmnb]
PFX QQ l binaand l.[^mn]
PFX QQ l binaann l.[mn]
PFX QQ w binaamp [w]
PFX QQ 0 binaamu .
PFX QQ 0 binaaba .
PFX QQ 0 binaagu .
PFX QQ 0 binaagi .
PFX QQ 0 binaazi .
PFX QQ 0 binaaki .
PFX QQ 0 binaabi .
PFX QQ 0 binaali .
PFX QQ 0 binaaga .
PFX QQ 0 binaaka .
PFX QQ 0 binaabu .
PFX QQ 0 binaalu .
PFX QQ 0 binaaku .
PFX QQ 0 binaatu .
PFX QQ 0 ebinaan [^lmnb]
PFX QQ l ebinaand l.[^mn]
PFX QQ l ebinaann l.[mn]
PFX QQ w ebinaamp [w]
PFX QQ 0 ebinaamu .
PFX QQ 0 ebinaaba .
PFX QQ 0 ebinaagu .
PFX QQ 0 ebinaagi .
PFX QQ 0 ebinaazi .
PFX QQ 0 ebinaaki .
PFX QQ 0 ebinaabi .
PFX QQ 0 ebinaali .
PFX QQ 0 ebinaaga .
PFX QQ 0 ebinaaka .
PFX QQ 0 ebinaabu .
PFX QQ 0 ebinaalu .
PFX QQ 0 ebinaaku .
PFX QQ 0 ebinaatu .
PFX QQ 0 linaan [^lmnb]
PFX QQ l linaand l.[^mn]
PFX QQ l linaann l.[mn]
PFX QQ w linaamp [w]
PFX QQ 0 linaamu .
PFX QQ 0 linaaba .
PFX QQ 0 linaagu .
PFX QQ 0 linaagi .
PFX QQ 0 linaazi .
PFX QQ 0 linaaki .
PFX QQ 0 linaabi .
PFX QQ 0 linaali .
PFX QQ 0 linaaga .
PFX QQ 0 linaaka .
PFX QQ 0 linaabu .
PFX QQ 0 linaalu .
PFX QQ 0 linaaku .
PFX QQ 0 linaatu .
PFX QQ 0 elinaan [^lmnb]
PFX QQ l elinaand l.[^mn]
PFX QQ l elinaann l.[mn]
PFX QQ w elinaamp [w]
PFX QQ 0 elinaamu .
PFX QQ 0 elinaaba .
PFX QQ 0 elinaagu .
PFX QQ 0 elinaagi .
PFX QQ 0 elinaazi .
PFX QQ 0 elinaaki .
PFX QQ 0 elinaabi .
PFX QQ 0 elinaali .
PFX QQ 0 elinaaga .
PFX QQ 0 elinaaka .
PFX QQ 0 elinaabu .
PFX QQ 0 elinaalu .
PFX QQ 0 elinaaku .
PFX QQ 0 elinaatu .
PFX QQ 0 ganaan [^lmnb]
PFX QQ l ganaand l.[^mn]
PFX QQ l ganaann l.[mn]
PFX QQ w ganaamp [w]
PFX QQ 0 ganaamu .
PFX QQ 0 ganaaba .
PFX QQ 0 ganaagu .
PFX QQ 0 ganaagi .
PFX QQ 0 ganaazi .
PFX QQ 0 ganaaki .
PFX QQ 0 ganaabi .
PFX QQ 0 ganaali .
PFX QQ 0 ganaaga .
PFX QQ 0 ganaaka .
PFX QQ 0 ganaabu .
PFX QQ 0 ganaalu .
PFX QQ 0 ganaaku .
PFX QQ 0 ganaatu .
PFX QQ 0 aganaan [^lmnb]
PFX QQ l aganaand l.[^mn]
PFX QQ l aganaann l.[mn]
PFX QQ w aganaamp [w]
PFX QQ 0 aganaamu .
PFX QQ 0 aganaaba .
PFX QQ 0 aganaagu .
PFX QQ 0 aganaagi .
PFX QQ 0 aganaazi .
PFX QQ 0 aganaaki .
PFX QQ 0 aganaabi .
PFX QQ 0 aganaali .
PFX QQ 0 aganaaga .
PFX QQ 0 aganaaka .
PFX QQ 0 aganaabu .
PFX QQ 0 aganaalu .
PFX QQ 0 aganaaku .
PFX QQ 0 aganaatu .
PFX QQ 0 kanaan [^lmnb]
PFX QQ l kanaand l.[^mn]
PFX QQ l kanaann l.[mn]
PFX QQ w kanaamp [w]
PFX QQ 0 kanaamu .
PFX QQ 0 kanaaba .
PFX QQ 0 kanaagu .
PFX QQ 0 kanaagi .
PFX QQ 0 kanaazi .
PFX QQ 0 kanaaki .
PFX QQ 0 kanaabi .
PFX QQ 0 kanaali .
PFX QQ 0 kanaaga .
PFX QQ 0 kanaaka .
PFX QQ 0 kanaabu .
PFX QQ 0 kanaalu .
PFX QQ 0 kanaaku .
PFX QQ 0 kanaatu .
PFX QQ 0 akanaan [^lmnb]
PFX QQ l akanaand l.[^mn]
PFX QQ l akanaann l.[mn]
PFX QQ w akanaamp [w]
PFX QQ 0 akanaamu .
PFX QQ 0 akanaaba .
PFX QQ 0 akanaagu .
PFX QQ 0 akanaagi .
PFX QQ 0 akanaazi .
PFX QQ 0 akanaaki .
PFX QQ 0 akanaabi .
PFX QQ 0 akanaali .
PFX QQ 0 akanaaga .
PFX QQ 0 akanaaka .
PFX QQ 0 akanaabu .
PFX QQ 0 akanaalu .
PFX QQ 0 akanaaku .
PFX QQ 0 akanaatu .
PFX QQ 0 bunaan [^lmnb]
PFX QQ l bunaand l.[^mn]
PFX QQ l bunaann l.[mn]
PFX QQ w bunaamp [w]
PFX QQ 0 bunaamu .
PFX QQ 0 bunaaba .
PFX QQ 0 bunaagu .
PFX QQ 0 bunaagi .
PFX QQ 0 bunaazi .
PFX QQ 0 bunaaki .
PFX QQ 0 bunaabi .
PFX QQ 0 bunaali .
PFX QQ 0 bunaaga .
PFX QQ 0 bunaaka .
PFX QQ 0 bunaabu .
PFX QQ 0 bunaalu .
PFX QQ 0 bunaaku .
PFX QQ 0 bunaatu .
PFX QQ 0 obunaan [^lmnb]
PFX QQ l obunaand l.[^mn]
PFX QQ l obunaann l.[mn]
PFX QQ w obunaamp [w]
PFX QQ 0 obunaamu .
PFX QQ 0 obunaaba .
PFX QQ 0 obunaagu .
PFX QQ 0 obunaagi .
PFX QQ 0 obunaazi .
PFX QQ 0 obunaaki .
PFX QQ 0 obunaabi .
PFX QQ 0 obunaali .
PFX QQ 0 obunaaga .
PFX QQ 0 obunaaka .
PFX QQ 0 obunaabu .
PFX QQ 0 obunaalu .
PFX QQ 0 obunaaku .
PFX QQ 0 obunaatu .
PFX QQ 0 lunaan [^lmnb]
PFX QQ l lunaand l.[^mn]
PFX QQ l lunaann l.[mn]
PFX QQ w lunaamp [w]
PFX QQ 0 lunaamu .
PFX QQ 0 lunaaba .
PFX QQ 0 lunaagu .
PFX QQ 0 lunaagi .
PFX QQ 0 lunaazi .
PFX QQ 0 lunaaki .
PFX QQ 0 lunaabi .
PFX QQ 0 lunaali .
PFX QQ 0 lunaaga .
PFX QQ 0 lunaaka .
PFX QQ 0 lunaabu .
PFX QQ 0 lunaalu .
PFX QQ 0 lunaaku .
PFX QQ 0 lunaatu .
PFX QQ 0 olunaan [^lmnb]
PFX QQ l olunaand l.[^mn]
PFX QQ l olunaann l.[mn]
PFX QQ w olunaamp [w]
PFX QQ 0 olunaamu .
PFX QQ 0 olunaaba .
PFX QQ 0 olunaagu .
PFX QQ 0 olunaagi .
PFX QQ 0 olunaazi .
PFX QQ 0 olunaaki .
PFX QQ 0 olunaabi .
PFX QQ 0 olunaali .
PFX QQ 0 olunaaga .
PFX QQ 0 olunaaka .
PFX QQ 0 olunaabu .
PFX QQ 0 olunaalu .
PFX QQ 0 olunaaku .
PFX QQ 0 olunaatu .
PFX QQ 0 zinaan [^lmnb]
PFX QQ l zinaand l.[^mn]
PFX QQ l zinaann l.[mn]
PFX QQ w zinaamp [w]
PFX QQ 0 zinaamu .
PFX QQ 0 zinaaba .
PFX QQ 0 zinaagu .
PFX QQ 0 zinaagi .
PFX QQ 0 zinaazi .
PFX QQ 0 zinaaki .
PFX QQ 0 zinaabi .
PFX QQ 0 zinaali .
PFX QQ 0 zinaaga .
PFX QQ 0 zinaaka .
PFX QQ 0 zinaabu .
PFX QQ 0 zinaalu .
PFX QQ 0 zinaaku .
PFX QQ 0 zinaatu .
PFX QQ 0 ezinaan [^lmnb]
PFX QQ l ezinaand l.[^mn]
PFX QQ l ezinaann l.[mn]
PFX QQ w ezinaamp [w]
PFX QQ 0 ezinaamu .
PFX QQ 0 ezinaaba .
PFX QQ 0 ezinaagu .
PFX QQ 0 ezinaagi .
PFX QQ 0 ezinaazi .
PFX QQ 0 ezinaaki .
PFX QQ 0 ezinaabi .
PFX QQ 0 ezinaali .
PFX QQ 0 ezinaaga .
PFX QQ 0 ezinaaka .
PFX QQ 0 ezinaabu .
PFX QQ 0 ezinaalu .
PFX QQ 0 ezinaaku .
PFX QQ 0 ezinaatu .
PFX QQ 0 kunaan [^lmnb]
PFX QQ l kunaand l.[^mn]
PFX QQ l kunaann l.[mn]
PFX QQ w kunaamp [w]
PFX QQ 0 kunaamu .
PFX QQ 0 kunaaba .
PFX QQ 0 kunaagu .
PFX QQ 0 kunaagi .
PFX QQ 0 kunaazi .
PFX QQ 0 kunaaki .
PFX QQ 0 kunaabi .
PFX QQ 0 kunaali .
PFX QQ 0 kunaaga .
PFX QQ 0 kunaaka .
PFX QQ 0 kunaabu .
PFX QQ 0 kunaalu .
PFX QQ 0 kunaaku .
PFX QQ 0 kunaatu .
PFX QQ 0 okunaan [^lmnb]
PFX QQ l okunaand l.[^mn]
PFX QQ l okunaann l.[mn]
PFX QQ w okunaamp [w]
PFX QQ 0 okunaamu .
PFX QQ 0 okunaaba .
PFX QQ 0 okunaagu .
PFX QQ 0 okunaagi .
PFX QQ 0 okunaazi .
PFX QQ 0 okunaaki .
PFX QQ 0 okunaabi .
PFX QQ 0 okunaali .
PFX QQ 0 okunaaga .
PFX QQ 0 okunaaka .
PFX QQ 0 okunaabu .
PFX QQ 0 okunaalu .
PFX QQ 0 okunaaku .
PFX QQ 0 okunaatu .
PFX QQ 0 ganaan [^lmnb]
PFX QQ l ganaand l.[^mn]
PFX QQ l ganaann l.[mn]
PFX QQ w ganaamp [w]
PFX QQ 0 ganaamu .
PFX QQ 0 ganaaba .
PFX QQ 0 ganaagu .
PFX QQ 0 ganaagi .
PFX QQ 0 ganaazi .
PFX QQ 0 ganaaki .
PFX QQ 0 ganaabi .
PFX QQ 0 ganaali .
PFX QQ 0 ganaaga .
PFX QQ 0 ganaaka .
PFX QQ 0 ganaabu .
PFX QQ 0 ganaalu .
PFX QQ 0 ganaaku .
PFX QQ 0 ganaatu .
PFX QQ 0 ogunaan [^lmnb]
PFX QQ l ogunaand l.[^mn]
PFX QQ l ogunaann l.[mn]
PFX QQ w ogunaamp [w]
PFX QQ 0 ogunaamu .
PFX QQ 0 ogunaaba .
PFX QQ 0 ogunaagu .
PFX QQ 0 ogunaagi .
PFX QQ 0 ogunaazi .
PFX QQ 0 ogunaaki .
PFX QQ 0 ogunaabi .
PFX QQ 0 ogunaali .
PFX QQ 0 ogunaaga .
PFX QQ 0 ogunaaka .
PFX QQ 0 ogunaabu .
PFX QQ 0 ogunaalu .
PFX QQ 0 ogunaaku .
PFX QQ 0 ogunaatu .
PFX QQ 0 tunaan [^lmnb]
PFX QQ l tunaand l.[^mn]
PFX QQ l tunaann l.[mn]
PFX QQ w tunaamp [w]
PFX QQ 0 tunaamu .
PFX QQ 0 tunaaba .
PFX QQ 0 tunaagu .
PFX QQ 0 tunaagi .
PFX QQ 0 tunaazi .
PFX QQ 0 tunaaki .
PFX QQ 0 tunaabi .
PFX QQ 0 tunaali .
PFX QQ 0 tunaaga .
PFX QQ 0 tunaaka .
PFX QQ 0 tunaabu .
PFX QQ 0 tunaalu .
PFX QQ 0 tunaaku .
PFX QQ 0 tunaatu .
PFX QQ 0 otunaan [^lmnb]
PFX QQ l otunaand l.[^mn]
PFX QQ l otunaann l.[mn]
PFX QQ w otunaamp [w]
PFX QQ 0 otunaamu .
PFX QQ 0 otunaaba .
PFX QQ 0 otunaagu .
PFX QQ 0 otunaagi .
PFX QQ 0 otunaazi .
PFX QQ 0 otunaaki .
PFX QQ 0 otunaabi .
PFX QQ 0 otunaali .
PFX QQ 0 otunaaga .
PFX QQ 0 otunaaka .
PFX QQ 0 otunaabu .
PFX QQ 0 otunaalu .
PFX QQ 0 otunaaku .
PFX QQ 0 otunaatu ."""

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
    "QQ": "QQ",
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

    out_flag = "JL"
    left_desc = FLAG_DESCRIPTIONS.get("QQ", "QQ")
    right_desc = FLAG_DESCRIPTIONS.get("Ob", "Ob")
    comment_line = "# Cross product of {} ({}) and {} ({}) to {}".format(
        "QQ", left_desc, "Ob", right_desc, out_flag
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
