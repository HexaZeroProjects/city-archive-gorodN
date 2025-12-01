"""Конфигурация приложения Flask."""
import os

class Config:
    """Базовый класс конфигурации."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    # Для Render: используем DATABASE_URL если есть, иначе SQLite
    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith('postgres://'):
        # Конвертируем postgres:// в postgresql:// для SQLAlchemy
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_DATABASE_URI = database_url or 'sqlite:///archive.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

