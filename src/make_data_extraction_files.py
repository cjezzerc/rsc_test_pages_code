import openpyxl

from config_locations_etc import *
from timestamp import timestamp


Table1_column_widths = {
    "A": 22,
    "B": 60,
    "C": 22,
    "D": 22,
}

Table2_column_widths = {
    "A": 22,
    "B": 60,
    "C": 26,
    "D": 60,
    "E": 26,
}

def make_data_extraction_files(phenotypes=None, codelists=None):

    print("WARNING - in data extraction files assume all intervals are 28 days")
    wb=openpyxl.Workbook()
    
    ws=wb.worksheets[0]
    ws.title='Table_1'
    ws.append(["PhenotypeID", "Title", "Flavour","Interval"])
    for p_id, p in phenotypes.items():
        if p.flavour=="Acute":
            interval=28
        else:
            interval=""
        if p.flavour!="Template":
            ws.append([p_id, p.title, p.flavour, interval])
    for col, width in Table1_column_widths.items():
        ws.column_dimensions[col].width = width

    wb.create_sheet()
    ws=wb.worksheets[1]
    
    ws.title='Table_2'
    ws.append(["PhenotypeID", "PhenotypeTitle", "CodelistID", "CodelistTitle", "Category"])
    for p_id, p in phenotypes.items():
        for c_id in p.codelists_mentioned:
            ws.append([p_id, p.title, c_id, codelists[c_id].title,"??"])
    for col, width in Table2_column_widths.items():
        ws.column_dimensions[col].width = width

    filename=f"phenotype_data_for_data_extraction_{timestamp}.xlsx"
    wb.save(DATA_EXTRACTION_FILES_DIR + filename)
    print("Wrote workbook:", filename)
