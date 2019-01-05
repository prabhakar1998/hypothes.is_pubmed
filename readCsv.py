# -*- coding: utf-8 -*-
from pprint import pprint
import xlrd
import MySQLdb
conn = MySQLdb.connect("localhost", "bhanu", "bhanujha", "comments")
cur = conn.cursor()

def store_rows_in_db(document_name):
    pass

def get_data_from_excel(sheet, start_row, n_col):
    rows = []
    row_end = start_row + 50
    if row_end > nrows:
        row_end = nrows
    for row_index in range(start_row, row_end):
        row = [worksheet.cell(row_index, col).value for col in range(0, n_col)]
        """
        ROW DATA: "Index", "Comment Type", "Research Paper DOI", "Source Url", "Source PMID", "Author", "Date of comment", "Comment"

        CREATE TABLE comments(
                  comment_id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
                  doi CHARACTER(150),
                  comment_type INT,
                  pmid CHARACTER(250) NOT NULL,
                  source_url CHARACTER(250),
                  author_name CHARACTER(250),
                  date_comment CHARACTER(250)  NOT NULL,
                  comment_text TEXT(500)
            );

        """
        print(row[7].decode('ascii', 'ignore').replace("'", "\'").replace('“','"').replace('”','"'))
        sql= "INSERT INTO comments  (comment_id, comment_type, doi, source_url, pmid, author_name, date_comment, comment_text) VALUES(%d, %d, %s, %s, %s, %s, %s, %s)"%(int(row[0]), int(0), MySQLdb.escape_string(row[2].replace("'", "`").encode('utf-8')), MySQLdb.escape_string(row[3].replace("'", "`").encode('utf-8')), MySQLdb.escape_string(row[4].replace("'", "`").encode('utf-8')), MySQLdb.escape_string(row[5].replace("'", "`").encode('utf-8')), MySQLdb.escape_string(row[6].replace("'", "`").encode('utf-8')),row[7].replace("'", "\'").replace('“','"').replace('”','"').decode('ascii', 'ignore'))
        conn.commit()
        print(sql)
        cur.execute(sql)
        rows.append(row)
    return rows


workbook = xlrd.open_workbook('PubMedCommonsArchiveWithSentiments2.xlsx')
worksheet = workbook.sheet_by_name('PubMedCommonsArchive')
nrows = worksheet.nrows
ncols = worksheet.ncols
start_row = 1
while start_row <= nrows:
    rows = get_data_from_excel(worksheet, start_row, ncols)
    store_rows_in_db(rows)
    start_row += 50
    break
pprint(rows[-1])
conn.close()