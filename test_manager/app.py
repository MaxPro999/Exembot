import os
from flask import Flask, render_template, request, redirect, send_from_directory, url_for, session, flash, send_file, abort
from werkzeug.utils import secure_filename
from auth import AuthManager
from test_manager import TestManager

# Инициализация Flask приложения
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY') or 'dev-secret-key'  # Безопасный ключ
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB лимит загрузки
app.config['ALLOWED_EXTENSIONS'] = {'csv', 'xlsx', 'xls'}

# Инициализация менеджеров
auth_manager = AuthManager()
test_manager = None  # Будет инициализирован после входа пользователя

def allowed_file(filename):
    """Проверяет допустимость расширения файла"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.before_request
def initialize_managers():
    """Инициализирует менеджер тестов при каждом запросе для аутентифицированных пользователей"""
    global test_manager
    if 'user_id' in session and test_manager is None:
        test_manager = TestManager(session['user_id'])

@app.route('/')
def home():
    """Главная страница - перенаправляет на вход или личный кабинет"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('main'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Обработка входа пользователя"""
    if request.method == 'POST':
        try:
            login = request.form.get('login', '').strip()
            password = request.form.get('password', '').strip()
            
            if not login or not password:
                flash('Заполните все поля', 'danger')
                return redirect(url_for('login'))
            
            success, msg = auth_manager.login(login, password)
            
            if success:
                session['user_id'] = auth_manager.current_user_id
                # Инициализация менеджера тестов
                global test_manager
                test_manager = TestManager(session['user_id'])
                flash(msg, 'success')
                return redirect(url_for('main'))
            else:
                flash(msg, 'danger')
        except Exception as e:
            flash(f'Ошибка входа: {str(e)}', 'danger')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Обработка регистрации нового пользователя"""
    if request.method == 'POST':
        try:
            login = request.form.get('login', '').strip()
            password = request.form.get('password', '').strip()
            confirm_password = request.form.get('confirm_password', '').strip()
            
            if not all([login, password, confirm_password]):
                flash('Заполните все поля', 'danger')
                return redirect(url_for('register'))
                
            if password != confirm_password:
                flash('Пароли не совпадают', 'danger')
                return redirect(url_for('register'))
                
            success, msg = auth_manager.register(login, password)
            
            if success:
                flash(msg, 'success')
                return redirect(url_for('login'))
            else:
                flash(msg, 'danger')
        except Exception as e:
            flash(f'Ошибка регистрации: {str(e)}', 'danger')
    
    return render_template('register.html')

@app.route('/main')
def main():
    """Главная страница пользователя"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if test_manager is None:
        flash('Ошибка инициализации системы', 'danger')
        return redirect(url_for('login'))
    
    try:
        tests = test_manager.get_user_tests()
        return render_template('main.html', tests=tests)
    except Exception as e:
        flash(f'Ошибка загрузки тестов: {str(e)}', 'danger')
        return redirect(url_for('login'))

@app.route('/upload', methods=['POST'])
def upload_file():
    """Загрузка файла с тестом"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if 'file' not in request.files:
        flash('Файл не выбран', 'danger')
        return redirect(url_for('main'))
    
    file = request.files['file']
    
    if file.filename == '':
        flash('Файл не выбран', 'danger')
        return redirect(url_for('main'))
    
    if file and allowed_file(file.filename):
        try:
            filename = secure_filename(file.filename)
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            session['current_file'] = filepath
            return render_template('test_form.html', filename=filename)
        except Exception as e:
            flash(f'Ошибка загрузки файла: {str(e)}', 'danger')
    else:
        flash('Недопустимый формат файла', 'danger')
    
    return redirect(url_for('main'))

@app.route('/save_test', methods=['POST'])
def save_test():
    """Сохранение теста в систему"""
    if 'user_id' not in session or 'current_file' not in session:
        flash('Сначала загрузите файл', 'danger')
        return redirect(url_for('main'))
    
    try:
        test_object = request.form.get('object', '').strip()
        test_type = request.form.get('type', '').strip()
        count = int(request.form.get('count', 1))
        
        if not test_object or not test_type:
            flash('Заполните все поля', 'danger')
            return redirect(url_for('main'))
        
        test_id, msg = test_manager.save_test(session['current_file'], test_object, test_type)
        
        if test_id:
            codes = test_manager.generate_access_codes(test_id, count)
            session['generated_codes'] = codes
            flash(msg, 'success')
            return render_template('test_form.html', codes=codes, saved=True)
        else:
            flash(msg, 'danger')
    except ValueError:
        flash('Некорректное количество кодов', 'danger')
    except Exception as e:
        flash(f'Ошибка сохранения теста: {str(e)}', 'danger')
    
    return redirect(url_for('main'))

@app.route('/download_codes')
def download_codes():
    """Скачивание кодов доступа в CSV"""
    if 'user_id' not in session or 'generated_codes' not in session:
        flash('Нет кодов для скачивания', 'danger')
        return redirect(url_for('main'))
    
    try:
        import tempfile
        import csv
        
        codes = session['generated_codes']
        fd, path = tempfile.mkstemp()
        
        with os.fdopen(fd, 'w', newline='', encoding='utf-8') as tmp:
            writer = csv.writer(tmp, delimiter=';')
            writer.writerow(['Номер', 'Код'])
            for i, code in enumerate(codes, 1):
                writer.writerow([i, code])
        
        return send_file(
            path,
            as_attachment=True,
            download_name='access_codes.csv',
            mimetype='text/csv'
        )
    except Exception as e:
        flash(f'Ошибка генерации файла: {str(e)}', 'danger')
        return redirect(url_for('main'))
    finally:
        try:
            os.remove(path)
        except:
            pass

@app.route('/download_template/<file_type>')
def download_template(file_type):
    """Скачивание шаблона теста"""
    try:
        templates_dir = os.path.join(app.root_path, 'static', 'templates')
        
        if file_type == 'csv':
            filename = 'test_template.csv'
        elif file_type == 'xlsx':
            filename = 'test_template.xlsx'
        else:
            flash('Неподдерживаемый формат файла', 'danger')
            return redirect(url_for('main'))
        
        return send_from_directory(
            directory=templates_dir,
            path=filename,
            as_attachment=True
        )
    except Exception as e:
        flash(f'Ошибка загрузки шаблона: {str(e)}', 'danger')
        return redirect(url_for('main'))

@app.route('/logout')
def logout():
    """Выход из системы"""
    session.clear()
    flash('Вы успешно вышли из системы', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)