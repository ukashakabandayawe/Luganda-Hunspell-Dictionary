from cross_product_common import upsert_pfx_block

AFF_FILE = r"e:\Luganda Hunspell Dictionary\Luganda.aff"


def main() -> None:
    print("Generating cross product: ob x PP -> BW")
    upsert_pfx_block(
        aff_file=AFF_FILE,
        subject_flag="ob",
        object_flag="PP",
        target_flag="BW",
        filter_1st_person=False,
        comment="# Cross product ob x PP -> BW\n",
    )
    print("Done. Updated BW in Luganda.aff")


if __name__ == "__main__":
    main()
