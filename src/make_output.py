import os.path, re

import openpyxl
from jinja2 import Template
from jinja2 import Environment, FileSystemLoader

from config_locations_etc import *


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
    jinja_environment = Environment(loader=FileSystemLoader("templates/"))
    # template = jinja_environment.get_template("phenotypes_index.md")
    template = jinja_environment.get_template("phenotypes_index.html")
    
    # template = Template(template_string)
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
        # phenotype_hyperlinks[p_id] = f"[{p_id}]({rel_path_to_phenotype_description})"
        hyperlink=f"<a href='{rel_path_to_phenotype_description}'>{p_id}</a>"
        hyperlink=re.sub(r'\.md', '.html', hyperlink) # temporary fix while md and html mix
        phenotype_hyperlinks[p_id] = hyperlink
        chl = []
        for c in p.codelists_mentioned:
            rel_path_to_codelist_description = os.path.relpath(
                codelists[c].description_fullpath,
                here,
            )
            # chl.append(f"[{c}]({rel_path_to_codelist_description})")
            hyperlink=f"<a href='{rel_path_to_codelist_description}'>{c}</a>"
            hyperlink=re.sub(r'\.md', '.html', hyperlink) # temporary fix while md and html mix
            chl.append(hyperlink)
        codelist_hyperlinks[p_id] = ", ".join(chl)
        thl = []
        for t in p.templates_mentioned:
            rel_path_to_template_description = os.path.relpath(
                phenotypes[t].description_fullpath, here
            )
            # thl.append(f"[{t}]({rel_path_to_template_description})")
            hyperlink=f"<a href='{rel_path_to_template_description}'>{t}</a>"
            hyperlink=re.sub(r'\.md', '.html', hyperlink) # temporary fix while md and html mix
            thl.append(hyperlink)
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
    jinja_environment = Environment(loader=FileSystemLoader("templates/"))
    # template = jinja_environment.get_template("phenotypes_index.md")
    template = jinja_environment.get_template("codelists_index.html")
    
    # template = Template(template_string)
    output_fullpath = CODELISTS_OUTPUT_INDEX
    here = os.path.dirname(output_fullpath)
    rel_path_to_phenotypes_index = os.path.relpath(PHENOTYPES_OUTPUT_INDEX, here)
    phenotype_hyperlinks = {}
    codelist_hyperlinks = {}
    for c_id, c in codelists.items():
        rel_path_to_codelist_description = os.path.relpath(c.description_fullpath, here)
        # codelist_hyperlinks[c_id] = f"[{c_id}]({rel_path_to_codelist_description})"
        # hyperlink = f"[{c_id}]({rel_path_to_codelist_description})"
        hyperlink=f"<a href='{rel_path_to_codelist_description}'>{c_id}</a>"
        hyperlink=re.sub(r'\.md', '.html', hyperlink) # temporary fix while md and html mix
        codelist_hyperlinks[c_id] = hyperlink
        phhl = []
        for p in c.phenotypes_used_in:
            rel_path_to_phenotype_description = os.path.relpath(
                phenotypes[p].description_fullpath,
                here,
            )
            # phhl.append(f"[{p}]({rel_path_to_phenotype_description})")
            # hyperlink=f"[{p}]({rel_path_to_phenotype_description})"
            hyperlink=f"<a href='{rel_path_to_phenotype_description}'>{c_id}</a>"
            hyperlink=re.sub(r'\.md', '.html', hyperlink) # temporary fix while md and html mix
            phhl.append(hyperlink)
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
    jinja_environment = Environment(loader=FileSystemLoader("templates/"))
    template = jinja_environment.get_template("phenotype_description.html")

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
                hyperlink = f"<a href='{rel_path_to_codelist_description}'>{c}</a>"
                hyperlink = re.sub(r'\.md', '.html', hyperlink)
                temp = re.sub(c, hyperlink, temp)
            for t in p.templates_mentioned:
                rel_path_to_template_description = os.path.relpath(
                    phenotypes[t].description_fullpath, here
                )
                hyperlink = f"<a href='{rel_path_to_template_description}'>{t}</a>"
                hyperlink = re.sub(r'\.md', '.html', hyperlink)
                temp = re.sub("T:" + t, hyperlink, temp)
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
    jinja_environment = Environment(loader=FileSystemLoader("templates/"))
    template = jinja_environment.get_template("codelist_description.html")

    for c_id, c in codelists.items():
        output_fullpath = c.description_fullpath
        here = os.path.dirname(output_fullpath)
        rel_path_to_phenotypes_index = os.path.relpath(PHENOTYPES_OUTPUT_INDEX, here)
        rel_path_to_codelists_index = os.path.relpath(CODELISTS_OUTPUT_INDEX, here)
        rel_path_to_logical_definition = os.path.relpath(
            c.logical_definition_fullpath, here
        )
        rel_path_to_expansion = os.path.relpath(c.expansion_fullpath, here)
        rel_path_to_logical_definition = re.sub(
            r"\.md$", ".html", rel_path_to_logical_definition
        )
        rel_path_to_expansion = re.sub(r"\.md$", ".html", rel_path_to_expansion)
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
    jinja_environment = Environment(loader=FileSystemLoader("templates/"))
    template = jinja_environment.get_template("codelist_logical_definition.html")

    for c_id, c in codelists.items():
        output_fullpath = c.logical_definition_fullpath
        here = os.path.dirname(output_fullpath)
        rel_path_to_phenotypes_index = os.path.relpath(PHENOTYPES_OUTPUT_INDEX, here)
        rel_path_to_codelists_index = os.path.relpath(CODELISTS_OUTPUT_INDEX, here)
        rel_path_to_description = os.path.relpath(c.description_fullpath, here)
        rel_path_to_expansion = os.path.relpath(c.expansion_fullpath, here)
        rel_path_to_description = re.sub(r"\.md$", ".html", rel_path_to_description)
        rel_path_to_expansion = re.sub(r"\.md$", ".html", rel_path_to_expansion)
        includes_just_concept_sorted=sorted(c.logical_definition["includes_just_concept"], key=lambda item: item["term"])
        includes_plus_descs_sorted=sorted(c.logical_definition["includes_plus_descs"], key=lambda item: item["term"])
        excludes_just_concept_sorted=sorted(c.logical_definition["excludes_just_concept"], key=lambda item: item["term"])
        excludes_plus_descs_sorted=sorted(c.logical_definition["excludes_plus_descs"], key=lambda item: item["term"])
        rendered_template = template.render(
            rel_path_to_phenotypes_index=rel_path_to_phenotypes_index,
            rel_path_to_codelists_index=rel_path_to_codelists_index,
            rel_path_to_description=rel_path_to_description,
            rel_path_to_expansion=rel_path_to_expansion,
            codelist=c,
            includes_just_concept_sorted=includes_just_concept_sorted,
            includes_plus_descs_sorted=includes_plus_descs_sorted,
            excludes_just_concept_sorted=excludes_just_concept_sorted,
            excludes_plus_descs_sorted=excludes_plus_descs_sorted,
        )
        with open(output_fullpath, "w") as ofh:
            ofh.write(rendered_template)


def create_codelist_output_expansion_files(codelists=None):
    jinja_environment = Environment(loader=FileSystemLoader("templates/"))
    template = jinja_environment.get_template("codelist_expansion.html")

    for c_id, c in codelists.items():
        output_fullpath = c.expansion_fullpath
        here = os.path.dirname(output_fullpath)
        rel_path_to_phenotypes_index = os.path.relpath(PHENOTYPES_OUTPUT_INDEX, here)
        rel_path_to_codelists_index = os.path.relpath(CODELISTS_OUTPUT_INDEX, here)
        rel_path_to_description = os.path.relpath(c.description_fullpath, here)
        rel_path_to_logical_definition = os.path.relpath(
            c.logical_definition_fullpath, here
        )
        rel_path_to_description = re.sub(r"\.md$", ".html", rel_path_to_description)
        rel_path_to_logical_definition = re.sub(
            r"\.md$", ".html", rel_path_to_logical_definition
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
