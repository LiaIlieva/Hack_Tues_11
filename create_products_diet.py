import requests

# Function to fetch products from Open Food Facts API
def fetch_products(query, page_size=10):
    url = f"https://world.openfoodfacts.org/cgi/search.pl?search_terms={query}&page_size={page_size}&json=1"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get('products', [])
    return []

# Function to create a daily diet plan
def create_diet_plan(user_info, nutritional_goals):
    # Extract nutritional goals
    calories_goal = nutritional_goals['calories']
    carbs_goal = nutritional_goals['carbs_grams']
    protein_goal = nutritional_goals['protein_grams']
    fat_goal = nutritional_goals['fat_grams']

    # Define meal categories and their calorie distribution
    meals = {
        'breakfast': 0.25,  # 25% of daily calories
        'lunch': 0.35,      # 35% of daily calories
        'dinner': 0.30,     # 30% of daily calories
        'snacks': 0.10      # 10% of daily calories
    }

    # Initialize diet plan
    diet_plan = {
        'breakfast': [],
        'lunch': [],
        'dinner': [],
        'snacks': []
    }

    # Fetch products for each meal
    for meal, calorie_ratio in meals.items():
        meal_calories = calories_goal * calorie_ratio
        meal_carbs = carbs_goal * calorie_ratio
        meal_protein = protein_goal * calorie_ratio
        meal_fat = fat_goal * calorie_ratio

        # Search for products that fit the meal's nutritional requirements
        query = "protein" if meal_protein > 10 else "snack"  # Example query
        products = fetch_products(query, page_size=5)

        # Select products that fit the meal's nutritional requirements
        selected_products = []
        total_calories = 0
        total_carbs = 0
        total_protein = 0
        total_fat = 0

        for product in products:
            nutriments = product.get('nutriments', {})
            product_calories = nutriments.get('energy-kcal_100g', 0)
            product_carbs = nutriments.get('carbohydrates_100g', 0)
            product_protein = nutriments.get('proteins_100g', 0)
            product_fat = nutriments.get('fat_100g', 0)

            # Check if the product fits the meal's nutritional requirements
            if (total_calories + product_calories <= meal_calories and
                total_carbs + product_carbs <= meal_carbs and
                total_protein + product_protein <= meal_protein and
                total_fat + product_fat <= meal_fat):
                print(product, selected_products)
                selected_products.append(product)
                total_calories += product_calories
                total_carbs += product_carbs
                total_protein += product_protein
                total_fat += product_fat

        diet_plan[meal] = selected_products
        # print(diet_plan)

    return diet_plan

# # Example user info
# user_info = {
#     'id': 1,
#     'weight': 70,  # in kg
#     'height': 175,  # in cm
#     'age': 25,
#     'goal': 'fat loss'  # Options: 'fat loss', 'muscle gain', 'maintain weight'
# }

# Calculate nutritional goals
# nutritional_goals = {
#     'calories': 2094,
#     'carbs_grams': 209,
#     'protein_grams': 157,
#     'fat_grams': 70
# }

# Create a daily diet plan
#diet_plan = create_diet_plan(user_info, nutritional_goals)

# # Display the diet plan
# print("Daily Diet Plan:")
# for meal, products in diet_plan.items():
#     print(f"\n{meal.capitalize()}:")
#     for product in products:
#         print(f"- {product.get('product_name', 'Unknown')}")
#         print(f"  Calories: {product.get('nutriments', {}).get('energy-kcal_100g', 'N/A')} kcal/100g")
#         print(f"  Carbs: {product.get('nutriments', {}).get('carbohydrates_100g', 'N/A')} g/100g")
#         print(f"  Protein: {product.get('nutriments', {}).get('proteins_100g', 'N/A')} g/100g")
#         print(f"  Fat: {product.get('nutriments', {}).get('fat_100g', 'N/A')} g/100g")