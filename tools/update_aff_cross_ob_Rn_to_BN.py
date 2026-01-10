from pathlib import Path
from cross_product_common import upsert_pfx_block

REPO_ROOT = Path(__file__).resolve().parents[1]
AFF_FILE = REPO_ROOT / "Luganda.aff"


def main() -> None:
    print("Generating cross product: ob x Rn -> BN")
    upsert_pfx_block(
        aff_file=AFF_FILE,
        subject_flag="ob",
        object_flag="Rn",
        target_flag="BN",
        filter_1st_person=False,
        comment="# Cross product ob x Rn -> BN\n",
    )
    print("Done. Updated BN in Luganda.aff")


if __name__ == "__main__":
    main()
