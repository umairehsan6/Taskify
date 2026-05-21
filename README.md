<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=11,20,24&height=150&section=header&text=Taskify&fontSize=52&fontColor=fff&animation=twinkling&fontAlignY=38&desc=Team%20Management%20%26%20Collaboration%20Tool&descAlignY=60&descSize=16"/>

[![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)](https://djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org/)
[![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white)](https://mysql.com/)
[![WebSockets](https://img.shields.io/badge/WebSockets-010101?style=for-the-badge&logo=socketdotio&logoColor=white)](https://channels.readthedocs.io/)
[![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)](https://developer.mozilla.org/en-US/docs/Web/HTML)

</div>

---

## 📸 Screenshots

> Add screenshots here — dashboard, task board, team view, analytics

| Admin Dashboard | Task Board | Analytics |
|----------------|-----------|-----------|
| ![dashboard](https://github.com/umairehsan6/Taskify/blob/master/screen%20shots/admin/admin-dashboard.png) | ![Employee Dashboard](https://github.com/umairehsan6/Taskify/blob/master/screen%20shots/employee/Home%20Page.png) | ![analytics](add-screenshot-url) |

---

## ✨ Features

### 👥 Role-Based Access Control
Four distinct permission levels — each with a tailored interface:

| Role | Capabilities |
|------|-------------|
| **Admin** | Full CRUD on users, departments, projects · assign tasks · view all stats |
| **Manager** | Create & assign projects · monitor team progress |
| **Team Lead** | Manage task assignments within their team |
| **Employee** | View & update assigned tasks · log work hours |

### ⚡ Real-Time Collaboration
- WebSocket-powered comment threads on every task
- Live file sharing within task threads
- Instant notifications on task updates

### ⏱️ Smart Time Tracking
- Time tracking microservice that auto-pauses tasks outside office hours
- Improves time tracking accuracy by **40%**
- Monthly stats, efficiency scores, and visual time charts

### 🔐 Security
- OTP verification on registration and sensitive actions
- JWT-based session authentication
- Role-gated API endpoints

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django, Python |
| Real-Time | Django Channels (WebSockets) |
| Frontend | HTML, CSS, JavaScript |
| Database | MySQL via Django ORM |
| Auth | JWT + OTP Verification |

---

## ⚡ Getting Started

### Prerequisites
- Python 3.10+
- MySQL

### Setup

```bash
# Clone the repo
git clone https://github.com/umairehsan6/Taskify.git
cd Taskify

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure your database in taskify/settings.py

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create a superuser (admin account)
python manage.py createsuperuser

# Seed admin user
python seed_admin.py

# Start the time tracking service (runs office-hours checks)
python manage.py check_office_hours

# Start the server
python manage.py runserver
```

Or simply:

```bash
python run.py
```

---

## 📁 Project Structure

```
Taskify/
├── app/                  # Core Django app
│   ├── models.py         # User, Task, Department, Project models
│   ├── views.py          # Role-based views
│   ├── consumers.py      # WebSocket consumers
│   └── urls.py
├── taskify/              # Project settings
├── media/                # Uploaded files
├── logs/                 # Application logs
├── seed_admin.py         # Admin seeder
├── run.py                # One-command startup
└── requirements.txt
```

---

## 📊 Modules

```
✅ User Management       — CRUD, roles, departments
✅ Project Management    — create, assign, track
✅ Task Management       — assign, update, comment, share files
✅ Time Tracking         — auto-pause, office hours, efficiency scores
✅ OTP Authentication    — secure login & verification
✅ Real-Time Updates     — WebSocket comment threads
✅ Analytics Dashboard   — monthly stats, charts, performance scores
```

---

<div align="center">

Made by [Umair Ehsan](https://github.com/umairehsan6)

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=11,20,24&height=80&section=footer"/>

</div>
