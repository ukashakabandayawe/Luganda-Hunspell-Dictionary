from pathlib import Path
from cross_product_common import upsert_pfx_block

REPO_ROOT = Path(__file__).resolve().parents[1]
AFF_FILE = REPO_ROOT / "Luganda.aff"


def main() -> None:
    print("Generating cross product: ip x OR -> cc")
    upsert_pfx_block(
        aff_file=AFF_FILE,
        subject_flag="ip",
        object_flag="OR",
        target_flag="cc",
        filter_1st_person=False,
        comment="# Cross product ip x OR (negative immediate past subject + special reflexive object) -> cc\n",
    )
    print("Done. Updated cc in Luganda.aff")


if __name__ == "__main__":
    main()
