from pathlib import Path
from cross_product_common import upsert_pfx_block

REPO_ROOT = Path(__file__).resolve().parents[1]
AFF_FILE = REPO_ROOT / "Luganda.aff"


def main() -> None:
    print("Generating cross product: JJ x Ob -> HH")
    upsert_pfx_block(
        aff_file=AFF_FILE,
        subject_flag="JJ",
        object_flag="Ob",
        target_flag="HH",
        filter_1st_person=True,
        comment="# Cross product JJ x Ob (distant past progressive subject + basic object) -> HH\n",
    )
    print("Done. Updated HH in Luganda.aff")


if __name__ == "__main__":
    main()
