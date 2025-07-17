# Credit Approval System

A Django-based backend system for evaluating credit eligibility, managing loan creation, and storing historical customer and loan data. Data ingestion is handled via background tasks using Celery and Redis.



# Tech Stack

- Django 4
- Django REST Framework
- PostgreSQL
- Celery 
- Redis
- Docker 
- Docker-Compose



# Setup Guide

# 1. Clone and move into the repo
```bash
git clone https://github.com/Rishabhusesit/credit_approval_system.git
cd credit_approval_system

# 2. Start the services

docker-compose up --build

- This runs:

- Django app at localhost:8000

- PostgreSQL

- Redis

- Celery worker


# 3. Apply Migrations

docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate


# 4. Load initial data

- Make sure customer_data.xlsx and loan_data.xlsx are in the project root. Then:

docker-compose exec web python manage.py load_data


# Ingestion via Celery
- Ingestion is triggered with:

docker-compose exec web python manage.py load_data


# Available API Endpoints
- Register Customer
POST /api/customers/register/

- Check Loan Eligibility
POST /api/loans/check-eligibility/

- Create Loan
POST /api/loans/create-loan/

- View Loan by ID
GET /api/loans/view-loan/<loan_id>/

- View All Loans of a Customer
GET /api/loans/view-loans/<customer_id>/

