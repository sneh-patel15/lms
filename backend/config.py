import os

# Load environment variables from .env file if present
try:
    from dotenv import load_dotenv
    # Look for .env in current dir or parent dir
    base_dir = os.path.dirname(os.path.abspath(__file__))
    load_dotenv(os.path.join(base_dir, ".env"))
    load_dotenv(os.path.join(os.path.dirname(base_dir), ".env"))
except ImportError:
    pass


class Config:
    # Database connection - credentials loaded securely from .env / environment variables
    MYSQL_USER = os.environ.get("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "")
    MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
    MYSQL_PORT = os.environ.get("MYSQL_PORT", "3306")
    MYSQL_DB = os.environ.get("MYSQL_DB", "library_db")

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-secret-key-in-production")

    # Business rules
    LOAN_PERIOD_DAYS = int(os.environ.get("LOAN_PERIOD_DAYS", 14))
    FINE_PER_DAY = float(os.environ.get("FINE_PER_DAY", 1.0))

    # Session cookie for cross-origin frontend during local dev
    SESSION_COOKIE_SAMESITE = "Lax"

    # SMTP Email configuration - credentials loaded securely from .env / environment variables
    SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
    SMTP_USE_TLS = os.environ.get("SMTP_USE_TLS", "true").lower() in ("true", "1", "yes")
    SMTP_USERNAME = os.environ.get("SMTP_USERNAME", "")
    SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
    SMTP_FROM_EMAIL = os.environ.get("SMTP_FROM_EMAIL", "librarymanagement@gmail.com")
    SMTP_FROM_NAME = os.environ.get("SMTP_FROM_NAME", "Reading Room Library")
    REMINDER_DAYS_BEFORE = int(os.environ.get("REMINDER_DAYS_BEFORE", 5))
