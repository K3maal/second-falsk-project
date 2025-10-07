from flask import Flask,request, redirect, url_for
import sqlite3
import os 


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
    
    
@app.route("/", methods=["GET"])
def home():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM clients ORDER BY date, time").fetchall()
    conn.close()


    
    html = ""
    header_path = os.path.join ('templates', 'header.html')
    with open (header_path , 'r') as f:
       html = f.read ()
       
    for row in rows:
        html += f""" 
        <li>
            <span><strong>{row['name']}</strong> - {row['date']} at {row['time']} ({row['type']})</span>
            <form action="/delete/{row['id']}" method="DELETE" style="margin:0;">
                <button type="submit" class="delete-btn">Delete</button>
            </form>
        </li>
        """
    end_path = os.path.join ('templates', 'end.html')
    with open (end_path, 'r') as f:
        html += f.read ()

    return html  
@app.route ('/clients', methods=["POST"])
def add ():
    init_db()   
    if request.method == "POST":
        name = request.form["name"]
        date = request.form["date"]
        time = request.form["time"]
        type_ = request.form["type"]
    
    conn = get_db_connection()
    conn.execute(
            "INSERT INTO clients (name, date, time, type) VALUES (?, ?, ?, ?)",
            (name, date, time, type_)
        )
    conn.commit()
    conn.close()
    return redirect (url_for ("home"), code = 303)



@app.route('/clients/<int:id>', methods=["DELETE"])
def delete(id):
    conn = get_db_connection()
    cur = conn.execute("DELETE FROM clients WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return '', 204

@app.route('/clients/<int:id>', methods=["PUT"])
def update(id):
    if request.method == "PUT":
        name = request.form["name"]
        date = request.form["date"]
        time = request.form["time"]
        type_ = request.form["type"]
    
    conn = get_db_connection()
    conn.execute(
            "UPDATE clients SET name = ?, date = ?, time = ?, type = ? WHERE id = ?",
            (name, date, time, type_, id)
        )
    conn.commit()
    conn.close()
    return '', 204

if __name__ == '__main__':
    app.run(debug=True)

