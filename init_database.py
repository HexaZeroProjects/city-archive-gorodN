"""Скрипт для инициализации базы данных."""
from app import app
from models import init_db

if __name__ == '__main__':
    with app.app_context():
        init_db()
    print('База данных успешно инициализирована!')
    print('Теперь вы можете запустить приложение командой: flask run')

