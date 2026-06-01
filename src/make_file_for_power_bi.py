import openpyxl

from config_locations_etc import *
from timestamp import timestamp


DIM_PHENOTYPES_COLUMN_WIDTHS = {
    "A": 22,
    "B": 60,
    "C": 60,
    "D": 60,
}

DIM_PHENOTYPE_DISEASE_CODELIST_COLUMN_WIDTHS = {
    "A": 22,
    "B": 26,
}


def make_file_for_power_bi(phenotypes=None):

    # this is a temporary bodge - copied from the script that makes the synthetic data
    # really want the definition of flavour to go into the .md files for phenotype descriptions
    phenotype_flavours = {
    "RSC-PH2": {"name": "BMI", "flavour": "categorisation"},
    "RSC-PH3": {"name": "Smoking_status", "flavour": "categorisation"},
    "RSC-PH5": {"name": "ILI", "flavour": "incidence"},
    "RSC-PH6": {"name": "TNSPH", "flavour": "incidence"},
    "RSC-PH7": {"name": "OTMED", "flavour": "incidence"},
    "RSC-PH8": {"name": "SINUS", "flavour": "incidence"},
    "RSC-PH9": {"name": "CROUP", "flavour": "incidence"},
    "RSC-PH10": {"name": "LARYNG", "flavour": "incidence"},
    "RSC-PH11": {"name": "BRONCH", "flavour": "incidence"},
    "RSC-PH12": {"name": "BRNIOL", "flavour": "incidence"},
    "RSC-PH13": {"name": "PNEUM", "flavour": "incidence"},
    "RSC-PH14": {"name": "ASTHEX", "flavour": "incidence"},
    "RSC-PH15": {"name": "COPDEX", "flavour": "incidence"},
    "RSC-PH16": {"name": "COVID", "flavour": "incidence"},
    "RSC-PH17": {"name": "LRTI", "flavour": "incidence"},
    "RSC-PH18": {"name": "URTI", "flavour": "incidence"},
    "RSC-PH19": {"name": "ECLD", "flavour": "incidence"},
    "RSC-PH20": {"name": "ARI", "flavour": "incidence"},
    
    "RSC-PH21": {"name": "VARZOS", "flavour": "incidence"},
    "RSC-PH22": {"name": "HERZOS", "flavour": "incidence"},
    "RSC-PH23": {"name": "DEMENT", "flavour": "prevalence"},
    "RSC-PH24": {"name": "COPD", "flavour": "prevalence"},
    
    "RSC-PH25": {"name": "AMOX", "flavour": "drug_admin/presc"},
    "RSC-PH26": {"name": "STATINS", "flavour": "drug_admin/presc"},
    "RSC-PH27": {"name": "RSV-V", "flavour": "drug_admin/presc"},
    
    "RSC-PH28": {"name": "PULSE", "flavour": "measured_item"},
    }

    data_visualisation_descriptions= {
        "incidence":"""This data visualisation shows the total number of cases of this condition recorded in primary care (per 100 000 people) during the entire 2025 calendar year, estimated using records from the RCGP RSC database.

Cases are identified from patient records using coded events that are considered likely to indicate a case of the condition. 
""",
        "prevalence":"""This data visualisation shows the prevalence of this condition on 31st December 2025, estimated using records from the RCGP RSC database for the entire 2025 calendar year.

Cases are identified from patient records using coded events that are considered likely to indicate the presence of the condition.
""",
        "categorisation":"""This data visualisation shows the proportion of people in each category for this categorisation, using records from the RCGP RSC database for the entire 2025 calendar year.

People are assigned to a category where coded entries in their record can be used to determine the relevant status.
""",

        "drug_admin/presc":"""This data visualisation shows the total number of people for whom at least one coded entry indicating a prescription or administration of this drug/vaccine can be found in the RCGP RSC database during the entire 2025 calendar year.
""",
        "measured_item":"""This data visualisation shows the total number of people for whom at least one coded entry indicating measurement of this quantity can be found in the RCGP RSC database during the entire 2025 calendar year. 
"""
    }
    


    wb=openpyxl.Workbook()
    
    ws=wb.worksheets[0]
    ws.title='DIM_Phenotypes'
    ws.append(["Phenotype ID", "Phenotype Title", "Phenotype Description","Data Visualisation Text"])
    for p_id, p in phenotypes.items():
        if p_id in phenotype_flavours:
            data_visualisation_description=data_visualisation_descriptions[phenotype_flavours[p_id]["flavour"]]
        else:
            data_visualisation_description="no-visualisation"
        ws.append([p_id, p.title, p.brief_description, data_visualisation_description])
    for col, width in DIM_PHENOTYPES_COLUMN_WIDTHS.items():
        ws.column_dimensions[col].width = width

    wb.create_sheet()
    ws=wb.worksheets[1]
    
    ws.title='DIM_PhenotypeDiseaseCodelist'
    ws.append(["Phenotype ID", "Disease Codelist ID"])
    for p_id, p in phenotypes.items():
        for c_id in p.codelists_mentioned:
            ws.append([p_id, c_id])
    for col, width in DIM_PHENOTYPE_DISEASE_CODELIST_COLUMN_WIDTHS.items():
        ws.column_dimensions[col].width = width

    filename=f"phenotype_data_for_power_bi_{timestamp}.xlsx"
    wb.save(DATA_FOR_POWER_BI_DIR + filename)
    print("Wrote workbook:", filename)
