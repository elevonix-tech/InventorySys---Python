from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os

app = Flask(__name__)

# Use a strong secret key for session management
app.secret_key = os.environ.get("SECRET_KEY", "a_very_strong_secret_key")

DATABASE = "database.db"


# Database initialization
def init_db():
    with sqlite3.connect(DATABASE) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS api_keys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                square_public_key TEXT,
                square_secret_key TEXT,
                paypal_client_id TEXT,
                paypal_secret_key TEXT,
                stripe_publishable_key TEXT,
                stripe_secret_key TEXT,
                escrow_api_key TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            );
        """)


init_db()


# Routes
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        with sqlite3.connect(DATABASE) as conn:
            try:
                conn.execute(
                    "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                    (username, email, password)
                )
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                return "Username or email already exists."
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            user = cursor.fetchone()

            if user and check_password_hash(user[3], password):
                session['username'] = user[1]
                session['user_id'] = user[0]
                return redirect(url_for('dashboard'))
        return "Invalid email or password."
    return render_template('login.html')


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        user_id = session['user_id']
        square_public_key = request.form.get('square_public_key')
        square_secret_key = request.form.get('square_secret_key')
        paypal_client_id = request.form.get('paypal_client_id')
        paypal_secret_key = request.form.get('paypal_secret_key')
        stripe_publishable_key = request.form.get('stripe_publishable_key')
        stripe_secret_key = request.form.get('stripe_secret_key')
        escrow_api_key = request.form.get('escrow_api_key')

        with sqlite3.connect(DATABASE) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO api_keys
                (user_id, square_public_key, square_secret_key, paypal_client_id, paypal_secret_key,
                stripe_publishable_key, stripe_secret_key, escrow_api_key)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, square_public_key, square_secret_key, paypal_client_id, paypal_secret_key,
                  stripe_publishable_key, stripe_secret_key, escrow_api_key))

        return "API keys saved successfully!"
    return render_template('dashboard.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('user_id', None)
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True)
