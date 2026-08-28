# KanMind Frontend

This directory contains the browser-based frontend for the KanMind task management application.

The frontend is based directly on the official KanMind frontend provided by Developer Akademie GmbH and is connected to the Django REST Framework backend located in:

```text
../backend
```

**Developed as part of the Developer Akademie GmbH advanced training program.**

## Technology Stack

- HTML
- CSS
- Vanilla JavaScript

No additional frontend framework is required to run the application locally.

## Backend Connection

The frontend communicates with the KanMind backend through the API at:

```text
http://127.0.0.1:8000/api/
```

The backend must be running before the frontend can use authentication, boards, tasks, and comments.

By default, the backend allows requests from:

```text
http://127.0.0.1:5500
http://localhost:5500
```

## Requirements

To run the frontend locally, you need:

- Python 3.11 or newer
- A running KanMind backend

No additional frontend dependencies need to be installed.

## Start the Frontend

Run the command from the project root directory.

### Windows

Open PowerShell:

```powershell
python -m http.server 5500 --directory frontend
```

### macOS / Linux

Open a terminal:

```bash
python3 -m http.server 5500 --directory frontend
```

The frontend will then be available at:

```text
http://127.0.0.1:5500/
```

## Start the Backend

The backend must run in parallel on port `8000`.

Backend setup instructions are available in:

```text
../backend/README.md
```

After the backend has been configured, it can be started from the `backend` directory with:

```bash
python manage.py runserver
```

The API will then be available at:

```text
http://127.0.0.1:8000/api/
```

## Local Development

A typical local development setup uses two terminals:

```text
Terminal 1
Backend:  http://127.0.0.1:8000/

Terminal 2
Frontend: http://127.0.0.1:5500/
```

The frontend sends API requests to the Django REST Framework backend for functionality including:

- User registration
- Login and authentication
- Boards
- Board members
- Tasks
- Task assignments
- Task reviews
- Comments

## Privacy and Imprint

The provided Imprint and Privacy sections intentionally do not contain personal information.

Before deploying or publishing the application in a context where legal information is required, these sections must be completed with the appropriate information.

Do not publish personal credentials, authentication tokens, secret keys, or other sensitive data.

## Source and Attribution

This frontend is based on the official KanMind frontend provided by Developer Akademie GmbH.

No frontend files from projects created by other course participants were used.

The original attribution and licensing information must remain intact.

**Developed as part of the Developer Akademie GmbH advanced training program.**

## License

The frontend and the components provided by Developer Akademie GmbH are subject to the:

**Developer Akademie Learning License (Non-commercial)**

The complete license is included in:

```text
LICENSE.md
```

The project may be publicly presented for non-commercial learning, portfolio, application, and reference purposes in accordance with the conditions of that license.

Commercial use, sale, monetization, paid services, or production operation are not permitted unless separately authorized by Developer Akademie GmbH.

## Related Documentation

For an overview of the complete KanMind project, see:

```text
../README.md
```

For detailed backend setup, API, authentication, permissions, and testing information, see:

```text
../backend/README.md
```
