from cross_product_common import upsert_pfx_block

AFF_FILE = r"e:\Luganda Hunspell Dictionary\Luganda.aff"


def main() -> None:
    print("Generating cross product: jj x Ob -> tt")
    upsert_pfx_block(
        aff_file=AFF_FILE,
        subject_flag="jj",
        object_flag="Ob",
        target_flag="tt",
        filter_1st_person=True,
        comment="# Cross product jj x Ob (negative past progressive subject + basic object) -> tt\n",
    )
    print("Done. Updated tt in Luganda.aff")


if __name__ == "__main__":
    main()
