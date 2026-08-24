# KanMind Frontend

Dieses Frontend basiert direkt auf dem offiziellen KanMind-Frontend der Developer Akademie und ist mit dem lokalen Backend unter `../backend` verbunden. Es wurden keine Frontend-Dateien aus Projekten von Kursteilnehmenden übernommen.

## API-Verbindung

```javascript
const API_BASE_URL = 'http://127.0.0.1:8000/api/';
```

## Start

Vom Projekt-Root aus:

```powershell
.\backend\.venv\Scripts\python.exe -m http.server 5500 --directory frontend
```

Danach `http://127.0.0.1:5500/` öffnen. Das Backend muss parallel auf Port `8000` laufen.

Imprint und Privacy enthalten absichtlich keine personenbezogenen Angaben. Sie müssen vor einer Veröffentlichung mit den korrekten eigenen Informationen ergänzt werden.

Die mitgelieferte `LICENSE.md` und der Hinweis auf die offizielle Developer-Akademie-Quelle bleiben erhalten.
