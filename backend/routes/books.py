from flask import Blueprint, request, jsonify
from flask_login import login_required
from extensions import db
from models import Book, Transaction

books_bp = Blueprint("books", __name__)


@books_bp.route("", methods=["GET"])
@login_required
def list_books():
    search = request.args.get("q", "").strip()
    query = Book.query
    if search:
        like = f"%{search}%"
        query = query.filter(
            db.or_(Book.title.ilike(like), Book.author.ilike(like), Book.isbn.ilike(like))
        )
    books = query.order_by(Book.title.asc()).all()
    return jsonify([b.to_dict() for b in books])


@books_bp.route("/<int:book_id>", methods=["GET"])
@login_required
def get_book(book_id):
    book = Book.query.get_or_404(book_id)
    return jsonify(book.to_dict())


@books_bp.route("", methods=["POST"])
@login_required
def create_book():
    data = request.get_json(silent=True) or {}
    required = ["title", "author"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    try:
        total_copies = int(data.get("total_copies", 1))
        if total_copies < 1:
            return jsonify({"error": "Total copies must be at least 1."}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "Total copies must be a valid number."}), 400

    isbn = data.get("isbn")
    if isbn:
        isbn = str(isbn).strip() or None
    if isbn and Book.query.filter_by(isbn=isbn).first():
        return jsonify({"error": "A book with this ISBN already exists."}), 409

    book = Book(
        title=data["title"].strip(),
        author=data["author"].strip(),
        isbn=isbn,
        category=data.get("category"),
        publisher=data.get("publisher"),
        total_copies=total_copies,
        available_copies=total_copies,
        shelf_location=data.get("shelf_location"),
    )
    db.session.add(book)
    db.session.commit()
    return jsonify(book.to_dict()), 201


@books_bp.route("/<int:book_id>", methods=["PUT"])
@login_required
def update_book(book_id):
    book = Book.query.get_or_404(book_id)
    data = request.get_json(silent=True) or {}

    old_total = book.total_copies
    for field in ["title", "author", "category", "publisher", "shelf_location"]:
        if field in data:
            val = data[field]
            if isinstance(val, str):
                val = val.strip()
            setattr(book, field, val)

    if "isbn" in data:
        new_isbn = data["isbn"]
        if new_isbn:
            new_isbn = str(new_isbn).strip() or None
        if new_isbn:
            existing = Book.query.filter(Book.isbn == new_isbn, Book.id != book_id).first()
            if existing:
                return jsonify({"error": "A book with this ISBN already exists."}), 409
        book.isbn = new_isbn

    if "total_copies" in data:
        try:
            new_total = int(data["total_copies"])
            if new_total < 1:
                return jsonify({"error": "Total copies must be at least 1."}), 400
        except (ValueError, TypeError):
            return jsonify({"error": "Total copies must be a valid number."}), 400

        currently_issued = old_total - book.available_copies
        if new_total < currently_issued:
            return jsonify({
                "error": f"Total copies cannot be less than the number of copies currently on loan ({currently_issued})."
            }), 400

        diff = new_total - old_total
        book.total_copies = new_total
        book.available_copies = book.available_copies + diff

    db.session.commit()
    return jsonify(book.to_dict())


@books_bp.route("/<int:book_id>", methods=["DELETE"])
@login_required
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    active_txns = Transaction.query.filter_by(book_id=book_id, status="issued").count()
    if active_txns > 0:
        return jsonify({
            "error": f"Cannot delete book: {active_txns} copy/copies currently out on loan."
        }), 400

    db.session.delete(book)
    db.session.commit()
    return jsonify({"message": "Book deleted."})
