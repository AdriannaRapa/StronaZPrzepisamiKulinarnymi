from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from config import Config

# Inicjalizacja aplikacji
app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
migrate = Migrate(app, db)

# Modele
from models import User, Recipe, Favorite

# Endpoint: Rejestracja użytkownika
@app.route('/register', methods=['POST'])
def register_user():
    data = request.json
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    new_user = User(name=data['name'], email=data['email'], password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "Użytkownik zarejestrowany pomyślnie!"}), 201

# Endpoint: Logowanie użytkownika
@app.route('/login', methods=['POST'])
def login_user():
    data = request.json
    user = User.query.filter_by(email=data['email']).first()
    if user and bcrypt.check_password_hash(user.password, data['password']):
        return jsonify({"message": "Logowanie pomyślne!", "user_id": user.id})
    return jsonify({"error": "Nieprawidłowy email lub hasło"}), 401

# Endpoint: Dodawanie przepisu
@app.route('/add_recipe', methods=['POST'])
def add_recipe():
    data = request.json
    new_recipe = Recipe(
        name=data['name'],
        category=data['category'],
        ingredients=data['ingredients'],
        steps=data['steps'],
        user_id=data['user_id']
    )
    db.session.add(new_recipe)
    db.session.commit()
    return jsonify({"message": "Przepis dodany pomyślnie!"}), 201

# Endpoint: Pobieranie przepisów
@app.route('/recipes', methods=['GET'])
def get_recipes():
    recipes = Recipe.query.all()
    result = [
        {
            "id": recipe.id,
            "name": recipe.name,
            "category": recipe.category,
            "ingredients": recipe.ingredients,
            "steps": recipe.steps,
            "user_id": recipe.user_id
        }
        for recipe in recipes
    ]
    return jsonify(result)

# Endpoint: Dodawanie przepisu do ulubionych
@app.route('/add_favorite', methods=['POST'])
def add_favorite():
    data = request.json
    new_favorite = Favorite(user_id=data['user_id'], recipe_id=data['recipe_id'])
    db.session.add(new_favorite)
    db.session.commit()
    return jsonify({"message": "Przepis dodany do ulubionych!"}), 201

# Endpoint: Pobieranie ulubionych przepisów
@app.route('/favorites/<int:user_id>', methods=['GET'])
def get_favorites(user_id):
    favorites = Favorite.query.filter_by(user_id=user_id).all()
    result = [
        {
            "id": favorite.id,
            "recipe_id": favorite.recipe_id
        }
        for favorite in favorites
    ]
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
