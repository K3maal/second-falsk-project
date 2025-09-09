from flask import Flask
import sqlite3, os 

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

@app.route('/add/<name>/<date>/<time>/<type>')
def add(name, date, time, type):
    conn = get_db_connection()
    conn.execute("INSERT INTO clients (name, date, time, type) VALUES (?, ?, ?, ?)",
                 (name, date, time, type))
    conn.commit()
    conn.close()
    return f"Added: {name} at {date} {time} for {type}"

@app.route('/delete/<int:id>')
def delete(id):
    conn = get_db_connection()
    conn.execute ("DELET FROM clients WHERE id = ?",(id,))
    conn.commit()
    conn.close()
    return f"Deleted appointment {id}"

@app.route('/update/<int:id>/<new_type>')
def update(id, new_type):
    conn = get_db_connection()
    conn.execute("UPDATE clients SET type = ?WHERE id = ?", (new_type, id))
    conn.commit()
    conn.close()
    return f"UPDATED apointment {id} to {new_type}"





if __name__ == '__main__':
    app.run(debug=True)
