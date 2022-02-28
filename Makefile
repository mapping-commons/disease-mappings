MAPPINGS_DIR=mappings
INPUT_DIR=raw_input/
OMIM=https://github.com/monarch-initiative/omim/releases/download/latest/omim.ttl
ORDO=http://www.orphadata.org/data/ORDO/ORDO_en_4.0.owl
MAPPINGS=ncit mondo ordo omim doid ncit_icd10_2016 ncit_icd10_2017
MAPPINGS_TSVS=$(patsubst %, mappings/%.sssom.tsv, $(MAPPINGS))

.PHONY:
map: $(MAPPINGS_TSVS)

.PHONY: dirs

dirs: $(INPUT) tmp/
$(INPUT) tmp/:
	mkdir -p $@

# get ICD10 mapping files
tmp/ncit_icd10_2016.csv: | tmp/
	wget "https://ncit.nci.nih.gov/ncitbrowser/ajax?action=export_maps_to_mapping&target=ICD10%202016" -O $@

tmp/ncit_icd10_2017.csv: | tmp/
	wget "https://ncit.nci.nih.gov/ncitbrowser/ajax?action=export_maps_to_mapping&target=ICD10CM%202017" -O $@
# This works for MONDO, DOID and NCIT [everything in obofoundry]
$(INPUT)%.owl: | $(INPUT)
	wget http://purl.obolibrary.org/obo/$*.owl -O $@

$(INPUT)omim.owl: | $(INPUT)
	wget $(OMIM) -O $@

$(INPUT)ordo.owl: | $(INPUT)
	wget $(ORDO) -O $@


tmp/%.json: $(INPUT)%.owl
	robot convert -i $< -o $@

.PHONY: sssom
sssom:
	echo "skipping.."
#	pip install from git for now. Eventually uncomment below.
#	python3 -m pip install --upgrade pip setuptools && python3 -m pip install --upgrade --force-reinstall sssom==0.3.7

$(MAPPINGS_DIR)/%.sssom.tsv: tmp/%.json | sssom
	sssom parse tmp/$*.json -I obographs-json -m metadata.yaml -o $@

.PHONY: map_ncit_icd10
map_ncit_icd10: $(MAPPINGS_DIR)/ncit_icd10_2016.sssom.tsv mappings/ncit_icd10_2017.sssom.tsv

$(MAPPINGS_DIR)/ncit_icd10_2016.sssom.tsv mappings/ncit_icd10_2017.sssom.tsv:
	python -m script.add-ext-mapping ncit
	
#* FOR DEV ONLY
p:
	echo $(MAPPINGS_TSVS)

q: $(MAPPINGS_DIR)/doid.sssom.tsv