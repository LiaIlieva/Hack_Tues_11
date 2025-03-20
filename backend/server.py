from flask import Flask, render_template, request, redirect, url_for, flash
import json
import os
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

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


# Save users to the JSON file
def save_users(users):
    with open(USER_DATA_FILE, 'w') as f:
        json.dump(users, f, indent=4)


@app.route('/')
def index():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    users = load_users()

    if email in users and users[email]['password'] == password:
        flash("Login successful!", "success")
        return redirect(url_for('index'))
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
            return redirect(url_for('index'))
        else:
            users[email] = {'username': username, 'password': password}
            save_users(users)
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for('index'))

    return render_template('register.html')


if __name__ == '__main__':
    app.run(debug=True)
