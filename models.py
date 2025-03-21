from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy() 

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    height = db.Column(db.Float, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    goal = db.Column(db.String(50), nullable=False)

    calories = db.Column(db.Float)
    carbs_grams = db.Column(db.Float)
    protein_grams = db.Column(db.Float)
    fat_grams = db.Column(db.Float)

    # Relationship with Product (one-to-many, user can have multiple products)
    products = db.relationship('Product', backref='user', lazy=True)

    def __repr__(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'weight': self.weight,
            'height': self.height,
            'age': self.age,
            'goal': self.goal
        }
    
    def save_diet_info(self, diet_plan):
        """Method to save diet info to the user."""
        self.calories = diet_plan['calories']
        self.carbs_grams = diet_plan['carbs_grams']
        self.protein_grams = diet_plan['protein_grams']
        self.fat_grams = diet_plan['fat_grams']
        db.session.commit()

    def clear_diet_info(self):
        """Method to clear diet info from the user on logout."""
        self.calories = None
        self.carbs_grams = None
        self.protein_grams = None
        self.fat_grams = None
        db.session.commit()


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    brands = db.Column(db.String(100), nullable=True)
    ingredients = db.Column(db.String(255), nullable=True)
    nutritional_info = db.Column(db.JSON, nullable=False)  # Store nutritional info as JSON
    barcode = db.Column(db.String(100), nullable=True, unique=True)  # Unique barcode for each product
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Relationship with User

    def __repr__(self):
        return f"<Product {self.name} ({self.barcode})>"

    def to_dict(self):
        """Convert the product to a dictionary for easier JSON serialization."""
        return {
            "name": self.name,
            "brands": self.brands,
            "ingredients": self.ingredients,
            "nutritional_info": self.nutritional_info,
            "barcode": self.barcode,
            "user_id": self.user_id
        }