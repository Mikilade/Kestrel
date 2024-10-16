"""
Configuration module for the application.

This module loads environment variables from a .env file and defines a Config class
with configuration settings for the application. It uses the python-dotenv library
to load environment variables and the os module to access them.

The Config class includes settings for:
- SECRET_KEY: A secret key for the application
- SQLALCHEMY_DATABASE_URI: The database connection URL
- SQLALCHEMY_TRACK_MODIFICATIONS: A flag to disable SQLAlchemy modification tracking

Make sure to create a .env file in the root directory of your project with the
necessary environment variables (SECRET_KEY and DATABASE_URL) before running the application.
"""

import os
from dotenv import load_dotenv

# Load env variables from .env file
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False