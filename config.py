import os
from datetime import timedelta

class Config:
    """Base configuration with shared settings."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback-development-key-12345')
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    """Development-specific settings."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///dev_database.model'

class ProductionConfig(Config):
    """Production-specific settings."""
    DEBUG = False
    # Enforce reading sensitive production URIs from environment variables
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
