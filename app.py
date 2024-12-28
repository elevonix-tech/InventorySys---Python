from flask import Flask, render_template, request, redirect, url_for 

import sqlite3 

 

app = Flask(__name__) 

 

# Database configuration 

DATABASE = "database.db" 

 

# Initialize the database 

def init_db(): 

  with sqlite3.connect(DATABASE) as conn: 

    conn.execute(""" 

      CREATE TABLE IF NOT EXISTS inventory ( 

        id INTEGER PRIMARY KEY AUTOINCREMENT, 

        item_name TEXT NOT NULL, 

        quantity INTEGER NOT NULL, 

        low_stock_level INTEGER NOT NULL 

      ); 

    """) 

    conn.execute(""" 

      CREATE TABLE IF NOT EXISTS users ( 

        id INTEGER PRIMARY KEY AUTOINCREMENT, 

        username TEXT UNIQUE NOT NULL, 

        password TEXT NOT NULL, 

        role TEXT NOT NULL 

      ); 

    """) 

 

init_db() 

 

# Routes 

@app.route('/') 

def home(): 

  return render_template('index.html') 

 

@app.route('/dashboard') 

def dashboard(): 

  with sqlite3.connect(DATABASE) as conn: 

    cursor = conn.cursor() 

    cursor.execute("SELECT * FROM inventory") 

    inventory = cursor.fetchall() 

  return render_template('dashboard.html', inventory=inventory) 

 

@app.route('/add_item', methods=['POST']) 

def add_item(): 

  item_name = request.form['item_name'] 

  quantity = int(request.form['quantity']) 

  low_stock_level = int(request.form['low_stock_level']) 

  with sqlite3.connect(DATABASE) as conn: 

    conn.execute("INSERT INTO inventory (item_name, quantity, low_stock_level) VALUES (?, ?, ?)", 

          (item_name, quantity, low_stock_level)) 

  return redirect(url_for('dashboard')) 

 

@app.route('/delete_item/<int:item_id>', methods=['POST']) 

def delete_item(item_id): 

  with sqlite3.connect(DATABASE) as conn: 

    conn.execute("DELETE FROM inventory WHERE id=?", (item_id,)) 

  return redirect(url_for('dashboard')) 

 

@app.route('/reports') 

def reports(): 

  # Placeholder for reports 

  return render_template('reports.html', reports_data={}) 

 

@app.route('/login', methods=['GET', 'POST']) 

def login(): 

  if request.method == 'POST': 

    username = request.form['username'] 

    password = request.form['password'] 

    with sqlite3.connect(DATABASE) as conn: 

      cursor = conn.cursor() 

      cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password)) 

      user = cursor.fetchone() 

    if user: 

      return redirect(url_for('dashboard')) 

    return "Invalid credentials" 

  return render_template('login.html') 

 

if __name__ == "__main__": 

  app.run(debug=True) 