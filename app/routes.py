from app.models import User, Recipe
from flask import Blueprint, request, jsonify, render_template

main = Blueprint('main', __name__)

# Strona główna
@main.route('/')
def home():
    return render_template('index.html')

# Pobieranie listy przepisów
@main.route('/recipes', methods=['GET'])
def get_recipes():
    recipes = Recipe.query.all()
    return jsonify([
        {
            "id": recipe.id,
            "name": recipe.name,
            "category": recipe.category,
            "ingredients": recipe.ingredients,
            "steps": recipe.steps
        } for recipe in recipes
    ])

# Dodawanie nowego przepisu
@main.route('/recipes', methods=['POST'])
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
    return jsonify({"message": "Przepis został dodany pomyślnie!"}), 201

# Endpoints dla podstron
@main.route('/converter.html')
def converter():
    return render_template('converter.html')

@main.route('/register.html')
def register():
    return render_template('register.html')

@main.route('/login.html')
def login():
    return render_template('login.html')

@main.route('/favourites.html')
def favourites():
    return render_template('favourites.html')

@main.route('/forum.html')
def forum():
    return render_template('forum.html')

@main.route('/faq.html')
def faq():
    return render_template('faq.html')

@main.route('/regulamin.html')
def regulamin():
    return render_template('regulamin.html')

@main.route('/contact.html')
def contact():
    return render_template('contact.html')

@main.route('/dinners.html')
def dinners():
    return render_template('dinners.html')

@main.route('/map.html')
def map():
    return render_template('map.html')

@main.route('/breakfast.html')
def breakfast():
    return render_template('breakfast.html')

@main.route('/drinks.html')
def drinks():
    return render_template('drinks.html')

@main.route('/snacks.html')
def snacks():
    return render_template('snacks.html')

@main.route('/appetizers.html')
def appetizers():
    return render_template('appetizers.html')

@main.route('/suppers.html')
def suppers():
    return render_template('suppers.html')

@main.route('/desserts.html')
def desserts():
    return render_template('desserts.html')

@main.route('/add_recipes.html')
def add_recipes():
    return render_template('add_recipes.html')

@main.route('/recipes.html')
def recipes():
    return render_template('recipes.html')


@main.route('/index.html')
def index():
    return render_template('index.html')


from werkzeug.security import generate_password_hash
from flask import Blueprint, request, jsonify
from app.models import User
from app import db


@main.route('/register', methods=['POST'])
def register_user():
    data = request.json

    # Sprawdzenie, czy wszystkie pola są obecne
    if not data.get('name') or not data.get('email') or not data.get('password'):
        return jsonify({"error": "Wszystkie pola są wymagane"}), 400

    # Sprawdzenie, czy użytkownik już istnieje
    existing_user = User.query.filter_by(email=data['email']).first()
    if existing_user:
        return jsonify({"error": "Użytkownik z takim e-mailem już istnieje"}), 400

    # Utworzenie nowego użytkownika i zapisanie do bazy
    new_user = User(
        name=data['name'],
        email=data['email'],
        password=data['password']  # Zapisujemy hasło bezpośrednio
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "Rejestracja zakończona sukcesem!"}), 201


@main.route('/test_db')
def test_db():
    try:
        result = db.session.execute('SELECT 1')
        return "Połączenie z bazą działa!", 200
    except Exception as e:
        return f"Błąd połączenia z bazą: {e}", 500
