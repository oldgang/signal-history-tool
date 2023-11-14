import pandas as pd

def convert_csv_to_xlsx(filename):
    read_file = pd.read_csv(r'filename')
    filename = filename.split('.')[0]
    filename += .xlsx
    read_file.to_excel(r'filename', index = None, header=True)