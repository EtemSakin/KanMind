# KanMind Backend

KanMind ist eine REST-API für ein Kanban-Board. Sie wurde mit Django, Django REST Framework und DRF Token Authentication umgesetzt und ist auf das KanMind-Frontend der Developer Akademie abgestimmt.

## Technischer Aufbau

- `auth_app`: Custom User, Registrierung, Login und E-Mail-Suche
- `kanban_app`: Boards, Tasks, Kommentare und objektbezogene Permissions
- `core`: Django-Konfiguration und zentrale URL-Konfiguration
- SQLite für die lokale Entwicklung

Der Custom User verwendet `email` als eindeutiges Login-Feld und besitzt kein `username`.

## Lokale Einrichtung unter Windows

Voraussetzungen: Python 3.11+ und `uv`.

```powershell
uv venv .venv --python 3.11
uv pip install --python .venv\Scripts\python.exe -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py runserver
```

Die API läuft anschließend unter `http://127.0.0.1:8000/api/`.

Wenn die Befehle vom übergeordneten Projektordner ausgeführt werden, zuerst wechseln:

```powershell
Set-Location backend
```

Optional kann ein Admin-Benutzer angelegt werden:

```powershell
.\.venv\Scripts\python.exe manage.py createsuperuser
```

## Konfiguration

Die lokalen Standardwerte funktionieren ohne zusätzliche Konfiguration. Für andere Umgebungen stehen diese Umgebungsvariablen bereit:

- `KANMIND_SECRET_KEY`
- `KANMIND_DEBUG` (`true` oder `false`)
- `KANMIND_ALLOWED_HOSTS` (kommagetrennt)
- `KANMIND_CORS_ALLOWED_ORIGINS` (kommagetrennt)

## Authentifizierung

Registrierung und Login liefern ein DRF-Token. Geschützte Requests verwenden:

```text
Authorization: Token <token>
```

## Endpunkte

| Methode | URL | Zweck |
|---|---|---|
| POST | `/api/registration/` | Benutzer registrieren |
| POST | `/api/login/` | Login und Token abrufen |
| GET | `/api/email-check/?email=...` | Benutzer anhand der E-Mail suchen |
| GET, POST | `/api/boards/` | Eigene Boards auflisten oder Board erstellen |
| GET, PATCH, DELETE | `/api/boards/<id>/` | Board anzeigen, ändern oder löschen |
| POST | `/api/tasks/` | Task erstellen |
| GET, PATCH, DELETE | `/api/tasks/<id>/` | Task anzeigen, ändern oder löschen |
| GET | `/api/tasks/assigned-to-me/` | Zugewiesene Tasks auflisten |
| GET | `/api/tasks/reviewing/` | Zu prüfende Tasks auflisten |
| GET, POST | `/api/tasks/<task_id>/comments/` | Kommentare auflisten oder erstellen |
| DELETE | `/api/tasks/<task_id>/comments/<comment_id>/` | Eigenen Kommentar löschen |

## Berechtigungen

| Aktion | Berechtigung |
|---|---|
| Board ansehen oder bearbeiten | Owner oder Member |
| Board löschen | nur Owner |
| Task erstellen, ansehen oder bearbeiten | Board-Owner oder Board-Member |
| Task löschen | Task-Ersteller oder Board-Owner |
| Kommentare ansehen oder erstellen | Board-Owner oder Board-Member |
| Kommentar löschen | nur Kommentar-Autor |

Assignee und Reviewer eines Tasks müssen zum zugehörigen Board gehören. Der Board-Owner wird bei Erstellung und Update automatisch in der Memberliste gehalten.

## Tests

```powershell
.\.venv\Scripts\python.exe manage.py test
```

Das zugehörige Browser-Frontend liegt unter `../frontend` und wird auf Port `5500` gestartet.
