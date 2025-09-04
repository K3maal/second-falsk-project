from flask import Flask
import sqlite3

def get_db_connection():
    conn = sqlite3.connect('contributors.db')
    conn.row_factory = sqlite3.Row
    return conn

app = Flask (__name__)

@app.route('/')
def appointments():
    conn = get_db_connection()
    rows = conn.execute('SELECT * FROM contributors').fetchall()
    conn.close()
    return str([dict(row) for row in rows])




if __name__ == '__main__':
    app.run(debug=True)