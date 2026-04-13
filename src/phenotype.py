from read_write_and_parse import (
    parse_description_for_title,
    parse_description_for_brief_description,
    parse_phenotype_description_for_codelist_usage,
    parse_phenotype_description_for_template_phenotype_usage,
    parse_phenotype_description_for_is_template_status,
)

from config_locations_etc import *

class Phenotype:
    __slots__ = [
        "id",
        "raw_description",
        "title",
        "brief_description",
        "codelists_mentioned",
        "templates_mentioned",
        "is_template",
        "description_fullpath",
    ]

    def __init__(self, phenotype_id=None, phenotype_raw_description=None):
        self.id = phenotype_id
        self.raw_description = phenotype_raw_description

        self.title = parse_description_for_title(
            description=phenotype_raw_description
        )

        self.brief_description = parse_description_for_brief_description(
            description=phenotype_raw_description
        )

        self.is_template = parse_phenotype_description_for_is_template_status(
            phenotype_description=phenotype_raw_description
        )

        self.codelists_mentioned = parse_phenotype_description_for_codelist_usage(
            phenotype_description=phenotype_raw_description
        )

        self.templates_mentioned = parse_phenotype_description_for_template_phenotype_usage(
            phenotype_description=phenotype_raw_description
        )


        self.description_fullpath=PHENOTYPES_OUTPUT_DESCRIPTIONS_DIR + f"{self.id}.md"

    def __to_dict__(self):
        return {
            x: self.__getattribute__(x)
            for x in [
                "id",
                "title",
                "brief_description",
                "codelists_mentioned",
                "is_template",
            ]
        }

    def __repr__(self):
        repr_strings = []
        repr_strings.append(f"Phenotype")
        repr_strings.append(f"=========")
        for x in [
            "id",
            "title",
            "brief_description",
            "codelists_mentioned",
            "is_template",
        ]:
            repr_strings.append(f"{x}: {self.__getattribute__(x)}")
        return "\n" + "\n".join(repr_strings) + "\n"
