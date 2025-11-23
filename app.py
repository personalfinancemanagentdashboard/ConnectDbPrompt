import os
from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    from models.user import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.api import api_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(api_bp)
    
    @app.route('/')
    def index():
        return redirect(url_for('dashboard.index'))
    
    with app.app_context():
        import models
        db.create_all()
    
    return app


app = create_app()
