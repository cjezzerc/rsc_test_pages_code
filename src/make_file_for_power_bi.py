import openpyxl

from config_locations_etc import *
from timestamp import timestamp


DIM_PHENOTYPES_COLUMN_WIDTHS = {
    "A": 22,
    "B": 60,
    "C": 80,
}

DIM_PHENOTYPE_DISEASE_CODELIST_COLUMN_WIDTHS = {
    "A": 22,
    "B": 26,
}


def make_file_for_power_bi(phenotypes=None):
    wb=openpyxl.Workbook()
    
    ws=wb.worksheets[0]
    ws.title='DIM_Phenotypes'
    ws.append(["Phenotype ID", "Phenotype Title", "Phenotype Description"])
    for p_id, p in phenotypes.items():
        ws.append([p_id, p.title, p.brief_description])
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
