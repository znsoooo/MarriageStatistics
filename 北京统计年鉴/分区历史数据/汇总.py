import os
from win32com.client import Dispatch

cwd = os.getcwd()
for file in os.listdir('.'):
    data = []
    if file.endswith('.xls'):
        xlApp = Dispatch("Excel.Application")
        xlwb = xlApp.Workbooks.Open(os.path.join(cwd, file))
        sheet_data = xlwb.Worksheets(1).UsedRange.Value
        line = sheet_data[0][0].split()
        for row in sheet_data[2:20]:
            line.append(str(row[8]))
    data.append(data)
    print('\t'.join(line))


