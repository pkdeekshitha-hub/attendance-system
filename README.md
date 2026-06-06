# Smart Attendance Management System

A full-stack web application for managing student attendance, tasks, and generating reports.

## Tech Stack
- **Frontend:** HTML, CSS, JavaScript, Bootstrap 5
- **Backend:** Python Flask, REST APIs
- **Database:** MySQL
- **Authentication:** JWT (JSON Web Tokens)

## Features
- Student registration and login
- Mark attendance (Present / Absent / Late)
- View attendance history
- Monthly attendance percentage with progress bar
- Task submission and tracking
- Admin dashboard with analytics
- Student performance charts
- Export attendance reports to Excel
- Admin can manage all students and tasks

## Project Structure

attendance-system/
├── backend/
│   ├── app.py
│   ├── config.py
│   └── routes/
│       ├── auth.py
│       ├── attendance.py
│       ├── admin.py
│       ├── tasks.py
│       └── export.py
└── frontend/
├── index.html
├── login.html
├── signup.html
├── dashboard.html
├── admin-login.html
└── admin.html


## API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/auth/register | Student registration |
| POST | /api/auth/login | Student login |
| POST | /api/auth/admin/login | Admin login |
| GET | /api/auth/profile | Get student profile |
| POST | /api/attendance/mark | Mark attendance |
| GET | /api/attendance/history | View history |
| GET | /api/attendance/percentage | Monthly percentage |
| GET | /api/admin/students | All students |
| GET | /api/admin/attendance | All attendance |
| GET | /api/admin/analytics | Dashboard analytics |
| POST | /api/tasks/submit | Submit task |
| GET | /api/tasks/my-tasks | View my tasks |
| GET | /api/export/attendance | Export to Excel |

## Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/pkdeekshitha-hub/attendance-system.git
cd attendance-system
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install flask flask-mysqldb flask-jwt-extended flask-cors bcrypt pandas openpyxl
```

### 3. Database Setup
- Create MySQL database called `attendance_db`
- Run the SQL from `database/schema.sql`
- Update `config.py` with your MySQL password

### 4. Run Backend
```bash
python app.py
```

### 5. Run Frontend
- Open `frontend/index.html` with Live Server in VS Code

## Default Admin Credentials
- Email: admin@school.com
- Password: admin123

## Developer
- **Name:** Deekshitha
- **GitHub:** github.com/pkdeekshitha-hub
"@ | Set-Content README.md

