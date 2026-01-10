from pathlib import Path
from cross_product_common import upsert_pfx_block

REPO_ROOT = Path(__file__).resolve().parents[1]
AFF_FILE = REPO_ROOT / "Luganda.aff"


def main() -> None:
    print("Generating cross product: JJ x OR -> ii")
    upsert_pfx_block(
        aff_file=AFF_FILE,
        subject_flag="JJ",
        object_flag="OR",
        target_flag="ii",
        filter_1st_person=False,
        comment="# Cross product JJ x OR (distant past progressive subject + special reflexive object) -> ii\n",
    )
    print("Done. Updated ii in Luganda.aff")


if __name__ == "__main__":
    main()
