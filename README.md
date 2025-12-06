# Transaction Service

A secure service for transferring funds between wallets with protection against race conditions and automatic commission
calculation.

---

## Overview

This project implements an internal system for transferring funds between user wallets and a technical wallet.

Key features:

- Safe transfers with balance validation
- Protection against **race conditions** for concurrent requests
- Pessimistic row locking (`select_for_update`) and atomic transactions (`transaction.atomic`)
- Automatic commission calculation for large transfers
- Asynchronous transfer notifications via Celery

---

## Technologies

- Python 3.11+
- Django 4+
- PostgreSQL
- Celery + Redis (for async tasks)
- httpx (for API testing)

---

## Configuration

Configuration is stored in `.env`, for examples see `.env.example`

### Install requirements:

```bash
pip install -r requirements.txt
```

### Apply migrations:

```bash
python manage.py migrate
```

### Run redis by the command

```bash
docker run -d -p 6379:6379 redis
```

### Run Celery worker for async notifications:

```bash
celery -A transfer worker -l info
```

### Run server:

```bash
python manage.py runserver
```

### Add superuser:

```bash
python manage.py createsuperuser --username admin --email admin@example.com
```
