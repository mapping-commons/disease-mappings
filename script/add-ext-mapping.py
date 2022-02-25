from hashlib import new
from posixpath import dirname
import sys
from importlib_metadata import metadata
import pandas as pd
from os.path import join
from os import listdir
import sssom
import yaml
from sssom.parsers import read_sssom_table
from sssom.typehints import MetadataType
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


def get_file_from_dir(ont: str, dir: str) -> str:
    f = [x for x in listdir(dir) if ont in x and x.endswith(".tsv")]
    return join(dir, f[0])


def main(ont):
    columns_needed = [
        "CODE",
        "RELATIONSHIP_TO_TARGET",
        "TARGET_CODE",
        "TARGET_TERM",
        "TARGET_TERMINOLOGY",
    ]
    df = pd.read_csv(
        get_file_from_dir(ont, RAW_INPUT_DIR),
        sep="\t",
        low_memory=False,
        usecols=columns_needed,
    )
    prefix = PREFIX_DICT[ont]
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
    new_df.insert(loc=3, column="match_type", value="Unspecified")
    new_df = new_df.drop_duplicates()
    ncit_sssom = read_sssom_table(get_file_from_dir("ncit", MAPPINGS_DIR))

    blank_columns = [
        x
        for x in ncit_sssom.df.columns.values.tolist()
        if x not in new_df.columns.values.tolist()
    ]
    for col_name in blank_columns:
        new_df[col_name] = ""

    new_prefix_map = ncit_sssom.prefix_map
    new_prefix_map["ICD10CM"] = "ICD10CM:"

    ncit_icd10_sssom = sssom.util.MappingSetDataFrame(
        df=new_df,
        metadata=ncit_sssom.metadata,
        prefix_map=new_prefix_map,
    )

    # sssom.from_sssom_dtaframe()
    merged_msdf = sssom.util.merge_msdf(
        ncit_sssom, ncit_icd10_sssom, reconcile=False
    )

    merged_msdf.df = merged_msdf.df.dropna(how="all")
    merged_msdf.prefix_map = new_prefix_map
    merged_msdf.metadata = ncit_sssom.metadata
    with open(join(MAPPINGS_DIR, "ncit-icd10.sssom.tsv"), "w") as file:
        write_table(merged_msdf, file)


if __name__ == "__main__":
    main(sys.argv[1])
