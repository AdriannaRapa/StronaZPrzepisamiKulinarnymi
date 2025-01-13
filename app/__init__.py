from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
import os  # Dodaj ten import na początku pliku
from flask_migrate import Migrate


migrate = Migrate()
db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/foodlab_db?charset=utf8mb4'

    app.config['SECRET_KEY'] = 'your_secret_key'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = 'static/uploads'  # Folder na zdjęcia przepisów
    app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)  # Utwórz folder, jeśli nie istnieje

    # Konfiguracja serwera SMTP (przykład dla interi)
    app.config['MAIL_SERVER'] = 'poczta.interia.pl'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USE_SSL'] = True  # Włącz SSL
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USERNAME'] = 'twojmail@interia.pl'  # Zastąp swoim e-mailem
    app.config['MAIL_PASSWORD'] = 'twojehasełko'          # Zastąp swoim hasłem
    app.config['MAIL_DEFAULT_SENDER'] = 'twojmail@interia.pl'
    app.config['MAIL_DEBUG'] = True

    # Inicjalizacja bazy danych i LoginManager
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'  # Trasa logowania
    mail.init_app(app)



    # Funkcja user_loader
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.query.get(int(user_id))  # Ładowanie użytkownika na podstawie ID

    # Rejestracja blueprinta
    from app.routes import main
    app.register_blueprint(main)

    return app

