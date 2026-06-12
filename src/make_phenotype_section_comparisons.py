from config_locations_etc import *
from read_and_parse import (
    read_phenotypes_to_publish,
    read_phenotype_description_files,
    parse_description_for_section,
)

from phenotype import Phenotype

def make_section_comparison_markdown_file(phenotypes=None, phenotype_sections=None, section=None):
    for p_id, p in phenotypes.items():
        print()
        print(f"## {section:} {p_id}: {p.title}")
        print()
        print(phenotype_sections[section][p_id])

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
phenotype_sections = {}
for phenotype_id in phenotypes_to_publish:
    phenotype_raw_description = phenotype_descriptions[phenotype_id]
    phenotypes[phenotype_id] = Phenotype(
        phenotype_id=phenotype_id, phenotype_raw_description=phenotype_raw_description
    )
    for section, header_text in [("overview", "overview"), ("template_usage", "template usage"), ("pseudocode","pseudocode")]:
        if section not in phenotype_sections:
            phenotype_sections[section] = {}
        phenotype_sections[section][phenotype_id] = parse_description_for_section(
            description=phenotypes[phenotype_id].raw_description,
            header_text=header_text,
        )

# make_section_comparison_markdown_file(phenotypes=phenotypes, phenotype_sections=phenotype_sections, section="overview")
# make_section_comparison_markdown_file(phenotypes=phenotypes, phenotype_sections=phenotype_sections, section="template_usage")
make_section_comparison_markdown_file(phenotypes=phenotypes, phenotype_sections=phenotype_sections, section="pseudocode")
