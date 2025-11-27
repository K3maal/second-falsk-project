from flask import Flask, jsonify, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
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

    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()



@app.route("/")
def index():
    return redirect(url_for('client_login'))



@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form.get("name")
        age = request.form.get("age")
        email = request.form.get("email")
        password = request.form.get("password")

        hashed_password = generate_password_hash(password)
        
        conn = get_db_connection()

        try:
            conn.execute(
                "INSERT INTO users (name, age, email, password) VALUES (?, ?, ?, ?)",
                (name, age, email, hashed_password)
            )
            conn.commit()
            conn.close()
            return redirect(url_for('client_login'))
        except sqlite3.IntegrityError:
            conn.close()
            signup_path = os.path.join('templates', 'signup.html')
            with open(signup_path, 'r') as f:
                html = f.read()
            return html.replace('{{error}}', '<div class="error">Email already exists!</div>')
    
    signup_path = os.path.join('templates', 'signup.html')
    with open(signup_path, 'r') as f:
        html = f.read()
    return html.replace('{{error}}', '')




@app.route("/login", methods=["GET", "POST"])
def client_login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password): 
            session['logged_in'] = True
            session['role'] = 'client' 
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            return redirect(url_for('home'))
        else:
            login_path = os.path.join('templates', 'login.html')
            with open(login_path, 'r') as f:
                html = f.read()
            return html.replace('{{error}}', '<div class="error">Invalid email or password!</div>')

    login_path = os.path.join('templates', 'login.html')
    with open(login_path, 'r') as f:
        html = f.read()
    return html.replace('{{error}}', '')



@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        print(f"Admin Login Attempt - Email: {email}")

        if email == "ali@admin.com" and password == "ali123":
            session['logged_in'] = True
            session['role'] = 'admin'
            print(" Admin logged in successfully")
            return redirect(url_for('home'))
        else:
            admin_path = os.path.join('templates', 'admin-login.html')
            with open(admin_path, 'r') as f:
                html = f.read()
            return html.replace('{{error}}', '<div class="error">Invalid admin credentials!</div>')
    
    admin_path = os.path.join('templates', 'admin-login.html')
    with open(admin_path, 'r') as f:
        html = f.read()
    return html.replace('{{error}}', '')




@app.route("/home", methods=["GET"])
def home():
    if 'logged_in' not in session:
        return redirect(url_for('client_login'))
    
    html = ""
    header_path = os.path.join('templates', 'header.html')
    with open(header_path, 'r') as f:
        html = f.read()

    if session.get('role') == 'admin':
        html += "<h2>Upcoming Appointments:</h2><ul>"
        html += "<ul>"
        conn = get_db_connection()
        rows = conn.execute("SELECT * FROM clients ORDER BY date, time").fetchall()
        conn.close()

        for row in rows:
            html += f""" 
            <li>
                <span><strong>{row['name']}</strong> - {row['date']} at {row['time']} ({row['type']})</span>
                <button class="delete-btn" onclick="deleteClient({row['id']})">Delete</button>
            </li>
            """
    end_path = os.path.join('templates', 'footer.html')
    with open(end_path, 'r') as f:
        html += f.read()
    
    return html





@app.route('/clients', methods=["POST"])
def add():
    if 'logged_in' not in session:
        return redirect(url_for('client_login'))
    
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
    
    if session.get('role') != 'admin':
        return jsonify({'error': 'Not authorized - Admin only'}), 403
    
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
    
    if session.get('role') != 'admin':
        return jsonify({'error': 'Not authorized - Admin only'}), 403
    
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





@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('client_login'))




if __name__ == '__main__':
    init_db()
    app.run(debug=True)