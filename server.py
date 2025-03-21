from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, session
from flask_session import Session
import json
import os
import secrets

template_folder = os.path.abspath('.')
app = Flask(__name__, template_folder=template_folder)
app.secret_key = secrets.token_hex(16)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

USER_DATA_FILE = 'users.json'


# Load users from the JSON file
def load_users():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'r') as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return {}
    return {}

def is_logged():
    return "email" in session and session["email"] is not None

@app.route("/logout")
def logout():
    session["email"] = None
    return redirect("/HTML/index.html")

# Save users to the JSON file
def save_users(users):
    with open(USER_DATA_FILE, 'w') as f:
        json.dump(users, f, indent=4)


@app.route('/')
def index():
    return redirect('/HTML/index.html')


@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    users = load_users()

    if email in users and users[email]['password'] == password:
        flash("Login successful!", "success")
        session["email"] = email
        return redirect("/HTML/enterdetails.html")
    else:
        flash("Invalid email or password.", "danger")
        return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['userName']
        email = request.form['email']
        password = request.form['password']
        users = load_users()

        if email in users:
            flash("Email already registered. Please login.", "danger")
            return redirect(url_for('register'))
        else:
            users[email] = {'username': username, 'password': password}
            save_users(users)
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for('index'))

    return redirect('/HTML/register.html')


@app.route('/<path:path>')
def send_file(path):
    if path.endswith("login.html") or path.endswith("register.html"):
        return send_from_directory('./', path)

    if path.endswith(".html"):
        if is_logged():
            return send_from_directory('./', path)
        else:
            return redirect("/HTML/login.html")

    return send_from_directory('./', path)

if __name__ == '__main__':
    # app.run(debug=True)
    app.run(host='0.0.0.0', port=5000, debug=False)
