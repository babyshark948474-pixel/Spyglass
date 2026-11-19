from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from flask_login import LoginManager
from dotenv import load_dotenv



db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'SECRET STUFF')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get( 'DATABASE_URL', 'mysql+pymysql://root:NOPEAKING@localhost:3306/testdb')

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'error'

    from .models import Users
    from .views import views
    from .auth import auth

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(Users, int(user_id))
    
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    with app.app_context():
        db.create_all()

    return app