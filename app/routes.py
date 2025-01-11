from flask import Blueprint, request, jsonify, render_template, current_app
from app.models import User
from flask_login import login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_required, current_user
from app import db





main = Blueprint('main', __name__)


@main.route('/login', methods=['POST'])
def login():
    email = request.json.get('email')
    password = request.json.get('password')
    user = User.query.filter_by(email=email).first()

    if user and check_password_hash(user.password, password):
        login_user(user)
        return jsonify({"message": "Zalogowano pomyślnie", "redirect_url": "/account.html"}), 200
    else:
        return jsonify({"message": "Nieprawidłowy e-mail lub hasło"}), 401


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

# Dodawanie nowego przepisu (tylko dla zalogowanych użytkowników)
@main.route('/recipes', methods=['POST'])
@login_required
def add_recipe():
    data = request.json

    new_recipe = Recipe(
        name=data['name'],
        category=data['category'],
        ingredients=data['ingredients'],
        steps=data['steps'],
        user_id=current_user.id
    )
    try:
        db.session.add(new_recipe)
        db.session.commit()
        return jsonify({"message": "Przepis został dodany pomyślnie!"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Błąd podczas dodawania przepisu: {str(e)}"}), 500

# Endpointy do renderowania stron HTML (dynamiczne)
@main.route('/<page>.html')
def render_page(page):
    try:
        return render_template(f"{page}.html")
    except Exception:
        return "Strona nie została znaleziona", 404

# Rejestracja użytkownika
@main.route('/register', methods=['POST'])
def register_user():
    data = request.json
    if not data.get('name') or not data.get('email') or not data.get('password'):
        return jsonify({"error": "Wszystkie pola są wymagane"}), 400

    existing_user = User.query.filter_by(email=data['email']).first()
    if existing_user:
        return jsonify({"error": "Użytkownik z takim e-mailem już istnieje"}), 400

    # Hashowanie hasła
    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')


    new_user = User(
        name=data['name'],
        email=data['email'],
        password=hashed_password
    )
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "Rejestracja zakończona sukcesem!"}), 201





# Test połączenia z bazą danych
@main.route('/test_db')
def test_db():
    try:
        db.session.execute('SELECT 1')
        return "Połączenie z bazą działa!", 200
    except Exception as e:
        return f"Błąd połączenia z bazą: {e}", 500

# Przelicznik kuchenny - jednostki
@main.route('/api/convert', methods=['POST'])
def convert_units():
    data = request.json
    product_name = data.get('product')
    input_value = data.get('value')
    input_unit = data.get('input_unit')
    output_unit = data.get('output_unit')

    product = Product.query.filter_by(name=product_name).first()
    if not product:
        return jsonify({"error": "Nie znaleziono produktu"}), 404

    conversion_factor = product.gram_to_ml if input_unit == 'ml' and output_unit == 'gram' else 1 / product.gram_to_ml
    result = input_value * conversion_factor

    return jsonify({
        "input_value": input_value,
        "input_unit": input_unit,
        "output_value": round(result, 2),
        "output_unit": output_unit
    })

# Przelicznik foremek
@main.route('/api/convert_shape', methods=['POST'])
def convert_shape():
    data = request.json
    recipe_width = data.get('recipe_width')
    recipe_height = data.get('recipe_height')
    home_width = data.get('home_width')
    home_height = data.get('home_height')

    if not all([recipe_width, recipe_height, home_width, home_height]):
        return jsonify({"error": "Brak wymiarów foremki"}), 400

    recipe_volume = recipe_width * recipe_height
    home_volume = home_width * home_height
    scaling_factor = home_volume / recipe_volume

    return jsonify({
        "scaling_factor": round(scaling_factor, 2)
    })

@main.route('/account', methods=['GET'])
@login_required
def account_page():
    return render_template('account.html')


@main.route('/account/data', methods=['GET'])
@login_required
def account_data():
    user_data = {
        "name": current_user.name,
        "email": current_user.email,
        "recipes": [
            {
                "id": recipe.id,
                "name": recipe.name,
                "category": recipe.category,
                "ingredients": recipe.ingredients,
                "steps": recipe.steps,
            } for recipe in current_user.recipes  # Relacja `User` -> `Recipe`
        ],
        "favorites": [
            {
                "id": fav.recipe.id,
                "name": fav.recipe.name,
                "category": fav.recipe.category
            } for fav in current_user.favorites  # Relacja `User` -> `Favorite`
        ]
    }
    return jsonify(user_data), 200



@main.route('/is_logged_in', methods=['GET'])
def is_logged_in():
    if current_user.is_authenticated:
        return jsonify({"logged_in": True}), 200
    return jsonify({"logged_in": False}), 200


@main.route('/logout', methods=['POST'])
@login_required
def logout():
    try:
        logout_user()
        return jsonify({"message": "Wylogowano pomyślnie"}), 200
    except Exception as e:
        current_app.logger.error(f"Błąd podczas wylogowywania: {str(e)}")
        return jsonify({"error": f"Błąd podczas wylogowywania: {str(e)}"}), 500




@main.route('/test_login', methods=['POST'])
def test_login():
    email = request.json.get('email')
    password = request.json.get('password')

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({"error": "Użytkownik nie istnieje"}), 404

    if check_password_hash(user.password, password):
        return jsonify({"message": "Logowanie działa poprawnie!"}), 200
    else:
        return jsonify({"error": "Nieprawidłowe hasło"}), 401


@main.route('/session_status', methods=['GET'])
def session_status():
    if current_user.is_authenticated:
        return jsonify({"status": "authenticated", "user_id": current_user.id}), 200
    return jsonify({"status": "unauthenticated"}), 200
