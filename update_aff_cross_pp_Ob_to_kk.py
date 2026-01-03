import os

from cross_product_common import upsert_pfx_block

AFF_FILE = r"e:\Luganda Hunspell Dictionary\Luganda.aff"


def main() -> None:
    print("Generating cross product: pp x Ob -> kk")
    upsert_pfx_block(
        aff_file=AFF_FILE,
        subject_flag="pp",
        object_flag="Ob",
        target_flag="kk",
        filter_1st_person=True,
        comment="# Cross product pp x Ob (negative present progressive subject + basic object) -> kk\n",
    )
    print("Done. Updated kk in Luganda.aff")


if __name__ == "__main__":
    main()
