from app import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    join_date = db.Column(db.Date, nullable=False, default=db.func.current_date())  # Nowe pole
    reset_token = db.Column(db.String(100), nullable=True)  # Token do resetowania hasła

    # Relacja z tabelą `recipes`
    recipes = db.relationship('Recipe', backref='user', lazy=True)

    # Relacja z tabelą `favorites`
    favorites = db.relationship('Favorite', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.name}>'


class Recipe(db.Model):
    __tablename__ = 'recipes'  # Upewnij się, że nazwa tabeli to 'recipes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    ingredients = db.Column(db.Text, nullable=False)
    steps = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    image_url = db.Column(db.String(255))


class Favorite(db.Model):
    __tablename__ = 'favorites'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=False)

    def __repr__(self):
        return f'<Favorite UserID: {self.user_id}, RecipeID: {self.recipe_id}>'

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    gram_to_ml = db.Column(db.Float, nullable=False)  # Współczynnik gram <-> ml

