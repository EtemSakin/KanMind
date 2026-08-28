# KanMind

KanMind is a full-stack Kanban task management application with a Django REST Framework backend and a browser-based frontend.

**Developed as part of the Developer Akademie GmbH advanced training program.**

This repository is intended exclusively for non-commercial learning, portfolio, application, and reference purposes.

## Overview

KanMind allows users to organize work in boards, create and manage tasks, assign responsibilities, review tasks, and collaborate through comments.

The project consists of a Django REST Framework API and a separate browser-based frontend.

## Features

- Email-based registration and login
- Token-based authentication
- Board creation and member management
- Task creation and editing
- Task assignment and review
- Task comments
- Object-level permissions
- Board membership validation
- Automated Django tests
- Environment-based configuration with `.env`

## Technology Stack

### Backend

- Python
- Django 5.2
- Django REST Framework
- DRF Token Authentication
- django-cors-headers
- python-dotenv
- SQLite

### Frontend

- HTML
- CSS
- Vanilla JavaScript

## Project Structure

```text
KanMind/
├── backend/
│   ├── auth_app/
│   ├── core/
│   ├── kanban_app/
│   ├── .env.example
│   └── README.md
│
├── frontend/
│   ├── README.md
│   └── LICENSE.md
│
├── KanMind.txt
└── README.md
```

## Quick Start

### 1. Set up the backend

Windows:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py migrate
python manage.py runserver
```

macOS / Linux:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver
```

The API will be available at:

```text
http://127.0.0.1:8000/api/
```

### 2. Start the frontend

Keep the backend running and open a second terminal in the project root.

Windows:

```powershell
python -m http.server 5500 --directory frontend
```

macOS / Linux:

```bash
python3 -m http.server 5500 --directory frontend
```

Then open:

```text
http://127.0.0.1:5500/
```

## Tests

With the backend virtual environment activated:

```bash
cd backend
python manage.py test
```

Detailed information about the backend setup, API endpoints, authentication, permissions, and tests is available in:

```text
backend/README.md
```

Frontend-specific information is available in:

```text
frontend/README.md
```

## Environment Configuration

The backend uses a local `.env` file for configuration.

Create it from:

```text
backend/.env.example
```

The local `.env` file is excluded from version control and should never contain secrets that are committed to the repository.

## Documentation

- `README.md` — Project overview and quick start
- `backend/README.md` — Backend setup, API, permissions, authentication, and tests
- `frontend/README.md` — Frontend setup, API connection, and license information

## License and Attribution

The frontend is based on the official KanMind frontend provided by Developer Akademie GmbH.

Components provided by Developer Akademie are subject to the **Developer Akademie Learning License (Non-commercial)** included in:

```text
frontend/LICENSE.md
```

This project may be publicly presented for non-commercial learning, portfolio, application, and reference purposes in accordance with the conditions of that license.

Commercial use, sale, monetization, paid services, or production operation are not permitted unless separately authorized by Developer Akademie GmbH.

**Developed as part of the Developer Akademie GmbH advanced training program.**
