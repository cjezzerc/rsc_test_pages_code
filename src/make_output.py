import os.path, re, shutil, datetime

import openpyxl
from jinja2 import Template
from jinja2 import Environment, FileSystemLoader
import markdown
import git

from config_locations_etc import *
from timestamp import timestamp

from read_and_parse import parse_text_for_codelist_usage, parse_text_for_phenotype_usage

TERMBROWSER_CONCEPT_URL = (
    "https://termbrowser.nhs.uk/?perspective=full&conceptId1={concept_id}"
    "&edition=uk-edition&server=https://termbrowser.nhs.uk/sct-browser-api/snomed"
    "&langRefset=999001261000000100,999000691000001104"
)

renderer_repo = git.Repo(search_parent_directories=True)
renderer_sha = renderer_repo.head.object.hexsha[:7]
if renderer_repo.is_dirty():
    renderer_sha = "dirty-" + renderer_sha
# AUTHORING
authoring_repo = git.Repo(AUTHORING)
authoring_sha = authoring_repo.head.object.hexsha[:7]
if authoring_repo.is_dirty():
    authoring_sha = "dirty-" + authoring_sha

build_info = {
    "timestamp": timestamp,
    "renderer": renderer_sha,
    "authoring": authoring_sha,
}


def make_clean_output_staging_root_dir():
    # remove all old files and subfolders not touching ".git"
    for fullpath in [PHENOTYPES_OUTPUT_DESCRIPTIONS_DIR, CODELISTS_OUTPUT_DESCRIPTIONS_DIR, CODELISTS_OUTPUT_FOR_DOWNLOAD_DIR, DOCS_OUTPUT_DIR]:
        if os.path.exists(fullpath):
            shutil.rmtree(fullpath)
    for fullpath in [PHENOTYPES_OUTPUT_INDEX, CODELISTS_OUTPUT_INDEX, DOCS_OUTPUT_INDEX]:
        if os.path.exists(fullpath):
            os.remove(fullpath)
    os.makedirs(f"{OUTPUT_STAGING_ROOT_DIR}", exist_ok=True)
    for fullpath in [PHENOTYPES_OUTPUT_DESCRIPTIONS_DIR, CODELISTS_OUTPUT_DESCRIPTIONS_DIR, CODELISTS_OUTPUT_FOR_DOWNLOAD_DIR, DOCS_OUTPUT_DIR]:
        os.makedirs(fullpath)


def copy_shared_banner_images():
    source_images_dir = os.path.normpath(
        os.path.join(os.path.dirname(__file__), "..", "images")
    )
    target_images_dir = os.path.join(OUTPUT_STAGING_ROOT_DIR, "images")
    os.makedirs(target_images_dir, exist_ok=True)

    for image_name in [RSC_IMAGE_FILENAME]:
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


def copy_READMEmd():
    source_READMEmd_path = os.path.normpath(
        os.path.join(os.path.dirname(__file__), "static", "README.md")
    )
    target_READMEmd_dir = os.path.join(OUTPUT_STAGING_ROOT_DIR)
    target_READMEmd_path = os.path.join(target_READMEmd_dir, "README.md")

    if not os.path.exists(source_READMEmd_path):
        raise FileNotFoundError(f"Required file not found: README.md")

    shutil.copy2(source_READMEmd_path, target_READMEmd_path)


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


def create_docs_output_files(phenotypes=None, codelists=None):
    print("Creating help docs pages")

    docs_pages = [
        {
            "slug": "index",
            "source_filename": "index.md",
            "output_filename": "index.html",
            "section_title": "Overview",
            "page_title": "Help: Introduction",
        },
        {
            "slug": "phenotypes",
            "source_filename": "phenotypes.md",
            "output_filename": "phenotypes.html",
            "section_title": "Phenotypes",
            "page_title": "Help: Phenotypes",
        },
        {
            "slug": "codelists",
            "source_filename": "codelists.md",
            "output_filename": "codelists.html",
            "section_title": "Codelists",
            "page_title": "Help: Codelists",
        },
        {
            "slug": "weekly_report",
            "source_filename": "weekly_report.md",
            "output_filename": "weekly_report.html",
            "section_title": "Weekly Report",
            "page_title": "Help: Weekly Report",
        },
        {
            "slug": "data_visualisations",
            "source_filename": "data_visualisations.md",
            "output_filename": "data_visualisations.html",
            "section_title": "Data Visualisations",
            "page_title": "Help: Data Visualisations",
        },
    ]

    jinja_environment = Environment(loader=FileSystemLoader("templates/"))
    template = jinja_environment.get_template("help_page.html")

    output_path_by_slug = {
        page["slug"]: os.path.join(DOCS_OUTPUT_DIR, page["output_filename"])
        for page in docs_pages
    }

    for page in docs_pages:
        source_path = os.path.join(DOCS_DIR, page["source_filename"])
        output_fullpath = output_path_by_slug[page["slug"]]
        here = os.path.dirname(output_fullpath)

        if os.path.isfile(source_path):
            with open(source_path, "r", encoding="utf-8") as fh:
                markdown_text = fh.read()
        else:
            markdown_text = (
                f"# Missing help document\n\n"
                f"Expected file: {page['source_filename']} in authoring docs folder."
            )

        markdown_text = re.sub(r"\.md([)#])", r".html\1", markdown_text)

        # print(parse_text_for_codelist_usage(markdown_text.split('\n')))
        for c in parse_text_for_codelist_usage([markdown_text]):
            rel_path_to_codelist_description = os.path.relpath(
                codelists[c].description_fullpath, here
            )
            hyperlink = f"<a href='{rel_path_to_codelist_description}'>{c} ({codelists[c].title})</a>"
            markdown_text=re.sub(c, hyperlink, markdown_text)

        for p in parse_text_for_phenotype_usage([markdown_text]):
            rel_path_to_phenotype_description = os.path.relpath(
                phenotypes[p].description_fullpath, here
            )
            hyperlink = f"<a href='{rel_path_to_phenotype_description}'>{p} ({phenotypes[p].title})</a>"
            markdown_text=re.sub(p, hyperlink, markdown_text)

        # phenotypes_mentioned=parse_text_for_phenotype_usage(markdown_text)
        rendered_body_html = markdown.markdown(
            markdown_text,
            extensions=["tables", "extra", "sane_lists"],
            tab_length=2,
        )
        rendered_body_html = add_bootstrap_table_classes(rendered_body_html)

        rel_path_to_phenotypes_index = os.path.relpath(PHENOTYPES_OUTPUT_INDEX, here)
        rel_path_to_codelists_index = os.path.relpath(CODELISTS_OUTPUT_INDEX, here)
        rel_path_to_help_index = os.path.relpath(DOCS_OUTPUT_INDEX, here)
        rel_path_to_rsc_image = get_rel_path_to_shared_image(RSC_IMAGE_FILENAME, here)
        rel_path_to_shared_css = get_rel_path_to_shared_css(here)

        help_sections = []
        for nav_page in docs_pages:
            help_sections.append(
                {
                    "slug": nav_page["slug"],
                    "title": nav_page["section_title"],
                    "rel_href": os.path.relpath(output_path_by_slug[nav_page["slug"]], here),
                }
            )

        rendered_template = template.render(
            build_info=build_info,
            page_title=page["page_title"],
            current_page=f"help_{page['slug']}",
            current_help_section=page["slug"],
            help_sections=help_sections,
            rendered_body_html=rendered_body_html,
            rel_path_to_help_index=rel_path_to_help_index,
            rel_path_to_phenotypes_index=rel_path_to_phenotypes_index,
            rel_path_to_codelists_index=rel_path_to_codelists_index,
            rel_path_to_rsc_image=rel_path_to_rsc_image,
            rel_path_to_shared_css=rel_path_to_shared_css,
        )

        with open(output_fullpath, "w") as ofh:
            ofh.write(rendered_template)


def create_phenotype_index_markdown_file(phenotypes=None, codelists=None):
   
    print(f"Creating phenotype index")

    jinja_environment = Environment(loader=FileSystemLoader("templates/"))
    template = jinja_environment.get_template("phenotypes_index.html")

    output_fullpath = PHENOTYPES_OUTPUT_INDEX
    here = os.path.dirname(output_fullpath)
    rel_path_to_codelists_index = os.path.relpath(CODELISTS_OUTPUT_INDEX, here)
    rel_path_to_phenotypes_index = os.path.relpath(PHENOTYPES_OUTPUT_INDEX, here)
    rel_path_to_help_index = os.path.relpath(DOCS_OUTPUT_INDEX, here)
    rel_path_to_help_phenotypes = os.path.relpath(os.path.join(DOCS_OUTPUT_DIR, "phenotypes.html"), here)
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
        rel_path_to_help_index=rel_path_to_help_index,
        rel_path_to_help_phenotypes=rel_path_to_help_phenotypes,
        rel_path_to_rsc_image=rel_path_to_rsc_image,
        rel_path_to_shared_css=rel_path_to_shared_css,
    )

    with open(output_fullpath, "w") as ofh:
        ofh.write(rendered_template)


def create_codelist_index_markdown_file(codelists=None, phenotypes=None):
    
    print(f"Creating codelist index")

    jinja_environment = Environment(loader=FileSystemLoader("templates/"))
    template = jinja_environment.get_template("codelists_index.html")

    output_fullpath = CODELISTS_OUTPUT_INDEX
    here = os.path.dirname(output_fullpath)
    rel_path_to_phenotypes_index = os.path.relpath(PHENOTYPES_OUTPUT_INDEX, here)
    rel_path_to_codelists_index = os.path.relpath(CODELISTS_OUTPUT_INDEX, here)
    rel_path_to_help_index = os.path.relpath(DOCS_OUTPUT_INDEX, here)
    rel_path_to_help_codelists = os.path.relpath(os.path.join(DOCS_OUTPUT_DIR, "codelists.html"), here)
    rel_path_to_rsc_image = get_rel_path_to_shared_image(RSC_IMAGE_FILENAME, here)
    rel_path_to_shared_css = get_rel_path_to_shared_css(here)
    phenotype_hyperlinks = {}
    codelist_hyperlinks = {}
    codelist_download_hyperlinks = {}
    for c_id, c in codelists.items():
        rel_path_to_codelist_description = os.path.relpath(c.description_fullpath, here)
        
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
            hyperlink = (
                f"<a href='{rel_path_to_phenotype_description}'>{phenotypes[p].id}</a>"
            )
            hyperlink = re.sub(
                r"\.md", ".html", hyperlink
            )  # temporary fix while md and html mix
            phhl.append(hyperlink)
        phenotype_hyperlinks[c_id] = ", ".join(phhl)
        rel_path_to_download_file = os.path.relpath(
                f"{CODELISTS_OUTPUT_FOR_DOWNLOAD_DIR}/{c_id}.txt",
            here,
        )
        codelist_download_hyperlinks[c_id] = (
            f"<a href='{rel_path_to_download_file}' class='btn btn-sm btn-outline-primary' download>Download</a>"
        )
    c_ids = list(codelists.keys())
    c_ids_sorted = sorted(c_ids, key=lambda c_id: int(c_id[5:]))

    rendered_template = template.render(
        build_info=build_info,
        codelists=codelists,
        c_ids_sorted=c_ids_sorted,
        codelist_hyperlinks=codelist_hyperlinks,
        phenotype_hyperlinks=phenotype_hyperlinks,
        codelist_download_hyperlinks=codelist_download_hyperlinks,
        current_page="codelists_index",
        rel_path_to_codelists_index=rel_path_to_codelists_index,
        rel_path_to_phenotypes_index=rel_path_to_phenotypes_index,
        rel_path_to_help_index=rel_path_to_help_index,
        rel_path_to_help_codelists=rel_path_to_help_codelists,
        rel_path_to_rsc_image=rel_path_to_rsc_image,
        rel_path_to_shared_css=rel_path_to_shared_css,
    )

    with open(output_fullpath, "w") as ofh:
        ofh.write(rendered_template)


def create_phenotype_output_description_files(phenotypes=None, codelists=None):
    jinja_environment = Environment(loader=FileSystemLoader("templates/"))
    template = jinja_environment.get_template("phenotype_description.html")
    print(f"Creating phenotype description files")

    for p_id, p in phenotypes.items():
        # print(f"Outputting description file for {p_id}")
        output_fullpath = p.description_fullpath
        here = os.path.dirname(output_fullpath)
        rel_path_to_phenotypes_index = os.path.relpath(PHENOTYPES_OUTPUT_INDEX, here)
        rel_path_to_codelists_index = os.path.relpath(CODELISTS_OUTPUT_INDEX, here)
        rel_path_to_help_index = os.path.relpath(DOCS_OUTPUT_INDEX, here)
        rel_path_to_help_phenotypes = os.path.relpath(os.path.join(DOCS_OUTPUT_DIR, "phenotypes.html"), here)
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
                hyperlink = f"<a href='{rel_path_to_template_description}'>{t} ({phenotypes[t].title})</a>"
                hyperlink = re.sub(r"\.md", ".html", hyperlink)
                temp = re.sub("T:" + t, hyperlink, temp)
            # temp = (parse_text_for_codelist_usage + temp).strip()[1:]  # strip trailing newlines
            modified_description.append(temp.rstrip())
        rendered_description_html = markdown.markdown(
            "\n".join(modified_description),
            extensions=["tables", "extra", "sane_lists"],
            tab_length=2,
        )  # tab_length=2 means 2 space indentation of bullets recognised; that is what vsc seems to default to
        rendered_description_html = add_bootstrap_table_classes(
            rendered_description_html
        )
        rendered_template = template.render(
            build_info=build_info,
            rel_path_to_phenotypes_index=rel_path_to_phenotypes_index,
            rel_path_to_codelists_index=rel_path_to_codelists_index,
            rel_path_to_help_index=rel_path_to_help_index,
            rel_path_to_help_phenotypes=rel_path_to_help_phenotypes,
            rel_path_to_rsc_image=rel_path_to_rsc_image,
            rel_path_to_shared_css=rel_path_to_shared_css,
            phenotype=p,
            rendered_description_html=rendered_description_html,
        )
        with open(output_fullpath, "w") as ofh:
            ofh.write(rendered_template)


def create_codelist_output_combo_files(codelists=None, snomed_release_identifier=None):
    jinja_environment = Environment(loader=FileSystemLoader("templates/"))
    template = jinja_environment.get_template("codelist_combo.html")

    meds_messages = {
        (
            "All",
            "A",
            "NULL",
        ): "Include medications with any of the following as either their sole active ingredient, or in combination form (with ANY other active ingredient):",
        (
            "All",
            "S",
            "NULL",
        ): "Include medications with any of the following as their sole active ingredient:",
    }
    print(f"Creating codelist description files")

    for c_id, c in codelists.items():
        output_fullpath = c.description_fullpath
        here = os.path.dirname(output_fullpath)
        rel_path_to_phenotypes_index = os.path.relpath(PHENOTYPES_OUTPUT_INDEX, here)
        rel_path_to_codelists_index = os.path.relpath(CODELISTS_OUTPUT_INDEX, here)
        rel_path_to_help_index = os.path.relpath(DOCS_OUTPUT_INDEX, here)
        rel_path_to_help_codelists = os.path.relpath(os.path.join(DOCS_OUTPUT_DIR, "codelists.html"), here)
        rel_path_to_download_file = os.path.relpath(
            f"{CODELISTS_OUTPUT_FOR_DOWNLOAD_DIR}/{c_id}.txt",
            here,
        )
        rel_path_to_rsc_image = get_rel_path_to_shared_image(RSC_IMAGE_FILENAME, here)
        rel_path_to_shared_css = get_rel_path_to_shared_css(here)

        modified_description = []
        for line in c.raw_description:
            # temp = (parse_text_for_codelist_usage + line).strip()[1:]  # strip trailing newlines
            modified_description.append(line.rstrip())
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

        meds_sorted = {}
        meds_logical_definition_available = False
        for details_tuple in c.logical_definition["meds"].keys():
            meds_sorted[details_tuple] = sorted(
                c.logical_definition["meds"][details_tuple],
                key=lambda item: item["term"],
            )
            if meds_sorted[details_tuple] != []:
                meds_logical_definition_available = True

        logical_definition_available = (
            includes_just_concept_sorted
            or includes_plus_descs_sorted
            or excludes_just_concept_sorted
            or excludes_plus_descs_sorted
            or meds_logical_definition_available
        )
        if not logical_definition_available:
            print(f"!!!!! Warning: no logical definition data found for {c_id}:'{c.title}'")
        expansion_sorted = sorted(c.expansion, key=lambda item: item["term"])
        expansion_available = expansion_sorted != []
        if not expansion_available:
            print(f"!!!!! Warning: no expansion data found for {c_id}:'{c.title}'")
        rendered_template = template.render(
            build_info=build_info,
            snomed_release_identifier=snomed_release_identifier,
            rel_path_to_phenotypes_index=rel_path_to_phenotypes_index,
            rel_path_to_codelists_index=rel_path_to_codelists_index,
            rel_path_to_help_index=rel_path_to_help_index,
            rel_path_to_help_codelists=rel_path_to_help_codelists,
            rel_path_to_rsc_image=rel_path_to_rsc_image,
            rel_path_to_shared_css=rel_path_to_shared_css,
            codelist=c,
            rendered_description_html=rendered_description_html,
            includes_just_concept_sorted=includes_just_concept_sorted,
            includes_plus_descs_sorted=includes_plus_descs_sorted,
            excludes_just_concept_sorted=excludes_just_concept_sorted,
            excludes_plus_descs_sorted=excludes_plus_descs_sorted,
            meds_sorted=meds_sorted,
            meds_messages=meds_messages,
            logical_definition_available=logical_definition_available,
            termbrowser_concept_url=TERMBROWSER_CONCEPT_URL,
            expansion_sorted=expansion_sorted,
            expansion_available=expansion_available,
            rel_path_to_download_file=rel_path_to_download_file,
        )
        with open(output_fullpath, "w") as ofh:
            ofh.write(rendered_template)


def create_codelist_download_files(codelists=None):
    for c_id, c in codelists.items():
        output_fullpath = os.path.join(
            CODELISTS_OUTPUT_FOR_DOWNLOAD_DIR,
            f"{c_id}.txt",
        )
        expansion_sorted = sorted(c.expansion, key=lambda item: item["term"])
        with open(output_fullpath, "w", encoding="utf-8", newline="") as ofh:
            ofh.write("concept_id\tterm\n")
            for item in expansion_sorted:
                concept_id = item["concept_id"]
                term = item["term"].replace("\t", " ").replace("\n", " ")
                ofh.write(f"{concept_id}\t{term}\n")

