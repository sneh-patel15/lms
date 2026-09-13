from flask import Blueprint, request, jsonify
from flask_login import login_required
from extensions import db
from models import Member, Transaction

members_bp = Blueprint("members", __name__)


@members_bp.route("", methods=["GET"])
@login_required
def list_members():
    search = request.args.get("q", "").strip()
    query = Member.query
    if search:
        like = f"%{search}%"
        query = query.filter(db.or_(Member.name.ilike(like), Member.email.ilike(like)))
    members = query.order_by(Member.name.asc()).all()
    return jsonify([m.to_dict() for m in members])


@members_bp.route("/<int:member_id>", methods=["GET"])
@login_required
def get_member(member_id):
    member = Member.query.get_or_404(member_id)
    return jsonify(member.to_dict())


@members_bp.route("", methods=["POST"])
@login_required
def create_member():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip()
    if not name or not email:
        return jsonify({"error": "Name and email are required."}), 400

    if Member.query.filter_by(email=email).first():
        return jsonify({"error": "A member with this email already exists."}), 409

    status = data.get("status", "active")
    if status not in ("active", "suspended"):
        status = "active"

    member = Member(
        name=name,
        email=email,
        phone=data.get("phone"),
        address=data.get("address"),
        status=status,
    )
    db.session.add(member)
    db.session.commit()
    return jsonify(member.to_dict()), 201


@members_bp.route("/<int:member_id>", methods=["PUT"])
@login_required
def update_member(member_id):
    member = Member.query.get_or_404(member_id)
    data = request.get_json(silent=True) or {}

    if "email" in data:
        new_email = (data.get("email") or "").strip()
        if not new_email:
            return jsonify({"error": "Email cannot be empty."}), 400
        existing = Member.query.filter(Member.email == new_email, Member.id != member_id).first()
        if existing:
            return jsonify({"error": "A member with this email already exists."}), 409
        member.email = new_email

    for field in ["name", "phone", "address", "status"]:
        if field in data:
            val = data[field]
            if isinstance(val, str):
                val = val.strip()
            setattr(member, field, val)

    db.session.commit()
    return jsonify(member.to_dict())


@members_bp.route("/<int:member_id>", methods=["DELETE"])
@login_required
def delete_member(member_id):
    member = Member.query.get_or_404(member_id)
    active_loans = Transaction.query.filter_by(member_id=member_id, status="issued").count()
    if active_loans > 0:
        return jsonify({
            "error": f"Cannot delete member: member currently has {active_loans} book(s) out on loan."
        }), 400

    db.session.delete(member)
    db.session.commit()
    return jsonify({"message": "Member deleted."})
