from flask import Flask, jsonify, request, redirect, url_for, session
import sqlite3
import os 

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'
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

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == "ali" and password == "ali123":
            session['logged_in'] = True
            return redirect(url_for('home'))
        else:
            login_path = os.path.join('templates', 'login.html')
            with open(login_path, 'r') as f:
                html = f.read()
            return html.replace('{{error}}', 'Invalid username or password!')
    
    login_path = os.path.join('templates', 'login.html')
    with open(login_path, 'r') as f:
        html = f.read()
    return html.replace('{{error}}', '')

@app.route("/home", methods=["GET"])
def home():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM clients ORDER BY date, time").fetchall()
    conn.close()
    
    html = ""
    header_path = os.path.join('templates', 'header.html')
    with open(header_path, 'r') as f:
        html = f.read()
    
    for row in rows:
        html += f""" 
        <li>
            <span><strong>{row['name']}</strong> - {row['date']} at {row['time']} ({row['type']})</span>
            <button class="delete-btn" onclick="deleteClient({row['id']})">Delete</button>
        </li>
        """
    
    end_path = os.path.join('templates', 'end.html')
    with open(end_path, 'r') as f:
        html += f.read()
    
    return html

@app.route('/clients', methods=["POST"])
def add():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    init_db()   
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
    
    return redirect(url_for("home"))

@app.route('/clients/<int:id>', methods=["DELETE"])
def delete(id):
    if 'logged_in' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM clients WHERE id = ?", (id,))
        conn.commit()
        
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({'error': 'Client not found'}), 404
        
        conn.close()
        return jsonify(), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    


@app.route('/clients/update/<int:id>', methods=["PUT"])
def update(id):
    if 'logged_in' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        data = request.get_json()
        
        name = data.get("name")
        date = data.get("date")
        time = data.get("time")
        type_ = data.get("type")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE clients SET name = ?, date = ?, time = ?, type = ? WHERE id = ?",
            (name, date, time, type_, id)
        )
        conn.commit()
        
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({'error': 'Client not found'}), 404
        
        conn.close()
        return jsonify({'message': 'Client updated successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)