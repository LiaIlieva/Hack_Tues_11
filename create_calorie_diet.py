def calculate_nutritional_diet(user):
    # Validate user data
    required_fields = ['weight', 'height', 'age', 'goal']
    for field in required_fields:
        if field not in user or user[field] is None:
            raise ValueError(f"Missing or invalid field: {field}")

    # Extract user info
    weight = user['weight']
    height = user['height']
    age = user['age']
    goal = user['goal']

    # Validate goal
    valid_goals = ['fat loss', 'muscle gain', 'maintain weight']
    if goal not in valid_goals:
        raise ValueError(f"Invalid goal: {goal}. Choose from {valid_goals}")

    # Step 1: Calculate Basal Metabolic Rate (BMR) using Mifflin-St Jeor Equation
    bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5

    # Step 2: Calculate Total Daily Energy Expenditure (TDEE)
    activity_factor = 1.55
    tdee = bmr * activity_factor

    # Step 3: Adjust calories based on goal
    if goal == 'fat loss':
        calories = tdee - 500
    elif goal == 'muscle gain':
        calories = tdee + 500
    elif goal == 'maintain weight':
        calories = tdee

    # Step 4: Determine macronutrient distribution
    if goal == 'fat loss':
        carbs_ratio = 0.40
        protein_ratio = 0.30
        fat_ratio = 0.30
    elif goal == 'muscle gain':
        carbs_ratio = 0.50
        protein_ratio = 0.30
        fat_ratio = 0.20
    elif goal == 'maintain weight':
        carbs_ratio = 0.45
        protein_ratio = 0.25
        fat_ratio = 0.30

    # Step 5: Calculate grams of each macronutrient
    carbs_grams = (calories * carbs_ratio) / 4
    protein_grams = (calories * protein_ratio) / 4
    fat_grams = (calories * fat_ratio) / 9

    # Return the results as a dictionary
    return {
        "calories": round(calories),
        "carbs_grams": round(carbs_grams),
        "protein_grams": round(protein_grams),
        "fat_grams": round(fat_grams)
    }

# Example user info
# user_info = {
#     'id': 1,
#     'weight': 70,  # in kg
#     'height': 175,  # in cm
#     'age': 25,
#     'goal': 'fat loss'  # Options: 'fat loss', 'muscle gain', 'maintain weight'
# }

def get_calorie_diet(user_info):
    # Calculate the optimal nutritional diet
    diet_plan = calculate_nutritional_diet(user_info)
    print("Optimal Nutritional Diet:")
    print(f"Calories: {diet_plan["calories"]} kcal")
    print(f"Carbs: {diet_plan["carbs_grams"]} g")
    print(f"Protein: {diet_plan["protein_grams"]} g")
    print(f"Fat: {diet_plan["fat_grams"]} g")

    return diet_plan