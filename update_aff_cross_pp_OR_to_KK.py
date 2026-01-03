from cross_product_common import upsert_pfx_block

AFF_FILE = r"e:\Luganda Hunspell Dictionary\Luganda.aff"


def main() -> None:
    print("Generating cross product: pp x OR -> KK")
    upsert_pfx_block(
        aff_file=AFF_FILE,
        subject_flag="pp",
        object_flag="OR",
        target_flag="KK",
        filter_1st_person=False,
        comment="# Cross product pp x OR (negative present progressive subject + special reflexive object) -> KK\n",
    )
    print("Done. Updated KK in Luganda.aff")


if __name__ == "__main__":
    main()
