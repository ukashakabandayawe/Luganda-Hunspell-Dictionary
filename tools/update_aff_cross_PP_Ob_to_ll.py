from pathlib import Path
from cross_product_common import upsert_pfx_block

REPO_ROOT = Path(__file__).resolve().parents[1]
AFF_FILE = REPO_ROOT / "Luganda.aff"


def main() -> None:
    print("Generating cross product: PP x Ob -> ll")
    upsert_pfx_block(
        aff_file=AFF_FILE,
        subject_flag="PP",
        object_flag="Ob",
        target_flag="ll",
        filter_1st_person=True,
        comment="# Cross product PP x Ob (present progressive subject + basic object) -> ll\n",
    )
    print("Done. Updated ll in Luganda.aff")


if __name__ == "__main__":
    main()
