from flask import Flask, render_template, request
import json
import MySQLdb

user_name = "USER_NAME"
password =  "PASSWORD"
dbname = "DBNAME"


conn = MySQLdb.connect("localhost", user_name, password, dbname)
conn.set_character_set('utf8')
cur = conn.cursor()

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
        # GET parameters
        rows_limit = 15
        print(request.args)
        rows_limit = int(request.args.get("rows_limit"))
        start_row = int(request.args.get("start_row"))
        db_rows = cur.execute("SELECT * FROM comments WHERE comment_type = 0 AND doi_index > %d LIMIT 15",(start_row,))
        if db_rows > 0:
            rows = cur.fetchall()
            print(len(rows))
            response = []
            for i in rows:
                i = list(i)
                i[4] = json.loads(i[4])
                response.append(i)
            rows = {'rows_count': len(response), 'rows':response}
        else:
            rows = {'error': 'No more records', 'rows_count': 0}
        return json.dumps(rows)


@app.route('/update_excel', methods=['GET'])
def update_excel():
    if request.method == 'GET':
        # GET parameters
        print(request.args)
        index = int(request.args.get("index"))
        comment_type = int(request.args.get("comment_type"))    
        cur.execute("UPDATE comments SET comment_type = %d  WHERE doi_index = %d", (comment_type, index))
        conn.commit()
        return json.dumps({'sucess': 1})


@app.route('/')
def hello():
    return render_template('index.html')

if __name__ == '__main__':
    app.run()
