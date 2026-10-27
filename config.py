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

    # Security & Password Reset Token Salt
    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT', 'resume-portal-reset-salt')
    RESET_TOKEN_MAX_AGE = int(os.environ.get('RESET_TOKEN_MAX_AGE', 3600))  # 1 hour

    # Resend Email Configuration (resend.com) - Primary Service
    RESEND_API_KEY = os.environ.get('RESEND_API_KEY', '')
    RESEND_URL = os.environ.get('RESEND_URL', 'https://api.resend.com/emails')
    RESEND_FROM_ADDRESS = os.environ.get('RESEND_FROM_ADDRESS', 'onboarding@resend.dev')
    MAIL_FROM_ADDRESS = os.environ.get('MAIL_FROM_ADDRESS', os.environ.get('RESEND_FROM_ADDRESS', 'onboarding@resend.dev'))
    MAIL_FROM_NAME = os.environ.get('MAIL_FROM_NAME', 'ResumePortal Academic Nexus')

    # Active Provider: 'resend' (default), 'zeptomail', or 'smtp'
    EMAIL_PROVIDER = os.environ.get('EMAIL_PROVIDER', 'resend').lower()

    # Optional secondary provider settings (e.g. ZeptoMail for future custom domain)
    ZEPTOMAIL_API_KEY = os.environ.get('ZEPTOMAIL_API_KEY', '')
    ZEPTOMAIL_URL = os.environ.get('ZEPTOMAIL_URL', 'https://api.zeptomail.in/v1.1/email')
    EMAIL_DELIVERY_METHOD = os.environ.get('EMAIL_DELIVERY_METHOD', 'api').lower()
    SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.resend.com')
    SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
    SMTP_USERNAME = os.environ.get('SMTP_USERNAME', 'resend')
    SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', os.environ.get('RESEND_API_KEY', ''))
    SMTP_USE_TLS = os.environ.get('SMTP_USE_TLS', 'true').lower() in ('true', '1', 'yes')


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
