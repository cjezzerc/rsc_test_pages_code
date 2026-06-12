import sys

from config_locations_etc import *
from read_and_parse import (
    read_phenotypes_to_publish,
    read_phenotype_description_files,
    parse_description_for_section,
)

from phenotype import Phenotype


def make_section_comparison_markdown_file(
    phenotypes=None, phenotype_sections=None, section=None
):
    
    print(f"\n# Section: {requested_section}\n")

    for p_id, p in phenotypes.items():
        section_text = phenotype_sections[section][p_id]
        if section_text != "no-section-found":
            header = f"## section:{section:} - {p_id}: {p.title}"
            separator_line = "<!--" + "=" * len(header) + "-->"
            print()
            print(separator_line)
            print(separator_line)
            print(header)
            print(separator_line)
            print(separator_line)
            print()
            print(section_text)


# allowed_sections=[("overview", "overview"), ("template_usage", "template usage"), ("pseudocode","pseudocode")]:
allowed_sections = {
    "brief_description": "brief description",
    "overview": "overview",
    "template_usage": "template usage",
    "input": "input",
    "output": "output",
    "pseudocode": "pseudocode",
    "condition_notes": "condition notes",

}

requested_section = sys.argv[1]

if requested_section not in allowed_sections.keys():
    print(f"Did not recognise {requested_section} as a valid section")
    print(f"Allowed values are: {" | ".join(list(allowed_sections.keys()))}")
    sys.exit()


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
    for section, header_text in allowed_sections.items():
        if section not in phenotype_sections:
            phenotype_sections[section] = {}
        phenotype_sections[section][phenotype_id] = parse_description_for_section(
            description=phenotypes[phenotype_id].raw_description,
            header_text=header_text,
        )

# make_section_comparison_markdown_file(phenotypes=phenotypes, phenotype_sections=phenotype_sections, section="overview")
# make_section_comparison_markdown_file(phenotypes=phenotypes, phenotype_sections=phenotype_sections, section="template_usage")
# make_section_comparison_markdown_file(phenotypes=phenotypes, phenotype_sections=phenotype_sections, section="pseudocode")
make_section_comparison_markdown_file(
    phenotypes=phenotypes,
    phenotype_sections=phenotype_sections,
    section=requested_section,
)
