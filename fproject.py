from flask import Flask, jsonify,request ,render_template
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
         font-family: Arial, sans-serif; 
         margin: 40px; 
         background: #f4f4f4; 
        }
             h1 {
          color: #333; 
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
        
        <h2>Upcoming Appointments</h2>

        <ul>
        <img src = "barber.jpeg"/>
    """
    for row in rows:
        html += f"<li><strong>{row['name']}</strong> - {row['date']} at {row['time']} ({row['type']})</li>"
    return html



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
    return jsonify({"status": "ok", "id": new_row["id"], "added": dict(new_row)}), 201



@app.route('/delete/<int:id>')
def delete(id):
    conn = get_db_connection()
    cur = conn.execute("DELETE FROM clients WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "ok", "id": id})



@app.route('/update/<int:id>/<new_type>')
def update(id, new_type):
    conn = get_db_connection()
    cur = conn.execute("UPDATE clients SET type = ? WHERE id = ?", (new_type, id))
    conn.commit()
    conn.close()
    return jsonify({"status": "ok", "id": id, "new_type": new_type})



if __name__ == '__main__':
    app.run(debug=True)

