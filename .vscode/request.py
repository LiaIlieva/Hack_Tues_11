from app.py import db, app
from flask import request, jsonify
import requests  # To make HTTP requests to external APIs
import json
from model.py import User


# Define a route for receiving POST requests with user data
@app.route('/user-info', methods=['POST'])
def user_info():
    try:
        # Get the user data from the incoming JSON request
        user_data = request.get_json()

        # Ensure the required fields are in the request
        required_fields = ['weight', 'height', 'goal', 'age']
        if any(field not in user_data for field in required_fields):
            return jsonify({
                'status': 'error',
                'message': 'Missing required user information (weight, height, goal, age).'
            }), 400
        
        new_user = User(
            weight=user_data['weight'],
            height=user_data['height'],
            age=user_data['age'],
            goal=user_data['goal']
        )
        db.session.add(new_user)
        db.session.commit()

       
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error processing user information: {str(e)}'
        }), 500
    

@app.route('/product', methods=['GET'])
def get_product_info():
    barcode = request.args.get('barcode')  # Get the barcode from query parameter
    if not barcode:
        return jsonify({'error': 'Barcode is required'}), 400
    
    # Now, you'll make a request to a national or external database to fetch product data.
    # For the sake of this example, we will use the Open Food Facts API.

    # Open Food Facts API URL (you can replace it with any national database API)
    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
    
    try:
        response = requests.get(url)
        product_data = response.json()

        # Check if the product exists in the database
        if product_data.get('status') != 1:
            return jsonify({'error': 'Product not found'}), 404

        # Extract relevant information (modify this based on the API response structure)
        product_info = {
            'name': product_data['product']['product_name'],
            'brands': product_data['product']['brands'],
            'ingredients': product_data['product'].get('ingredients_text', 'N/A'),
            'nutritional_info': product_data['product'].get('nutriments', 'N/A'),
            'barcode': product_data['product']['code']
        }

        return jsonify(product_info)

    except Exception as e:
        return jsonify({'error': str(e)}), 500