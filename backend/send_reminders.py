"""
CLI script to process loan due date reminders.
Can be run via cron, Windows Task Scheduler, or manually:
    python send_reminders.py
"""
import sys
import os

# Ensure backend directory is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from email_service import process_due_date_reminders

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        print("Checking for loans due in 5 days or fewer...")
        result = process_due_date_reminders()
        print(f"Summary:")
        print(f"  Total checked:    {result['total_active_checked']}")
        print(f"  Reminders sent:   {result['reminders_sent']}")
        print(f"  Failed:           {result['failed']}")
        print(f"  Skipped/Not due:  {result['skipped']}")
        if result["details"]:
            print("\nDetails:")
            for d in result["details"]:
                print(f"  - [{d.get('status', '').upper()}] Txn #{d.get('txn_id')}: {d.get('member')} ({d.get('email')}) - Book: '{d.get('book')}', Days left: {d.get('days_left')}")
                if "error" in d:
                    print(f"      Error: {d['error']}")

