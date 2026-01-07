from cross_product_common import upsert_pfx_block

AFF_FILE = r"e:\Luganda Hunspell Dictionary\Luganda.aff"


def main() -> None:
    print("Generating cross product: ob x IP -> BK")
    upsert_pfx_block(
        aff_file=AFF_FILE,
        subject_flag="ob",
        object_flag="IP",
        target_flag="BK",
        filter_1st_person=False,
        comment="# Cross product ob x IP -> BK\n",
    )
    print("Done. Updated BK in Luganda.aff")


if __name__ == "__main__":
    main()
