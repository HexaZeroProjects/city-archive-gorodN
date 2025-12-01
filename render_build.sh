#!/bin/bash
# Скрипт для инициализации БД при деплое на Render
python -c "from app import app; from models import init_db; app.app_context().push(); init_db()"

