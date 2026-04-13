import os.path, sys, re, copy, csv

import openpyxl
from jinja2 import Template

from config_locations_etc import *


def read_phenotypes_to_publish(phenotypes_to_publish_file=None):
    # ws = openpyxl.load_workbook(phenotypes_to_publish_file).worksheets[0]
    # phenotypes_index = []
    # next(ws.rows)  # skip header row
    # for row in ws.iter_rows(min_row=2):
    #     phenotype_id = row[0].value
    #     phenotypes_index.append(phenotype_id)
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


def create_phenotype_index_markdown_file(phenotypes=None, codelists=None):
    template_string = """
[Go to Codelist Index]({{ rel_path_to_codelists_index }})

# Phenotype Index

| id | title | brief description | codelists used | templates used |
|----|-------|-------------------|----------------|----------------|
{%- for p_id in p_ids_sorted %} 
    {%- set p = phenotypes[p_id] %} 
| {{ phenotype_hyperlinks[p.id] }} | {{p.title}} | {{ p.brief_description }} | {{codelist_hyperlinks[p.id]}}| {{template_hyperlinks[p.id]}} |
    {%- endfor %}

"""
    template = Template(template_string)
    output_fullpath = PHENOTYPES_OUTPUT_INDEX
    here = os.path.dirname(output_fullpath)
    rel_path_to_codelists_index = os.path.relpath(CODELISTS_OUTPUT_INDEX, here)
    phenotype_hyperlinks = {}
    codelist_hyperlinks = {}
    template_hyperlinks = {}
    for p_id, p in phenotypes.items():
        rel_path_to_phenotype_description = os.path.relpath(
            p.description_fullpath, here
        )
        phenotype_hyperlinks[p_id] = f"[{p_id}]({rel_path_to_phenotype_description})"
        chl = []
        for c in p.codelists_mentioned:
            rel_path_to_codelist_description = os.path.relpath(
                codelists[c].description_fullpath,
                here,
            )
            chl.append(f"[{c}]({rel_path_to_codelist_description})")
        codelist_hyperlinks[p_id] = ", ".join(chl)
        thl = []
        for t in p.templates_mentioned:
            rel_path_to_template_description = os.path.relpath(
                phenotypes[t].description_fullpath, here
            )
            thl.append(f"[{t}]({rel_path_to_template_description})")
        template_hyperlinks[p_id] = ", ".join(thl)
    p_ids = list(phenotypes.keys())
    p_ids_sorted = sorted(p_ids, key=lambda p_id: int(p_id[6:]))

    rendered_template = template.render(
        phenotypes=phenotypes,
        p_ids_sorted=p_ids_sorted,
        codelist_hyperlinks=codelist_hyperlinks,
        phenotype_hyperlinks=phenotype_hyperlinks,
        template_hyperlinks=template_hyperlinks,
        rel_path_to_codelists_index=rel_path_to_codelists_index,
    )

    with open(output_fullpath, "w") as ofh:
        ofh.write(rendered_template)


def create_codelist_index_markdown_file(codelists=None, phenotypes=None):
    template_string = """
[Go to Phenotype Index]({{ rel_path_to_phenotypes_index }})
    
# Codelist Index

| id | title | brief description | phenotypes used in |
|----|-------|-------------------|----------------|
{%- for c_id in c_ids_sorted %}
{%- set c = codelists[c_id] %} 
| {{ codelist_hyperlinks[c.id] }} | {{c.title}} | {{ c.brief_description }} | {{phenotype_hyperlinks[c.id]}}|
{%- endfor %}

"""
    template = Template(template_string)
    output_fullpath = CODELISTS_OUTPUT_INDEX
    here = os.path.dirname(output_fullpath)
    rel_path_to_phenotypes_index = os.path.relpath(PHENOTYPES_OUTPUT_INDEX, here)
    phenotype_hyperlinks = {}
    codelist_hyperlinks = {}
    for c_id, c in codelists.items():
        rel_path_to_codelist_description = os.path.relpath(c.description_fullpath, here)
        codelist_hyperlinks[c_id] = f"[{c_id}]({rel_path_to_codelist_description})"
        phhl = []
        for p in c.phenotypes_used_in:
            rel_path_to_phenotype_description = os.path.relpath(
                phenotypes[p].description_fullpath,
                here,
            )
            phhl.append(f"[{p}]({rel_path_to_phenotype_description})")
        phenotype_hyperlinks[c_id] = ", ".join(phhl)
    c_ids = list(codelists.keys())
    c_ids_sorted = sorted(c_ids, key=lambda c_id: int(c_id[5:]))

    rendered_template = template.render(
        codelists=codelists,
        c_ids_sorted=c_ids_sorted,
        codelist_hyperlinks=codelist_hyperlinks,
        phenotype_hyperlinks=phenotype_hyperlinks,
        rel_path_to_phenotypes_index=rel_path_to_phenotypes_index,
    )

    with open(output_fullpath, "w") as ofh:
        ofh.write(rendered_template)


def create_phenotype_output_description_files(phenotypes=None, codelists=None):
    template_string = """
[Back to Phenotype Index]({{ rel_path_to_phenotypes_index }})

[Back to Codelist Index]({{ rel_path_to_codelists_index }})

# RSC Phenotype {{ phenotype.id }}

{%- for line in modified_description %}
{{ line }}
{%- endfor %}  
"""
    template = Template(template_string)

    for p_id, p in phenotypes.items():
        print(f"Outputting description file for {p_id}")
        output_fullpath = p.description_fullpath
        here = os.path.dirname(output_fullpath)
        rel_path_to_phenotypes_index = os.path.relpath(PHENOTYPES_OUTPUT_INDEX, here)
        rel_path_to_codelists_index = os.path.relpath(CODELISTS_OUTPUT_INDEX, here)

        modified_description = []
        for line in p.raw_description:
            temp = line
            for c in p.codelists_mentioned:
                rel_path_to_codelist_description = os.path.relpath(
                    codelists[c].description_fullpath, here
                )
                temp = re.sub(c, f"[{c}]({rel_path_to_codelist_description})", temp)
            for t in p.templates_mentioned:
                rel_path_to_template_description = os.path.relpath(
                    phenotypes[t].description_fullpath, here
                )
                temp = re.sub(
                    "T:" + t, f"[{t}]({rel_path_to_template_description})", temp
                )
            temp = ("|" + temp).strip()[1:]  # strip trailing newlines
            modified_description.append(temp)
        rendered_template = template.render(
            rel_path_to_phenotypes_index=rel_path_to_phenotypes_index,
            rel_path_to_codelists_index=rel_path_to_codelists_index,
            phenotype=p,
            modified_description=modified_description,
        )
        with open(output_fullpath, "w") as ofh:
            ofh.write(rendered_template)


def create_codelist_output_description_files(codelists=None):
    template_string = """
[Back to Phenotype Index]({{ rel_path_to_phenotypes_index }})

[Back to Codelist Index]({{ rel_path_to_codelists_index }})

## RSC Codelist: {{ codelist.id }}

[Codelist Logical Definition]({{ rel_path_to_logical_definition }})

[Codelist Expansion]({{ rel_path_to_expansion }})

{%- for line in modified_description %}
{{ line }}
{%- endfor %}  

"""
    template = Template(template_string)

    for c_id, c in codelists.items():
        output_fullpath = c.description_fullpath
        here = os.path.dirname(output_fullpath)
        rel_path_to_phenotypes_index = os.path.relpath(PHENOTYPES_OUTPUT_INDEX, here)
        rel_path_to_codelists_index = os.path.relpath(CODELISTS_OUTPUT_INDEX, here)
        rel_path_to_logical_definition = os.path.relpath(
            c.logical_definition_fullpath, here
        )
        rel_path_to_expansion = os.path.relpath(c.expansion_fullpath, here)
        modified_description = []
        for line in c.raw_description:
            temp = ("|" + line).strip()[1:]  # strip trailing newlines
            modified_description.append(temp)
        rendered_template = template.render(
            rel_path_to_phenotypes_index=rel_path_to_phenotypes_index,
            rel_path_to_codelists_index=rel_path_to_codelists_index,
            rel_path_to_logical_definition=rel_path_to_logical_definition,
            rel_path_to_expansion=rel_path_to_expansion,
            codelist=c,
            modified_description=modified_description,
        )
        with open(output_fullpath, "w") as ofh:
            ofh.write(rendered_template)


def create_codelist_output_logical_definition_files(codelists=None):

    template_string = """
[Back to Phenotype Index]({{ rel_path_to_phenotypes_index }})

[Back to Codelist Index]({{ rel_path_to_codelists_index }})

## RSC Codelist: {{ codelist.id }}

# Title: {{ codelist.title }}

[Codelist Description]({{ rel_path_to_description }})

[Codelist Expansion]({{ rel_path_to_expansion }})

# LOGICAL_DEFINITION

## Include

| SNOMED ID | Plus descendants | Term | 
|----|-------|----|
{%- for item in includes_sorted %} 
| [{{ item["concept_id"]}}](https://termbrowser.nhs.uk/?perspective=full&conceptId1={{ item["concept_id"] }}&edition=uk-edition&server=https://termbrowser.nhs.uk/sct-browser-api/snomed&langRefset=999001261000000100,999000691000001104) | {{ item["include_desc"] }} | {{ item["term"] }} |
{%- endfor %}

## Exclude

{% if codelist.logical_definition["excludes"] %}
| SNOMED ID | Plus descendants | Term | 
|----|-------|----|
{%- for item in excludes_sorted %} 
| [{{ item["concept_id"]}}](https://termbrowser.nhs.uk/?perspective=full&conceptId1={{ item["concept_id"] }}&edition=uk-edition&server=https://termbrowser.nhs.uk/sct-browser-api/snomed&langRefset=999001261000000100,999000691000001104) | {{ item["include_desc"] }} | {{ item["term"] }} |
{%- endfor %}
{% else %}
No exclusions
{% endif %}


"""
    template = Template(template_string)

    for c_id, c in codelists.items():
        output_fullpath = c.logical_definition_fullpath
        here = os.path.dirname(output_fullpath)
        rel_path_to_phenotypes_index = os.path.relpath(PHENOTYPES_OUTPUT_INDEX, here)
        rel_path_to_codelists_index = os.path.relpath(CODELISTS_OUTPUT_INDEX, here)
        rel_path_to_description = os.path.relpath(c.description_fullpath, here)
        rel_path_to_expansion = os.path.relpath(c.expansion_fullpath, here)
        includes_sorted=sorted(c.logical_definition["includes"], key=lambda item: item["term"])
        excludes_sorted=sorted(c.logical_definition["excludes"], key=lambda item: item["term"])
        rendered_template = template.render(
            rel_path_to_phenotypes_index=rel_path_to_phenotypes_index,
            rel_path_to_codelists_index=rel_path_to_codelists_index,
            rel_path_to_description=rel_path_to_description,
            rel_path_to_expansion=rel_path_to_expansion,
            codelist=c,
            includes_sorted=includes_sorted,
            excludes_sorted=excludes_sorted,
        )
        with open(output_fullpath, "w") as ofh:
            ofh.write(rendered_template)


def create_codelist_output_expansion_files(codelists=None):

    template_string = """
[Back to Phenotype Index]({{ rel_path_to_phenotypes_index }})

[Back to Codelist Index]({{ rel_path_to_codelists_index }})

## RSC Codelist: {{ codelist.id }}

# Title: {{ codelist.title }}

[Codelist Description]({{ rel_path_to_description }})

[Codelist Logical Definition]({{ rel_path_to_logical_definition }})

# EXPANSION

| SNOMED ID | Term | 
|----|-------|
{%- for item in expansion_sorted %} 
| [{{ item["concept_id"]}}](https://termbrowser.nhs.uk/?perspective=full&conceptId1={{ item["concept_id"] }}&edition=uk-edition&server=https://termbrowser.nhs.uk/sct-browser-api/snomed&langRefset=999001261000000100,999000691000001104) | {{ item["term"] }} |
{%- endfor %}

"""
    template = Template(template_string)

    for c_id, c in codelists.items():
        output_fullpath = c.expansion_fullpath
        here = os.path.dirname(output_fullpath)
        rel_path_to_phenotypes_index = os.path.relpath(PHENOTYPES_OUTPUT_INDEX, here)
        rel_path_to_codelists_index = os.path.relpath(CODELISTS_OUTPUT_INDEX, here)
        rel_path_to_description = os.path.relpath(c.description_fullpath, here)
        rel_path_to_logical_definition = os.path.relpath(
            c.logical_definition_fullpath, here
        )
        expansion_sorted=sorted(c.expansion, key=lambda item: item["term"])
        rendered_template = template.render(
            rel_path_to_phenotypes_index=rel_path_to_phenotypes_index,
            rel_path_to_codelists_index=rel_path_to_codelists_index,
            rel_path_to_description=rel_path_to_description,
            rel_path_to_logical_definition=rel_path_to_logical_definition,
            codelist=c,
            expansion_sorted=expansion_sorted,
        )
        with open(output_fullpath, "w") as ofh:
            ofh.write(rendered_template)
