import os

# ROOT_DIR = "../"
ROOT_DIR=os.environ["ROOT_DIR"]+"/"
# PHENOTYPE_LIST = ROOT_DIR + "config_files/phenotypes_for_website_table.xlsx"
FROM_ORCHID_DIR = ROOT_DIR + "files_from_orchid/codelists_for_website/"
CODELIST_EXPANSIONS = FROM_ORCHID_DIR + "flatlists_for_website.txt"
CODELIST_DEFINITIONS = FROM_ORCHID_DIR + "logical_definitions_for_website.txt"
CODELIST_MEDS_DEFINITIONS = FROM_ORCHID_DIR + "logical_definitions_for_medications_for_website.txt"
RSC_IMAGE_FILENAME = "rsc_image.png"
SHARED_CSS_FILENAME = "shared.css"



AUTHORING="/home/jeremy/GIT/rsc_test_pages_authoring/"
PHENOTYPE_LIST = AUTHORING + "/phenotypes_to_publish.txt"
PHENOTYPE_DESCRIPTIONS_DIR = AUTHORING + "phenotypes/"
CODELIST_DESCRIPTIONS_DIR = AUTHORING + "codelists/"
DOCS_DIR = AUTHORING + "docs/"
# PHENOTYPE_DESCRIPTIONS_DIR = ROOT_DIR + "markdown_descriptions/phenotypes/"

OUTPUT_STAGING_ROOT_DIR = "/home/jeremy/GIT/rsc_test_pages/"
# OUTPUT_STAGING_ROOT_DIR = ROOT_DIR + "github_pages_staging/"
PHENOTYPES_OUTPUT_INDEX = OUTPUT_STAGING_ROOT_DIR + "phenotypes_index.html"
PHENOTYPES_OUTPUT_DESCRIPTIONS_DIR = OUTPUT_STAGING_ROOT_DIR + "phenotypes/"
CODELISTS_OUTPUT_INDEX = OUTPUT_STAGING_ROOT_DIR + "codelists_index.html"
# CODELISTS_OUTPUT_INDEX = OUTPUT_STAGING_ROOT_DIR + "phenotypes_index.md" # just to make sure exists to keep jekyll happy
# CODELISTS_OUTPUT_DESCRIPTIONS_DIR = OUTPUT_STAGING_ROOT_DIR + "codelists/descriptions/"
CODELISTS_OUTPUT_DESCRIPTIONS_DIR = OUTPUT_STAGING_ROOT_DIR + "codelists/"
DOCS_OUTPUT_DIR = OUTPUT_STAGING_ROOT_DIR + "docs/"
DOCS_OUTPUT_INDEX = DOCS_OUTPUT_DIR + "index.html"
CODELISTS_OUTPUT_FOR_DOWNLOAD_DIR = OUTPUT_STAGING_ROOT_DIR + "codelists_for_download/"
# CODELISTS_OUTPUT_LOGICAL_DEFINITIONS_DIR = OUTPUT_STAGING_ROOT_DIR + "codelists/logical_definitions/"
# CODELISTS_OUTPUT_EXPANSIONS_DIR = OUTPUT_STAGING_ROOT_DIR + "codelists/expansions/"

DATA_FOR_POWER_BI_DIR = os.environ["DATA_FOR_POWER_BI_DIR"]+"/"
DOCX_DIR = os.environ["DOCX_DIR"]+"/"