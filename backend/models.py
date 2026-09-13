from datetime import date
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=True)
    role = db.Column(db.Enum("admin", "librarian", name="role_enum"), default="librarian")
    reset_token = db.Column(db.String(100), nullable=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "full_name": self.full_name,
            "email": self.email,
            "role": self.role,
        }


class Book(db.Model):
    __tablename__ = "books"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    isbn = db.Column(db.String(20), unique=True)
    category = db.Column(db.String(100))
    publisher = db.Column(db.String(150))
    total_copies = db.Column(db.Integer, default=1, nullable=False)
    available_copies = db.Column(db.Integer, default=1, nullable=False)
    shelf_location = db.Column(db.String(50))
    added_on = db.Column(db.DateTime, server_default=db.func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "isbn": self.isbn,
            "category": self.category,
            "publisher": self.publisher,
            "total_copies": self.total_copies,
            "available_copies": self.available_copies,
            "shelf_location": self.shelf_location,
        }


class Member(db.Model):
    __tablename__ = "members"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.String(255))
    membership_date = db.Column(db.Date, default=date.today)
    status = db.Column(db.Enum("active", "suspended", name="status_enum"), default="active")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "address": self.address,
            "membership_date": self.membership_date.isoformat() if self.membership_date else None,
            "status": self.status,
        }


class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey("books.id"), nullable=False)
    member_id = db.Column(db.Integer, db.ForeignKey("members.id"), nullable=False)
    issue_date = db.Column(db.Date, nullable=False, default=date.today)
    due_date = db.Column(db.Date, nullable=False)
    return_date = db.Column(db.Date, nullable=True)
    fine_amount = db.Column(db.Numeric(6, 2), default=0.00)
    status = db.Column(db.Enum("issued", "returned", name="txn_status_enum"), default="issued")
    reminder_sent = db.Column(db.Boolean, default=False, nullable=False)
    reminder_sent_at = db.Column(db.DateTime, nullable=True)
    is_ready = db.Column(db.Boolean, default=False, nullable=False)

    book = db.relationship("Book")
    member = db.relationship("Member")

    def to_dict(self):
        return {
            "id": self.id,
            "book_id": self.book_id,
            "book_title": self.book.title if self.book else None,
            "member_id": self.member_id,
            "member_name": self.member.name if self.member else None,
            "issue_date": self.issue_date.isoformat() if self.issue_date else None,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "return_date": self.return_date.isoformat() if self.return_date else None,
            "fine_amount": float(self.fine_amount) if self.fine_amount is not None else 0.0,
            "status": self.status,
            "reminder_sent": bool(self.reminder_sent),
            "reminder_sent_at": self.reminder_sent_at.isoformat() if self.reminder_sent_at else None,
            "is_ready": bool(self.is_ready),
        }
