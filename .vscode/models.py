from app.py import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    weight = db.Column(db.Float, nullable=False)
    height = db.Column(db.Float, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    goal = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return {
            'id': self.id,
            'weight': self.weight,
            'height': self.height,
            'age': self.age,
            'goal': self.goal
        }