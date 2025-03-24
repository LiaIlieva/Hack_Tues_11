from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, session
from flask_session import Session
from models import db, User, Product  # Ensure Product is imported
import json
import os
import secrets
from flask_migrate import Migrate



template_folder = os.path.abspath('.')
app = Flask(__name__, template_folder=template_folder)
app.secret_key = secrets.token_hex(16)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
migrate = Migrate(app, db)  # Initialize Flask-Migrate

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

def find_current_user() -> User:
    email = session["email"]
    user = db.session.query(User).filter_by(email=email).first()  # Fetch user from DB  
    return user

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
    user = users[email]

    if user['password'] == password:
        flash("Login successful!", "success")
        session["email"] = email
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
            return redirect(url_for('register'))
        else:
            users[email] = {'username': username, 'password': password}
            save_users(users)
            
            # Create a new user
            new_user = User(
                username=username,
                email=email,
                weight=None,
                height=None,
                age=None,
                goal=None
            )

            db.session.add(new_user)
            db.session.commit()
            
            flash("Registration successful!", "success")
            return redirect(url_for('enterdetails'))

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

# _______________________________________________________________________________

from flask import Flask, request, jsonify, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import torch
from transformers import BertTokenizer, BertForSequenceClassification
from flask_session import Session
import secrets
from werkzeug.security import check_password_hash
from LLM_goal_classifier import get_goal
from create_calorie_diet import get_calorie_diet
from create_products_diet import create_diet_plan
from analyzing_food_model import analize_food
from get_similar_foods_model import get_similar_food

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Load Pretrained Model and Tokenizer
MODEL_PATH = "bert-base-uncased"  # Load directly from Hugging Face
try:
    tokenizer = BertTokenizer.from_pretrained(MODEL_PATH)
    model = BertForSequenceClassification.from_pretrained(MODEL_PATH, num_labels=3)
    model.eval()
    print("✅ Model and tokenizer loaded successfully!")
except Exception as e:
    print(f"❌ Error loading model: {e}")

# Define label mapping
LABEL_MAP = {0: "fat_loss", 1: "muscle_gain", 2: "maintain_weight"}

# Create database if not exists
with app.app_context():
    db.create_all()

@app.route("/user-details", methods=["POST"])
def enter_user_details():
    try:
        user_details = request.form
        required_fields = ["weight", "height", "goal", "age"]

        user = find_current_user()
        if not user:
            flash("User not found", "error")
            return
        
        # Check if all required fields are present
        if any(field not in user_details for field in required_fields):
            flash("Missing required user information.", "error")
            return

        # Classify user's goal
        goal = get_goal(user_details["goal"])
        if not goal:  # If the goal is unrelated or confidence is too low
            flash("Unable to classify goal. Please provide a valid fitness goal.", "error")
            return

        user.weight = float(user_details["weight"])
        user.height = float(user_details["height"])
        user.goal = goal
        user.age = float(user_details["age"])

        db.session.commit()
        return redirect(url_for('index'))

    except Exception as e:
        flash(f"Error processing user info: {str(e)}", "error")
        return

@app.route("/user-info", methods=["POST"])
def user_info():
    try:
        user_data = request.get_json()
        required_fields = ["username", "email", "weight", "height", "goal", "age"]

        # Check if all required fields are present
        if any(field not in user_data for field in required_fields):
            return jsonify({"status": "error", "message": "Missing required user information."}), 400

        # Ensure the goal field is not empty
        if not user_data["goal"]:
            return jsonify({"status": "error", "message": "Goal cannot be empty."}), 400

        # Classify user's goal
        goal = get_goal(user_data["goal"])
        if not goal:  # If the goal is unrelated or confidence is too low
            return jsonify(
                {"status": "error", "message": "Unable to classify goal. Please provide a valid fitness goal."}), 400

        # Create a new user
        new_user = User(
            username=user_data["username"],
            email=user_data["email"],
            weight=user_data["weight"],
            height=user_data["height"],
            age=user_data["age"],
            goal=goal,  # Ensure goal is not None
        )

        db.session.add(new_user)
        db.session.commit()

        return jsonify({"status": "success", "message": "User added successfully", "goal_category": goal})

    except Exception as e:
        return jsonify({"status": "error", "message": f"Error processing user info: {str(e)}"}), 500


from deep_translator import GoogleTranslator
from flask import request, jsonify
from models import db, Product  # Adjust this import according to your project structure

def translate_to_english(text):
    """Translates text to English using Google Translate."""
    if text:
        return GoogleTranslator(source="auto", target="en").translate(text)
    return text  # Return the original text if it's None or empty

@app.route("/product", methods=["POST"])
def get_product_info():
    try:
        if not is_logged():
            return jsonify({"error": "User not logged in"}), 401

        user = find_current_user()  # Fetch the user from DB
        if not user:
            return jsonify({"error": "User not found"}), 404

        product_data = request.get_json()

        if product_data.get("status") != 1:
            return jsonify({"error": "Product not found"}), 404

        # 🚨 Delete ALL previous products linked to this user 🚨
        print(f'Clearing previous products for user {user.id}')
        db.session.query(Product).filter_by(user_id=user.id).delete()
        db.session.commit()

        # Extract new product data
        product = product_data.get("product")  

        # Translate all relevant product fields to English
        product_info = {
            "name": translate_to_english(product.get("product_name")),
            "brands": translate_to_english(product.get("brands")),
            "ingredients": translate_to_english(product.get("ingredients_text")),
            "nutritional_info": product.get("nutriments"),  # Nutritional info might be a dict, so consider how to handle it
            "barcode": product.get("code")
        }

        # If nutritional info is a dictionary, you might want to translate individual keys like:
        if product_info["nutritional_info"]:
            product_info["nutritional_info"] = {key: translate_to_english(value) if isinstance(value, str) else value
                                                 for key, value in product_info["nutritional_info"].items()}

        # Create a new Product record
        new_product = Product(
            name=product_info['name'],
            brands=product_info['brands'],
            ingredients=product_info['ingredients'],
            nutritional_info=product_info['nutritional_info'],
            barcode=product_info['barcode'],
            user_id=user.id  # Associate with the logged-in user
        )

        db.session.add(new_product)
        db.session.commit()

        return jsonify({"status": "success", "message": "Product added successfully"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route("/get-calorie-diet", methods=["GET"])
def calorie_diet():
    if not is_logged():
        return jsonify({"error": "User not logged in"}), 401

    user = find_current_user()  # Fetch user from DB
    if not user:
        return jsonify({"error": "User not found"}), 404

    diet_plan = get_calorie_diet(user)

    user.save_diet_info(diet_plan)

    return jsonify({
        "status": "success",
        "calorie_diet": {
            "calories": diet_plan['calories'],
            "carbs_grams": diet_plan['carbs_grams'],
            "protein_grams": diet_plan['protein_grams'],
            "fat_grams": diet_plan['fat_grams']
        }
    })


@app.route("/get-product-diet", methods=["GET"])
def product_diet():
    if not is_logged():
        return jsonify({"error": "User not logged in"}), 401

    user = find_current_user()  # Fetch the user from DB
    if not user:
        return jsonify({"error": "User not found"}), 404

    nutritional_goals = {
        'calories': user.calories,  # This can be fetched from the user's saved info
        'carbs_grams': user.carbs_grams,
        'protein_grams': user.protein_grams,
        'fat_grams': user.fat_grams
    }

    diet_plan = create_diet_plan(user, nutritional_goals)
    formatted_diet_plan = {}
    for meal, products in diet_plan.items():
        formatted_products = []
        for product in products:
            formatted_product = {
                "product_name": product.get("product_name", "Unknown"),
                "calories": product.get("nutriments", {}).get("energy-kcal_100g", "N/A"),
                "carbs": product.get("nutriments", {}).get("carbohydrates_100g", "N/A"),
                "protein": product.get("nutriments", {}).get("proteins_100g", "N/A"),
                "fat": product.get("nutriments", {}).get("fat_100g", "N/A")
            }
            formatted_products.append(formatted_product)
        formatted_diet_plan[meal] = formatted_products

    return jsonify({
        "status": "success",
        "diet_plan": formatted_diet_plan
    })

from create_products_diet_2 import generate_meal_plan

# @app.route("/get-meal-plan", methods=["GET"])
# def product_diet():
#     # if not is_logged():
#     #     return jsonify({"error": "User not logged in"}), 401

#     # user = find_current_user()  # Fetch the user from DB
#     # if not user:
#     #     return jsonify({"error": "User not found"}), 404

#     test_user = User(
#         id=3,
#         username="test_user",
#         email="test@example.com",
#         weight=70.0,  # kg
#         height=175.0,  # cm
#         age=25,
#         goal="muscle_gain",
#         calories=2500,
#         protein_grams=180,
#         carbs_grams=300,
#         fat_grams=70
#     )
   
#     diet_plan = generate_meal_plan(test_user)
#     print("Generated Meal Plan:", diet_plan)

#     return jsonify({
#         "status": "success",
#         "diet_plan": diet_plan
#     })


@app.route("/analyze-food", methods=['GET'])
def analyze_food_route():
    if not is_logged():
        return jsonify({"error": "User not logged in"}), 401

    user = find_current_user()  # Fetch user from DB
    if not user:
        return jsonify({"error": "User not found"}), 404

    product = Product.query.filter_by(user_id=user.id).first()
    print(product)

    if not product:
        return jsonify({"error": "No products found for the logged-in user."}), 404

    evaluation = analize_food(user, product)

    return jsonify({
        "status": "success",
        "evaluation": evaluation
    })

@app.route("/get-similar-food", methods=["GET"])
def get_similar_food_route():
    try:
        if not is_logged():
            return jsonify({"error": "User not logged in"}), 401

        user = find_current_user()  # Fetch user from DB       
        if not user:
            return jsonify({"error": "User not found"}), 404

        product = Product.query.filter_by(user_id=user.id).first()

        if not product:
            return jsonify({"error": "No products found for the logged-in user."}), 404

        similar_foods = get_similar_food(product)

        return jsonify({
            "status": "success",
            "similar_foods": [
                {
                    "product_name": food.get('product_name', 'N/A'),  # Use .get() for dictionaries
                    "ingredients": food.get('ingredients_text', 'N/A')  # Use .get() for dictionaries
                } for food in similar_foods
            ]
        })

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # app.run(debug=True)
    ssl_context = ("cert.pem", "key.pem")
    # app.run(host='0.0.0.0', port=5000, debug=False)
    app.run(host='0.0.0.0', port=8443, debug=False, ssl_context=ssl_context)
