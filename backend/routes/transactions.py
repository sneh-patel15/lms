from datetime import date, timedelta
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required
from extensions import db
from models import Transaction, Book, Member

transactions_bp = Blueprint("transactions", __name__)


@transactions_bp.route("", methods=["GET"])
@login_required
def list_transactions():
    status = request.args.get("status")
    query = Transaction.query
    if status in ("issued", "returned"):
        query = query.filter_by(status=status)
    txns = query.order_by(Transaction.issue_date.desc()).all()
    return jsonify([t.to_dict() for t in txns])


@transactions_bp.route("/issue", methods=["POST"])
@login_required
def issue_book():
    data = request.get_json(silent=True) or {}
    raw_book_id = data.get("book_id")
    raw_member_id = data.get("member_id")

    if not raw_book_id or not raw_member_id:
        return jsonify({"error": "book_id and member_id are required."}), 400

    try:
        book_id = int(raw_book_id)
        member_id = int(raw_member_id)
    except (ValueError, TypeError):
        return jsonify({"error": "book_id and member_id must be valid integers."}), 400

    book = db.session.get(Book, book_id)
    member = db.session.get(Member, member_id)
    if not book or not member:
        return jsonify({"error": "Book or member not found."}), 404
    if member.status != "active":
        return jsonify({"error": "Member is suspended and cannot borrow books."}), 403
    if book.available_copies < 1:
        return jsonify({"error": "No available copies of this book."}), 409

    # Prevent borrowing the same book if already currently issued to this member
    existing_loan = Transaction.query.filter_by(
        book_id=book.id, member_id=member.id, status="issued"
    ).first()
    if existing_loan:
        return jsonify({"error": "This member already has an active loan for this book."}), 400

    loan_days = current_app.config["LOAN_PERIOD_DAYS"]
    txn = Transaction(
        book_id=book.id,
        member_id=member.id,
        issue_date=date.today(),
        due_date=date.today() + timedelta(days=loan_days),
        status="issued",
    )
    book.available_copies -= 1
    db.session.add(txn)
    db.session.commit()
    return jsonify(txn.to_dict()), 201


@transactions_bp.route("/return/<int:txn_id>", methods=["POST"])
@login_required
def return_book(txn_id):
    txn = Transaction.query.get_or_404(txn_id)
    if txn.status == "returned":
        return jsonify({"error": "This book has already been returned."}), 409

    today = date.today()
    txn.return_date = today
    txn.status = "returned"
    txn.is_ready = True

    if today > txn.due_date:
        days_late = (today - txn.due_date).days
        txn.fine_amount = days_late * current_app.config["FINE_PER_DAY"]

    if txn.book:
        txn.book.available_copies = min(txn.book.total_copies, txn.book.available_copies + 1)
    db.session.commit()
    return jsonify(txn.to_dict())


@transactions_bp.route("/ready/<int:txn_id>", methods=["POST"])
@login_required
def toggle_ready(txn_id):
    txn = Transaction.query.get_or_404(txn_id)
    data = request.get_json(silent=True) or {}
    if "ready" in data:
        txn.is_ready = bool(data["ready"])
    else:
        txn.is_ready = not txn.is_ready
    db.session.commit()
    return jsonify(txn.to_dict())


@transactions_bp.route("/check-reminders", methods=["POST"])
@login_required
def trigger_reminders():
    from email_service import process_due_date_reminders
    summary = process_due_date_reminders()
    return jsonify(summary)


@transactions_bp.route("/stats", methods=["GET"])
@login_required
def dashboard_stats():
    total_books = db.session.query(db.func.coalesce(db.func.sum(Book.total_copies), 0)).scalar()
    available_books = db.session.query(
        db.func.coalesce(db.func.sum(Book.available_copies), 0)
    ).scalar()
    total_members = Member.query.count()
    books_issued = Transaction.query.filter_by(status="issued").count()
    overdue = Transaction.query.filter(
        Transaction.status == "issued", Transaction.due_date < date.today()
    ).count()

    return jsonify(
        {
            "total_books": int(total_books),
            "available_books": int(available_books),
            "total_members": total_members,
            "books_issued": books_issued,
            "overdue": overdue,
        }
    )
