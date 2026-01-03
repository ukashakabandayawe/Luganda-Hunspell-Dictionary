from cross_product_common import upsert_pfx_block

AFF_FILE = r"e:\Luganda Hunspell Dictionary\Luganda.aff"


def main() -> None:
    print("Generating cross product: IP x OR -> ww")
    upsert_pfx_block(
        aff_file=AFF_FILE,
        subject_flag="IP",
        object_flag="OR",
        target_flag="ww",
        filter_1st_person=False,
        comment="# Cross product IP x OR (immediate past subject + special reflexive object) -> ww\n",
    )
    print("Done. Updated ww in Luganda.aff")


if __name__ == "__main__":
    main()
