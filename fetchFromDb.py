import MySQLdb
self.conn = MySQLdb.connect("localhost", "bhanu", "bhanujha", "comments")
self.cur = self.conn.cursor()

"""
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

last_comment_id = 1
self.cur.execute("SELECT * FROM comments WHERE comment_id > %d LIMIT 15", (last_comment_id,))
user_data = self.cur.fetchone()

