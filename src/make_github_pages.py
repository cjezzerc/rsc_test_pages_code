import openpyxl

from config_locations_etc import *
from read_write_and_parse import (
    read_phenotypes_to_publish,
    read_phenotype_description_files,
    read_codelist_description_files,
    create_phenotype_index_markdown_file,
    create_codelist_index_markdown_file,
    create_phenotype_output_description_files,
    create_codelist_output_description_files,
    create_codelist_output_logical_definition_files,
    create_codelist_output_expansion_files,
    read_and_set_expansions,
    read_and_set_logical_definitions,
)
from phenotype import Phenotype
from codelist import Codelist

# Get list of phenotypes to be published
phenotypes_to_publish = read_phenotypes_to_publish(
    phenotypes_to_publish_file=PHENOTYPE_LIST
)

# Read the phenotype descriptions files
phenotype_descriptions = read_phenotype_description_files(
    phenotype_descriptions_dir=PHENOTYPE_DESCRIPTIONS_DIR,
    phenotypes_to_publish=phenotypes_to_publish,
)

# Create a dictionary of Phenotype objects
# During this process phenotype descriptions are scanned for mentions of codelists
phenotypes = {}
for phenotype_id in phenotypes_to_publish:
    phenotype_raw_description = phenotype_descriptions[phenotype_id]
    phenotypes[phenotype_id] = Phenotype(
        phenotype_id=phenotype_id, phenotype_raw_description=phenotype_raw_description
    )

# List of codelists ids is created, via combining all Phenotype objects' codelists_mentioned attributes
codelists_to_publish = set()
for p in phenotypes.values():
    codelists_to_publish.update(p.codelists_mentioned)
codelists_to_publish = list(codelists_to_publish)

# Read the codelist descriptions files
codelist_descriptions = read_codelist_description_files(
    codelist_descriptions_dir=CODELIST_DESCRIPTIONS_DIR,
    codelists_to_publish=codelists_to_publish,
)

# Create a dictionary of Codelist objects
codelists = {}
for codelist_id in codelists_to_publish:
    if codelist_id in codelist_descriptions:
        codelist_raw_description = codelist_descriptions[codelist_id]
    else:
        codelist_raw_description = ""
    codelists[codelist_id] = Codelist(
        codelist_id=codelist_id, codelist_raw_description=codelist_raw_description
    )


# Scan all Phenotype objects' codelists_mentioned attributes and set the phenotypes_used_in attributes of Codelist objects
for p_id, p in phenotypes.items():
    for codelist_id in p.codelists_mentioned:
        codelists[codelist_id].phenotypes_used_in.append(p_id)

# Set the "expansion" attributes of all Codelist objects
read_and_set_expansions(codelists=codelists)

# Set the "logical_definition" attributes of all Codelist objects
read_and_set_logical_definitions(codelists=codelists)

# create output files
create_phenotype_index_markdown_file(phenotypes=phenotypes, codelists=codelists)
create_codelist_index_markdown_file(phenotypes=phenotypes, codelists=codelists)
create_phenotype_output_description_files(phenotypes=phenotypes, codelists=codelists)
create_codelist_output_description_files(codelists=codelists)
create_codelist_output_logical_definition_files(codelists=codelists)
create_codelist_output_expansion_files(codelists=codelists)
