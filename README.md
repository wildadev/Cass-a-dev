# Cass — Your AI Executive Assistant

Cass is a personal AI executive assistant powered by Claude that handles day-to-day administrative tasks: email triage and drafting, calendar management, meeting prep, web research, and task tracking.

## Features

- **Chat Interface** — Talk to Cass naturally, with voice input support
- **Email Management** — Read, search, and draft replies (Gmail). All drafts require your approval before sending
- **Calendar** — View events, check availability, create meetings (Google Calendar)
- **Web Research** — Quick lookups and deep multi-source research reports
- **Task Tracking** — Track tasks across projects with priority levels and status
- **Persistent Memory** — Learns your preferences, contacts, and working style over time
- **Dashboard** — Central view with approval queue, active tasks, calendar, and activity log
- **Feedback Loop** — Gets better over time based on your approvals, edits, and feedback
- **Mobile Responsive** — Full workspace on desktop, optimized layout on mobile

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- [Anthropic API key](https://console.anthropic.com/)
- Google Cloud project with Gmail and Calendar APIs enabled (for email/calendar features)

### Setup

```bash
# Clone and enter the project
cd Cass-a-dev

# Copy environment template and fill in your keys
cp .env.example .env

# Install Python dependencies
pip install -e .

# Install frontend dependencies
cd frontend && npm install --legacy-peer-deps && cd ..

# Start the backend
uvicorn cass.main:app --reload --port 8000

# In another terminal, start the frontend
cd frontend && npm run dev
```

Open http://localhost:5173 to start using Cass.

### Google OAuth Setup (for Email & Calendar)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project and enable Gmail API + Google Calendar API
3. Create OAuth 2.0 credentials (Web application)
4. Set redirect URI to `http://localhost:8000/auth/google/callback`
5. Add `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` to your `.env`
6. Connect your account through the Cass onboarding flow

## Architecture

```
cass/              Python backend (FastAPI)
├── agent/         AI agent loop (Claude tool-use cycle)
├── tools/         Tool definitions (email, calendar, research, memory, tasks, files)
├── services/      External API wrappers (Gmail, Calendar, web)
├── routes/        REST API endpoints
└── models/        Database models + Pydantic schemas

frontend/          React + TypeScript + Tailwind CSS
├── components/    UI panels (Dashboard, Chat, Tasks, etc.)
├── hooks/         Custom hooks (SSE streaming)
└── api/           API client
```

## Docker

```bash
docker build -t cass .
docker run -p 8000:8000 --env-file .env -v ./data:/app/data cass
```
