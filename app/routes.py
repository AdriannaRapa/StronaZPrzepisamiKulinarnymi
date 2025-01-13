from flask import Blueprint, flash, redirect, request, jsonify, url_for, render_template, current_app, session
from app.models import User, Favorite, Recipe
from flask_login import login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
import re
from flask_mail import Message
from app import mail, db
import secrets
from werkzeug.utils import secure_filename
from flask_login import login_required, current_user

main = Blueprint('main', __name__)


@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        # Wyświetlenie formularza logowania
        return render_template('login.html')

    if request.method == 'POST':
        # Sprawdzenie, czy dane są przesyłane w formacie JSON
        if request.is_json:
            data = request.get_json()
            email = data.get('email')
            password = data.get('password')
        else:
            # Dane z formularza HTML
            email = request.form.get('email')
            password = request.form.get('password')

        # Logika sprawdzania danych użytkownika
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            # Odpowiedź JSON, jeśli żądanie pochodzi z JavaScript
            if request.is_json:
                return jsonify({"message": "Zalogowano pomyślnie", "redirect_url": "/account.html"}), 200
            # Przekierowanie, jeśli pochodzi z formularza HTML
            return redirect(url_for('main.account'))

        # Obsługa błędów logowania
        if request.is_json:
            return jsonify({"message": "Nieprawidłowy e-mail lub hasło"}), 401
        else:
            flash("Nieprawidłowy e-mail lub hasło")
            return redirect(url_for('main.login'))


# Strona główna
@main.route('/')
def home():
    return render_template('index.html')


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
    try:
        db.session.add(new_user)
        db.session.commit()

        # Wyślij e-mail powitalny
        send_welcome_email(new_user.email, new_user.name)

        return jsonify({"message": "Rejestracja zakończona sukcesem!"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Błąd podczas rejestracji: {str(e)}"}), 500



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


@main.route('/api/user', methods=['GET'])
def get_user_data():
    user = current_user
    if user.is_authenticated:
        return jsonify({
            "name": user.name,
            "email": user.email,
            "password": "********",  # Hasło ukryte
            "join_date": user.join_date.strftime('%Y-%m-%d')
        })
    return jsonify({"error": "User not authenticated"}), 401


@main.route('/api/user/update_name', methods=['POST'])
@login_required
def update_user_name():
    new_name = request.json.get('name')
    if not new_name:
        return jsonify({"error": "Name cannot be empty"}), 400

    user = current_user
    user.name = new_name
    db.session.commit()
    return jsonify({"message": "Name updated successfully"})


@main.route('/api/user/update_email', methods=['POST'])
@login_required
def update_user_email():
    new_email = request.json.get('email')

    # Walidacja formatu e-maila
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if not re.match(email_regex, new_email):
        return jsonify({"error": "Niepoprawny format e-maila"}), 400

    # Sprawdź, czy email jest podany
    if not new_email:
        return jsonify({"error": "Email nie może być pusty"}), 400

    # Sprawdź, czy nowy email jest unikalny
    existing_user = User.query.filter_by(email=new_email).first()
    if existing_user:
        return jsonify({"error": "Podany e-mail już istnieje w systemie"}), 400

    try:
        # Aktualizuj email użytkownika
        user = current_user
        user.email = new_email
        db.session.commit()
        return jsonify({"message": "Adres e-mail został zaktualizowany pomyślnie", "email": new_email}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Błąd podczas aktualizacji e-maila: {str(e)}"}), 500



@main.route('/api/user/update_password', methods=['POST'])
@login_required
def update_password():
    data = request.json
    current_password = data.get('current_password')
    new_password = data.get('new_password')

    # Walidacja: sprawdź, czy oba pola są wypełnione
    if not current_password or not new_password:
        return jsonify({"error": "Oba pola są wymagane"}), 400

    # Sprawdzenie poprawności bieżącego hasła
    if not check_password_hash(current_user.password, current_password):
        return jsonify({"error": "Nieprawidłowe bieżące hasło"}), 400

    # Walidacja nowego hasła (długość, inne wymagania)
    if len(new_password) < 8:
        return jsonify({"error": "Hasło musi mieć co najmniej 8 znaków"}), 400

    # Zaktualizuj hasło (zahashowane)
    current_user.password = generate_password_hash(new_password)
    db.session.commit()

    return jsonify({"message": "Hasło zostało zaktualizowane"}), 200




@main.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '').strip()  # Pobierz zapytanie z parametrów URL
    if not query:
        return render_template('search_results.html', recipes=[], query=query)

    # Wyszukiwanie w tabeli Recipe
    results = Recipe.query.filter(
        (Recipe.name.ilike(f"%{query}%")) | (Recipe.description.ilike(f"%{query}%"))
    ).all()

    # Przekazanie wyników do szablonu
    return render_template('search_results.html', recipes=results, query=query)


@main.route('/delete-account', methods=['DELETE'])
@login_required
def delete_account():
    try:
        # Pobierz bieżącego użytkownika
        user = current_user

        # Usuń wszystkie przepisy użytkownika
        Recipe.query.filter_by(user_id=user.id).delete()

        # Usuń wszystkie ulubione przepisy użytkownika
        Favorite.query.filter_by(user_id=user.id).delete()

        # Usuń użytkownika z bazy danych
        db.session.delete(user)
        db.session.commit()

        # Wyloguj użytkownika i usuń sesję
        logout_user()

        return jsonify({'message': 'Konto zostało pomyślnie usunięte.'}), 200

    except Exception as e:
        db.session.rollback()
        print('Błąd podczas usuwania konta:', e)
        return jsonify({'error': 'Błąd serwera podczas usuwania konta.'}), 500


# Funkcja do wysyłania e-maila powitalnego
def send_welcome_email(email, name):
    try:
        msg = Message(
            subject="Witamy w FoodLab!",
            recipients=[email],
            body=f"Cześć {name},\n\nDziękujemy za rejestrację w FoodLab. Mamy nadzieję, że znajdziesz tu mnóstwo inspiracji kulinarnych!\n\nPozdrawiamy,\nZespół FoodLab"
        )
        mail.send(msg)
        print(f"E-mail powitalny wysłany do {email}")
    except Exception as e:
        print(f"Błąd podczas wysyłania e-maila: {e}")

@main.route('/forgot-password', methods=['POST'])
def forgot_password():
    email = request.form.get('email')

    # Znajdź użytkownika po e-mailu
    user = User.query.filter_by(email=email).first()
    if not user:
        flash("Nie znaleziono użytkownika z tym adresem e-mail.", "danger")
        return redirect(url_for('main.forgot_password_page'))

    # Wygeneruj token i wyślij e-mail
    reset_token = secrets.token_urlsafe(32)
    user.reset_token = reset_token
    db.session.commit()

    reset_url = url_for('main.reset_password', token=reset_token, _external=True)
    send_reset_email(email, reset_url)

    flash("Link do resetowania hasła został wysłany na podany adres e-mail.", "success")
    return redirect(url_for('main.login'))  # Przekierowanie na stronę logowania


def send_reset_email(email, reset_url):
    try:
        msg = Message(
            subject="Resetowanie hasła - FoodLab",
            recipients=[email],
            body=f"Kliknij w poniższy link, aby zresetować swoje hasło:\n{reset_url}\n\nJeśli nie prosiłeś o resetowanie hasła, zignoruj tę wiadomość."
        )
        mail.send(msg)
        print(f"E-mail do resetowania hasła wysłany do {email}")
    except Exception as e:
        print(f"Błąd podczas wysyłania e-maila: {e}")

@main.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user = User.query.filter_by(reset_token=token).first()
    if not user:
        flash("Nieprawidłowy token", "danger")
        return redirect(url_for('main.login'))  # Endpoint strony logowania

    if request.method == 'POST':
        new_password = request.form.get('password')
        user.password = generate_password_hash(new_password, method='pbkdf2:sha256')
        user.reset_token = None
        db.session.commit()
        flash("Hasło zostało pomyślnie zresetowane!", "success")
        return redirect(url_for('main.login'))  # Endpoint strony logowania

    return render_template('reset_password.html')  # Strona resetowania hasła



def allowed_file(filename):
    allowed_extensions = current_app.config['ALLOWED_EXTENSIONS']
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

@main.route('/recipes', methods=['POST'])
@login_required
def add_recipe():
    if 'recipe-image' not in request.files:
        return jsonify({"error": "Zdjęcie przepisu jest wymagane"}), 400

    file = request.files['recipe-image']
    if not file or not allowed_file(file.filename):
        return jsonify({"error": "Nieprawidłowy format pliku"}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    data = request.form  # Pobieramy dane z formularza
    if not data.get('recipe-name') or not data.get('recipe-category') or not data.get('recipe-ingredients') or not data.get('recipe-steps'):
        return jsonify({"error": "Wszystkie pola są wymagane"}), 400

    try:
        new_recipe = Recipe(
            name=data['recipe-name'],
            category=data['recipe-category'],
            ingredients=data['recipe-ingredients'],
            steps=data['recipe-steps'],
            user_id=current_user.id,
            image_url=file_path  # Ścieżka do zapisanego pliku
        )

        db.session.add(new_recipe)
        db.session.commit()

        return jsonify({"message": "Przepis został dodany pomyślnie!"}), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Błąd podczas dodawania przepisu: {e}")
        return jsonify({"error": f"Błąd podczas dodawania przepisu: {str(e)}"}), 500


@main.route('/api/recipes', methods=['GET'])
def get_recipes():
    try:
        category = request.args.get('category')
        if category:
            recipes = Recipe.query.filter_by(category=category).all()
        else:
            recipes = Recipe.query.all()

        recipes_data = [
            {
                "id": recipe.id,
                "name": recipe.name,
                "category": recipe.category,
                "ingredients": recipe.ingredients,
                "steps": recipe.steps,
                "image_url": f"/{recipe.image_url}"
            }
            for recipe in recipes
        ]
        return jsonify(recipes_data), 200
    except Exception as e:
        current_app.logger.error(f"Błąd podczas pobierania przepisów: {e}")
        return jsonify({"error": "Nie udało się pobrać przepisów"}), 500



@main.route('/favorite/<int:recipe_id>', methods=['POST'])
@login_required
def add_to_favorites(recipe_id):
    try:
        # Logika dodawania do ulubionych
        favorite = Favorite(user_id=current_user.id, recipe_id=recipe_id)
        db.session.add(favorite)
        db.session.commit()
        return jsonify({"message": "Przepis dodano do ulubionych"}), 200
    except Exception as e:
        current_app.logger.error(f"Błąd podczas dodawania do ulubionych: {e}")
        return jsonify({"error": "Nie udało się dodać do ulubionych"}), 500


@main.route('/recipe/<int:recipe_id>', methods=['GET'])
def recipe_details(recipe_id):
    try:
        recipe = Recipe.query.get_or_404(recipe_id)
        current_app.logger.info(f"Ścieżka obrazu dla przepisu {recipe.name}: {recipe.image_url}")
        return render_template('recipe_details.html', recipe=recipe)
    except Exception as e:
        current_app.logger.error(f"Błąd: {e}")
        return redirect(url_for('main.index'))


@main.route('/contact', methods=['POST'])
def contact():
    try:
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')

        if not name or not email or not message:
            return jsonify({"error": "Wszystkie pola są wymagane"}), 400

        # Tworzenie wiadomości
        msg = Message(
            subject=f"Nowa wiadomość od {name} ({email})",  # Adres e-mail w temacie
            sender="twojmail@interia.pl",  # Zawsze wysyłaj z adresu Interia
            recipients=["twojmail@interia.pl"],
            body=f"Imię i nazwisko: {name}\nE-mail nadawcy: {email}\n\nWiadomość:\n{message}"
        )
        mail.send(msg)
        return jsonify({"message": "Wiadomość została wysłana pomyślnie"}), 200

    except Exception as e:
        print(f"Błąd podczas wysyłania e-maila: {e}")
        return jsonify({"error": "Wystąpił błąd podczas wysyłania wiadomości"}), 500
