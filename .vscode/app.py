from flask import Flask
from flask_sqlalchemy import SQLAlchemy


# Initialize the Flask application
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# run only once
with app.app_context():
    db.create_all()


# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
