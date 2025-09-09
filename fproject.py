from flask import Flask, jsonify
import sqlite3, os 


app = Flask (__name__)

DB_PATH = os.path.join(os.path.dirname(__file__), "data.db")

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




@app.route('/')
def appointments():
    conn = get_db_connection()
    rows = conn.execute('SELECT * FROM clients').fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])


@app.route('/add/<name>/<date>/<time>/<type>')
def add(name, date, time, type):
    conn = get_db_connection()
    conn.execute(
    "INSERT INTO clients (name, date, time, type) VALUES (?, ?, ?, ?)",
    (name, date, time, type)
)
    conn.commit()
    new_row = conn.execute("SELECT * FROM clients ORDER BY id DESC LIMIT 1").fetchone()
    conn.close()
    return jsonify({"status": "ok", "added":dict(new_row)}), 201


@app.route('/delete/<int:id>')
def delete(id):
    conn = get_db_connection()
    cur = conn.execute("DELETE FROM clients WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "ok", "deleted_id": id, "rows_affected": cur.rowcount})


@app.route('/update/<int:id>/<new_type>')
def update(id, new_type):
    conn = get_db_connection()
    cur = conn.execute("UPDATE clients SET type = ? WHERE id = ?", (new_type, id))
    conn.commit()
    conn.close()
    return jsonify({"status": "ok", "updated_id": id, "rows_affected": cur.rowcount, "new_type": new_type})



if __name__ == '__main__':
    app.run(debug=True)
