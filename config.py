import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'smart-grocery-super-secret-key-2026')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'database.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Business Logic Defaults
    DEFAULT_DEAD_STOCK_DAYS = 30
    DEFAULT_MAX_STOCK_LEVEL = 200
    EXPORTS_DIR = os.path.join(BASE_DIR, 'exports')
