# KanMind

Vollständiges lokales KanMind-Projekt mit getrenntem Frontend und Backend.

**Entwickelt im Rahmen des Weiterbildungsprogramms der Developer Akademie GmbH.**

Dieses Repository dient ausschließlich nicht-kommerziellen Lern-, Portfolio-, Bewerbungs- und Referenzzwecken.

```text
KanMind/
├── backend/      Django REST Framework API
├── frontend/     HTML/CSS/Vanilla-JavaScript-Frontend
├── KanMind.txt   ursprünglicher Projektbrief
└── README.md
```

## Anwendung starten

Zwei PowerShell-Terminals im Projektordner öffnen.

Terminal 1 – Backend:

```powershell
.\backend\.venv\Scripts\python.exe backend\manage.py runserver 127.0.0.1:8000
```

Terminal 2 – Frontend:

```powershell
.\backend\.venv\Scripts\python.exe -m http.server 5500 --directory frontend
```

Anschließend im Browser öffnen:

```text
http://127.0.0.1:5500/
```

Das Frontend kommuniziert über `http://127.0.0.1:8000/api/` mit dem Backend. CORS ist für `127.0.0.1:5500` und `localhost:5500` freigegeben.

Als Frontendbasis dient ausschließlich das offizielle KanMind-Frontend der Developer Akademie. Personenbezogene Imprint-/Privacy-Angaben sind nicht hinterlegt.

## Lizenz

Für die von der Developer Akademie bereitgestellten Frontend-Bestandteile gilt die [Developer Akademie Lernlizenz (Nicht-kommerziell)](frontend/LICENSE.md). Der eigenständig entwickelte Backend-Code wird zusammen mit dem Frontend ausschließlich im Rahmen der dort geregelten Portfolio-Nutzung veröffentlicht.

Eine kommerzielle Nutzung, ein Verkauf, eine Monetarisierung oder ein produktiver Betrieb sind nicht gestattet.

## Backend testen

```powershell
.\backend\.venv\Scripts\python.exe backend\manage.py test
```

Weitere Details stehen in `backend/README.md` und `frontend/README.md`.
