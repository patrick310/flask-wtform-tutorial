"""Initialize app."""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

def create_app():
    """Construct the core flask_wtforms_tutorial."""
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object("config.Config")
    if os.getenv('DATABASE_URI'):
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://uzbiy6sxtg1wi:smTY464FvRGfYMB@35.202.17.55/dbekqfrcjb4dfy'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    
    db.init_app(app)
    
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .auth.models import User
    
    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

    with app.app_context():
        # Import parts of our flask_wtforms_tutorial
        '''
        from .auth import auth
        app.register_blueprint(auth.auth)
        
        from .admin import admin
        app.register_blueprint(admin.admin_bp, url_prefix='/admin')
        
        from .surveys import surveys
        app.register_blueprint(surveys.survey_bp)
        '''
        db.metadata.create_all(db.engine)

        user = User(id=1, email="kayla@mbusi.com", password= generate_password_hash("12345",method='sha256'), name="admin")

        db.session.add(user)
        db.session.commit()

        
        return app
