# 🎓 College Placement System

A complete web-based College Placement System built with Python (Flask) + SQLite.

## Features

### Student Portal
- ✅ Register with name, email, branch, CGPA, skills, resume link
- ✅ Login / Logout
- ✅ View and edit profile
- ✅ Browse all recruiting companies
- ✅ Apply to companies (CGPA eligibility check)
- ✅ Track application status in real-time

### Admin Portal
- ✅ Secure admin login (default: admin / admin123)
- ✅ Dashboard with stats (students, companies, placements)
- ✅ View all registered students
- ✅ Add / Edit / Delete companies
- ✅ View all applications and update their status
  - Applied → Shortlisted → Interview Scheduled → Selected / Rejected

### Company Features
- ✅ 8 pre-loaded companies (TCS, Infosys, Wipro, Accenture, Amazon, Google, Microsoft, Cognizant)
- ✅ Role, package, location, branches, eligibility CGPA, last date

---

## Setup & Run

### 1. Install Requirements
```bash
pip install -r requirements.txt
```

### 2. Run the Application
```bash
python app.py
```

### 3. Open in Browser
```
http://127.0.0.1:5000
```

---

## Default Admin Credentials
| Field    | Value     |
|----------|-----------|
| Username | `admin`   |
| Password | `admin123`|

---

## Project Structure
```
placement_system/
│
├── app.py                    # Main Flask application
├── requirements.txt          # Python dependencies
├── placement.db              # SQLite database (auto-created)
│
└── templates/
    ├── base.html             # Base layout with navbar
    ├── home.html             # Landing page
    ├── register.html         # Student registration
    ├── student_login.html    # Student login
    ├── student_dashboard.html# Student dashboard
    ├── edit_profile.html     # Edit profile
    ├── companies.html        # Companies list & apply
    ├── admin_login.html      # Admin login
    ├── admin_dashboard.html  # Admin dashboard
    ├── admin_students.html   # Manage students
    ├── admin_companies.html  # Manage companies
    ├── add_company.html      # Add company form
    ├── edit_company.html     # Edit company form
    └── admin_applications.html # Manage applications
```

---

## Tech Stack
- **Backend:** Python 3, Flask
- **Database:** SQLite (built-in, no setup needed)
- **Frontend:** HTML5, Bootstrap 5, Font Awesome 6
- **Auth:** Session-based with SHA-256 password hashing
