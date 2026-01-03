from cross_product_common import upsert_pfx_block

AFF_FILE = r"e:\Luganda Hunspell Dictionary\Luganda.aff"


def main() -> None:
    print("Generating cross product: PP x OR -> LL")
    upsert_pfx_block(
        aff_file=AFF_FILE,
        subject_flag="PP",
        object_flag="OR",
        target_flag="LL",
        filter_1st_person=False,
        comment="# Cross product PP x OR (present progressive subject + special reflexive object) -> LL\n",
    )
    print("Done. Updated LL in Luganda.aff")


if __name__ == "__main__":
    main()
