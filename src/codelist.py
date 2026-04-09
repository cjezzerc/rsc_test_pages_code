import read_write_and_parse
from config_locations_etc import *


class Codelist:
    __slots__ = [
        "id",
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
        self.raw_description =codelist_raw_description

        self.title="TBI"
        self.brief_description="TBI"
        self.phenotypes_used_in=[]
        self.expansion=[]
        self.logical_definition={"includes":[], "excludes":[]}
        self.description_fullpath=CODELISTS_OUTPUT_DESCRIPTIONS_DIR + f"{self.id}.md"
        self.logical_definition_fullpath=CODELISTS_OUTPUT_LOGICAL_DEFINITIONS_DIR + f"{self.id}_ld.md"
        self.expansion_fullpath=CODELISTS_OUTPUT_EXPANSIONS_DIR + f"{self.id}_exp.md"

        # self.title = read_write_and_parse.parse_codelist_for_title(
        #     codelist_description=codelist_raw_description
        # )

        # self.brief_description = (
        #     read_write_and_parse.parse_codelist_for_brief_description(
        #         codelist_description=codelist_raw_description
        #     )
        # )

    def __repr__(self):
        repr_strings=[]
        repr_strings.append(f"Codelist")
        repr_strings.append(f"=========")
        for x in [
                "id",
                "title",
                "brief_description",
                "phenotypes_used_in"
            ]:
            repr_strings.append(f"{x}: {self.__getattribute__(x)}")
        return "\n"+"\n".join(repr_strings)+"\n"
    
