from cross_product_common import upsert_pfx_block

AFF_FILE = r"e:\Luganda Hunspell Dictionary\Luganda.aff"


def main() -> None:
    print("Generating cross product: jj x OR -> uu")
    upsert_pfx_block(
        aff_file=AFF_FILE,
        subject_flag="jj",
        object_flag="OR",
        target_flag="uu",
        filter_1st_person=False,
        comment="# Cross product jj x OR (negative past progressive subject + special reflexive object) -> uu\n",
    )
    print("Done. Updated uu in Luganda.aff")


if __name__ == "__main__":
    main()
