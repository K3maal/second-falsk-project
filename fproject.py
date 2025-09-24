from flask import Flask, jsonify,request ,render_template, redirect, url_for
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
    
    
@app.route("/", methods=["GET", "POST"])
def home():
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

    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM clients ORDER BY date, time").fetchall()
    conn.close()

    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Barber Shop</title>

        <style>
            body { 
                background-image: url('/static/barber.jpeg');
            }
            h1 {
                color: white; 
                text-align: center;
                padding: 3px;
                background: #333;
            }
            h2 {
                color: white;
                background: #333;
                display: inline-block;
                padding: 5px 10px;
                border-radius: 6px;

                }
            form {
                background: #fff; 
                padding: 20px; 
                border-radius: 8px; 
                margin-bottom: 30px; 
                box-shadow: 0 2px 6px rgba(0,0,0,0.1); 
            }
            input, select { 
                padding: 8px; 
                margin: 8px 0; 
                width: 100%; 
                border: 1px solid #ccc; 
                border-radius: 4px; 
            }
            button { 
                padding: 10px 20px; 
                background: #333; 
                color: white; 
                border: none; 
                border-radius: 4px; 
                cursor: pointer; 
            }
            button:hover { 
                background: #555; 
            }
            ul {
                list-style-type: none; 
                padding: 0; 
            }
            li { 
                background: #fff; 
                padding: 10px; 
                margin: 5px 0; 
                border-radius: 6px; 
                box-shadow: 0 1px 4px rgba(0,0,0,0.1);
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .delete-btn {
                background: #e74c3c;
                color: #fff;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                cursor: pointer;
            }
            .delete-btn:hover {
                background: #c0392b;
            }
        </style>

    </head>
    <body>
        <h1>Barber Shop Appointments</h1>
        <form method="POST">
            <label>Name:</label>
            <input type="text" name="name" required>
            
            <label>Date:</label>
            <input type="date" name="date" required>
            
            <label>Time:</label>
            <input type="time" name="time" required>
            
            <label>Service Type:</label>
            <select name="type" required>
                <option value="Haircut">Haircut</option>
                <option value="Beard Trim">Beard Trim</option>
                <option value="Shave">Shave</option>
                <option value="Combo">Haircut + Beard</option>
            </select>
            
            <button type="submit">Book Appointment</button>
        </form>
        
        <h2>Upcoming Appointments:
        /h2>

        <ul>
    """
    for row in rows:
        html += f"""
        <li>
            <span><strong>{row['name']}</strong> - {row['date']} at {row['time']} ({row['type']})</span>
            <form action="/delete/{row['id']}" method="post" style="margin:0;">
                <button type="submit" class="delete-btn">Delete</button>
            </form>
        </li>
        """
    html += """
        </ul>
    </body>
    </html>
    """
    return html


@app.route('/delete/<int:id>', methods=["POST"])
def delete(id):
    conn = get_db_connection()
    cur = conn.execute("DELETE FROM clients WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    # return jsonify({"status": "ok", "id": id})
    return redirect(url_for("home"), code=303)


if __name__ == '__main__':
    app.run(debug=True)