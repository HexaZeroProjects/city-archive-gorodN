# Инструкция по деплою на Render.com

## Проблема: Render использует неправильную команду запуска

Если Render все еще пытается запустить `gunicorn your_application.wsgi`, выполните следующие шаги:

## Решение:

### Шаг 1: Убедитесь, что Procfile закоммичен в Git

```bash
git add Procfile
git commit -m "Add Procfile for Render deployment"
git push
```

### Шаг 2: В Render Dashboard

1. Откройте ваш сервис: **city-archive-gorodN**
2. Перейдите в **Settings**
3. Найдите раздел **"Build & Deploy"** или **"Environment"**
4. Проверьте следующие настройки:

#### Build Command:
```
pip install -r requirements.txt
```

#### Start Command:
**ОСТАВЬТЕ ПУСТЫМ** - Render должен автоматически использовать Procfile

Если поле Start Command заполнено и содержит `gunicorn your_application.wsgi`:
- **УДАЛИТЕ** это содержимое
- Оставьте поле **ПУСТЫМ**
- Сохраните изменения

### Шаг 3: Перезапустите деплой

1. В Render Dashboard нажмите **"Manual Deploy"**
2. Выберите **"Deploy latest commit"**
3. Дождитесь завершения деплоя

### Шаг 4: Проверьте логи

После деплоя проверьте логи. Должна быть строка:
```
Running 'gunicorn --bind 0.0.0.0:$PORT app:app'
```

Если все еще видите `gunicorn your_application.wsgi`, значит:
- Procfile не закоммичен в Git
- Или Render кэширует старую версию

## Альтернативное решение (если Procfile не работает):

Если Procfile все еще не работает, можно создать файл `.render.yaml` в корне проекта:

```yaml
services:
  - type: web
    name: city-archive-gorodN
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn --bind 0.0.0.0:$PORT app:app
```

Но лучше использовать Procfile - это стандартный способ для Python приложений.

## Проверка:

После успешного деплоя:
1. Откройте ваш сайт: https://city-archive-gorodn.onrender.com
2. Должна загрузиться главная страница
3. Можно войти: admin/admin123 или user/user123


