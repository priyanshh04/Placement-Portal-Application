# Placement Portal Application

Role-based campus placement portal built with Flask, Jinja2, Bootstrap, and SQLite.

## Features

- Admin login seeded automatically on first run
- Student and company registration
- Admin approval flow for companies and placement drives
- Student applications with duplicate-application protection
- Company-side applicant tracking and status updates
- Resume upload support using local file storage
- Search, blacklisting, deactivation, and history views

## Project Structure

```text
placement-portal/
|-- app/
|   |-- __init__.py
|   |-- admin_routes.py
|   |-- auth_routes.py
|   |-- company_routes.py
|   |-- extensions.py
|   |-- models.py
|   |-- student_routes.py
|   |-- utils.py
|   |-- static/
|   |   `-- css/
|   |       `-- styles.css
|   |-- templates/
|   |   |-- base.html
|   |   |-- index.html
|   |   |-- auth/
|   |   |   |-- login.html
|   |   |   |-- register_company.html
|   |   |   `-- register_student.html
|   |   |-- admin/
|   |   |   `-- dashboard.html
|   |   |-- company/
|   |   |   |-- applications.html
|   |   |   |-- dashboard.html
|   |   |   |-- edit_drive.html
|   |   |   `-- profile.html
|   |   `-- student/
|   |       |-- dashboard.html
|   |       `-- profile.html
|   `-- uploads/
|-- requirements.txt
`-- run.py
```

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

Open `http://127.0.0.1:5000`

## Default Admin Credentials

- Email: `admin@placement.local`
- Password: `admin123`