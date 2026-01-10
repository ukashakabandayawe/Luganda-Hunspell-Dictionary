from pathlib import Path
from cross_product_common import upsert_pfx_block

REPO_ROOT = Path(__file__).resolve().parents[1]
AFF_FILE = REPO_ROOT / "Luganda.aff"


def main() -> None:
    print("Generating cross product: ob x rP -> BU")
    upsert_pfx_block(
        aff_file=AFF_FILE,
        subject_flag="ob",
        object_flag="rP",
        target_flag="BU",
        filter_1st_person=False,
        comment="# Cross product ob x rP -> BU\n",
    )
    print("Done. Updated BU in Luganda.aff")


if __name__ == "__main__":
    main()
