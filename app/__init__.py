"""
This module creates and configures a Flask application.

The create_app function is responsible for:
1. Initializing the Flask application
2. Loading configuration from a Config object
3. Setting up Cross-Origin Resource Sharing (CORS)
4. Initializing database and migration extensions
5. Registering blueprints for routing

The function returns the configured Flask application instance.

Dependencies:
- Flask: Web framework
- Config: Application configuration (imported from config.py)
- db, migrate: Database and migration extensions (imported from app.extensions)
- CORS: Cross-Origin Resource Sharing extension
- bp: Main blueprint for routes (imported from app.routes)
"""

from flask import Flask
from config import Config
from app.extensions import db, migrate
from flask_cors import CORS
from dotenv import load_dotenv
import os

def create_app(config_class=Config, test_case=False):
    """
    Create and configure an instance of the Flask application.

    This function:
    1. Initializes a new Flask app
    2. Applies configuration from the specified config_class
    3. Sets up Cross-Origin Resource Sharing (CORS)
    4. Initializes database and migration extensions
    5. Registers the main blueprint for routing

    Args:
        config_class (object): The configuration class to use. Defaults to Config.

    Returns:
        Flask: A configured Flask application instance.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)
    if test_case:
        load_dotenv
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('TEST_DB_URL')
    CORS(app)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Import and register blueprints
    from app.routes import bp as main_bp
    app.register_blueprint(main_bp)

    return app