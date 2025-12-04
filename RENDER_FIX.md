# КРИТИЧЕСКОЕ РЕШЕНИЕ для Render.com

## Проблема:
Render игнорирует Procfile и использует `gunicorn your_application.wsgi`

## РЕШЕНИЕ - нужно вручную изменить в Dashboard:

### Вариант 1: Через Settings (ОБЯЗАТЕЛЬНО!)

1. Откройте ваш сервис на Render: **city-archive-gorodN**
2. Перейдите в **Settings** (вкладка вверху)
3. Прокрутите вниз до раздела **"Build & Deploy"**
4. Найдите поле **"Start Command"**
5. **УДАЛИТЕ** все содержимое из этого поля (если там `gunicorn your_application.wsgi`)
6. Введите: `gunicorn --bind 0.0.0.0:$PORT app:app`
7. **Сохраните изменения** (кнопка Save внизу страницы)
8. Нажмите **"Manual Deploy"** → **"Deploy latest commit"**

### Вариант 2: Если поля Start Command нет

1. Откройте **Settings**
2. Найдите раздел **"Environment"**
3. Добавьте переменную окружения:
   - Key: `START_COMMAND`
   - Value: `gunicorn --bind 0.0.0.0:$PORT app:app`

### Вариант 3: Пересоздать сервис (если ничего не помогает)

1. **Удалите** текущий сервис
2. Создайте **новый Web Service**
3. Подключите тот же репозиторий
4. Render автоматически подхватит Procfile или render.yaml

## Важно:
- Procfile уже в репозитории: `web: gunicorn --bind 0.0.0.0:$PORT app:app`
- render.yaml тоже добавлен
- Но Render использует команду из настроек Dashboard, а не из файлов!

## После исправления:
Проверьте логи - должна быть строка:
```
==> Running 'gunicorn --bind 0.0.0.0:$PORT app:app'
```


