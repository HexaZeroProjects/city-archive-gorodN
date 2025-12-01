"""Конфигурация приложения Flask."""
import os

class Config:
    """Базовый класс конфигурации."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///archive.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

