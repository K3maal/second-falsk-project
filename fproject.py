from flask import Flask
import sqlite3

def get_db_connection():
    conn = sqlite3.connect('data.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            type TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


app = Flask (__name__)

@app.route('/')
def appointments():
    conn = get_db_connection()
    rows = conn.execute('SELECT * FROM clients').fetchall()
    conn.close()

    return str([dict(row) for row in rows])


if __name__ == '__main__':
    app.run(debug=True)
