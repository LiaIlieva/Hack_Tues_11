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
def get_similar_food(product_info):
    from sentence_transformers import SentenceTransformer
    import requests
    import numpy as np
    from sklearn.metrics.pairwise import cosine_similarity

    # Load a pretrained model for text embeddings (e.g., Sentence-BERT)
    model = SentenceTransformer('all-MiniLM-L6-v2')
    product_text = f"{product_info['name']} {product_info['ingredients']}"
    product_embedding = model.encode(product_text)

    # Step 2: Fetch similar foods from the Open Food Facts API
    top_k=3
    # Query the Open Food Facts API
    query = product_info['name']  # Use the product name as the search query
    url = f"https://world.openfoodfacts.org/cgi/search.pl?search_terms={query}&page_size=10&json=1"
    response = requests.get(url)

    if response.status_code != 200:
        print("Failed to fetch data from Open Food Facts API.")
        return []

    # Parse the API response
    products = response.json().get('products', [])

    # Encode each product's name and ingredients
    product_embeddings = []
    valid_products = []
    for product in products:
        name = product.get('product_name', '')
        ingredients = product.get('ingredients_text', '')
        if name and ingredients:  # Ensure the product has a name and ingredients
            product_text = f"{name} {ingredients}"
            embedding = model.encode(product_text)
            product_embeddings.append(embedding)
            valid_products.append(product)

    if not product_embeddings:
        print("No valid products found.")
        return []

    # Compute cosine similarity between the given product and all other products
    similarities = cosine_similarity([product_embedding], product_embeddings)[0]

    # Sort products by similarity and return the top-k most similar ones
    sorted_indices = np.argsort(similarities)[::-1]  # Descending order
    similar_products = [valid_products[i] for i in sorted_indices[:top_k]]
    return similar_products

# Step 3: Fetch and display similar foods
# similar_foods = fetch_similar_foods(product_embedding, top_k=3)
# print("Similar Foods from Open Food Facts:")
# for i, food in enumerate(similar_foods, 1):
#     print(f"{i}. {food.get('product_name', 'Unknown')} - Ingredients: {food.get('ingredients_text', 'N/A')}")