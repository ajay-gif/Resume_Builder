import os
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

def get_database_uri():
    """
    Retrieves and formats database URI.
    Render provides PostgreSQL connection strings with 'postgres://',
    which SQLAlchemy 1.4+ / 2.0+ requires to be 'postgresql://'.
    """
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        return database_url
    # Local fallback default if DATABASE_URL is not set
    return 'sqlite:///resumes.db'


class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-dev-secret-change-in-prod-resume-portal')
    SQLALCHEMY_DATABASE_URI = get_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Production-grade PostgreSQL connection pooling (vital for Render)
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }

    # Billing & Monetization Config (Phase 4)
    DEFAULT_FREE_DOWNLOADS = int(os.environ.get('DEFAULT_FREE_DOWNLOADS', 1))
    PAYMENT_WEBHOOK_SECRET = os.environ.get('PAYMENT_WEBHOOK_SECRET', 'test-webhook-secret-key')


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    # Ensure a stronger secret key in real production deployments
    SECRET_KEY = os.environ.get('SECRET_KEY', os.urandom(24).hex())


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_ENGINE_OPTIONS = {}
    WTF_CSRF_ENABLED = False


config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
