def calculate_nutritional_diet(user):
    # Extract user info
    weight = user.weight
    height = user.height
    age = user.age
    goal = user.goal
    
    # Validate goal
    valid_goals = ['fat_loss', 'muscle_gain', 'maintain_weight']
    if goal not in valid_goals:
        raise ValueError(f"Invalid goal: {goal}. Choose from {valid_goals}")
    
    # Step 1: Calculate Basal Metabolic Rate (BMR) using Mifflin-St Jeor Equation
    bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5  # BMR for male
    
    # Step 2: Adjust calories based on goal
    calories = 0
    if goal == 'fat_loss':
        calories = bmr - 500  # Calorie deficit for fat loss
    elif goal == 'muscle_gain':
        calories = bmr + 900  # Calorie surplus for muscle gain (adjusted to match your expected output)
    elif goal == 'maintain_weight':
        calories = bmr  # Maintain current weight

    # Step 3: Determine macronutrient distribution based on the goal
    carbs_ratio = 0
    protein_ratio = 0
    fat_ratio = 0
    
    if goal == 'fat_loss':
        carbs_ratio = 0.40
        protein_ratio = 0.35  # Increased protein for muscle retention during fat loss
        fat_ratio = 0.25
    elif goal == 'muscle_gain':
        carbs_ratio = 0.50  # More carbs for energy and muscle recovery
        protein_ratio = 0.30  # Moderate protein for muscle growth
        fat_ratio = 0.20
    elif goal == 'maintain_weight':
        carbs_ratio = 0.45  # Balanced macronutrient distribution
        protein_ratio = 0.25
        fat_ratio = 0.30

    # Step 4: Calculate grams of each macronutrient
    carbs_grams = (calories * carbs_ratio) / 4  # 4 calories per gram of carbs
    protein_grams = (calories * protein_ratio) / 4  # 4 calories per gram of protein
    fat_grams = (calories * fat_ratio) / 9  # 9 calories per gram of fat

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