from posixpath import dirname
import sys
import pandas as pd
from os.path import join
from os import listdir
import sssom
import yaml
from sssom.parsers import read_sssom_table
from sssom.writers import write_table

MAPPINGS_DIR = join(dirname(dirname(__file__)), "mappings")
RAW_INPUT_DIR = join(dirname(dirname(__file__)), "raw_input")
TMP_DIR = join(dirname(dirname(__file__)), "tmp")
META = join(dirname(dirname(__file__)), "metadata.yaml")

PREFIX_DICT = {"ncit": "NCI:"}
PREDICATE_DICT = {
    "Broader Than": "skos:narrowMatch",
    "Related To": "skos:relatedMatch",
    "Has Synonym": "skos:exactMatch",
    "Narrower Than": "skos:broadMatch",
}
with open(META, "r") as stream:
    try:
        metadata_yaml = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

# "Broader Than": "oboInOwl:hasBroadSynonym",
# "Related To": "oboInOwl:hasRelatedSynonym",
# "Has Synonym": "oboInOwl:hasExactSynonym",
# "Narrower Than": "oboInOwl:hasNarrowSynonym"


def get_file_from_dir(ont: str, dir: str, ext: str = ".tsv") -> str:
    # sep = "\t" if ext == ".tsv" else ","
    f = [x for x in listdir(dir) if ont in x and x.endswith(ext)]
    return f


def main(ont):
    columns_needed = [
        "CODE",
        "RELATIONSHIP_TO_TARGET",
        "TARGET_CODE",
        "TARGET_TERM",
        "TARGET_TERMINOLOGY",
    ]
    prefix = PREFIX_DICT[ont]
    ncit_file = get_file_from_dir("ncit", MAPPINGS_DIR)[0]
    ncit_sssom = read_sssom_table(join(MAPPINGS_DIR, ncit_file))

    # blank_columns = [
    #     x
    #     for x in ncit_sssom.df.columns.values.tolist()
    #     if x not in new_df.columns.values.tolist()
    # ]
    # for col_name in blank_columns:
    #     new_df[col_name] = ""

    ncit_sssom.metadata["mapping_date"] = "2018-07-05"
    new_prefix_map = dict()
    new_prefix_map["NCI"] = ncit_sssom.prefix_map["NCI"]
    new_prefix_map[
        "ICD10CM"
    ] = "http://apps.who.int/classifications/icd10/browse/2010/en#/"

    # merged_msdf = sssom.util.merge_msdf(
    #     ncit_sssom, ncit_icd10_sssom, reconcile=False
    # )

    # merged_msdf.df = merged_msdf.df.dropna(how="all")
    # merged_msdf.prefix_map = new_prefix_map
    # merged_msdf.metadata = ncit_sssom.metadata

    list_of_files = get_file_from_dir(ont, TMP_DIR, ".csv")

    for fn in list_of_files:
        fp = join(TMP_DIR, fn)
        df = pd.read_csv(
            fp,
            low_memory=False,
            usecols=columns_needed,
        )
        df["CODE"] = prefix + df["CODE"].astype(str)
        df["RELATIONSHIP_TO_TARGET"] = df["RELATIONSHIP_TO_TARGET"].apply(
            lambda x: PREDICATE_DICT.get(x)
        )

        df["TARGET_CODE"] = (
            df["TARGET_TERMINOLOGY"].str.split(" ", expand=True)[0]
            + ":"
            + df["TARGET_CODE"]
        )

        new_df = df.drop(columns=["TARGET_TERMINOLOGY"], axis=1)

        new_df = new_df.rename(
            columns={
                "CODE": "subject_id",
                "RELATIONSHIP_TO_TARGET": "predicate_id",
                "TARGET_CODE": "object_id",
                "TARGET_TERM": "subject_label",
            }
        )
        # new_df.insert(loc=3, column="match_type", value="Unspecified")
        new_df = new_df.drop_duplicates()
        ncit_icd10_sssom = sssom.util.MappingSetDataFrame(
            df=new_df,
            metadata=ncit_sssom.metadata,
            prefix_map=new_prefix_map,
        )
        new_fn = fn.replace(".csv", ".sssom.tsv")
        with open(join(MAPPINGS_DIR, new_fn), "w") as file:
            write_table(ncit_icd10_sssom, file)


if __name__ == "__main__":
    main(sys.argv[1])
