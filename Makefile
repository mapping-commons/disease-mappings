MAPPINGS_DIR=mappings

.PHONY: inputs

inputs: raw_input tmp raw_input/mondo.owl tmp/mondo.json
raw_input/:
	mkdir -p $@
tmp/:
	mkdir -p $@

raw_input/mondo.owl:
	wget http://purl.obolibrary.org/obo/mondo.owl -O $@


tmp/mondo.json: raw_input/mondo.owl
	robot convert -i $< -o $@

.PHONY: sssom
sssom:
	echo "skipping.."
#	python3 -m pip install --upgrade pip setuptools && python3 -m pip install --upgrade --force-reinstall sssom==0.3.7

tmp/%.sssom.tsv: tmp/%.json | sssom
	sssom parse tmp/$*.json -I obographs-json -m tmp/mondo_metadata.yaml -o $@
