import re
import os
from pathlib import Path

# Cross product generator: RR x OR => JH
# Description:
# - Left block `RR`: RR
# - Right block `OR`: Special reflexive object markers
# - Output flag `JH`: Cross-product prefixes for RR x OR

REPO_ROOT = Path(__file__).resolve().parents[1]
AFF_FILE = REPO_ROOT / "Luganda.aff"

# If set to a flag name (e.g. "HB"), the generated cross-product block will be inserted
# immediately before the first "PFX <flag>" line when the output flag block doesn't
# already exist in the .aff.
INSERT_BEFORE_FLAG = "".strip() or None

rule_left_raw = """
PFX RR Y 555
PFX RR 0 ndimu .
PFX RR 0 ndiba .
PFX RR 0 ndigu .
PFX RR 0 ndigi .
PFX RR 0 ndizi .
PFX RR 0 ndiki .
PFX RR 0 ndibi .
PFX RR 0 ndili .
PFX RR 0 ndiga .
PFX RR 0 ndika .
PFX RR 0 ndibu .
PFX RR 0 ndilu .
PFX RR 0 ndiku .
PFX RR 0 nditu .
PFX RR 0 olin [^lmn]
PFX RR l olind l.[^mn]
PFX RR l olinn l.[mn]
PFX RR w olimp [w]
PFX RR 0 olimu .
PFX RR 0 oliba .
PFX RR 0 oligu .
PFX RR 0 oligi .
PFX RR 0 olizi .
PFX RR 0 oliki .
PFX RR 0 olibi .
PFX RR 0 olili .
PFX RR 0 oliga .
PFX RR 0 olika .
PFX RR 0 olibu .
PFX RR 0 olilu .
PFX RR 0 oliku .
PFX RR 0 olitu .
PFX RR 0 alin [^lmn]
PFX RR l alind l.[^mn]
PFX RR l alinn l.[mn]
PFX RR w alimp [w]
PFX RR 0 alimu .
PFX RR 0 aliba .
PFX RR 0 aligu .
PFX RR 0 aligi .
PFX RR 0 alizi .
PFX RR 0 aliki .
PFX RR 0 alibi .
PFX RR 0 alili .
PFX RR 0 aliga .
PFX RR 0 alika .
PFX RR 0 alibu .
PFX RR 0 alilu .
PFX RR 0 aliku .
PFX RR 0 alitu .
PFX RR 0 tulin [^lmn]
PFX RR l tulind l.[^mn]
PFX RR l tulinn l.[mn]
PFX RR w tulimp [w]
PFX RR 0 tulimu .
PFX RR 0 tuliba .
PFX RR 0 tuligu .
PFX RR 0 tuligi .
PFX RR 0 tulizi .
PFX RR 0 tuliki .
PFX RR 0 tulibi .
PFX RR 0 tulili .
PFX RR 0 tuliga .
PFX RR 0 tulika .
PFX RR 0 tulibu .
PFX RR 0 tulilu .
PFX RR 0 tuliku .
PFX RR 0 tulitu .
PFX RR 0 mulin [^lmn]
PFX RR l mulind l.[^mn]
PFX RR l mulinn l.[mn]
PFX RR w mulimp [w]
PFX RR 0 mulimu .
PFX RR 0 muliba .
PFX RR 0 muligu .
PFX RR 0 muligi .
PFX RR 0 mulizi .
PFX RR 0 muliki .
PFX RR 0 mulibi .
PFX RR 0 mulili .
PFX RR 0 muliga .
PFX RR 0 mulika .
PFX RR 0 mulibu .
PFX RR 0 mulilu .
PFX RR 0 muliku .
PFX RR 0 mulitu .
PFX RR 0 balin [^lmn]
PFX RR l balind l.[^mn]
PFX RR l balinn l.[mn]
PFX RR w balimp [w]
PFX RR 0 balimu .
PFX RR 0 baliba .
PFX RR 0 baligu .
PFX RR 0 baligi .
PFX RR 0 balizi .
PFX RR 0 baliki .
PFX RR 0 balibi .
PFX RR 0 balili .
PFX RR 0 baliga .
PFX RR 0 balika .
PFX RR 0 balibu .
PFX RR 0 balilu .
PFX RR 0 baliku .
PFX RR 0 balitu .
PFX RR 0 abalin [^lmn]
PFX RR l abalind l.[^mn]
PFX RR l abalinn l.[mn]
PFX RR w abalimp [w]
PFX RR 0 abalimu .
PFX RR 0 abaliba .
PFX RR 0 abaligu .
PFX RR 0 abaligi .
PFX RR 0 abalizi .
PFX RR 0 abaliki .
PFX RR 0 abalibi .
PFX RR 0 abalili .
PFX RR 0 abaliga .
PFX RR 0 abalika .
PFX RR 0 abalibu .
PFX RR 0 abalilu .
PFX RR 0 abaliku .
PFX RR 0 abalitu .
PFX RR 0 gulin [^lmn]
PFX RR l gulind l.[^mn]
PFX RR l gulinn l.[mn]
PFX RR w gulimp [w]
PFX RR 0 gulimu .
PFX RR 0 guliba .
PFX RR 0 guligu .
PFX RR 0 guligi .
PFX RR 0 gulizi .
PFX RR 0 guliki .
PFX RR 0 gulibi .
PFX RR 0 gulili .
PFX RR 0 guliga .
PFX RR 0 gulika .
PFX RR 0 gulibu .
PFX RR 0 gulilu .
PFX RR 0 guliku .
PFX RR 0 gulitu .
PFX RR 0 ogulin [^lmn]
PFX RR l ogulind l.[^mn]
PFX RR l ogulinn l.[mn]
PFX RR w ogulimp [w]
PFX RR 0 ogulimu .
PFX RR 0 oguliba .
PFX RR 0 oguligu .
PFX RR 0 oguligi .
PFX RR 0 ogulizi .
PFX RR 0 oguliki .
PFX RR 0 ogulibi .
PFX RR 0 ogulili .
PFX RR 0 oguliga .
PFX RR 0 ogulika .
PFX RR 0 ogulibu .
PFX RR 0 ogulilu .
PFX RR 0 oguliku .
PFX RR 0 ogulitu .
PFX RR 0 gilin [^lmn]
PFX RR l gilind l.[^mn]
PFX RR l gilinn l.[mn]
PFX RR w gilimp [w]
PFX RR 0 gilimu .
PFX RR 0 giliba .
PFX RR 0 giligu .
PFX RR 0 giligi .
PFX RR 0 gilizi .
PFX RR 0 giliki .
PFX RR 0 gilibi .
PFX RR 0 gilili .
PFX RR 0 giliga .
PFX RR 0 gilika .
PFX RR 0 gilibu .
PFX RR 0 gililu .
PFX RR 0 giliku .
PFX RR 0 gilitu .
PFX RR 0 egilin [^lmn]
PFX RR l egilind l.[^mn]
PFX RR l egilinn l.[mn]
PFX RR w egilimp [w]
PFX RR 0 egilimu .
PFX RR 0 egiliba .
PFX RR 0 egiligu .
PFX RR 0 egiligi .
PFX RR 0 egilizi .
PFX RR 0 egiliki .
PFX RR 0 egilibi .
PFX RR 0 egilili .
PFX RR 0 egiliga .
PFX RR 0 egilika .
PFX RR 0 egilibu .
PFX RR 0 egililu .
PFX RR 0 egiliku .
PFX RR 0 egilitu .
PFX RR 0 elin [^lmn]
PFX RR l elind l.[^mn]
PFX RR l elinn l.[mn]
PFX RR w elimp [w]
PFX RR 0 elimu .
PFX RR 0 eliba .
PFX RR 0 eligu .
PFX RR 0 eligi .
PFX RR 0 elizi .
PFX RR 0 eliki .
PFX RR 0 elibi .
PFX RR 0 elili .
PFX RR 0 eliga .
PFX RR 0 elika .
PFX RR 0 elibu .
PFX RR 0 elilu .
PFX RR 0 eliku .
PFX RR 0 elitu .
PFX RR 0 zilin [^lmn]
PFX RR l zilind l.[^mn]
PFX RR l zilinn l.[mn]
PFX RR w zilimp [w]
PFX RR 0 zilimu .
PFX RR 0 ziliba .
PFX RR 0 ziligu .
PFX RR 0 ziligi .
PFX RR 0 zilizi .
PFX RR 0 ziliki .
PFX RR 0 zilibi .
PFX RR 0 zilili .
PFX RR 0 ziliga .
PFX RR 0 zilika .
PFX RR 0 zilibu .
PFX RR 0 zililu .
PFX RR 0 ziliku .
PFX RR 0 zilitu .
PFX RR 0 ezilin [^lmn]
PFX RR l ezilind l.[^mn]
PFX RR l ezilinn l.[mn]
PFX RR w ezilimp [w]
PFX RR 0 ezilimu .
PFX RR 0 eziliba .
PFX RR 0 eziligu .
PFX RR 0 eziligi .
PFX RR 0 ezilizi .
PFX RR 0 eziliki .
PFX RR 0 ezilibi .
PFX RR 0 ezilili .
PFX RR 0 eziliga .
PFX RR 0 ezilika .
PFX RR 0 ezilibu .
PFX RR 0 ezililu .
PFX RR 0 eziliku .
PFX RR 0 ezilitu .
PFX RR 0 kilin [^lmn]
PFX RR l kilind l.[^mn]
PFX RR l kilinn l.[mn]
PFX RR w kilimp [w]
PFX RR 0 kilimu .
PFX RR 0 kiliba .
PFX RR 0 kiligu .
PFX RR 0 kiligi .
PFX RR 0 kilizi .
PFX RR 0 kiliki .
PFX RR 0 kilibi .
PFX RR 0 kilili .
PFX RR 0 kiliga .
PFX RR 0 kilika .
PFX RR 0 kilibu .
PFX RR 0 kililu .
PFX RR 0 kiliku .
PFX RR 0 kilitu .
PFX RR 0 ekilin [^lmn]
PFX RR l ekilind l.[^mn]
PFX RR l ekilinn l.[mn]
PFX RR w ekilimp [w]
PFX RR 0 ekilimu .
PFX RR 0 ekiliba .
PFX RR 0 ekiligu .
PFX RR 0 ekiligi .
PFX RR 0 ekilizi .
PFX RR 0 ekiliki .
PFX RR 0 ekilibi .
PFX RR 0 ekilili .
PFX RR 0 ekiliga .
PFX RR 0 ekilika .
PFX RR 0 ekilibu .
PFX RR 0 ekililu .
PFX RR 0 ekiliku .
PFX RR 0 ekilitu .
PFX RR 0 bilin [^lmn]
PFX RR l bilind l.[^mn]
PFX RR l bilinn l.[mn]
PFX RR w bilimp [w]
PFX RR 0 bilimu .
PFX RR 0 biliba .
PFX RR 0 biligu .
PFX RR 0 biligi .
PFX RR 0 bilizi .
PFX RR 0 biliki .
PFX RR 0 bilibi .
PFX RR 0 bilili .
PFX RR 0 biliga .
PFX RR 0 bilika .
PFX RR 0 bilibu .
PFX RR 0 bililu .
PFX RR 0 biliku .
PFX RR 0 bilitu .
PFX RR 0 ebilin [^lmn]
PFX RR l ebilind l.[^mn]
PFX RR l ebilinn l.[mn]
PFX RR w ebilimp [w]
PFX RR 0 ebilimu .
PFX RR 0 ebiliba .
PFX RR 0 ebiligu .
PFX RR 0 ebiligi .
PFX RR 0 ebilizi .
PFX RR 0 ebiliki .
PFX RR 0 ebilibi .
PFX RR 0 ebilili .
PFX RR 0 ebiliga .
PFX RR 0 ebilika .
PFX RR 0 ebilibu .
PFX RR 0 ebililu .
PFX RR 0 ebiliku .
PFX RR 0 ebilitu .
PFX RR 0 lilin [^lmn]
PFX RR l lilind l.[^mn]
PFX RR l lilinn l.[mn]
PFX RR w lilimp [w]
PFX RR 0 lilimu .
PFX RR 0 liliba .
PFX RR 0 liligu .
PFX RR 0 liligi .
PFX RR 0 lilizi .
PFX RR 0 liliki .
PFX RR 0 lilibi .
PFX RR 0 lilili .
PFX RR 0 liliga .
PFX RR 0 lilika .
PFX RR 0 lilibu .
PFX RR 0 lililu .
PFX RR 0 liliku .
PFX RR 0 lilitu .
PFX RR 0 elilin [^lmn]
PFX RR l elilind l.[^mn]
PFX RR l elilinn l.[mn]
PFX RR w elilimp [w]
PFX RR 0 elilimu .
PFX RR 0 eliliba .
PFX RR 0 eliligu .
PFX RR 0 eliligi .
PFX RR 0 elilizi .
PFX RR 0 eliliki .
PFX RR 0 elilibi .
PFX RR 0 elilili .
PFX RR 0 eliliga .
PFX RR 0 elilika .
PFX RR 0 elilibu .
PFX RR 0 elililu .
PFX RR 0 eliliku .
PFX RR 0 elilitu .
PFX RR 0 galin [^lmn]
PFX RR l galind l.[^mn]
PFX RR l galinn l.[mn]
PFX RR w galimp [w]
PFX RR 0 galimu .
PFX RR 0 galiba .
PFX RR 0 galigu .
PFX RR 0 galigi .
PFX RR 0 galizi .
PFX RR 0 galiki .
PFX RR 0 galibi .
PFX RR 0 galili .
PFX RR 0 galiga .
PFX RR 0 galika .
PFX RR 0 galibu .
PFX RR 0 galilu .
PFX RR 0 galiku .
PFX RR 0 galitu .
PFX RR 0 agalin [^lmn]
PFX RR l agalind l.[^mn]
PFX RR l agalinn l.[mn]
PFX RR w agalimp [w]
PFX RR 0 agalimu .
PFX RR 0 agaliba .
PFX RR 0 agaligu .
PFX RR 0 agaligi .
PFX RR 0 agalizi .
PFX RR 0 agaliki .
PFX RR 0 agalibi .
PFX RR 0 agalili .
PFX RR 0 agaliga .
PFX RR 0 agalika .
PFX RR 0 agalibu .
PFX RR 0 agalilu .
PFX RR 0 agaliku .
PFX RR 0 agalitu .
PFX RR 0 kalin [^lmn]
PFX RR l kalind l.[^mn]
PFX RR l kalinn l.[mn]
PFX RR w kalimp [w]
PFX RR 0 kalimu .
PFX RR 0 kaliba .
PFX RR 0 kaligu .
PFX RR 0 kaligi .
PFX RR 0 kalizi .
PFX RR 0 kaliki .
PFX RR 0 kalibi .
PFX RR 0 kalili .
PFX RR 0 kaliga .
PFX RR 0 kalika .
PFX RR 0 kalibu .
PFX RR 0 kalilu .
PFX RR 0 kaliku .
PFX RR 0 kalitu .
PFX RR 0 akalin [^lmn]
PFX RR l akalind l.[^mn]
PFX RR l akalinn l.[mn]
PFX RR w akalimp [w]
PFX RR 0 akalimu .
PFX RR 0 akaliba .
PFX RR 0 akaligu .
PFX RR 0 akaligi .
PFX RR 0 akalizi .
PFX RR 0 akaliki .
PFX RR 0 akalibi .
PFX RR 0 akalili .
PFX RR 0 akaliga .
PFX RR 0 akalika .
PFX RR 0 akalibu .
PFX RR 0 akalilu .
PFX RR 0 akaliku .
PFX RR 0 akalitu .
PFX RR 0 bulin [^lmn]
PFX RR l bulind l.[^mn]
PFX RR l bulinn l.[mn]
PFX RR w bulimp [w]
PFX RR 0 bulimu .
PFX RR 0 buliba .
PFX RR 0 buligu .
PFX RR 0 buligi .
PFX RR 0 bulizi .
PFX RR 0 buliki .
PFX RR 0 bulibi .
PFX RR 0 bulili .
PFX RR 0 buliga .
PFX RR 0 bulika .
PFX RR 0 bulibu .
PFX RR 0 bulilu .
PFX RR 0 buliku .
PFX RR 0 bulitu .
PFX RR 0 obulin [^lmn]
PFX RR l obulind l.[^mn]
PFX RR l obulinn l.[mn]
PFX RR w obulimp [w]
PFX RR 0 obulimu .
PFX RR 0 obuliba .
PFX RR 0 obuligu .
PFX RR 0 obuligi .
PFX RR 0 obulizi .
PFX RR 0 obuliki .
PFX RR 0 obulibi .
PFX RR 0 obulili .
PFX RR 0 obuliga .
PFX RR 0 obulika .
PFX RR 0 obulibu .
PFX RR 0 obulilu .
PFX RR 0 obuliku .
PFX RR 0 obulitu .
PFX RR 0 lulin [^lmn]
PFX RR l lulind l.[^mn]
PFX RR l lulinn l.[mn]
PFX RR w lulimp [w]
PFX RR 0 lulimu .
PFX RR 0 luliba .
PFX RR 0 luligu .
PFX RR 0 luligi .
PFX RR 0 lulizi .
PFX RR 0 luliki .
PFX RR 0 lulibi .
PFX RR 0 lulili .
PFX RR 0 luliga .
PFX RR 0 lulika .
PFX RR 0 lulibu .
PFX RR 0 lulilu .
PFX RR 0 luliku .
PFX RR 0 lulitu .
PFX RR 0 olulin [^lmn]
PFX RR l olulind l.[^mn]
PFX RR l olulinn l.[mn]
PFX RR w olulimp [w]
PFX RR 0 olulimu .
PFX RR 0 oluliba .
PFX RR 0 oluligu .
PFX RR 0 oluligi .
PFX RR 0 olulizi .
PFX RR 0 oluliki .
PFX RR 0 olulibi .
PFX RR 0 olulili .
PFX RR 0 oluliga .
PFX RR 0 olulika .
PFX RR 0 olulibu .
PFX RR 0 olulilu .
PFX RR 0 oluliku .
PFX RR 0 olulitu .
PFX RR 0 kulin [^lmn]
PFX RR l kulind l.[^mn]
PFX RR l kulinn l.[mn]
PFX RR w kulimp [w]
PFX RR 0 kulimu .
PFX RR 0 kuliba .
PFX RR 0 kuligu .
PFX RR 0 kuligi .
PFX RR 0 kulizi .
PFX RR 0 kuliki .
PFX RR 0 kulibi .
PFX RR 0 kulili .
PFX RR 0 kuliga .
PFX RR 0 kulika .
PFX RR 0 kulibu .
PFX RR 0 kulilu .
PFX RR 0 kuliku .
PFX RR 0 kulitu .
PFX RR 0 okulin [^lmn]
PFX RR l okulind l.[^mn]
PFX RR l okulinn l.[mn]
PFX RR w okulimp [w]
PFX RR 0 okulimu .
PFX RR 0 okuliba .
PFX RR 0 okuligu .
PFX RR 0 okuligi .
PFX RR 0 okulizi .
PFX RR 0 okuliki .
PFX RR 0 okulibi .
PFX RR 0 okulili .
PFX RR 0 okuliga .
PFX RR 0 okulika .
PFX RR 0 okulibu .
PFX RR 0 okulilu .
PFX RR 0 okuliku .
PFX RR 0 okulitu .
PFX RR 0 otulin [^lmn]
PFX RR l otulind l.[^mn]
PFX RR l otulinn l.[mn]
PFX RR w otulimp [w]
PFX RR 0 otulimu .
PFX RR 0 otuliba .
PFX RR 0 otuligu .
PFX RR 0 otuligi .
PFX RR 0 otulizi .
PFX RR 0 otuliki .
PFX RR 0 otulibi .
PFX RR 0 otulili .
PFX RR 0 otuliga .
PFX RR 0 otulika .
PFX RR 0 otulibu .
PFX RR 0 otulilu .
PFX RR 0 otuliku .
PFX RR 0 otulitu .
PFX RR 0 zitalo ."""

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
    "RR": "RR",
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

    out_flag = "JH"
    left_desc = FLAG_DESCRIPTIONS.get("RR", "RR")
    right_desc = FLAG_DESCRIPTIONS.get("OR", "OR")
    comment_line = "# Cross product of {} ({}) and {} ({}) to {}".format(
        "RR", left_desc, "OR", right_desc, out_flag
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
