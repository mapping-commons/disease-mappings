MAPPINGS_DIR=mappings
OMIM=https://github.com/monarch-initiative/omim/releases/download/latest/omim.ttl
ORDO=http://www.orphadata.org/data/ORDO/ORDO_en_4.0.owl
MAPPINGS=ncit ordo doid ncit_icd10_2016 ncit_icd10_2017 mondo_hasdbref_icd10cm
MAPPINGS_TSVS=$(patsubst %, mappings/%.sssom.tsv, $(MAPPINGS))

.PHONY:
map: $(MAPPINGS_TSVS)

.PHONY: dirs

dirs: raw_input/ tmp/
raw_input/ tmp/:
	mkdir -p $@

# get ICD10 mapping files
tmp/ncit_icd10_2016.csv: | tmp/
	wget "https://ncit.nci.nih.gov/ncitbrowser/ajax?action=export_maps_to_mapping&target=ICD10%202016" -O $@

tmp/ncit_icd10_2017.csv: | tmp/
	wget "https://ncit.nci.nih.gov/ncitbrowser/ajax?action=export_maps_to_mapping&target=ICD10CM%202017" -O $@

# This works for DOID and NCIT [everything in obofoundry]
raw_input/%.owl: | raw_input/
	wget http://purl.obolibrary.org/obo/$*.owl -O $@

raw_input/omim.owl: | raw_input/
	wget $(OMIM) -O $@

raw_input/ordo.owl: | raw_input/
	wget $(ORDO) -O $@


tmp/%.json: raw_input/%.owl
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

# $(MAPPINGS_DIR)/mondo_hasdbref_icd10cm.sssom.tsv:
# 	wget http://purl.obolibrary.org/obo/mondo/mappings/mondo_hasdbxref_icd10cm.sssom.tsv -O $@
$(MAPPINGS_DIR)/mondo_hasdbref_icd10cm.sssom.tsv:
	wget https://raw.githubusercontent.com/monarch-initiative/mondo/master/src/ontology/mappings/mondo_hasdbxref_icd10cm.sssom.tsv -O $@

#* FOR DEV ONLY
p:
	echo $(MAPPINGS_TSVS)

q: $(MAPPINGS_DIR)/doid.sssom.tsv