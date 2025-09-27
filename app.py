from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, redirect, url_for, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import jwt
from models import Note, db, User

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
SECRET_KEY = "123456" 

db.init_app(app)
with app.app_context():
    db.create_all()


def generate_token(user_id):
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(hours=2)  # Token valid only for 2 hours
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def verify_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload["user_id"]
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.cookies.get("token")
        if not token:
            return redirect(url_for("login"))
        user_id = verify_token(token)
        if not user_id:
            return redirect(url_for("login"))
        return f(user_id, *args, **kwargs)
    return decorated_function


# @app.context_processor
# def inject_page():
#     return dict(current_page=request.endpoint)


def decode_jwt():
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload  # contains user_id and name
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

@app.context_processor
def inject_user():
    payload = decode_jwt()
    if payload:
        return dict(
            is_authenticated=True,
            current_user=payload.get("name"),
            current_page=request.endpoint
        )
    return dict(
        is_authenticated=False,
        current_user=None,
        current_page=request.endpoint
    )


@app.route("/")
@login_required
def home(user_id):
    user = User.query.get(user_id)
    return render_template("home.html", user=user)

@app.route("/login", methods=["GET"])
def login():
    return render_template("login.html")

@app.route("/signup", methods=["GET"])
def signup():
    return render_template("signup.html")


@app.route("/api/signup", methods=["POST"])
def api_signup():
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    confirm = data.get("confirm_password", "")

    if not name or not email or not password or not confirm:
        return jsonify({"status": "error", "message": "All fields are required."}), 400

    if password != confirm:
        return jsonify({"status": "error", "message": "Passwords do not match."}), 400

    if User.query.filter_by(user_email=email).first():
        return jsonify({"status": "error", "message": "Email already registered."}), 400

    hashed_password = generate_password_hash(password)
    new_user = User(user_name=name, user_email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"status": "success", "message": "Account created! Please login."})


@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(user_email=email).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({"status": "error", "message": "Invalid email or password."}), 401

    payload = {
        "user_id": str(user.user_id),
        "name": user.user_name,
        "exp": datetime.utcnow() + timedelta(hours=2)  # 2h expiry
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    response = jsonify({"status": "success", "redirect": url_for("home")})
    response.set_cookie("access_token", token, httponly=True, samesite="Strict")
    return response


@app.route("/logout")
def logout():
    response = redirect(url_for("login"))
    response.delete_cookie("access_token")
    return response


# --------------------------------
@app.route("/notes")
@login_required
def notes_page(user_id):
    user = User.query.get(user_id)
    notes = Note.query.filter_by(user_id=user_id).all()
    return render_template("notes.html", user=user.user_name, notes=notes)

@app.route("/add_note", methods=["POST"])
@login_required
def add_note(user_id):
    data = request.get_json()
    new_note = Note(
        note_title=data["title"],
        note_content=data["content"],
        user_id=user_id,
    )
    db.session.add(new_note)
    db.session.commit()
    return jsonify({"message": "Note added successfully!"})




@app.route("/edit_note/<note_id>", methods=["POST"])
@login_required
def edit_note(user_id, note_id):
    data = request.get_json()
    note = Note.query.get(note_id)

    if not note or note.user_id != user_id:
        return jsonify({"message": "Not found"}), 404

    note.note_title = data["title"]
    note.note_content = data["content"]
    note.last_update = datetime.utcnow()
    db.session.commit()
    return jsonify({"message": "Note updated successfully!"})





@app.route("/delete_note/<note_id>", methods=["DELETE"])
@login_required
def delete_note(user_id, note_id):
    note = Note.query.get(note_id)

    if not note or note.user_id != user_id:
        return jsonify({"message": "Not found"}), 404

    db.session.delete(note)
    db.session.commit()
    return jsonify({"message": "Note deleted successfully!"})





if __name__ == "__main__":
    app.run(debug=True)
