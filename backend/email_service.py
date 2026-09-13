import logging
import smtplib
from datetime import date, datetime, timedelta
from email.message import EmailMessage
from flask import current_app
from extensions import db
from models import Transaction

logger = logging.getLogger(__name__)


def send_due_date_email(to_email, member_name, book_title, due_date, days_left):
    """
    Sends a due date reminder email via SMTP.
    Authenticates using the configured personal SMTP account, while setting the
    visible 'From' header to the library management email address.
    """
    cfg = current_app.config
    smtp_server = cfg.get("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = cfg.get("SMTP_PORT", 587)
    use_tls = cfg.get("SMTP_USE_TLS", True)
    smtp_user = cfg.get("SMTP_USERNAME", "")
    smtp_password = cfg.get("SMTP_PASSWORD", "")
    from_email = cfg.get("SMTP_FROM_EMAIL", "librarymanagement@gmail.com")
    from_name = cfg.get("SMTP_FROM_NAME", "Reading Room Library")

    msg = EmailMessage()
    msg["Subject"] = f"Book Return Reminder: '{book_title}' is due in {days_left} day{'s' if days_left != 1 else ''}"
    msg["From"] = f"{from_name} <{from_email}>"
    msg["To"] = to_email
    msg["Reply-To"] = from_email

    plain_body = f"""Hello {member_name},

This is a friendly reminder that your borrowed book '{book_title}' is due for return on {due_date} ({days_left} day{'s' if days_left != 1 else ''} remaining).

Please return the book to the library on or before {due_date} to avoid late return fines.

If you are already ready to return this book or have questions, please contact us.

Thank you,
{from_name}
{from_email}
"""

    html_body = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f4f4f5; color: #1f2937; margin: 0; padding: 24px; }}
    .card {{ max-width: 520px; margin: 0 auto; background: #ffffff; border-radius: 8px; border: 1px solid #e5e7eb; padding: 28px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }}
    .header {{ border-bottom: 2px solid #3b82f6; padding-bottom: 12px; margin-bottom: 20px; }}
    h2 {{ color: #111827; margin: 0 0 6px 0; font-size: 20px; }}
    .brand {{ font-size: 13px; color: #6b7280; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600; }}
    .highlight-box {{ background-color: #eff6ff; border-left: 4px solid #3b82f6; padding: 14px; margin: 18px 0; border-radius: 4px; }}
    .highlight-box p {{ margin: 4px 0; font-size: 14px; }}
    .footer {{ margin-top: 24px; padding-top: 14px; border-top: 1px solid #e5e7eb; font-size: 12px; color: #6b7280; text-align: center; }}
  </style>
</head>
<body>
  <div class="card">
    <div class="header">
      <div class="brand">{from_name}</div>
      <h2>Upcoming Loan Due Date</h2>
    </div>
    <p>Hello <strong>{member_name}</strong>,</p>
    <p>This is a reminder that your borrowed book is due for return soon:</p>
    <div class="highlight-box">
      <p>📖 <strong>Book:</strong> {book_title}</p>
      <p>📅 <strong>Due Date:</strong> {due_date}</p>
      <p>⏳ <strong>Remaining:</strong> {days_left} day{'s' if days_left != 1 else ''}</p>
    </div>
    <p>Please return the book to the library on or before <strong>{due_date}</strong> to ensure it remains available for other readers and to avoid any overdue fees.</p>
    <div class="footer">
      Sent by {from_name} &bull; <a href="mailto:{from_email}">{from_email}</a>
    </div>
  </div>
</body>
</html>
"""

    msg.set_content(plain_body)
    msg.add_alternative(html_body, subtype="html")

    try:
        with smtplib.SMTP(smtp_server, smtp_port, timeout=12) as server:
            if use_tls:
                server.starttls()
            if smtp_user and smtp_password:
                server.login(smtp_user, smtp_password)
            server.send_message(msg)
        return True, None
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False, str(e)


def send_password_reset_email(to_email, user_name, reset_token, reset_link):
    """
    Sends a password reset email via SMTP with a reset link and token.
    """
    cfg = current_app.config
    smtp_server = cfg.get("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = cfg.get("SMTP_PORT", 587)
    use_tls = cfg.get("SMTP_USE_TLS", True)
    smtp_user = cfg.get("SMTP_USERNAME", "")
    smtp_password = cfg.get("SMTP_PASSWORD", "")
    from_email = cfg.get("SMTP_FROM_EMAIL", "librarymanagement@gmail.com")
    from_name = cfg.get("SMTP_FROM_NAME", "Reading Room Library")

    msg = EmailMessage()
    msg["Subject"] = "Password Reset Request — Reading Room Library"
    msg["From"] = f"{from_name} <{from_email}>"
    msg["To"] = to_email
    msg["Reply-To"] = from_email

    plain_body = f"""Hello {user_name},

We received a request to reset your password for your Reading Room Library account.

To reset your password, visit the following link (valid for 1 hour):
{reset_link}

Alternatively, you can manually enter your reset token:
{reset_token}

If you did not request this password reset, please ignore this email. Your password will remain unchanged.

Thank you,
{from_name}
{from_email}
"""

    html_body = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f4f4f5; color: #1f2937; margin: 0; padding: 24px; }}
    .card {{ max-width: 520px; margin: 0 auto; background: #ffffff; border-radius: 8px; border: 1px solid #e5e7eb; padding: 28px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }}
    .header {{ border-bottom: 2px solid #ad8636; padding-bottom: 12px; margin-bottom: 20px; }}
    h2 {{ color: #111827; margin: 0 0 6px 0; font-size: 20px; }}
    .brand {{ font-size: 13px; color: #6b7280; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600; }}
    .btn {{ display: inline-block; background-color: #23303a; color: #ffffff !important; text-decoration: none; padding: 12px 24px; border-radius: 6px; font-weight: 600; font-size: 14px; margin: 16px 0; }}
    .code-box {{ background: #f9fafb; border: 1px dashed #d1d5db; padding: 12px; border-radius: 6px; font-family: monospace; font-size: 13px; word-break: break-all; margin: 12px 0; color: #374151; }}
    .footer {{ margin-top: 24px; padding-top: 14px; border-top: 1px solid #e5e7eb; font-size: 12px; color: #6b7280; text-align: center; }}
  </style>
</head>
<body>
  <div class="card">
    <div class="header">
      <div class="brand">{from_name}</div>
      <h2>Password Reset Request</h2>
    </div>
    <p>Hello <strong>{user_name}</strong>,</p>
    <p>We received a request to reset your password for your Reading Room account. Click the button below to choose a new password (valid for 1 hour):</p>
    <p style="text-align: center;">
      <a href="{reset_link}" class="btn" style="color: #ffffff;">Reset My Password</a>
    </p>
    <p style="font-size: 13px; color: #6b7280;">If the button doesn't work, copy and paste this link into your browser:</p>
    <div class="code-box"><a href="{reset_link}">{reset_link}</a></div>
    <p style="font-size: 13px; color: #6b7280;">Or use your reset token directly on the reset page:</p>
    <div class="code-box">{reset_token}</div>
    <p style="font-size: 12px; color: #9ca3af;">If you did not request a password reset, you can safely ignore this email. Your password will remain unchanged.</p>
    <div class="footer">
      Sent by {from_name} &bull; <a href="mailto:{from_email}">{from_email}</a>
    </div>
  </div>
</body>
</html>
"""

    msg.set_content(plain_body)
    msg.add_alternative(html_body, subtype="html")

    try:
        with smtplib.SMTP(smtp_server, smtp_port, timeout=12) as server:
            if use_tls:
                server.starttls()
            if smtp_user and smtp_password:
                server.login(smtp_user, smtp_password)
            server.send_message(msg)
        logger.info(f"Password reset email sent to {to_email}")
        return True, None
    except Exception as e:
        logger.error(f"Failed to send password reset email to {to_email}: {e}")
        return False, str(e)


def process_due_date_reminders():
    """
    Scans active loans and sends reminders for books due within REMINDER_DAYS_BEFORE (default: 5 days).
    Reminders are sent once only (reminder_sent == False).
    Loans that are marked ready or returned are excluded.
    """
    today = date.today()
    reminder_days = current_app.config.get("REMINDER_DAYS_BEFORE", 5)

    # Eligible: currently issued, not marked ready, and reminder not yet sent
    txns = Transaction.query.filter(
        Transaction.status == "issued",
        Transaction.is_ready.is_(False),
        Transaction.reminder_sent.is_(False),
    ).all()

    sent_count = 0
    failed_count = 0
    skipped_count = 0
    details = []

    for txn in txns:
        if not txn.due_date:
            skipped_count += 1
            continue

        days_until_due = (txn.due_date - today).days

        # Trigger when due date is within the reminder window (e.g. 5 days or fewer) and not overdue
        if 0 <= days_until_due <= reminder_days:
            member = txn.member
            book = txn.book

            if not member or not member.email:
                skipped_count += 1
                details.append({
                    "txn_id": txn.id,
                    "status": "skipped",
                    "reason": "Member email missing"
                })
                continue

            book_title = book.title if book else "Borrowed Book"
            success, err = send_due_date_email(
                to_email=member.email,
                member_name=member.name,
                book_title=book_title,
                due_date=txn.due_date.isoformat(),
                days_left=days_until_due,
            )

            if success:
                txn.reminder_sent = True
                txn.reminder_sent_at = datetime.utcnow()
                db.session.commit()
                sent_count += 1
                details.append({
                    "txn_id": txn.id,
                    "member": member.name,
                    "email": member.email,
                    "book": book_title,
                    "days_left": days_until_due,
                    "status": "sent",
                })
            else:
                failed_count += 1
                details.append({
                    "txn_id": txn.id,
                    "member": member.name,
                    "email": member.email,
                    "status": "failed",
                    "error": err,
                })
        else:
            skipped_count += 1

    return {
        "checked_at": datetime.utcnow().isoformat(),
        "total_active_checked": len(txns),
        "reminders_sent": sent_count,
        "failed": failed_count,
        "skipped": skipped_count,
        "details": details,
    }

