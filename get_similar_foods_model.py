# Install the required libraries:
# pip install sentence-transformers torch requests numpy scikit-learn



# Example product_info
# product_info = {
#     'name': 'Protein Bar',
#     'brands': 'Brand X',
#     'ingredients': 'protein, sugar, cocoa, milk, peanuts',
#     'nutritional_info': {
#         'calories': 250,
#         'fat': 8,
#         'protein': 20,
#         'sugar': 12
#     },
#     'barcode': '123456789'
# }

# Step 1: Encode the product's name and ingredients into embeddings
# def get_similar_food(product):
#     from sentence_transformers import SentenceTransformer
#     import requests
#     import numpy as np
#     from sklearn.metrics.pairwise import cosine_similarity

#     # Load a pretrained model for text embeddings (e.g., Sentence-BERT)
#     model = SentenceTransformer('all-MiniLM-L6-v2')
#     product_text = f"{product.name} {product.ingredients}"  # Use dot notation
#     product_embedding = model.encode(product_text)

#     # Step 2: Fetch similar foods from the Open Food Facts API
#     top_k = 3
#     # Query the Open Food Facts API
#     query = product.name  # Use dot notation
#     url = f"https://world.openfoodfacts.org/cgi/search.pl?search_terms={query}&page_size=10&json=1"
#     response = requests.get(url)

#     if response.status_code != 200:
#         print("Failed to fetch data from Open Food Facts API.")
#         return []

#     # Parse the API response
#     products = response.json().get('products', [])

#     # Encode each product's name and ingredients
#     product_embeddings = []
#     valid_products = []
#     for product in products:
#         name = product.get('product_name', '')
#         ingredients = product.get('ingredients_text', '')
#         if name and ingredients:  # Ensure the product has a name and ingredients
#             product_text = f"{name} {ingredients}"
#             embedding = model.encode(product_text)
#             product_embeddings.append(embedding)
#             valid_products.append(product)

#     if not product_embeddings:
#         print("No valid products found.")
#         return []

#     # Compute cosine similarity between the given product and all other products
#     similarities = cosine_similarity([product_embedding], product_embeddings)[0]

#     # Sort products by similarity and return the top-k most similar ones
#     sorted_indices = np.argsort(similarities)[::-1]  # Descending order
#     similar_products = [valid_products[i] for i in sorted_indices[:top_k]]
#     return similar_products

# Step 3: Fetch and display similar foods
# similar_foods = fetch_similar_foods(product_embedding, top_k=3)
# print("Similar Foods from Open Food Facts:")
# for i, food in enumerate(similar_foods, 1):
#     print(f"{i}. {food.get('product_name', 'Unknown')} - Ingredients: {food.get('ingredients_text', 'N/A')}")

import requests
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import random
from deep_translator import GoogleTranslator

def translate_to_english(text):
    """Translates Bulgarian text to English."""
    return GoogleTranslator(source="auto", target="en").translate(text)

def get_similar_food(product):
    # 🔥 Best model for text similarity
    model = SentenceTransformer("sentence-t5-large")

    # Translate product name and ingredients to English
    product_name_en = translate_to_english(product.name) if product.name else ''
    product_ingredients_en = translate_to_english(product.ingredients) if product.ingredients else ''

    # Encode product text (give more weight to ingredients)
    product_text = f"{product_name_en} {product_ingredients_en * 5}"
    product_embedding = model.encode(product_text, normalize_embeddings=True)

    # Fetch similar foods from Open Food Facts API
    query = product.name.split()[0] if product.name else ' '.join(product_ingredients_en.split()[:2])

    print(query)

    url = f"https://world.openfoodfacts.org/cgi/search.pl?search_terms={query}&page_size=50&json=1"
    response = requests.get(url)

    if response.status_code != 200:
        print("Failed to fetch data from Open Food Facts API.")
        return []

    products = response.json().get('products', [])
    if not products:
        print("No products found from API.")
        return []

    product_embeddings = []
    valid_products = []
    product_category = None  # Store the category of the scanned product

    for p in products:
        name = p.get('product_name', '').strip()
        ingredients = p.get('ingredients_text', '').strip()
        category = p.get('categories', '').strip().lower()

        # Store the category of the scanned product if it's the same name
        if name.lower() == product.name.lower() if product.name else False:
            product_category = category

        # Skip missing data
        if not name or not ingredients or not category:
            continue

        # Encode product text, weighting ingredients more heavily
        combined_text = f"{name} {ingredients * 5}"
        embedding = model.encode(combined_text, normalize_embeddings=True)

        product_embeddings.append(embedding)
        valid_products.append(p)

    # Compute cosine similarity
    if valid_products:
        similarities = cosine_similarity([product_embedding], product_embeddings)[0]
        sorted_indices = np.argsort(similarities)[::-1]  # Sort descending
        similar_products = [valid_products[i] for i in sorted_indices[:3]]  # Take top 3

        if similar_products:
            print("Found Similar Products:", [p.get('product_name', 'Unknown') for p in similar_products])
            return similar_products

    # 🔥 If no strong matches, use the main ingredient and find similar products
    if product_ingredients_en:
        main_ingredient = product_ingredients_en.split(',')[0]  # Take the first ingredient
        print(f"Trying to find products based on the main ingredient: {main_ingredient}")
        ingredient_query = main_ingredient.strip()

        # Fetch products based on main ingredient
        url_ingredient = f"https://world.openfoodfacts.org/cgi/search.pl?search_terms={ingredient_query}&page_size=50&json=1"
        response_ingredient = requests.get(url_ingredient)

        if response_ingredient.status_code == 200:
            ingredient_products = response_ingredient.json().get('products', [])
            if ingredient_products:
                # Return top 3 products with the main ingredient
                print(f"Returning similar products based on main ingredient: {main_ingredient}")
                return ingredient_products[:3]

    # 🔥 If still no results, return any 3 random products
    if len(products) >= 3:
        random_products = random.sample(products, 3)
        print("Returning any 3 random products:", [p.get('product_name', 'Unknown') for p in random_products])
        return random_products

    # If everything fails, return an empty list
    return []
