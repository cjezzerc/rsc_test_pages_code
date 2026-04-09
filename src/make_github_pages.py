import openpyxl

from config_locations_etc import *
from read_write_and_parse import (
    read_phenotypes_to_publish,
    read_phenotype_description_files,
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

# Dictionary of Codelists objects is created, via combining all Phenotype objects' codelists_mentioned attributes
codelists_to_publish = set()
for p in phenotypes.values():
    codelists_to_publish.update(p.codelists_mentioned)
codelists = {
    c: Codelist(codelist_id=c, codelist_raw_description="")
    for c in codelists_to_publish
}

# Scan all Phenotype objects' codelists_mentioned attributes and set the phenotypes_used_in attributes of Codelist objects 
for p_id, p in phenotypes.items():
    for codelist_id in p.codelists_mentioned:
        codelists[codelist_id].phenotypes_used_in.append(p_id)

# Set the "expansion" attributes of all Codelist objects
read_and_set_expansions(codelists=codelists)

# Set the "logical_definition" attributes of all Codelist objects
read_and_set_logical_definitions(codelists=codelists)

# create output files
create_phenotype_index_markdown_file(
    phenotypes=phenotypes, codelists=codelists
)
create_codelist_index_markdown_file(
    phenotypes=phenotypes, codelists=codelists
)
create_phenotype_output_description_files(phenotypes=phenotypes, codelists=codelists)
create_codelist_output_description_files(codelists=codelists)
create_codelist_output_logical_definition_files(codelists=codelists)
create_codelist_output_expansion_files(codelists=codelists)
