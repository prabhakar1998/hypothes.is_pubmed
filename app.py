from flask import Flask, render_template, request
import xlrd
import json
import xlwt
import inflect
from xlrd import open_workbook
from xlutils.copy import copy

app = Flask(__name__)



def get_data_from_excel(sheet, start_row, n_col, nrows, rows_limit=15):
    rows = []
    row_end = start_row + rows_limit
    if row_end > nrows:
        row_end = nrows
    row_index = start_row
    while True:
        if row_index >= nrows:
            break
        if rows_limit <= 0:
            break
        if sheet.cell(row_index, 1).value == "":
            row = [sheet.cell(row_index, col).value for col in range(0, n_col)]
            rows.append(row)
            rows_limit -= 1
        row_index += 1
    return rows


@app.route('/get_comments', methods=['GET'])
def get_comments():
    if request.method == 'GET':
        workbook = xlrd.open_workbook('comments.xlsx')
        worksheet = workbook.sheet_by_name('PubMedCommonsArchive')
        nrows = worksheet.nrows
        ncols = worksheet.ncols
        # GET parameters
        start_row=1
        rows_limit=15
        print(request.args)
        start_row = int(request.args.get("start_row"))
        rows_limit = int(request.args.get("rows_limit"))
        rows = get_data_from_excel(worksheet, start_row, ncols, nrows, rows_limit)
        return json.dumps(rows)


@app.route('/update_excel', methods=['GET'])
def update_excel():
    if request.method == 'GET':
        # GET parameters
        inflect_object = inflect.engine()
        rb = open_workbook("comments.xlsx")
        wb = copy(rb)
        print(request.args)
        index = int(request.args.get("index"))
        comment_type = int(request.args.get("comment_type"))
        sheet_write = wb.get_sheet(0)
        sheet_write.write(index, 1, comment_type)
        wb.save('comments.xlsx')
        return json.dumps({'sucess': 1})


@app.route('/')
def hello():
    return render_template('index.html')

if __name__ == '__main__':
    app.run()
