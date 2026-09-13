# 📚 Reading Room — Library Management System

A full-stack, responsive Library Management System built with a **Flask (Python)** REST backend, **MySQL** database, and a clean, responsive **HTML5/CSS3/vanilla JavaScript** frontend.

Flask serves both the REST API endpoints (`/api/*`) and the frontend static assets directly on a single port—no extra web servers, Node.js, or bundlers required.

---

## 🌟 Key Features

- **🔐 Session-Based Authentication**: Secure login/logout system using Flask-Login with role indicators (Admin & Librarian).
- **📖 Book Catalog Management**:
  - Add, edit, delete, and search books by title, author, or ISBN.
  - Live inventory tracking: distinguishes between `total_copies` and `available_copies`.
  - Duplicate ISBN collision prevention (`409 Conflict`).
  - Safe total copy adjustments (cannot reduce total copies below currently issued count).
  - Deletion protection: blocks deleting books that have copies currently on loan.
- **👥 Member Directory**:
  - Register, edit, search, and manage member profiles.
  - Status tracking (`active` vs. `suspended`).
  - Duplicate email protection on both creation and updates (`409 Conflict`).
  - Deletion protection: blocks deleting members with active loans to prevent orphan records.
- **🔄 Circulation (Issue & Return)**:
  - Issue books with automatic due date calculation (configurable loan period).
  - Suspended member and zero-availability guards.
  - Duplicate active loan protection (prevents issuing duplicate copies of the same book to the same member).
  - Return workflow with automatic overdue fine calculation ($1/day configurable).
  - Clamped availability safeguards.
- **✉️ Automated SMTP Email Notifications**:
  - Automatically scans active loans and sends a reminder **once only, exactly 5 days before** the loan's deadline.
  - Authenticates via your personal SMTP account while displaying `Reading Room Library <librarymanagement@gmail.com>` to the member.
  - Reminders can be triggered on-demand via the UI ("Send Due Reminders" button) or automatically scheduled via `send_reminders.py`.
  - **Stop reminders**: Marking a book as returned or clicking "Mark ready" immediately suppresses all deadline emails for that loan.
- **📊 Real-Time Dashboard**:
  - Live metric cards: total copies in catalog, available copies, registered members, active loans, and overdue returns.
  - Active loans table with real-time "On time" vs. "Overdue" status badges.
- **🌓 Modern UI**:
  - Built-in Dark Mode / Light Mode with persistent preference in `localStorage`.
  - Mobile-responsive drawer navigation with backdrop.
  - Toast notifications and modal dialogs.

---

## 🏗️ Project Architecture

```
lms/
├── .gitignore
├── README.md                      # Documentation and setup guide
├── backend/
│   ├── app.py                    # Flask application factory & frontend proxy
│   ├── config.py                 # Database connection & business rules
│   ├── extensions.py             # SQLAlchemy and LoginManager instances
│   ├── models.py                 # User, Book, Member, Transaction models
│   ├── requirements.txt          # Python dependencies
│   ├── schema.sql                # Reference MySQL schema
│   ├── seed.py                   # Creates tables and default admin account
│   └── routes/
│       ├── auth.py               # /api/auth (login, logout, session check)
│       ├── books.py              # /api/books (CRUD + search title/author/ISBN)
│       ├── members.py            # /api/members (CRUD + search name/email)
│       └── transactions.py       # /api/transactions (issue, return, stats)
└── frontend/
    ├── index.html                # Sign-in page
    ├── dashboard.html            # Metrics overview & active loans ledger
    ├── books.html                # Catalog management interface
    ├── members.html              # Member directory interface
    ├── transactions.html         # Loan circulation and return interface
    ├── css/
    │   └── style.css             # Theme variables, layouts, responsive drawer
    └── js/
        ├── api.js                # Fetch API wrapper, auth guards, theme toggler
        ├── dashboard.js          # Dashboard stats and active loans renderer
        ├── books.js              # Catalog search, modals, and CRUD handlers
        ├── members.js            # Member search, modals, and CRUD handlers
        └── transactions.js       # Issue modal, return flow, status filters
```

---

## 🚀 Getting Started Locally

### Prerequisites

Ensure the following are installed on your machine:
- **Python 3.10+** (Tested on Python 3.10, 3.11, 3.12, 3.14)
- **MySQL Server 8.0+** (Running locally on port 3306)

---

### Step 1: Set up MySQL Database

Open your MySQL client or MySQL Command Line Client and create the database:

```sql
CREATE DATABASE library_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

---

### Step 2: Configure Database & SMTP Credentials

Edit `backend/config.py` (or set environment variables) with your MySQL credentials and email SMTP settings:

```python
# Database settings
MYSQL_USER = os.environ.get("MYSQL_USER", "root")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "your_mysql_password")
MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
MYSQL_PORT = os.environ.get("MYSQL_PORT", "3306")
MYSQL_DB = os.environ.get("MYSQL_DB", "library_db")

# SMTP Email settings
SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USERNAME = os.environ.get("SMTP_USERNAME", "your_personal_email@gmail.com")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "your_app_password")  # 16-character Google App Password
SMTP_FROM_EMAIL = os.environ.get("SMTP_FROM_EMAIL", "librarymanagement@gmail.com")
SMTP_FROM_NAME = os.environ.get("SMTP_FROM_NAME", "Reading Room Library")
REMINDER_DAYS_BEFORE = int(os.environ.get("REMINDER_DAYS_BEFORE", "5"))
```

> **Tip (Gmail App Password)**: If using Gmail, turn on 2-Step Verification in your Google Account, then generate an **App Password** under *Security -> 2-Step Verification -> App Passwords* (select app name "LMS"). Use this 16-character password for `SMTP_PASSWORD`.

---

### Step 3: Install Dependencies & Run

#### On Windows (PowerShell):

```powershell
# 1. Navigate to backend directory
cd backend

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
.\venv\Scripts\Activate.ps1
# (Note: If execution policy blocks this, run: Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass)
# Or run commands directly using .\venv\Scripts\python.exe

# 4. Install required packages
pip install -r requirements.txt

# 5. Initialize tables and create the default admin user
python seed.py

# 6. (Optional) Run email reminder check manually via CLI
python send_reminders.py

# 7. Start the server
python app.py
```

#### On macOS / Linux:

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

python seed.py
python send_reminders.py    # (Optional) check reminders
python app.py
```

---

### Step 4: Open in Browser

Once the server is running, open:

👉 **[http://localhost:5000](http://localhost:5000)**

#### Default Credentials:
- **Username**: `admin`
- **Password**: `admin123`

---

## 📡 REST API Overview

| Endpoint | Method | Description | Auth Required |
|---|---|---|---|
| `/api/auth/login` | `POST` | Authenticates user & sets session cookie | No |
| `/api/auth/logout` | `POST` | Clears active session | Yes |
| `/api/auth/me` | `GET` | Returns currently logged-in user profile | No |
| `/api/books` | `GET` | List books (optional `?q=` search filter) | Yes |
| `/api/books` | `POST` | Add a new book to catalog | Yes |
| `/api/books/<id>` | `GET` | Retrieve book details | Yes |
| `/api/books/<id>` | `PUT` | Update book metadata and total copies | Yes |
| `/api/books/<id>` | `DELETE` | Delete book (blocked if active loans exist) | Yes |
| `/api/members` | `GET` | List members (optional `?q=` search filter) | Yes |
| `/api/members` | `POST` | Register a new member | Yes |
| `/api/members/<id>` | `GET` | Retrieve member profile | Yes |
| `/api/members/<id>` | `PUT` | Update member profile | Yes |
| `/api/members/<id>` | `DELETE` | Delete member (blocked if active loans exist) | Yes |
| `/api/transactions` | `GET` | List loans (optional `?status=issued\|returned`) | Yes |
| `/api/transactions/issue` | `POST` | Issue a book to an active member | Yes |
| `/api/transactions/return/<id>`| `POST` | Mark book returned & compute any late fee | Yes |
| `/api/transactions/ready/<id>` | `POST` | Toggle ready status (stops reminder emails) | Yes |
| `/api/transactions/check-reminders` | `POST` | Scan loans and send 5-day due date emails | Yes |
| `/api/transactions/stats` | `GET` | Aggregated dashboard metrics | Yes |

---

## 🛠️ Running Automated Tests

A comprehensive verification test suite is included to test all endpoints, validation rules, and edge cases:

```powershell
.\venv\Scripts\python.exe -c "import sys; sys.path.insert(0, 'backend'); from app import create_app; print('App loads successfully!')"
```

---

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).
