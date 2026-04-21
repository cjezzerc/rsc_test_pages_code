import re

from read_and_parse import (
    parse_description_for_title,
    parse_description_for_brief_description,
)

from config_locations_etc import *


class Codelist:
    __slots__ = [
        "id",
        "id_for_sorting",
        "raw_description",
        "title",
        "phenotypes_used_in",
        "brief_description",
        "logical_definition",
        "expansion",
        "description_fullpath",
        "logical_definition_fullpath",
        "expansion_fullpath",
    ]

    def __init__(self, codelist_id=None, codelist_raw_description=None):
        self.id = codelist_id
        self.id_for_sorting = int(re.sub(r'RSC-C','',self.id))
        self.raw_description = codelist_raw_description

        self.title = "No title available"
        self.brief_description = "No brief description available"
        self.phenotypes_used_in = []
        self.expansion = []
        self.logical_definition = {
            "includes_plus_descs": [],
            "includes_just_concept": [],
            "excludes_plus_descs": [],
            "excludes_just_concept": [],
        }
        self.description_fullpath = CODELISTS_OUTPUT_DESCRIPTIONS_DIR + f"{self.id}.html"
        self.logical_definition_fullpath = (
            CODELISTS_OUTPUT_LOGICAL_DEFINITIONS_DIR + f"{self.id}_ld.html"
        )
        self.expansion_fullpath = CODELISTS_OUTPUT_EXPANSIONS_DIR + f"{self.id}_exp.html"

        self.title = parse_description_for_title(description=codelist_raw_description)

        self.brief_description = parse_description_for_brief_description(
            description=codelist_raw_description
        )

    def __repr__(self):
        repr_strings = []
        repr_strings.append(f"Codelist")
        repr_strings.append(f"=========")
        for x in ["id", "title", "brief_description", "phenotypes_used_in"]:
            repr_strings.append(f"{x}: {self.__getattribute__(x)}")
        return "\n" + "\n".join(repr_strings) + "\n"
