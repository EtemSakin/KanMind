# KanMind Backend

KanMind Backend is the Django REST Framework API for the KanMind task management application.

It provides authentication, board management, task management, comments, object-level permissions, and validation for collaborative Kanban workflows.

**Developed as part of the Developer Akademie GmbH advanced training program.**

## Technology Stack

- Python
- Django 5.2
- Django REST Framework
- DRF Token Authentication
- django-cors-headers
- python-dotenv
- SQLite

## Project Structure

```text
backend/
├── auth_app/
│   ├── api/
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── admin.py
│   ├── managers.py
│   ├── models.py
│   └── tests.py
│
├── kanban_app/
│   ├── api/
│   │   ├── permissions.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── admin.py
│   ├── models.py
│   ├── test_comments.py
│   ├── test_tasks.py
│   └── tests.py
│
├── core/
│   ├── settings.py
│   ├── urls.py
│   └── views.py
│
├── .env.example
├── manage.py
├── requirements.txt
└── README.md
```

## Application Structure

### `auth_app`

Handles authentication and user-related functionality.

Main responsibilities:

- Custom user model
- Email-based login
- User registration
- DRF token authentication
- Email lookup
- Custom user manager
- User administration

The custom user model uses `email` as the unique login identifier and does not require a username.

### `kanban_app`

Handles Kanban-specific functionality.

Main responsibilities:

- Boards
- Board members
- Tasks
- Assignees
- Reviewers
- Comments
- Object-level permissions
- Board membership validation

### `core`

Contains the central Django project configuration.

Main responsibilities:

- Django settings
- Root URL configuration
- API root view
- Environment configuration
- CORS configuration

## Requirements

- Python 3.11 or newer
- pip

## Local Setup

### Windows

Open PowerShell and navigate to the backend directory:

```powershell
cd backend
```

Create a virtual environment:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the dependencies:

```powershell
python -m pip install -r requirements.txt
```

Create the local environment file:

```powershell
Copy-Item .env.example .env
```

Apply the database migrations:

```powershell
python manage.py migrate
```

Start the development server:

```powershell
python manage.py runserver
```

### macOS / Linux

Open a terminal and navigate to the backend directory:

```bash
cd backend
```

Create a virtual environment:

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

Install the dependencies:

```bash
python -m pip install -r requirements.txt
```

Create the local environment file:

```bash
cp .env.example .env
```

Apply the database migrations:

```bash
python manage.py migrate
```

Start the development server:

```bash
python manage.py runserver
```

The API will then be available at:

```text
http://127.0.0.1:8000/api/
```

## Environment Configuration

The backend loads environment variables from:

```text
backend/.env
```

The repository contains a template:

```text
backend/.env.example
```

Available environment variables:

```text
KANMIND_SECRET_KEY
KANMIND_DEBUG
KANMIND_ALLOWED_HOSTS
KANMIND_CORS_ALLOWED_ORIGINS
```

Example:

```env
KANMIND_SECRET_KEY=replace-with-a-secure-secret-key
KANMIND_DEBUG=true
KANMIND_ALLOWED_HOSTS=127.0.0.1,localhost
KANMIND_CORS_ALLOWED_ORIGINS=http://127.0.0.1:5500,http://localhost:5500
```

The local `.env` file is excluded from Git and should never contain secrets that are committed to the repository.

## Database

KanMind uses SQLite for local development.

After installing the dependencies, initialize the database with:

```bash
python manage.py migrate
```

The local database file is excluded from version control.

## Authentication

KanMind uses Django REST Framework token authentication.

### Registration

```http
POST /api/registration/
```

Creates a new user account and returns authentication data.

### Login

```http
POST /api/login/
```

Authenticates an existing user and returns authentication data.

### Authentication Header

Protected requests use:

```text
Authorization: Token <token>
```

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/registration/` | Register a new user |
| POST | `/api/login/` | Log in and receive authentication data |
| GET | `/api/email-check/?email=...` | Find a user by email address |

### Boards

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/boards/` | List boards accessible to the current user |
| POST | `/api/boards/` | Create a new board |
| GET | `/api/boards/<id>/` | Retrieve a board |
| PATCH | `/api/boards/<id>/` | Update a board |
| DELETE | `/api/boards/<id>/` | Delete a board |

### Tasks

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/tasks/` | Create a task |
| GET | `/api/tasks/<id>/` | Retrieve a task |
| PATCH | `/api/tasks/<id>/` | Update a task |
| DELETE | `/api/tasks/<id>/` | Delete a task |
| GET | `/api/tasks/assigned-to-me/` | List tasks assigned to the current user |
| GET | `/api/tasks/reviewing/` | List tasks reviewed by the current user |

### Comments

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/tasks/<task_id>/comments/` | List task comments |
| POST | `/api/tasks/<task_id>/comments/` | Create a task comment |
| DELETE | `/api/tasks/<task_id>/comments/<comment_id>/` | Delete a comment |

## Permissions

KanMind uses object-level permissions for boards, tasks, and comments.

| Action | Permission |
|---|---|
| View a board | Board owner or member |
| Update a board | Board owner or member |
| Delete a board | Board owner |
| Create a task | Board owner or member |
| View a task | Board owner or member |
| Update a task | Board owner or member |
| Delete a task | Task creator or board owner |
| View comments | Board owner or member |
| Create comments | Board owner or member |
| Delete a comment | Comment author |

## Board and Task Rules

The board owner is automatically included in the board member list.

Task assignees and reviewers must belong to the corresponding board.

A task cannot be moved to another board through an update.

## Admin Interface

The Django admin interface is available at:

```text
http://127.0.0.1:8000/admin/
```

Create an admin user with:

```bash
python manage.py createsuperuser
```

The admin interface includes management for:

- Users
- Boards
- Tasks
- Comments

## Tests

Run the complete backend test suite with:

```bash
python manage.py test
```

The test suite covers areas including:

- Registration
- Login
- Authentication
- Boards
- Tasks
- Comments
- Permissions
- Validation
- Object-level access rules

## CORS

The backend is configured for the local frontend by default.

Default allowed origins:

```text
http://127.0.0.1:5500
http://localhost:5500
```

These values can be changed through:

```text
KANMIND_CORS_ALLOWED_ORIGINS
```

## Frontend

The matching browser frontend is located at:

```text
../frontend
```

It normally runs locally on port:

```text
5500
```

Frontend-specific setup and license information is documented in:

```text
../frontend/README.md
```

## Security Notes

- Do not commit the local `.env` file.
- Do not commit real secret keys.
- Use test data for public demonstrations.
- The included development configuration is not intended for production use.
- Disable Django debug mode for non-development environments.

## License and Attribution

This backend was developed as part of the KanMind project within the Developer Akademie GmbH advanced training program.

The repository includes frontend components provided by Developer Akademie GmbH.

Those provided components are subject to the **Developer Akademie Learning License (Non-commercial)**.

See:

```text
../frontend/LICENSE.md
```

for the applicable license terms.

This project is intended for non-commercial learning, portfolio, application, and reference purposes.

**Developed as part of the Developer Akademie GmbH advanced training program.**
