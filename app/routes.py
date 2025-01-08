from flask import Blueprint, request, jsonify, render_template
from flask_login import login_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User, Recipe, Product
from app import db

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

# Dodawanie nowego przepisu (tylko dla zalogowanych użytkowników)
@main.route('/recipes', methods=['POST'])
@login_required
def add_recipe():
    data = request.json

    # Tworzenie przepisu z przypisaniem do zalogowanego użytkownika
    new_recipe = Recipe(
        name=data['name'],
        category=data['category'],
        ingredients=data['ingredients'],
        steps=data['steps'],
        user_id=current_user.id  # Przepis należy do aktualnie zalogowanego użytkownika
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

    new_user = User(
        name=data['name'],
        email=data['email'],
        password=data['password']  # Zapisywanie hasła w jawnej formie (niesugerowane do produkcji)
    )
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "Rejestracja zakończona sukcesem!"}), 201



# Logowanie użytkownika
@main.route('/login', methods=['POST'])
def login_user_route():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Proszę podać e-mail i hasło"}), 400

    # Debugowanie: sprawdź, jakie dane są przesyłane
    print(f"Logowanie: email={email}, password={password}")

    # Znajdź użytkownika w bazie
    user = User.query.filter_by(email=email).first()

    if user:
        print(f"Znaleziono użytkownika: {user.email}, password in DB: {user.password}")
    else:
        print("Użytkownik nie został znaleziony")

    # Porównanie hasła
    if user and user.password == password:
        login_user(user)
        print("Hasło poprawne, logowanie użytkownika")
        return jsonify({"message": "Zalogowano pomyślnie"}), 200
    else:
        print("Nieprawidłowy e-mail lub hasło")
        return jsonify({"error": "Nieprawidłowy e-mail lub hasło"}), 401



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

    # Pobranie danych o produkcie
    product = Product.query.filter_by(name=product_name).first()
    if not product:
        return jsonify({"error": "Nie znaleziono produktu"}), 404

    # Przeliczanie jednostek
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