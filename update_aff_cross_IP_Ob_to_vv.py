from cross_product_common import upsert_pfx_block

AFF_FILE = r"e:\Luganda Hunspell Dictionary\Luganda.aff"


def main() -> None:
    print("Generating cross product: IP x Ob -> vv")
    upsert_pfx_block(
        aff_file=AFF_FILE,
        subject_flag="IP",
        object_flag="Ob",
        target_flag="vv",
        filter_1st_person=True,
        comment="# Cross product IP x Ob (immediate past subject + basic object) -> vv\n",
    )
    print("Done. Updated vv in Luganda.aff")


if __name__ == "__main__":
    main()
