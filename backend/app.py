import re
from datetime import date, datetime

from flask import Flask, jsonify, request
from flask_cors import CORS
from mysql.connector import Error, IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

from db import get_db_connection

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_PATTERN = re.compile(r"^\d{10}$")


def json_error(message, status=400):
    return jsonify(success=False, message=message), status


def serialize_value(value):
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return value


def row_to_dict(row):
    return {key: serialize_value(value) for key, value in row.items()}


def safe_user(row):
    return {
        "id": row["id"],
        "name": row["name"],
        "email": row["email"],
        "phone": row["phone"],
        "age": row.get("age"),
        "sport": row.get("sport"),
        "location": row.get("location"),
        "bio": row.get("bio"),
    }


def get_json():
    payload = request.get_json(silent=True)
    return payload if isinstance(payload, dict) else None


def fetch_rows(query, params=()):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(query, params)
        return [row_to_dict(row) for row in cursor.fetchall()]
    finally:
        cursor.close()
        connection.close()


def fetch_one(query, params=()):
    rows = fetch_rows(query, params)
    return rows[0] if rows else None


def resource_routes(table, columns, singular):
    @app.get(f"/api/{table}", endpoint=f"list_{table}")
    def list_resource():
        return jsonify(success=True, data=fetch_rows(f"SELECT {columns} FROM {table} ORDER BY id"))

    @app.get(f"/api/{table}/<int:resource_id>", endpoint=f"get_{table}")
    def get_resource(resource_id):
        row = fetch_one(f"SELECT {columns} FROM {table} WHERE id = %s", (resource_id,))
        if not row:
            return json_error(f"{singular.title()} not found.", 404)
        return jsonify(success=True, data=row)


@app.get("/api/test")
def api_test():
    return jsonify(success=True, message="SportPath backend is running.")


@app.get("/api/db-test")
def db_test():
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT 1")
        cursor.fetchone()
        return jsonify(success=True, message="Database connection is working.")
    finally:
        cursor.close()
        connection.close()


@app.post("/api/register")
def register():
    payload = get_json()
    if not payload:
        return json_error("A JSON request body is required.")

    name = str(payload.get("name", "")).strip()
    email = str(payload.get("email", "")).strip().lower()
    phone = str(payload.get("phone", "")).strip()
    password = str(payload.get("password", ""))

    if not all((name, email, phone, password)):
        return json_error("Name, email, phone, and password are required.")
    if len(name) > 120:
        return json_error("Name must be 120 characters or fewer.")
    if not EMAIL_PATTERN.fullmatch(email):
        return json_error("Please enter a valid email address.")
    if not PHONE_PATTERN.fullmatch(phone):
        return json_error("Phone number must contain exactly 10 digits.")
    if len(password) < 6:
        return json_error("Password must contain at least 6 characters.")

    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (name, email, phone, password) VALUES (%s, %s, %s, %s)",
            (name, email, phone, generate_password_hash(password)),
        )
        connection.commit()
        return jsonify(success=True, message="Registration successful."), 201
    except IntegrityError:
        connection.rollback()
        return json_error("That email or phone number is already registered.", 409)
    finally:
        cursor.close()
        connection.close()


@app.post("/api/login")
def login():
    payload = get_json()
    if not payload:
        return json_error("A JSON request body is required.")

    email = str(payload.get("email", "")).strip().lower()
    phone = str(payload.get("phone", "")).strip()
    password = str(payload.get("password", ""))
    if not email or not phone or not password:
        return json_error("Email, phone, and password are required.")

    user = fetch_one("SELECT * FROM users WHERE email = %s AND phone = %s", (email, phone))
    if not user or not check_password_hash(user["password"], password):
        return json_error("Email, phone, or password is incorrect.", 401)
    return jsonify(success=True, message="Login successful.", user=safe_user(user))


@app.post("/api/forgot-password")
def forgot_password():
    payload = get_json()
    if not payload:
        return json_error("A JSON request body is required.")

    email = str(payload.get("email", "")).strip().lower()
    phone = str(payload.get("phone", "")).strip()
    new_password = str(payload.get("new_password", ""))
    if not email or not phone or not new_password:
        return json_error("Email, phone, and new password are required.")
    if not EMAIL_PATTERN.fullmatch(email):
        return json_error("Please enter a valid email address.")
    if not PHONE_PATTERN.fullmatch(phone):
        return json_error("Phone number must contain exactly 10 digits.")
    if len(new_password) < 6:
        return json_error("Password must contain at least 6 characters.")

    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            "UPDATE users SET password = %s WHERE email = %s AND phone = %s",
            (generate_password_hash(new_password), email, phone),
        )
        if cursor.rowcount == 0:
            connection.rollback()
            return json_error("Email and phone number do not match a registered account.", 404)
        connection.commit()
        return jsonify(success=True, message="Password reset successfully.")
    finally:
        cursor.close()
        connection.close()


@app.get("/api/profile/<int:user_id>")
def get_profile(user_id):
    user = fetch_one("SELECT * FROM users WHERE id = %s", (user_id,))
    if not user:
        return json_error("User not found.", 404)
    return jsonify(success=True, user=safe_user(user))


@app.put("/api/profile/<int:user_id>")
def update_profile(user_id):
    payload = get_json()
    if not payload:
        return json_error("A JSON request body is required.")

    phone = str(payload.get("phone", "")).strip()
    age_value = payload.get("age")
    sport = str(payload.get("sport", "")).strip()
    location = str(payload.get("location", "")).strip()
    bio = str(payload.get("bio", "")).strip()
    if phone and not PHONE_PATTERN.fullmatch(phone):
        return json_error("Phone number must contain exactly 10 digits.")
    try:
        age = int(age_value) if age_value not in (None, "") else None
    except (TypeError, ValueError):
        return json_error("Age must be a whole number.")
    if age is not None and not 1 <= age <= 120:
        return json_error("Age must be between 1 and 120.")

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
        if not cursor.fetchone():
            return json_error("User not found.", 404)
        cursor.execute(
            "UPDATE users SET phone = NULLIF(%s, ''), age = %s, sport = NULLIF(%s, ''), "
            "location = NULLIF(%s, ''), bio = NULLIF(%s, '') WHERE id = %s",
            (phone, age, sport, location, bio, user_id),
        )
        connection.commit()
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        return jsonify(success=True, message="Profile updated successfully.", user=safe_user(cursor.fetchone()))
    except IntegrityError:
        connection.rollback()
        return json_error("That phone number is already registered.", 409)
    finally:
        cursor.close()
        connection.close()


resource_routes("sports", "id, name, slug, description, created_at", "sport")
resource_routes("careers", "id, title, description, skills, pathway", "career")
resource_routes("academies", "id, name, type, location, sport, description, website", "academy")
resource_routes("scholarships", "id, name, provider, eligibility, url, description", "scholarship")
resource_routes("tournaments", "id, name, level, sport, location, event_date, description", "tournament")
resource_routes("equipment", "id, sport, name, description", "equipment")


@app.get("/api/sports/<int:sport_id>/athletes")
def sport_athletes(sport_id):
    return jsonify(success=True, data=fetch_rows(
        "SELECT id, sport_id, name, description FROM athletes WHERE sport_id = %s ORDER BY id",
        (sport_id,),
    ))


@app.get("/api/sports/<int:sport_id>/academies")
def sport_academies(sport_id):
    sport = fetch_one("SELECT name FROM sports WHERE id = %s", (sport_id,))
    if not sport:
        return json_error("Sport not found.", 404)
    return jsonify(success=True, data=fetch_rows(
        "SELECT id, name, type, location, sport, description, website FROM academies WHERE sport = %s ORDER BY id",
        (sport["name"],),
    ))


@app.get("/api/sports/<int:sport_id>/equipment")
def sport_equipment(sport_id):
    sport = fetch_one("SELECT name FROM sports WHERE id = %s", (sport_id,))
    if not sport:
        return json_error("Sport not found.", 404)
    return jsonify(success=True, data=fetch_rows(
        "SELECT id, sport, name, description FROM equipment WHERE sport = %s ORDER BY id",
        (sport["name"],),
    ))


@app.post("/api/feedback")
def create_feedback():
    payload = get_json()
    if not payload or not str(payload.get("message", "")).strip():
        return json_error("A feedback message is required.")
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            "INSERT INTO feedback (user_id, name, email, message) VALUES (%s, %s, %s, %s)",
            (payload.get("user_id"), payload.get("name"), payload.get("email"), str(payload["message"]).strip()),
        )
        connection.commit()
        return jsonify(success=True, message="Feedback submitted successfully."), 201
    finally:
        cursor.close()
        connection.close()


@app.get("/api/feedback")
def list_feedback():
    return jsonify(success=True, data=fetch_rows(
        "SELECT id, user_id, name, email, message, created_at FROM feedback ORDER BY created_at DESC"
    ))


@app.post("/api/admin/login")
def admin_login():
    payload = get_json()
    if not payload:
        return json_error("A JSON request body is required.")
    email = str(payload.get("email", "")).strip().lower()
    password = str(payload.get("password", ""))
    admin = fetch_one("SELECT * FROM admins WHERE email = %s", (email,))
    if not admin or not check_password_hash(admin["password"], password):
        return json_error("Email or password is incorrect.", 401)
    return jsonify(success=True, message="Admin login successful.", admin={"id": admin["id"], "name": admin["name"], "email": admin["email"]})


@app.get("/api/admin/users")
def admin_users():
    return jsonify(success=True, data=fetch_rows(
        "SELECT id, name, email, phone, age, sport, location, bio, created_at, updated_at FROM users ORDER BY id"
    ))


@app.errorhandler(Error)
def handle_database_error(error):
    app.logger.error("Database error: %s", error)
    if getattr(error, "errno", None) in (1045, 1698):
        return json_error("MySQL rejected the backend credentials. Check DB_USER and DB_PASSWORD in backend/.env.", 503)
    if getattr(error, "errno", None) == 1049:
        return json_error("Database sportpath_db does not exist. Run backend/database.sql in phpMyAdmin.", 503)
    return json_error("Database unavailable. Start XAMPP MySQL and verify backend/.env settings.", 503)


@app.errorhandler(404)
def handle_not_found(error):
    if request.path.startswith("/api/"):
        return json_error("API endpoint not found.", 404)
    return error


@app.errorhandler(Exception)
def handle_unexpected_error(error):
    app.logger.exception("Unexpected server error")
    return json_error("The server could not complete the request.", 500)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
