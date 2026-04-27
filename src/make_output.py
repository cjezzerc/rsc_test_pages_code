import os.path, re, shutil, datetime

import openpyxl
from jinja2 import Template
from jinja2 import Environment, FileSystemLoader
import markdown
import git

from config_locations_etc import *
from timestamp import timestamp



TERMBROWSER_CONCEPT_URL = (
    "https://termbrowser.nhs.uk/?perspective=full&conceptId1={concept_id}"
    "&edition=uk-edition&server=https://termbrowser.nhs.uk/sct-browser-api/snomed"
    "&langRefset=999001261000000100,999000691000001104"
)

ORCHID_BANNER_FILENAME = "orchid_banner.png"
RSC_IMAGE_FILENAME = "rsc_image.png"
SHARED_CSS_FILENAME = "shared.css"

renderer_repo = git.Repo(search_parent_directories=True)
renderer_sha = renderer_repo.head.object.hexsha[:7]
if renderer_repo.is_dirty():
    renderer_sha="dirty-"+renderer_sha
# AUTHORING
authoring_repo = git.Repo(AUTHORING)
authoring_sha = authoring_repo.head.object.hexsha[:7]
if authoring_repo.is_dirty():
    authoring_sha="dirty-"+authoring_sha

build_info={"timestamp":timestamp, "renderer":renderer_sha, "authoring":authoring_sha}


def copy_shared_banner_images():
    source_images_dir = os.path.normpath(
        os.path.join(os.path.dirname(__file__), "..", "images")
    )
    target_images_dir = os.path.join(OUTPUT_STAGING_ROOT_DIR, "images")
    os.makedirs(target_images_dir, exist_ok=True)

    for image_name in (ORCHID_BANNER_FILENAME, RSC_IMAGE_FILENAME):
        source_path = os.path.join(source_images_dir, image_name)
        target_path = os.path.join(target_images_dir, image_name)
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"Required banner image not found: {source_path}")
        shutil.copy2(source_path, target_path)


def copy_shared_stylesheet():
    source_css_path = os.path.normpath(
        os.path.join(os.path.dirname(__file__), "static", SHARED_CSS_FILENAME)
    )
    target_css_dir = os.path.join(OUTPUT_STAGING_ROOT_DIR, "assets", "css")
    target_css_path = os.path.join(target_css_dir, SHARED_CSS_FILENAME)
    os.makedirs(target_css_dir, exist_ok=True)

    if not os.path.exists(source_css_path):
        raise FileNotFoundError(f"Required stylesheet not found: {source_css_path}")

    shutil.copy2(source_css_path, target_css_path)


def get_rel_path_to_shared_css(here):
    return os.path.relpath(
        os.path.join(OUTPUT_STAGING_ROOT_DIR, "assets", "css", SHARED_CSS_FILENAME),
        here,
    )


def get_rel_path_to_shared_image(image_name, here):
    return os.path.relpath(
        os.path.join(OUTPUT_STAGING_ROOT_DIR, "images", image_name),
        here,
    )


def add_bootstrap_table_classes(html_fragment):
    # table_classes = "table table-striped table-bordered table-sm"
    table_classes = "table table-bordered table-sm"

    def _inject(match):
        attrs = match.group(1) or ""
        class_match = re.search(r'class=["\']([^"\']*)["\']', attrs)

        if class_match:
            existing = class_match.group(1).strip().split()
            for cls in table_classes.split():
                if cls not in existing:
                    existing.append(cls)
            new_class_attr = f'class="{' '.join(existing)}"'
            attrs = re.sub(
                r'class=["\'][^"\']*["\']',
                new_class_attr,
                attrs,
                count=1,
            )
            return f"<table{attrs}>"

        return f'<table{attrs} class="{table_classes}">'

    return re.sub(r"<table([^>]*)>", _inject, html_fragment)


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
    rel_path_to_phenotypes_index = os.path.relpath(PHENOTYPES_OUTPUT_INDEX, here)
    rel_path_to_orchid_banner = get_rel_path_to_shared_image(
        ORCHID_BANNER_FILENAME, here
    )
    rel_path_to_rsc_image = get_rel_path_to_shared_image(RSC_IMAGE_FILENAME, here)
    rel_path_to_shared_css = get_rel_path_to_shared_css(here)
    phenotype_hyperlinks = {}
    codelist_hyperlinks = {}
    template_hyperlinks = {}
    for p_id, p in phenotypes.items():
        rel_path_to_phenotype_description = os.path.relpath(
            p.description_fullpath, here
        )
        # phenotype_hyperlinks[p_id] = f"[{p_id}]({rel_path_to_phenotype_description})"
        hyperlink = f"<a href='{rel_path_to_phenotype_description}'>{p_id}</a>"
        hyperlink = re.sub(
            r"\.md", ".html", hyperlink
        )  # temporary fix while md and html mix
        phenotype_hyperlinks[p_id] = hyperlink
        chl = []
        for c in p.codelists_mentioned:
            rel_path_to_codelist_description = os.path.relpath(
                codelists[c].description_fullpath,
                here,
            )
            # chl.append(f"[{c}]({rel_path_to_codelist_description})")
            hyperlink = f"<a href='{rel_path_to_codelist_description}'>{c}</a>"
            hyperlink = re.sub(
                r"\.md", ".html", hyperlink
            )  # temporary fix while md and html mix
            chl.append(hyperlink)
        codelist_hyperlinks[p_id] = ", ".join(chl)
        thl = []
        for t in p.templates_mentioned:
            rel_path_to_template_description = os.path.relpath(
                phenotypes[t].description_fullpath, here
            )
            # thl.append(f"[{t}]({rel_path_to_template_description})")
            hyperlink = f"<a href='{rel_path_to_template_description}'>{t}</a>"
            hyperlink = re.sub(
                r"\.md", ".html", hyperlink
            )  # temporary fix while md and html mix
            thl.append(hyperlink)
        template_hyperlinks[p_id] = ", ".join(thl)
    p_ids = list(phenotypes.keys())
    p_ids_sorted = sorted(p_ids, key=lambda p_id: int(p_id[6:]))

    rendered_template = template.render(
        build_info=build_info,
        phenotypes=phenotypes,
        p_ids_sorted=p_ids_sorted,
        codelist_hyperlinks=codelist_hyperlinks,
        phenotype_hyperlinks=phenotype_hyperlinks,
        template_hyperlinks=template_hyperlinks,
        current_page="phenotypes_index",
        rel_path_to_phenotypes_index=rel_path_to_phenotypes_index,
        rel_path_to_codelists_index=rel_path_to_codelists_index,
        rel_path_to_orchid_banner=rel_path_to_orchid_banner,
        rel_path_to_rsc_image=rel_path_to_rsc_image,
        rel_path_to_shared_css=rel_path_to_shared_css,
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
    rel_path_to_codelists_index = os.path.relpath(CODELISTS_OUTPUT_INDEX, here)
    rel_path_to_orchid_banner = get_rel_path_to_shared_image(
        ORCHID_BANNER_FILENAME, here
    )
    rel_path_to_rsc_image = get_rel_path_to_shared_image(RSC_IMAGE_FILENAME, here)
    rel_path_to_shared_css = get_rel_path_to_shared_css(here)
    phenotype_hyperlinks = {}
    codelist_hyperlinks = {}
    for c_id, c in codelists.items():
        rel_path_to_codelist_description = os.path.relpath(c.description_fullpath, here)
        # codelist_hyperlinks[c_id] = f"[{c_id}]({rel_path_to_codelist_description})"
        # hyperlink = f"[{c_id}]({rel_path_to_codelist_description})"
        hyperlink = f"<a href='{rel_path_to_codelist_description}'>{c_id}</a>"
        hyperlink = re.sub(
            r"\.md", ".html", hyperlink
        )  # temporary fix while md and html mix
        codelist_hyperlinks[c_id] = hyperlink
        phhl = []
        for p in c.phenotypes_used_in:
            rel_path_to_phenotype_description = os.path.relpath(
                phenotypes[p].description_fullpath,
                here,
            )
            # phhl.append(f"[{p}]({rel_path_to_phenotype_description})")
            # hyperlink=f"[{p}]({rel_path_to_phenotype_description})"
            hyperlink = (
                f"<a href='{rel_path_to_phenotype_description}'>{phenotypes[p].id}</a>"
            )
            hyperlink = re.sub(
                r"\.md", ".html", hyperlink
            )  # temporary fix while md and html mix
            phhl.append(hyperlink)
        phenotype_hyperlinks[c_id] = ", ".join(phhl)
    c_ids = list(codelists.keys())
    c_ids_sorted = sorted(c_ids, key=lambda c_id: int(c_id[5:]))

    rendered_template = template.render(
        build_info=build_info,
        codelists=codelists,
        c_ids_sorted=c_ids_sorted,
        codelist_hyperlinks=codelist_hyperlinks,
        phenotype_hyperlinks=phenotype_hyperlinks,
        current_page="codelists_index",
        rel_path_to_codelists_index=rel_path_to_codelists_index,
        rel_path_to_phenotypes_index=rel_path_to_phenotypes_index,
        rel_path_to_orchid_banner=rel_path_to_orchid_banner,
        rel_path_to_rsc_image=rel_path_to_rsc_image,
        rel_path_to_shared_css=rel_path_to_shared_css,
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
        rel_path_to_orchid_banner = get_rel_path_to_shared_image(
            ORCHID_BANNER_FILENAME, here
        )
        rel_path_to_rsc_image = get_rel_path_to_shared_image(RSC_IMAGE_FILENAME, here)
        rel_path_to_shared_css = get_rel_path_to_shared_css(here)

        modified_description = []
        for line in p.raw_description:
            temp = line
            for c in p.codelists_mentioned:
                rel_path_to_codelist_description = os.path.relpath(
                    codelists[c].description_fullpath, here
                )
                hyperlink = f"<a href='{rel_path_to_codelist_description}'>{c} ({codelists[c].title})</a>"
                hyperlink = re.sub(r"\.md", ".html", hyperlink)
                temp = re.sub(c, hyperlink, temp)
            for t in p.templates_mentioned:
                rel_path_to_template_description = os.path.relpath(
                    phenotypes[t].description_fullpath, here
                )
                hyperlink = f"<a href='{rel_path_to_template_description}'>{t}</a>"
                hyperlink = re.sub(r"\.md", ".html", hyperlink)
                temp = re.sub("T:" + t, hyperlink, temp)
            temp = ("|" + temp).strip()[1:]  # strip trailing newlines
            modified_description.append(temp)
        rendered_description_html = markdown.markdown(
            "\n".join(modified_description), extensions=["tables", "extra", "sane_lists"], tab_length=2
        )  # tab_length=2 means 2 space indentation of bullets recognised; that is what vsc seems to default to
        rendered_description_html = add_bootstrap_table_classes(
            rendered_description_html
        )
        rendered_template = template.render(
            build_info=build_info,
            rel_path_to_phenotypes_index=rel_path_to_phenotypes_index,
            rel_path_to_codelists_index=rel_path_to_codelists_index,
            rel_path_to_orchid_banner=rel_path_to_orchid_banner,
            rel_path_to_rsc_image=rel_path_to_rsc_image,
            rel_path_to_shared_css=rel_path_to_shared_css,
            phenotype=p,
            rendered_description_html=rendered_description_html,
        )
        with open(output_fullpath, "w") as ofh:
            ofh.write(rendered_template)


def create_codelist_output_combo_files(codelists=None):
    jinja_environment = Environment(loader=FileSystemLoader("templates/"))
    template = jinja_environment.get_template("codelist_combo.html")

    for c_id, c in codelists.items():
        output_fullpath = c.description_fullpath
        here = os.path.dirname(output_fullpath)
        rel_path_to_phenotypes_index = os.path.relpath(PHENOTYPES_OUTPUT_INDEX, here)
        rel_path_to_codelists_index = os.path.relpath(CODELISTS_OUTPUT_INDEX, here)
        rel_path_to_orchid_banner = get_rel_path_to_shared_image(
            ORCHID_BANNER_FILENAME, here
        )
        rel_path_to_rsc_image = get_rel_path_to_shared_image(RSC_IMAGE_FILENAME, here)
        rel_path_to_shared_css = get_rel_path_to_shared_css(here)

        modified_description = []
        for line in c.raw_description:
            temp = ("|" + line).strip()[1:]  # strip trailing newlines
            modified_description.append(temp)
        rendered_description_html = markdown.markdown(
            "\n".join(modified_description),
            extensions=["tables", "extra", "sane_lists"],
        )
        rendered_description_html = add_bootstrap_table_classes(
            rendered_description_html
        )
        includes_just_concept_sorted = sorted(
            c.logical_definition["includes_just_concept"], key=lambda item: item["term"]
        )
        includes_plus_descs_sorted = sorted(
            c.logical_definition["includes_plus_descs"], key=lambda item: item["term"]
        )
        excludes_just_concept_sorted = sorted(
            c.logical_definition["excludes_just_concept"], key=lambda item: item["term"]
        )
        excludes_plus_descs_sorted = sorted(
            c.logical_definition["excludes_plus_descs"], key=lambda item: item["term"]
        )
        logical_definition_available = (
            includes_just_concept_sorted
            or includes_plus_descs_sorted
            or excludes_just_concept_sorted
            or excludes_plus_descs_sorted
        )
        if not logical_definition_available:
            print(f"Warning: no logical definition data found for {c_id}")
        expansion_sorted = sorted(c.expansion, key=lambda item: item["term"])
        expansion_available = expansion_sorted != []
        if not expansion_available:
            print(f"Warning: no expansion data found for {c_id}")
        rendered_template = template.render(
            build_info=build_info,
            rel_path_to_phenotypes_index=rel_path_to_phenotypes_index,
            rel_path_to_codelists_index=rel_path_to_codelists_index,
            rel_path_to_orchid_banner=rel_path_to_orchid_banner,
            rel_path_to_rsc_image=rel_path_to_rsc_image,
            rel_path_to_shared_css=rel_path_to_shared_css,
            codelist=c,
            rendered_description_html=rendered_description_html,
            includes_just_concept_sorted=includes_just_concept_sorted,
            includes_plus_descs_sorted=includes_plus_descs_sorted,
            excludes_just_concept_sorted=excludes_just_concept_sorted,
            excludes_plus_descs_sorted=excludes_plus_descs_sorted,
            logical_definition_available=logical_definition_available,
            termbrowser_concept_url=TERMBROWSER_CONCEPT_URL,
            expansion_sorted=expansion_sorted,
            expansion_available=expansion_available,
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
        rel_path_to_orchid_banner = get_rel_path_to_shared_image(
            ORCHID_BANNER_FILENAME, here
        )
        rel_path_to_rsc_image = get_rel_path_to_shared_image(RSC_IMAGE_FILENAME, here)
        rel_path_to_shared_css = get_rel_path_to_shared_css(here)
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
        rendered_description_html = markdown.markdown(
            "\n".join(modified_description),
            extensions=["tables", "extra", "sane_lists"],
        )
        rendered_description_html = add_bootstrap_table_classes(
            rendered_description_html
        )

        rendered_template = template.render(
            build_info=build_info,
            rel_path_to_phenotypes_index=rel_path_to_phenotypes_index,
            rel_path_to_codelists_index=rel_path_to_codelists_index,
            rel_path_to_orchid_banner=rel_path_to_orchid_banner,
            rel_path_to_rsc_image=rel_path_to_rsc_image,
            rel_path_to_shared_css=rel_path_to_shared_css,
            rel_path_to_logical_definition=rel_path_to_logical_definition,
            rel_path_to_expansion=rel_path_to_expansion,
            codelist=c,
            rendered_description_html=rendered_description_html,
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
        rel_path_to_orchid_banner = get_rel_path_to_shared_image(
            ORCHID_BANNER_FILENAME, here
        )
        rel_path_to_rsc_image = get_rel_path_to_shared_image(RSC_IMAGE_FILENAME, here)
        rel_path_to_shared_css = get_rel_path_to_shared_css(here)
        rel_path_to_description = os.path.relpath(c.description_fullpath, here)
        rel_path_to_expansion = os.path.relpath(c.expansion_fullpath, here)
        rel_path_to_description = re.sub(r"\.md$", ".html", rel_path_to_description)
        rel_path_to_expansion = re.sub(r"\.md$", ".html", rel_path_to_expansion)
        includes_just_concept_sorted = sorted(
            c.logical_definition["includes_just_concept"], key=lambda item: item["term"]
        )
        includes_plus_descs_sorted = sorted(
            c.logical_definition["includes_plus_descs"], key=lambda item: item["term"]
        )
        excludes_just_concept_sorted = sorted(
            c.logical_definition["excludes_just_concept"], key=lambda item: item["term"]
        )
        excludes_plus_descs_sorted = sorted(
            c.logical_definition["excludes_plus_descs"], key=lambda item: item["term"]
        )
        rendered_template = template.render(
            build_info=build_info,
            rel_path_to_phenotypes_index=rel_path_to_phenotypes_index,
            rel_path_to_codelists_index=rel_path_to_codelists_index,
            rel_path_to_orchid_banner=rel_path_to_orchid_banner,
            rel_path_to_rsc_image=rel_path_to_rsc_image,
            rel_path_to_shared_css=rel_path_to_shared_css,
            rel_path_to_description=rel_path_to_description,
            rel_path_to_expansion=rel_path_to_expansion,
            termbrowser_concept_url=TERMBROWSER_CONCEPT_URL,
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
        rel_path_to_orchid_banner = get_rel_path_to_shared_image(
            ORCHID_BANNER_FILENAME, here
        )
        rel_path_to_rsc_image = get_rel_path_to_shared_image(RSC_IMAGE_FILENAME, here)
        rel_path_to_shared_css = get_rel_path_to_shared_css(here)
        rel_path_to_description = os.path.relpath(c.description_fullpath, here)
        rel_path_to_logical_definition = os.path.relpath(
            c.logical_definition_fullpath, here
        )
        rel_path_to_description = re.sub(r"\.md$", ".html", rel_path_to_description)
        rel_path_to_logical_definition = re.sub(
            r"\.md$", ".html", rel_path_to_logical_definition
        )
        expansion_sorted = sorted(c.expansion, key=lambda item: item["term"])
        rendered_template = template.render(
            build_info=build_info,
            rel_path_to_phenotypes_index=rel_path_to_phenotypes_index,
            rel_path_to_codelists_index=rel_path_to_codelists_index,
            rel_path_to_orchid_banner=rel_path_to_orchid_banner,
            rel_path_to_rsc_image=rel_path_to_rsc_image,
            rel_path_to_shared_css=rel_path_to_shared_css,
            rel_path_to_description=rel_path_to_description,
            rel_path_to_logical_definition=rel_path_to_logical_definition,
            termbrowser_concept_url=TERMBROWSER_CONCEPT_URL,
            codelist=c,
            expansion_sorted=expansion_sorted,
        )
        with open(output_fullpath, "w") as ofh:
            ofh.write(rendered_template)
