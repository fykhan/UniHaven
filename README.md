# UniHaven

UniHaven is a university-managed accommodation platform designed to help students and university staff search, manage, and reserve housing in Hong Kong. Each participating university has their own administration team to manage listings and handle reservations for their students.

---

## Features

* Token + Session-based authentication
* University-based access control for accommodations
* Add, edit, and delete accommodation listings
* Filter accommodations by:

  * Property type
  * Availability period
  * Number of beds / bedrooms
  * Price range
  * Distance from a university campus
* Reservation system with availability checks
* Ratings and reviews for accommodations
* Notifications sent to staff emails upon reservations
* Distance pre-calculated from all major campuses

---

## Tech Stack

* Python 3.12
* Django 4.x
* Django REST Framework
* SQLite (for development)
* Token-based API authentication
* Email backend (console for development)

---

## Project Structure

```
unihaven/
├── users/              # Handles user creation and university-specific profile logic
├── accommodations/     # Accommodation models, distance logic, and admin views
├── api/                # REST API endpoints, authentication, filtering, reservations
├── templates/          # HTML templates for web views (e.g., login, dashboard)
├── static/             # Static files (CSS, JS)
└── manage.py           # Django management script
```

---

## Authentication

* Users are authenticated via:

  * Token Authentication (for API tools like curl, Postman)
  * Session Authentication (for web browser views)
* Each user belongs to a specific university
* All accommodation operations are restricted based on university affiliation

---

## Sample API Usage

API Documentation provided in repository

### List Accommodations for a University

```
curl -H "Authorization: Token <your_token>" \
http://127.0.0.1:8000/api/filter/
```

### Create a Reservation

```
curl -X POST -H "Authorization: Token <your_token>" \
-H "Content-Type: application/json" \
-d '{
  "accommodation": 1,
  "student_name": "Alice",
  "student_email": "alice@example.com",
  "start_date": "2025-06-01",
  "end_date": "2025-07-31"
}' http://127.0.0.1:8000/api/reservations/
```

---

## Supported Universities & Campuses

* HKU - Main Campus: 22.28405, 114.13784
* CUHK - Main Campus: 22.41907, 114.20693
* HKUST - Main Campus: 22.33584, 114.26355
* Additional HKU satellite campuses supported with distance computation

---

## Getting Started

1. Clone the repository:

```
git clone https://github.com/fykhan/UniHaven.git
cd UniHaven
```

2. Create virtual environment and install dependencies:

```
python -m venv env
source env/bin/activate  # or env\Scripts\activate on Windows
pip install -r requirements.txt
```

3. Apply migrations:

```
python manage.py migrate
```

4. Create a superuser:

```
python manage.py createsuperuser
```

5. Run the development server:

```
python manage.py runserver
```

---
