from flask import Flask
from config import Config
from app.extensions import db, migrate
from flask_cors import CORS

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    CORS(app)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Import and register blueprints
    from app.routes import bp as main_bp
    app.register_blueprint(main_bp)

    return app