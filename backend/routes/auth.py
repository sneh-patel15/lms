import re
import secrets
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db
from models import User
from email_service import send_password_reset_email

auth_bp = Blueprint("auth", __name__)

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
USERNAME_REGEX = re.compile(r"^[A-Za-z0-9_.-]{3,50}$")


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    login_id = (data.get("username") or data.get("email") or data.get("login") or "").strip()
    password = data.get("password", "")

    if not login_id or not password:
        return jsonify({"error": "Username/email and password are required."}), 400

    # Support login with either username or email
    user = User.query.filter(
        (User.username == login_id) | (User.email == login_id)
    ).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid username or password."}), 401

    login_user(user)
    return jsonify({"message": "Logged in.", "user": user.to_dict()})


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    full_name = (data.get("full_name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    username = (data.get("username") or "").strip()
    password = data.get("password", "")

    if not full_name:
        return jsonify({"error": "Full name is required."}), 400
    if not email or not EMAIL_REGEX.match(email):
        return jsonify({"error": "A valid email address is required."}), 400
    if not username or not USERNAME_REGEX.match(username):
        return jsonify({"error": "Username must be 3-50 characters (letters, numbers, underscores, dots, hyphens)."}), 400
    if not password or len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters."}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username is already taken."}), 409
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email is already registered."}), 409

    user = User(
        full_name=full_name,
        email=email,
        username=username,
        role="librarian",
    )
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    login_user(user)
    return jsonify({"message": "Registration successful.", "user": user.to_dict()}), 201


@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    data = request.get_json(silent=True) or {}
    login_id = (data.get("login") or data.get("email") or data.get("username") or "").strip()

    if not login_id:
        return jsonify({"error": "Username or email is required."}), 400

    user = User.query.filter(
        (User.username == login_id) | (User.email == login_id)
    ).first()

    if user and user.email:
        token = secrets.token_urlsafe(32)
        user.reset_token = token
        user.reset_token_expiry = datetime.utcnow() + timedelta(hours=1)
        db.session.commit()

        host_url = request.host_url.rstrip("/")
        reset_link = f"{host_url}/index.html?view=reset&token={token}"

        send_password_reset_email(
            to_email=user.email,
            user_name=user.full_name or user.username,
            reset_token=token,
            reset_link=reset_link,
        )

    return jsonify({
        "message": "If an account matching that username or email exists, password reset instructions have been sent to the registered email."
    }), 200


@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    data = request.get_json(silent=True) or {}
    token = (data.get("token") or "").strip()
    new_password = data.get("new_password", "")

    if not token:
        return jsonify({"error": "Reset token is required."}), 400
    if not new_password or len(new_password) < 6:
        return jsonify({"error": "New password must be at least 6 characters."}), 400

    user = User.query.filter_by(reset_token=token).first()
    if not user or not user.reset_token_expiry or user.reset_token_expiry < datetime.utcnow():
        return jsonify({"error": "Invalid or expired password reset token."}), 400

    user.set_password(new_password)
    user.reset_token = None
    user.reset_token_expiry = None
    db.session.commit()

    return jsonify({"message": "Password reset successful! You can now sign in with your new password."}), 200


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out."})


@auth_bp.route("/me", methods=["GET"])
def me():
    if not current_user.is_authenticated:
        return jsonify({"user": None}), 200
    return jsonify({"user": current_user.to_dict()})
