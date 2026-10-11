import os
import secrets
from functools import wraps

import bcrypt
import pymysql
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_session import Session
from cachelib.file import FileSystemCache

load_dotenv()
app = Flask(__name__)
secret = os.getenv("SECRET_KEY")
if not secret or secret == "replace_with_a_long_random_secret":
    raise RuntimeError("Set SECRET_KEY in .env before starting the app.")
app.config.update(
    SECRET_KEY=secret,
    SESSION_TYPE="cachelib",
    SESSION_CACHELIB=FileSystemCache(cache_dir=".sessions", threshold=500),
    SESSION_PERMANENT=False,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
)
Session(app)


def connect_db():
    return pymysql.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "registration"),
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )


def query(sql, values, fetch=False):
    connection = connect_db()
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, values)
            if fetch:
                return cursor.fetchall()
        connection.commit()
    finally:
        connection.close()


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


@app.before_request
def check_csrf():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(32)
    if request.method == "POST":
        token = request.form.get("csrf_token", "")
        if not secrets.compare_digest(token, session["csrf_token"]):
            return render_template("error.html", message="Please reload the page and try again."), 400


def start_session(user_id, name):
    session.clear()
    session["user_id"] = user_id
    session["name"] = name
    session["csrf_token"] = secrets.token_hex(32)
    app.session_interface.regenerate(session)


@app.route("/")
def home():
    return redirect(url_for("todos" if "user_id" in session else "login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    errors = []
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")
        if not name: errors.append("Name is required")
        if not email: errors.append("Email is required")
        if not password: errors.append("Password is required")
        if not confirm: errors.append("Confirm password is required")
        if password and confirm and password != confirm:
            errors.append("Passwords do not match")
        if len(name) > 100: errors.append("Name is too long (100 characters at most)")
        if len(email) > 255: errors.append("Email is too long (255 characters at most)")
        if len(password.encode("utf-8")) > 72:
            errors.append("Password is too long (72 bytes at most)")
        if not errors:
            password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
            try:
                query("INSERT INTO users (email, name, password_hash) VALUES (%s, %s, %s)",
                      (email, name, password_hash))
            except pymysql.err.IntegrityError as error:
                if error.args[0] == 1062:
                    errors.append("Email Already Exists")
                else:
                    raise
            if not errors:
                user = query("SELECT user_id, name, password_hash FROM users WHERE email = %s", (email,), True)[0]
                start_session(user["user_id"], user["name"])
                return redirect(url_for("todos"))
    return render_template("register.html", errors=errors)


@app.route("/login", methods=["GET", "POST"])
def login():
    errors = []
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        if not email: errors.append("Email is required")
        if not password: errors.append("Password is required")
        if not errors:
            rows = query("SELECT user_id, name, password_hash FROM users WHERE email = %s", (email,), True)
            valid = False
            if rows and len(password.encode("utf-8")) <= 72:
                try:
                    valid = bcrypt.checkpw(password.encode("utf-8"), rows[0]["password_hash"].encode("utf-8"))
                except ValueError:
                    valid = False
            if valid:
                start_session(rows[0]["user_id"], rows[0]["name"])
                return redirect(url_for("todos"))
            errors.append("Invalid email or password")
    return render_template("login.html", errors=errors)


@app.route("/logout", methods=["POST"])
@login_required
def logout():
    session.clear()
    return redirect(url_for("login"))


def list_page(errors=None):
    items = query("SELECT todo_id, title, is_done, created_at FROM todos WHERE user_id = %s ORDER BY todo_id DESC",
                  (session["user_id"],), True)
    return render_template("todos.html", items=items, errors=errors or [])


@app.route("/todos")
@login_required
def todos():
    return list_page()


def title_errors(title):
    if not title: return ["Title is required"]
    if len(title) > 200: return ["Title is too long"]
    return []


@app.route("/todos/add", methods=["POST"])
@login_required
def add_todo():
    title = request.form.get("title", "").strip()
    errors = title_errors(title)
    if errors: return list_page(errors)
    query("INSERT INTO todos (user_id, title) VALUES (%s, %s)", (session["user_id"], title))
    flash("To-do added.")
    return redirect(url_for("todos"))


@app.route("/todos/<int:todo_id>/save", methods=["POST"])
@login_required
def save_todo(todo_id):
    title = request.form.get("title", "").strip()
    errors = title_errors(title)
    if errors: return list_page(errors)
    done = 1 if request.form.get("is_done") == "1" else 0
    query("UPDATE todos SET title = %s WHERE todo_id = %s AND user_id = %s", (title, todo_id, session["user_id"]))
    query("UPDATE todos SET is_done = %s WHERE todo_id = %s AND user_id = %s", (done, todo_id, session["user_id"]))
    flash("To-do saved.")
    return redirect(url_for("todos"))


@app.route("/todos/<int:todo_id>/delete", methods=["POST"])
@login_required
def delete_todo(todo_id):
    query("DELETE FROM todos WHERE todo_id = %s AND user_id = %s", (todo_id, session["user_id"]))
    flash("Delete request completed.")
    return redirect(url_for("todos"))


@app.errorhandler(pymysql.MySQLError)
def database_error(error):
    app.logger.error("Database operation failed: %s", type(error).__name__)
    return render_template("error.html", message="Cannot complete the database request. Check MySQL and your .env settings."), 503


@app.errorhandler(404)
def not_found(error):
    return render_template("error.html", message="Page not found."), 404


@app.errorhandler(500)
def server_error(error):
    return render_template("error.html", message="Something went wrong. Please try again."), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
