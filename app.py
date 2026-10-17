from flask import Flask, request, render_template, redirect, url_for, session, flash
import sqlite3
import hashlib
import os
import random
import re
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

DATABASE = "database.db"

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

@app.route("/")
def index():
    return "Сервер работает!"

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        num1 = random.randint(1, 10)
        num2 = random.randint(1, 10)
        session['captcha'] = num1 + num2
        return render_template("register.html", num1=num1, num2=num2)
    
    username = request.form.get("username", "").strip()
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")
    confirm = request.form.get("confirm_password", "")
    captcha = request.form.get("captcha", "")
    
    if not re.match(r'^[a-zA-Z0-9]{3,20}$', username):
        flash("Имя пользователя: только латиница и цифры, от 3 до 20 символов", "error")
        return redirect(url_for("register"))
    
    if '@' not in email or '.' not in email.split('@')[-1]:
        flash("Введите корректный email", "error")
        return redirect(url_for("register"))
    
    if len(password) < 6 or not re.search(r'[a-zA-Z]', password) or not re.search(r'\d', password):
        flash("Пароль: минимум 6 символов, должны быть буквы и цифры", "error")
        return redirect(url_for("register"))
    
    if password != confirm:
        flash("Пароли не совпадают", "error")
        return redirect(url_for("register"))
    
    if not captcha.isdigit() or int(captcha) != session.get('captcha'):
        flash("Неверный ответ капчи", "error")
        return redirect(url_for("register"))
    
    salt = os.urandom(16).hex()
    hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()
    password_hash = f"{salt}:{hash}"
    
    conn = get_db()
    
    user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    if user:
        conn.close()
        flash("Пользователь с таким именем уже существует", "error")
        return redirect(url_for("register"))
    
    user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    if user:
        conn.close()
        flash("Пользователь с таким email уже зарегистрирован", "error")
        return redirect(url_for("register"))
    
    try:
        conn.execute("INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                    (username, email, password_hash))
        conn.commit()
        conn.close()
        
        flash("Регистрация успешна! Войдите в систему.", "success")
        return redirect(url_for("login"))
    
    except Exception:
        conn.close()
        flash("Пользователь с таким именем или email уже зарегистрирован", "error")
        return redirect(url_for("register"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        num1 = random.randint(1, 10)
        num2 = random.randint(1, 10)
        session['captcha'] = num1 + num2
        return render_template("login.html", num1=num1, num2=num2)
    
    login = request.form.get("login", "").strip()
    password = request.form.get("password", "")
    captcha = request.form.get("captcha", "")
    
    if not captcha.isdigit() or int(captcha) != session.get('captcha'):
        flash("Неверный ответ капчи", "error")
        return redirect(url_for("login"))
    
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE username = ? OR email = ?", 
                       (login, login)).fetchone()
    
    if not user:
        conn.close()
        flash("Неверный логин или пароль", "error")
        return redirect(url_for("login"))
    
    salt, hash = user['password_hash'].split(':')
    check_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()
    
    if hash != check_hash:
        conn.close()
        flash("Неверный логин или пароль", "error")
        return redirect(url_for("login"))
    
    session.clear()
    session['user_id'] = user['id']
    session['username'] = user['username']
    conn.close()
    
    flash("Вы успешно вошли в систему!", "success")
    return redirect(url_for("profile"))

@app.route("/profile")
def profile():
    if 'user_id' not in session:
        flash("Пожалуйста, войдите в систему", "error")
        return redirect(url_for("login"))
    
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
    conn.close()
    
    return render_template("profile.html", user=user)

@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("Вы успешно вышли из системы", "success")
    return redirect(url_for("login"))

if __name__ == "__main__":
    init_db()
    app.run(debug=False, host='127.0.0.1', port=5000)