# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from auth import AuthManager
from test_manager import TestManager
import os
from werkzeug.utils import secure_filename
import tempfile
import csv
app = Flask(__name__)
app.secret_key = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB

# Инициализация менеджеров
auth_manager = AuthManager()
test_manager = None

@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('main'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        success, msg = auth_manager.login(login, password)
        if success:
            session['user_id'] = auth_manager.current_user_id
            global test_manager
            test_manager = TestManager(session['user_id'])
            flash(msg, 'success')
            return redirect(url_for('main'))
        flash(msg, 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash('Пароли не совпадают', 'danger')
            return redirect(url_for('register'))
        
        success, msg = auth_manager.register(login, password)
        if success:
            flash(msg, 'success')
            return redirect(url_for('login'))
        flash(msg, 'danger')
    return render_template('register.html')

@app.route('/main')
def main():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    tests = test_manager.get_user_tests()
    return render_template('main.html', tests=tests)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('Файл не выбран', 'danger')
        return redirect(url_for('main'))
    
    file = request.files['file']
    if file.filename == '':
        flash('Файл не выбран', 'danger')
        return redirect(url_for('main'))
    
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        session['current_file'] = filepath
        return render_template('test_form.html', filename=filename)
    
    return redirect(url_for('main'))

@app.route('/save_test', methods=['POST'])
def save_test():
    if 'current_file' not in session:
        flash('Сначала загрузите файл', 'danger')
        return redirect(url_for('main'))
    
    test_object = request.form['object']
    test_type = request.form['type']
    count = int(request.form.get('count', 1))
    
    test_id, msg = test_manager.save_test(session['current_file'], test_object, test_type)
    if test_id:
        codes = test_manager.generate_access_codes(test_id, count)
        session['generated_codes'] = codes
        flash(msg, 'success')
        return render_template('test_form.html', codes=codes, saved=True)
    
    flash(msg, 'danger')
    return redirect(url_for('main'))

@app.route('/download_codes')
def download_codes():
    codes = session.get('generated_codes', [])
    if not codes:
        flash('Нет кодов для скачивания', 'danger')
        return redirect(url_for('main'))
    

    
    fd, path = tempfile.mkstemp()
    try:
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
    finally:
        os.remove(path)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)