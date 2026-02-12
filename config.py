class Config:
    """Base configuration"""
    SECRET_KEY = 'dev-secret-key-12345-change-in-production'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # In-memory database - NO FILES!
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = 2592000
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False


class TestingConfig(Config):
    DEBUG = True
    TESTING = True


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
