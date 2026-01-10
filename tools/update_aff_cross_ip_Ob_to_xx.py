from pathlib import Path
from cross_product_common import upsert_pfx_block

REPO_ROOT = Path(__file__).resolve().parents[1]
AFF_FILE = REPO_ROOT / "Luganda.aff"


def main() -> None:
    print("Generating cross product: ip x Ob -> xx")
    upsert_pfx_block(
        aff_file=AFF_FILE,
        subject_flag="ip",
        object_flag="Ob",
        target_flag="xx",
        filter_1st_person=True,
        comment="# Cross product ip x Ob (negative immediate past subject + basic object) -> xx\n",
    )
    print("Done. Updated xx in Luganda.aff")


if __name__ == "__main__":
    main()
