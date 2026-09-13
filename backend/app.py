import os
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from config import Config
from extensions import db, login_manager
from models import User

from routes.auth import auth_bp
from routes.books import books_bp
from routes.members import members_bp
from routes.transactions import transactions_bp

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")


def create_app():
    app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    CORS(app, supports_credentials=True)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @login_manager.unauthorized_handler
    def unauthorized():
        return jsonify({"error": "Authentication required."}), 401

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(books_bp, url_prefix="/api/books")
    app.register_blueprint(members_bp, url_prefix="/api/members")
    app.register_blueprint(transactions_bp, url_prefix="/api/transactions")

    # Serve the plain HTML/CSS/JS frontend directly from Flask
    @app.route("/")
    def index():
        return send_from_directory(FRONTEND_DIR, "index.html")

    @app.route("/<path:path>")
    def static_proxy(path):
        return send_from_directory(FRONTEND_DIR, path)

    return app


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
