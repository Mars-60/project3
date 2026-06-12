<div align="center">

<img src="https://img.shields.io/badge/Atlas-5b7fff?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAzMiAzMiI+PGNpcmNsZSBjeD0iMTYiIGN5PSIxNiIgcj0iMTQiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iMS41IiBmaWxsPSJub25lIi8+PGVsbGlwc2UgY3g9IjE2IiBjeT0iMTYiIHJ4PSI2IiByeT0iMTQiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iMS41IiBmaWxsPSJub25lIi8+PGxpbmUgeDE9IjIiIHkxPSIxNiIgeDI9IjMwIiB5Mj0iMTYiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iMS41Ii8+PC9zdmc+" alt="Atlas">

# Atlas 

**Your local AI memory layer for Windows.**  
Atlas silently tracks your PC activity in the background and lets you explore everything — apps used, websites visited, screen time, and more — through a beautiful dashboard. Ask questions about your day in plain English using the built-in AI chat.

[![Python](https://img.shields.io/badge/Python-3.10+-3776ab?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.x-black?style=flat-square&logo=flask)](https://flask.palletsprojects.com)
[![Gemini](https://img.shields.io/badge/Gemini_AI-chat-4285f4?style=flat-square&logo=google)](https://aistudio.google.com)
[![Platform](https://img.shields.io/badge/Platform-Windows-0078d4?style=flat-square&logo=windows)](https://www.microsoft.com/windows)
[![Demo](https://img.shields.io/badge/Demo-Live-5b7fff?style=flat-square&logo=vercel)](https://atlas-live-demo.vercel.app/)

[![Live Demo](https://img.shields.io/badge/Live_Demo-atlas--live--demo.vercel.app-5b7fff?style=for-the-badge&logo=vercel&logoColor=white)](https://atlas-live-demo.vercel.app/)

> **[→ Try the live demo](https://atlas-live-demo.vercel.app/)** — explore the dashboard with sample data, no setup needed.

</div>

---

## What is Atlas?

Atlas is a **local, privacy-first activity tracker** that runs silently in the background on your Windows PC. No cloud. No subscriptions. Everything stays on your machine.

Once set up, Atlas:
- **Records** which apps you use and for how long
- **Tracks** which websites you visit and your time on each
- **Captures** window titles and screen content via OCR
- **Answers** natural language questions about your activity using Gemini AI

Open the dashboard any time to see your day — or ask *"What was I doing at 3pm?"* and get an instant answer.

---

## Features

| Feature | Description |
|---|---|
| 🔇 **Silent background recording** | Starts at login, no terminal, no popups |
| 📊 **Live dashboard** | Screen time, app usage, website time, hourly chart |
| 🌐 **Browser tracking** | Chrome extension tracks tabs and time per site |
| 🤖 **AI chat** | Ask anything about your activity in plain English |
| 📁 **Activity feed** | Full searchable log of every captured event |
| 🔒 **100% local** | All data stored in SQLite on your machine |
| ⚙️ **One-time setup** | Single `.bat` file handles everything |

---

## How It Works

```
┌────────────────────────────────────────────────────┐
│                   Your Windows PC                  │
│                                                    │
│  ┌─────────────┐    ┌──────────────┐               │
│  │Window Logger│    │Chrome Ext.   │               │
│  │(active app, │    │(tab switches,│               │
│  │window title)│    │ heartbeats)  │               │
│  └──────┬──────┘    └──────┬───────┘               │
│         │                  │                       │
│         └────────┬─────────┘                       │
│                  ▼                                 │
│          ┌──────────────┐                          │
│          │  Flask API   │  ◄── SQLite DB           │
│          │  :5000       │  ◄── Gemini AI           │
│          └──────┬───────┘                          │
│                 │                                  │
│          ┌──────▼───────┐                          │
│          │ atlas.html   │  ← You open this         │
│          │  Dashboard   │                          │
│          └──────────────┘                          │
└────────────────────────────────────────────────────┘
```

---

## Requirements

- Windows 10 or 11
- Python 3.10 or higher → [Download](https://www.python.org/downloads/) *(check "Add to PATH")*
- Google Chrome
- Tesseract OCR → [Download](https://github.com/UB-Mannheim/tesseract/wiki) *(install to default path)*
- A free Gemini API key → [Get one here](https://aistudio.google.com/app/apikey)

---

## Installation

### Step 1 — Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/atlas.git
cd atlas
```

Or [download as ZIP](https://github.com/YOUR_USERNAME/atlas/archive/refs/heads/main.zip) and extract.

### Step 2 — Run setup

Double-click `setup.bat` and follow the prompts. It will:

1.  Check Python and pip
2.  Create a virtual environment
3.  Install all dependencies
4.  Check Tesseract OCR
5.  Ask for your Gemini API key and save it
6.  Initialize the database
7.  Ask if you want Atlas to auto-start on login (recommended: Y)

> **Setup takes about 3–5 minutes on first run.**

### Step 3 — Install the Chrome Extension

1. Open Chrome and go to `chrome://extensions`
2. Enable **Developer mode** (top right toggle)
3. Click **Load unpacked**
4. Select the `extension` folder inside the project

### Step 4 — Register auto-start (if not done during setup)

Right-click `register_task.ps1` → **Run with PowerShell**  
*(Requires Admin once — never again after this)*

---

## Usage

### Accessing the Dashboard

After setup, Atlas runs silently in the background from every login.

**To open the dashboard:** Double-click the **"Atlas Dashboard"** shortcut on your Desktop, or open `frontend/atlas.html` directly in Chrome.

```
frontend/atlas.html  ← open this in Chrome
```

### Dashboard Overview

| Section | What it shows |
|---|---|
| **Home** | Total logs, apps tracked, days of memory |
| **Dashboard** | Screen time, app usage bars, website time, hourly chart |
| **Activity Feed** | Full searchable log of all captured events |
| **Ask Atlas AI** | Chat with Gemini about your activity |

### Asking Atlas Questions

Click the chat button (bottom right) or press `Ctrl+Space` anywhere on the dashboard.

Example questions:
- *"What was I doing today?"*
- *"How much time did I spend on YouTube this week?"*
- *"What websites did I visit yesterday?"*
- *"Summarize my coding sessions"*

---

## Project Structure

```
atlas/
├── backend/
│   ├── agents/              # Gemini AI memory agents
│   ├── ai/                  # Gemini API client
│   ├── api/
│   │   └── server.py        # Flask REST API
│   ├── collectors/
│   │   ├── window_logger.py # Active window tracker
│   │   └── ocr_collector.py # Screen OCR capture
│   ├── database/
│   │   └── db.py            # SQLite operations
│   ├── retrieval/           # RAG pipeline components
│   └── utils/
├── extension/
│   ├── background.js        # Chrome extension (tab tracking)
│   ├── manifest.json
│   └── popup.html
├── frontend/
│   └── atlas.html           # Dashboard (single-file)
├── data/                    # SQLite database (gitignored)
├── .env                     # Your API key (gitignored)
├── start_atlas.py           # Silent background launcher
├── setup.bat                # One-click installer
├── register_task.ps1        # Task Scheduler registration
├── atlas_silent_launch.vbs  # Windowless startup helper
└── requirements.txt
```

---

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/browser_activity` | POST | Receives tab data from Chrome extension |
| `/dashboard_stats` | GET | App + site durations for a date range |
| `/recent` | GET | Latest activity logs |
| `/stats` | GET | Total log count, apps, days |
| `/chat` | POST | Ask Gemini a question about your activity |

---

## Privacy

- **All data is stored locally** in `data/activity.db` (SQLite)
- **Nothing is sent to the cloud** except your questions to Gemini AI
- **The `.env` file** containing your API key is gitignored and never uploaded
- **To delete all your data:** delete `data/activity.db` and restart Atlas

---

## Troubleshooting

**Dashboard shows "No data — start the Flask server"**  
→ Atlas isn't running. Run `register_task.ps1` as Admin, then restart your PC.  
→ Or manually start it: open PowerShell in the project folder and run:
```powershell
.\venv\Scripts\python.exe start_atlas.py
```

**Chrome extension shows fetch errors**  
→ Make sure Atlas is running (check Task Manager for `pythonw.exe`)  
→ Go to `chrome://extensions`, find Atlas, and click the refresh icon

**Websites show 0s time**  
→ Make sure the Chrome extension is loaded and enabled  
→ The heartbeat updates every 5 seconds — give it a minute

**Setup fails at "Installing packages"**  
→ Check your internet connection  
→ Try running `setup.bat` as Administrator

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.10+, Flask, flask-cors |
| AI | Google Gemini API |
| Database | SQLite (local, no server needed) |
| OCR | Tesseract OCR + pytesseract |
| Screenshots | Pillow (PIL) |
| Window Tracking | pywin32, pygetwindow |
| Frontend | Vanilla HTML/CSS/JS (single file, no framework) |
| Browser | Chrome Extension (Manifest V3) |
| Deployment | Runs locally on Windows |

---

## Contributing

Pull requests are welcome. For major changes, please open an issue first.

1. Fork the repo
2. Create your branch: `git checkout -b feature/your-feature`
3. Commit: `git commit -m "Add your feature"`
4. Push: `git push origin feature/your-feature`
5. Open a Pull Request

---

<div align="center">

Built by [Adnan Raza](https://github.com/YOUR_USERNAME) · CSE @ JMI, New Delhi, India  
*A personal project to track and understand how I spend my time on my PC.*

</div>
