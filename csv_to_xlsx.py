import pandas as pd

def convert_csv_to_xlsx(filename):
    read_file = pd.read_csv(filename)
    filename = filename.split('.')[0]
    filename += ".xlsx"
    read_file.to_excel(filename, index = None, header=True)

convert_csv_to_xlsx('output.csv')