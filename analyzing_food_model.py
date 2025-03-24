from transformers import pipeline

# Load a zero-shot classification model for ingredient analysis
ingredient_classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# # Define user profile
# user_profile = {
#     'id': 1,
#     'weight': 70,  # in kg
#     'height': 175,  # in cm
#     'age': 250,
#     'goal': 'fat loss'  # Options: 'fat loss', 'muscle gain', 'maintain weight'
# }

# Define product information
# product_info = {
#     'name': 'Protein Bar',
#     'brands': 'Brand X',
#     'ingredients': 'protein, sugar, cocoa, milk, peanuts',
#     'nutritional_info': {
#         'calories': 250,  # per serving
#         'fat': 8,  # in grams
#         'protein': 20,  # in grams
#         'sugar': 12  # in grams
#     },
#     'barcode': '123456789'
# }

# Define rules for food evaluation
def evaluate_food(goal, product_info):
    goal = goal
    calories = product_info.nutritional_info['energy-kcal']
    fat = product_info.nutritional_info['fat']
    protein = product_info.nutritional_info['proteins']
    sugar = product_info.nutritional_info['sugars']

    # Rule-based evaluation
    if goal == 'fat_loss':
        if calories > 300 or fat > 10 or sugar > 15:
            return "Bad: High in calories, fat, or sugar. Not suitable for fat loss."
        elif protein < 10:
            return "Moderate: Low in protein. Consume in limited quantities."
        else:
            return "Good: Suitable for fat loss."

    elif goal == 'muscle_gain':
        if protein < 15:
            return "Bad: Low in protein. Not suitable for muscle gain."
        elif calories < 200:
            return "Moderate: Low in calories. Consume in larger quantities."
        else:
            return "Good: Suitable for muscle gain."

    elif goal == 'maintain_weight':
        if calories > 400 or fat > 15 or sugar > 20:
            return "Bad: High in calories, fat, or sugar. Not suitable for maintaining weight."
        elif protein < 10:
            return "Moderate: Low in protein. Consume in limited quantities."
        else:
            return "Good: Suitable for maintaining weight."

    else:
        return "Unknown goal. Cannot evaluate."

# Analyze ingredients for allergens or unhealthy components
from deep_translator import GoogleTranslator

# Translate text from Bulgarian to English
def translate_to_english(text):
    return GoogleTranslator(source="auto", target="en").translate(text)

# Analyze ingredients for allergens or unhealthy components
def analyze_ingredients(ingredients):
    if not ingredients:
        return "No ingredient data available."

    # 🔄 Translate ingredients to English
    translated_ingredients = translate_to_english(ingredients)
    
    # Define unhealthy labels in English
    unhealthy_labels = ["sugar", "artificial sweeteners", "trans fat", "high fructose corn syrup"]
    
    # Perform classification using the translated ingredients
    result = ingredient_classifier(translated_ingredients, candidate_labels=unhealthy_labels)

    if result['scores'][0] > 0.5:  # Confidence threshold
        return f"Warning: Contains {result['labels'][0]}. Consume in moderation."
    
    return "No unhealthy ingredients detected."

# Evaluate the product
def evaluate_product(user_profile, product_info):
    # Evaluate based on nutritional info
    nutritional_evaluation = evaluate_food(user_profile.goal, product_info)

    # Analyze ingredients
    ingredient_evaluation = analyze_ingredients(product_info.ingredients)

    # Combine results
    evaluation = {
        'product_name': product_info.name,
        'nutritional_evaluation': nutritional_evaluation,
        'ingredient_evaluation': ingredient_evaluation
    }
    return evaluation

# Test the evaluation
def analize_food(user_profile, product_info):
    evaluation = evaluate_product(user_profile, product_info)
    print("Product Evaluation:")
    print(f"Product Name: {evaluation['product_name']}")
    print(f"Nutritional Evaluation: {evaluation['nutritional_evaluation']}")
    print(f"Ingredient Evaluation: {evaluation['ingredient_evaluation']}")
    return evaluation