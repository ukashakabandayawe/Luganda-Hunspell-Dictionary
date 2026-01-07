from cross_product_common import upsert_pfx_block

AFF_FILE = r"e:\Luganda Hunspell Dictionary\Luganda.aff"


def main() -> None:
    print("Generating cross product: ob x pS -> BR")
    upsert_pfx_block(
        aff_file=AFF_FILE,
        subject_flag="ob",
        object_flag="pS",
        target_flag="BR",
        filter_1st_person=False,
        comment="# Cross product ob x pS -> BR\n",
    )
    print("Done. Updated BR in Luganda.aff")


if __name__ == "__main__":
    main()
