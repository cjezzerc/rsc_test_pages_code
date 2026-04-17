import os.path, sys, re, csv

from config_locations_etc import *


def read_phenotypes_to_publish(phenotypes_to_publish_file=None):
    phenotypes_index = []
    with open(phenotypes_to_publish_file) as fh:
        for line in fh.readlines():
            temp = line.strip()
            if temp != "":  # ignore blank lines
                phenotypes_index.append(temp)
    return phenotypes_index


def read_phenotype_description_files(
    phenotype_descriptions_dir=None, phenotypes_to_publish=None
):
    phenotype_descriptions = {}  # dict of markdown keyed by phenotype id
    for phenotype_id in phenotypes_to_publish:
        description_file = os.path.join(
            phenotype_descriptions_dir, phenotype_id + ".md"
        )
        if os.path.isfile(description_file):
            with open(description_file, "r") as f:
                markdown = f.readlines()
            phenotype_descriptions[phenotype_id] = markdown
        else:
            print(
                f"Error: no description file found for {phenotype_id} at {description_file}"
            )
            sys.exit()
    return phenotype_descriptions


def parse_description_for_brief_description(description=None):
    # look for text following "## brief description" (case insensitive) line, and before next "## ...." line found
    in_brief_description = False
    brief_description = "no-brief-description-found"
    for line in description:
        if re.search(r"^##[ ]+brief description", line.lower()):
            in_brief_description = True
            continue
        if in_brief_description and line[:3] == "## ":
            in_brief_description = False
            continue
        if in_brief_description:
            if brief_description == "no-brief-description-found":
                brief_description = ""
            brief_description += " " + line.strip()
    brief_description = brief_description.strip()
    return brief_description


def parse_description_for_title(description=None):
    # find first line starting with "# " and use that as title
    title = "No-title-found"
    for line in description:
        if line[:2] == "# ":
            if len(line) > 2:
                title = line[2:].strip()
            break
    return title


def parse_phenotype_description_for_is_template_status(phenotype_description=None):
    # find if contains '## template note' (case insensitive)
    is_template = False
    for line in phenotype_description:
        if re.search(r"^## template note", line.lower()):
            is_template = True
            break
    return is_template


def parse_phenotype_description_for_codelist_usage(phenotype_description=None):
    # find all occurrences of RSC-C followed by pure digits
    codelists_mentioned = []
    for line in phenotype_description:
        codelists_mentioned += re.findall(r"\bRSC-C\d+\b", line)
    return codelists_mentioned


def parse_phenotype_description_for_template_phenotype_usage(
    phenotype_description=None,
):
    # find all occurrences of T:RSC-PH followed by pure digits
    # before returning the list, the "T:" part is stripped off
    templates_mentioned = []
    for line in phenotype_description:
        templates_mentioned += re.findall(r"\bT:RSC-PH\d+\b", line)
    templates_mentioned_trimmed = [x[2:] for x in templates_mentioned]
    return templates_mentioned_trimmed


def read_codelist_description_files(
    codelist_descriptions_dir=None, codelists_to_publish=None
):
    codelist_descriptions = {}  # dict of markdown keyed by phenotype id
    for codelist_id in codelists_to_publish:
        description_file = os.path.join(codelist_descriptions_dir, codelist_id + ".md")
        if os.path.isfile(description_file):
            with open(description_file, "r") as f:
                markdown = f.readlines()
            codelist_descriptions[codelist_id] = markdown
        else:
            print(
                f"Warning: no description file found for {codelist_id} at {description_file}"
            )
            # sys.exit()
    return codelist_descriptions


def read_and_set_expansions(codelists=None):
    with open(CODELIST_EXPANSIONS, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            codelist_id = "RSC-C" + row["ConditionID"]
            concept_id = row["ConceptID"]
            term = row["Term"]
            if codelist_id in codelists:
                codelists[codelist_id].expansion.append(
                    {"concept_id": concept_id, "term": term}
                )


def read_and_set_logical_definitions(codelists=None):
    with open(CODELIST_DEFINITIONS, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            codelist_id = "RSC-C" + row["ConditionID"]
            operator = row["ECLElement"]
            concept_id = row["ConceptID"]
            term = row["TERM"]
            if codelist_id in codelists:
                if operator == "AddSubtype":
                    codelists[codelist_id].logical_definition["includes"].append(
                        {"concept_id": concept_id, "term": term, "include_desc": False}
                    )
                if operator == "AddSupertype":
                    codelists[codelist_id].logical_definition["includes"].append(
                        {"concept_id": concept_id, "term": term, "include_desc": True}
                    )
                if operator == "MinusSubtype":
                    codelists[codelist_id].logical_definition["excludes"].append(
                        {"concept_id": concept_id, "term": term, "include_desc": False}
                    )
                if operator == "MinusSupertype":
                    codelists[codelist_id].logical_definition["excludes"].append(
                        {"concept_id": concept_id, "term": term, "include_desc": True}
                    )
