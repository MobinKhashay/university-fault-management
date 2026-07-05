# University Fault Report & Management System

سامانه هوشمند گزارش و مدیریت خرابی‌های دانشگاه ارومیه

## About

A web-based platform for reporting, tracking, and managing university facility faults with automatic technician assignment based on specialty and shift.

## Tech Stack

- **Backend:** Python, Django
- **Frontend:** HTML5, CSS3, JavaScript
- **Database:** SQLite3

## Setup & Installation

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/university-fault-management.git
cd university-fault-management

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run migrations
python manage.py makemigrations
python manage.py migrate

# 5. Create superuser (admin)
python manage.py createsuperuser

# 6. Run development server
python manage.py runserver
```

## Project Structure

```
├── config/              # Django project settings
├── accounts/            # User auth, registration, profile
├── reports/             # Fault reports, locations, categories
├── technicians/         # Technician management
├── admin_panel/         # Admin dashboard & management
├── notifications/       # User notifications
├── faq/                 # FAQ management
├── templates/           # HTML templates
├── static/              # CSS, JS, images
├── media/               # User uploads
└── manage.py
```

## Team

- **Product Owner:** [Name]
- **Scrum Master:** [Name]
- **Backend Developer:** [Name]
- **Frontend Developer:** [Name]

## License

This project is developed for the Software Engineering 2 course at Urmia University (1404-1405).
