# -*- coding: utf-8 -*-
from pprint import pprint
import xlrd
import json
import MySQLdb
conn = MySQLdb.connect("localhost", "bhanu", "bhanujha", "comments")
conn.set_character_set('utf8')
cur = conn.cursor()
global doi_index

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
                          doi_index INT PRIMARY KEY,
                          doi CHARACTER(150),
                          comment_type int,
                          source_url CHARACTER(250),
                          pmid CHARACTER(250),
                          comment_text TEXT(5000)
        );

        comment_text = {
          size: int,
            0: {
              author_name: CHARACTER, 
              date_comment: CHARACTER,
              comment: CHARACTER,
            }
          1: {
              author_name: CHARACTER, 
              date_comment: CHARACTER,
              comment: CHARACTER,
            }
            2: {
              author_name: CHARACTER, 
              date_comment: CHARACTER,
              comment: CHARACTER,
            }
            .
            .
            .
            .

        }

        // logics:
          1. if doi exists:
            (i) get comment_text from db where doi matches
            (ii) json.loads(comment_text)
            (iii) str(size + 1) = new_key
            (iv) now insert the new comments data in dict
            (v) update db!

          2 else
            make new data and insert it!

        """
        global doi_index
        doi = str(row[2].replace("'", "`"))
        source_url = row[3].replace("'", "`")
        pmid = row[4].replace("'", "`").split(":")[1]
        comment_text = row[7].replace("'", "`")
        date_comment = row[6].replace("'", "`")
        author_name = row[5].replace("'", "`")
        comment_details = {}
        comment_details['comment'] = comment_text
        comment_details['date_comment'] = date_comment
        comment_details['author_name'] = author_name
        db_rows = cur.execute("SELECT * FROM comments WHERE doi = %s", (doi,))
        # print(db_rows)
        if db_rows == 0:
            comment_text = {}
            comment_text[0] = comment_details
            comment_text['size'] = 1
            cur.execute("INSERT INTO comments  VALUES (%d, %s, %d, %s, %s, %s);", (doi_index, str(doi), 0, str(source_url), str(pmid), str(json.dumps(comment_text))))
            doi_index += 1
        else:
            print("86")
            comment_data = list(cur.fetchone())
            comment_text = comment_data[-1]
            comment_text = json.loads(comment_text)
            size = comment_text['size']
            comment_text[size] = comment_details
            comment_text['size'] = size + 1
            sql = "UPDATE comments SET comment_text = %s  WHERE doi = %s"
            cur.execute(sql, (json.dumps(comment_text), doi))
        conn.commit()
        rows.append(row)
    return rows

doi_index = 0
workbook = xlrd.open_workbook('comments.xlsx')
worksheet = workbook.sheet_by_name('PubMedCommonsArchive')
nrows = worksheet.nrows
ncols = worksheet.ncols
start_row = 1
while start_row <= nrows:
    print(worksheet, start_row, ncols)
    rows = get_data_from_excel(worksheet, start_row, ncols)
    start_row += 50
    break
pprint(rows[-1])
conn.close()