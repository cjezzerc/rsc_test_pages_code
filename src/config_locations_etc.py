import os

# ROOT_DIR = "../"
ROOT_DIR=os.environ["ROOT_DIR"]
# PHENOTYPE_LIST = ROOT_DIR + "config_files/phenotypes_for_website_table.xlsx"
FROM_ORCHID_DIR = ROOT_DIR + "files_from_orchid/codelist_examples_for_website/"
CODELIST_EXPANSIONS = FROM_ORCHID_DIR + "flatlist_for_website_examples.txt"
CODELIST_DEFINITIONS = FROM_ORCHID_DIR + "logical_definitions_for_website_examples.txt"

AUTHORING="/home/jeremy/GIT/rsc_test_pages_authoring/"
PHENOTYPE_LIST = AUTHORING + "/phenotypes_to_publish.txt"
PHENOTYPE_DESCRIPTIONS_DIR = AUTHORING + "phenotypes/"
CODELIST_DESCRIPTIONS_DIR = AUTHORING + "codelists/"
# PHENOTYPE_DESCRIPTIONS_DIR = ROOT_DIR + "markdown_descriptions/phenotypes/"

OUTPUT_STAGING_ROOT_DIR = "/home/jeremy/GIT/rsc_test_pages/"
# OUTPUT_STAGING_ROOT_DIR = ROOT_DIR + "github_pages_staging/"
PHENOTYPES_OUTPUT_INDEX = OUTPUT_STAGING_ROOT_DIR + "phenotypes_index.html"
PHENOTYPES_OUTPUT_DESCRIPTIONS_DIR = OUTPUT_STAGING_ROOT_DIR + "phenotypes/"
CODELISTS_OUTPUT_INDEX = OUTPUT_STAGING_ROOT_DIR + "codelists_index.md"
# CODELISTS_OUTPUT_INDEX = OUTPUT_STAGING_ROOT_DIR + "phenotypes_index.md" # just to make sure exists to keep jekyll happy
CODELISTS_OUTPUT_DESCRIPTIONS_DIR = OUTPUT_STAGING_ROOT_DIR + "codelists/descriptions/"
CODELISTS_OUTPUT_LOGICAL_DEFINITIONS_DIR = OUTPUT_STAGING_ROOT_DIR + "codelists/logical_definitions/"
CODELISTS_OUTPUT_EXPANSIONS_DIR = OUTPUT_STAGING_ROOT_DIR + "codelists/expansions/"