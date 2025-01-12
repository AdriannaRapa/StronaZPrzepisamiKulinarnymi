from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail


db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/foodlab_db'
    app.config['SECRET_KEY'] = 'your_secret_key'



    # Konfiguracja serwera SMTP (przykład dla Gmail)
    app.config['MAIL_SERVER'] = 'poczta.interia.pl'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USE_SSL'] = True  # Włącz SSL
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USERNAME'] = 'foodlab@interia.pl'  # Zastąp swoim e-mailem
    app.config['MAIL_PASSWORD'] = 'PoliBuda#321'          # Zastąp swoim hasłem
    app.config['MAIL_DEFAULT_SENDER'] = 'foodlab@interia.pl'
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
