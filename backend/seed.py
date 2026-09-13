"""Run once after creating the database: python seed.py
Creates the tables (if not present) and a default admin login.
"""
from app import create_app
from extensions import db
from models import User

app = create_app()

with app.app_context():
    db.create_all()

    if not User.query.filter_by(username="admin").first():
        admin = User(
            username="admin",
            full_name="Administrator",
            email="admin@library.com",
            role="admin"
        )
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.commit()
        print("Created default admin user -> username: admin / password: admin123")
    else:
        print("Admin user already exists.")
