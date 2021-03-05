# Mapping Commons Template
Template repo for other mapping-commons registries. 

Steps:
1. Create a [new repo from this template](https://github.com/mapping-commons/mapping-commons-template/generate).
2. Update `mappings.yml`
3. Expose your sssom files in the `mappings` directory. Make sure for every mapping follows the conventions below.

## Conventions for mappings

1. Every mapping should be exposed in three ways:
   1. SSSOM TSV: `mapping_id.sssom.tsv`. A regular TSV file without a header.
   2. SSSOM Metadata: `mapping_id.sssom.yml`. A yml file containing the mapping set metadata for the SSSOM TSV.
   3. SSSOM TSV (embedded): `mapping_id_embedded.sssom.tsv`. The SSSOM Metdata is included in the header of the SSSOM TSV, see [here](https://w3id.org/sssom/SSSOM.md#embedded-mode).
2. All the metadata you include in the mappings.yml should be included (added to, if necessary) in the SSSOM Metadata.
3. In most cases, mappings should be between two sources, and the identifiers of the subject should belong to one sources, and the identifiers of the object to the other.
