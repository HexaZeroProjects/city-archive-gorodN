"""Основное приложение Flask для архива обращений граждан."""
from datetime import date, datetime
from flask import Flask, render_template, request, redirect, url_for, make_response, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, AppealCategory, Appeal, User, News, init_db
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

# Настройка Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Для доступа к данной странице необходимо войти в систему.'
login_manager.login_message_category = 'info'


@login_manager.user_loader
def load_user(user_id):
    """Загрузка пользователя для Flask-Login."""
    return User.query.get(int(user_id))


def admin_required(f):
    """Декоратор для проверки прав администратора."""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        if not current_user.is_admin:
            flash('Недостаточно прав для доступа к данной странице.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


def get_theme():
    """Получение текущей темы из cookie или параметра запроса."""
    theme = request.args.get('theme')
    if theme in ['normal', 'accessible']:
        return theme
    theme = request.cookies.get('theme', 'normal')
    return theme if theme in ['normal', 'accessible'] else 'normal'


@app.route('/')
def index():
    """Главная страница."""
    theme = get_theme()
    # Получаем последние 3 новости для главной страницы
    latest_news = News.query.order_by(News.created_at.desc()).limit(3).all()
    response = make_response(render_template('index.html', latest_news=latest_news, theme=theme))
    if request.args.get('theme'):
        response.set_cookie('theme', theme, max_age=60*60*24*365)  # 1 год
    return response


@app.route('/types')
def types():
    """Страница "Виды обращений граждан"."""
    theme = get_theme()
    categories = AppealCategory.query.order_by(AppealCategory.name).all()
    response = make_response(render_template('types.html', categories=categories, theme=theme))
    if request.args.get('theme'):
        response.set_cookie('theme', theme, max_age=60*60*24*365)
    return response


@app.route('/storage')
def storage():
    """Страница "Организация хранения обращений"."""
    theme = get_theme()
    
    # Статистика по категориям
    category_stats = db.session.query(
        AppealCategory.name,
        db.func.count(Appeal.id).label('count')
    ).join(Appeal).group_by(AppealCategory.id, AppealCategory.name).all()
    
    # Статистика по годам
    year_stats = db.session.query(
        db.func.strftime('%Y', Appeal.date).label('year'),
        db.func.count(Appeal.id).label('count')
    ).group_by('year').order_by('year').all()
    
    response = make_response(render_template(
        'storage.html',
        category_stats=category_stats,
        year_stats=year_stats,
        theme=theme
    ))
    if request.args.get('theme'):
        response.set_cookie('theme', theme, max_age=60*60*24*365)
    return response


@app.route('/appeals')
@login_required
def appeals():
    """Страница "Архив обращений" с фильтром."""
    theme = get_theme()
    
    # Получаем все категории для выпадающего списка
    categories = AppealCategory.query.order_by(AppealCategory.name).all()
    
    # Получаем параметры фильтрации
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    category_id = request.args.get('category_id')
    status = request.args.get('status')
    
    # Начальный запрос
    query = Appeal.query
    
    # Применяем фильтры
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
            query = query.filter(Appeal.date >= date_from_obj)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
            query = query.filter(Appeal.date <= date_to_obj)
        except ValueError:
            pass
    
    if category_id and category_id != 'all':
        try:
            query = query.filter(Appeal.category_id == int(category_id))
        except ValueError:
            pass
    
    if status and status != 'all':
        query = query.filter(Appeal.status == status)
    
    # Если фильтры не заданы, показываем обращения за последний год
    if not any([date_from, date_to, category_id, status]):
        one_year_ago = date.today().replace(year=date.today().year - 1)
        query = query.filter(Appeal.date >= one_year_ago)
    
    # Получаем уникальные статусы из БД для выпадающего списка
    statuses = db.session.query(Appeal.status).distinct().order_by(Appeal.status).all()
    status_list = [s[0] for s in statuses]
    
    # Выполняем запрос
    appeals_list = query.order_by(Appeal.date.desc()).all()
    
    response = make_response(render_template(
        'appeals.html',
        appeals=appeals_list,
        categories=categories,
        statuses=status_list,
        date_from=date_from or '',
        date_to=date_to or '',
        selected_category=category_id or 'all',
        selected_status=status or 'all',
        theme=theme
    ))
    if request.args.get('theme'):
        response.set_cookie('theme', theme, max_age=60*60*24*365)
    return response


@app.route('/news')
def news():
    """Страница "Новости архива"."""
    theme = get_theme()
    news_list = News.query.order_by(News.created_at.desc()).all()
    response = make_response(render_template('news.html', news_list=news_list, theme=theme))
    if request.args.get('theme'):
        response.set_cookie('theme', theme, max_age=60*60*24*365)
    return response


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Страница входа в систему."""
    theme = get_theme()
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username and password:
            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password):
                login_user(user)
                next_page = request.args.get('next')
                return redirect(next_page or url_for('appeals'))
            else:
                flash('Неверное имя пользователя или пароль.', 'error')
        else:
            flash('Необходимо заполнить все поля.', 'error')
    
    response = make_response(render_template('login.html', theme=theme))
    if request.args.get('theme'):
        response.set_cookie('theme', theme, max_age=60*60*24*365)
    return response


@app.route('/logout')
def logout():
    """Выход из системы."""
    if current_user.is_authenticated:
        logout_user()
        flash('Вы успешно вышли из системы.', 'info')
    return redirect(url_for('index'))


@app.route('/contacts')
def contacts():
    """Страница "Контакты архива"."""
    theme = get_theme()
    response = make_response(render_template('contacts.html', theme=theme))
    if request.args.get('theme'):
        response.set_cookie('theme', theme, max_age=60*60*24*365)
    return response


# Административные маршруты для управления новостями
@app.route('/admin/news')
@login_required
@admin_required
def admin_news_list():
    """Список новостей для администратора."""
    theme = get_theme()
    news_list = News.query.order_by(News.created_at.desc()).all()
    response = make_response(render_template('admin/news_list.html', news_list=news_list, theme=theme))
    if request.args.get('theme'):
        response.set_cookie('theme', theme, max_age=60*60*24*365)
    return response


@app.route('/admin/news/create', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_news_create():
    """Создание новой новости."""
    theme = get_theme()
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        
        if title and content:
            news_item = News(title=title, content=content, created_at=datetime.utcnow())
            db.session.add(news_item)
            db.session.commit()
            flash('Новость успешно создана.', 'info')
            return redirect(url_for('admin_news_list'))
        else:
            flash('Необходимо заполнить все поля.', 'error')
    
    response = make_response(render_template('admin/news_form.html', news_item=None, theme=theme))
    if request.args.get('theme'):
        response.set_cookie('theme', theme, max_age=60*60*24*365)
    return response


@app.route('/admin/news/<int:news_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_news_edit(news_id):
    """Редактирование новости."""
    theme = get_theme()
    news_item = News.query.get_or_404(news_id)
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        
        if title and content:
            news_item.title = title
            news_item.content = content
            db.session.commit()
            flash('Новость успешно обновлена.', 'info')
            return redirect(url_for('admin_news_list'))
        else:
            flash('Необходимо заполнить все поля.', 'error')
    
    response = make_response(render_template('admin/news_form.html', news_item=news_item, theme=theme))
    if request.args.get('theme'):
        response.set_cookie('theme', theme, max_age=60*60*24*365)
    return response


@app.route('/admin/news/<int:news_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_news_delete(news_id):
    """Удаление новости."""
    news_item = News.query.get_or_404(news_id)
    db.session.delete(news_item)
    db.session.commit()
    flash('Новость успешно удалена.', 'info')
    return redirect(url_for('admin_news_list'))


@app.errorhandler(404)
def not_found(error):
    """Обработчик ошибки 404."""
    theme = get_theme()
    return render_template('404.html', theme=theme), 404


if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(debug=True)

