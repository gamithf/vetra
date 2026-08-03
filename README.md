# 🐾 Vetra — Veterinary Clinic Management System

Vetra is an **AI-assisted operating system for modern veterinary clinics**. It connects the front desk, the exam room, and the billing counter into one real-time platform.

- **Vet role** — live patient queue with urgency triage, patient EMR timeline, and a floating **AI Co-Pilot** that auto-locks onto the active patient, transcribes the vet's voice (via **Groq Cloud — Whisper Large V3**), and runs a **real multi-agent pipeline** (Gemini 2.5 Flash) that reasons through the visit, writes the medical record, reconciles inventory, and generates the bill.
- **Staff role** — calendar, check-in/check-out, emergency intake, low-stock inventory alerts, and automated checkout that reconciles completed visits into invoices.

---

## ✨ Features

### Front Desk (Staff)
- Today's overview dashboard with live stats (appointments, checked in, low stock, pending invoices).
- Grouped calendar view of appointments.
- One-click **check-in** → patient appears in the vet's queue in real time.
- **Emergency intake** wizard for urgent walk-ins.
- **Pending checkout** — completed visits without an invoice are surfaced automatically, with a checkout modal and payment methods.

### Exam Room (Vet)
- **Patient queue** sorted by urgency (urgent cases flagged red) then time.
- Full **EMR timeline** — species, breed, weight, microchip, vaccination and treatment history.
- **AI Co-Pilot** floating widget that **auto-locks to the active patient** (no manual patient-ID entry).
- **Voice-to-text** dictation via Groq Cloud's Whisper Large V3 (free tier) — text is editable before submitting.
- On submit, the **agent pipeline** runs live over a WebSocket: *Patient Context → Medical Reasoning → Clinical Note → Medical Record → Inventory → Billing → Finalize*, streaming each agent's thinking and actions in real time.

### Platform
- **JWT authentication** with bcrypt password hashing.
- **Role-based access** (`vet` / `staff` / `admin`) with guarded routes.
- **WebSockets** for real-time cross-role updates.
- **Agentic AI** — a dedicated Gemini 2.5 Flash service that performs real database actions (records, inventory, invoices) on behalf of the vet.

---

## 🧱 Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19, TypeScript, Vite, Tailwind CSS v4, TanStack Query, React Hook Form + Zod, Axios, Recharts, Sonner |
| Backend | FastAPI, SQLModel, async SQLAlchemy, asyncpg, Pydantic v2, JWT (python-jose), bcrypt, httpx |
| Database | PostgreSQL |
| AI | Groq Cloud — Whisper Large V3 (voice transcription), Gemini 2.5 Flash (agentic pipeline) |
| Realtime | WebSockets |

---

## 📁 Project Structure

```
vetra/
├── agent/                     # Gemini 2.5 Flash agentic service
│   ├── app/
│   │   ├── main.py            # FastAPI app + WebSocket /agent
│   │   ├── orchestrator.py    # multi-agent pipeline
│   │   ├── gemini.py          # Gemini client (thinking + structured plan)
│   │   ├── tools.py           # real actions against the Vetra backend
│   │   └── config.py          # settings (env-driven)
│   ├── requirements.txt
│   └── .env.example
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── deps.py          # auth dependencies + role guards
│   │   │   └── v1/
│   │   │       ├── router.py    # API router registration
│   │   │       └── endpoints/   # auth, users, owners, pets, rooms,
│   │   │                        # appointments, medical_records, vaccinations,
│   │   │                        # lab_results, clinical_notes, inventory,
│   │   │                        # prescriptions, invoices, weight_records,
│   │   │                        # dashboard, transcription
│   │   ├── core/                # security, exceptions, config
│   │   ├── models/              # SQLModel models (14 tables)
│   │   ├── schemas/             # Pydantic request/response schemas
│   │   ├── config.py            # settings (env-driven)
│   │   ├── database.py          # async engine + session factory
│   │   ├── main.py              # FastAPI app, CORS, WebSocket
│   │   └── enums.py             # shared enums
│   ├── alembic/                 # migrations
│   ├── scripts/seed.py          # database seed script
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── lib/                 # api client (single real API, no demo)
│   │   ├── components/          # UI primitives + copilot/agent-stream/checkout/emergency
│   │   ├── context/             # auth context
│   │   ├── pages/               # landing, login, register, dashboards
│   │   └── App.tsx              # routing
│   └── package.json
└── DEMO_SCRIPT.md               # 5-minute walkthrough (real full-stack pipeline)
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Node.js 20+
- PostgreSQL running locally

### 1. Backend

```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate | macOS/Linux: source venv/bin/activate
pip install -r requirements.txt

# Configure environment (copy and edit)
cp .env.example .env
```

Then run migrations + seed:

```bash
alembic upgrade head
python scripts/seed.py
```

Start the API:

```bash
uvicorn app.main:app --reload
```

API docs available at `http://localhost:8000/docs`.

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

### 3. Agent Service (AI pipeline)

```bash
cd agent
python -m venv venv
# Windows: venv\Scripts\activate | macOS/Linux: source venv/bin/activate
pip install -r requirements.txt

# Configure environment (copy and edit)
cp .env.example .env
#   GEMINI_API_KEY=<your Gemini API key>
```

Start the agent service:

```bash
uvicorn app.main:app --port 8001 --reload
```

The frontend connects to the agent service via WebSocket (`ws://localhost:8001/agent`) — override with `VITE_AGENT_URL` if deployed elsewhere.

---

## ⚙️ Environment Variables

### Backend (`.env`)
| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Async PostgreSQL connection string | `postgresql+asyncpg://postgres:postgres@localhost:5432/vetra` |
| `SECRET_KEY` | JWT signing secret (change in production) | — |
| `GROQ_TRANSCRIBE_API_KEY` | Groq Cloud key for Whisper Large transcription (free) | — |

Get a Groq key at [console.groq.com](https://console.groq.com). Without it, voice transcription returns a 400 "not configured" error.

### Agent Service (`agent/.env`)
| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google AI Studio key for Gemini 2.5 Flash | — |
| `GEMINI_MODEL` | Gemini model name | `gemini-2.5-flash` |
| `VETRA_API_URL` | Main backend API base (tool actions) | `http://localhost:8000/api/v1` |
| `HOST` / `PORT` | Agent service bind address | `0.0.0.0` / `8001` |

### Frontend
- `VITE_API_BASE_URL` — API origin (see `frontend/.env.example`).
- `VITE_AGENT_URL` — agent WebSocket URL (defaults to `ws://localhost:8001/agent`).

---

## 🔑 Seed Credentials

| Role | Email | Password |
|------|-------|----------|
| Vet | `vet1@vetra.com` | `password123` |
| Vet | `vet2@vetra.com` | `password123` |
| Vet | `vet3@vetra.com` | `password123` |
| Staff | `staff1@vetra.com` | `password123` |
| Staff | `staff2@vetra.com` | `password123` |
| Admin | `admin1@vetra.com` | `password123` |

---

## 🎤 Voice Transcription (Groq Cloud)

The AI Co-Pilot records audio via the MediaRecorder API (`audio/webm`) and POSTs it to `POST /api/v1/transcribe`. The backend streams the file to Groq's **Whisper Large v3** endpoint and returns the transcript, which the vet can edit before submitting.

---

## 🧠 Agentic AI Pipeline (Gemini 2.5 Flash)

When the vet submits a transcript, the frontend opens a WebSocket to the agent service (`/agent`). The orchestrator runs a multi-agent pipeline and streams each step's status, live "thinking" text, and tool actions back to the UI:

| Agent | Responsibility |
|-------|----------------|
| Context | Loads the patient from the backend |
| Medical | Streams Gemini's clinical reasoning over the transcript |
| Notes | Saves the raw transcript + structured SOAP note |
| Records | Writes the medical record (diagnosis, treatment, type) |
| Inventory | Matches and deducts consumed supplies |
| Billing | Generates itemized invoice lines via Gemini |
| Finalize | Marks the appointment completed |

Every tool action is performed with the logged-in vet's JWT against the main backend API, so role-based permissions are preserved.

> Previously the pipeline was a client-side simulation enabled with `?demo=1`. That demo layer has been removed — the pipeline now performs real database operations.

---

## 🧭 Demo / Presentation

For a polished 5-minute product walkthrough (narration + what to click), see **[DEMO_SCRIPT.md](./DEMO_SCRIPT.md)**. Run the app with `?demo=1` and use the one-click **Staff / Vet** login buttons on the login page.

---

## 📡 API Overview (v1)

| Group | Endpoints |
|-------|-----------|
| Auth | `POST /auth/login`, `POST /auth/register`, `GET /auth/me` |
| Owners / Pets | CRUD + `GET /pets/{id}/medical-records`, `.../vaccinations`, `.../lab-results`, `.../weight-history` |
| Appointments | CRUD, `GET /today`, `GET /pending-checkout`, `POST /emergency`, `/{id}/check-in`, `/{id}/start`, `/{id}/complete`, `/{id}/create-invoice` |
| Clinical Notes | `POST /` (pure note save — record creation, inventory & billing handled by the agent service), CRUD |
| Inventory | CRUD, `GET /low-stock`, `/{id}/adjust` |
| Invoices | CRUD, `/{id}/items`, `/{id}/pay` |
| Dashboard | `GET /vet`, `GET /staff` |
| Transcription | `POST /transcribe` (Groq Whisper) |
| Realtime | WebSocket at `ws://localhost:8000/ws` |
| Agent (service on :8001) | WebSocket at `ws://localhost:8001/agent` |

Auth is required via `Authorization: Bearer <token>` (except where noted). Role guards restrict administrative/pet-sensitive actions.

---

## 🔄 Appointment Lifecycle

`SCHEDULED → CHECKED_IN → IN_PROGRESS → COMPLETED`

1. **Staff** checks a patient in.
2. Status change is reflected in the **vet queue in real time**.
3. The **vet** opens the patient (co-pilot auto-locks), starts the exam, and dictates notes.
4. Submitting the transcript runs the **agent pipeline**: medical reasoning, medical record creation, inventory deduction, and invoice generation — then marks the appointment **COMPLETED**.
5. **Staff** sees the completed visit under **Pending Checkout**, generates the invoice (if the pipeline did not), and processes payment.

---

## ✅ Lint & Build

```bash
# Frontend
cd frontend
npm run lint     # oxlint
npm run build    # tsc -b && vite build

# Backend
cd backend
python -m py_compile app      # syntax sanity check

# Agent service
cd agent
python -m py_compile app      # syntax sanity check
```

---

## 🔒 Production Notes

- Set a strong `SECRET_KEY` and rotate it in production.
- Restrict CORS origins in `app/main.py` and `agent/app/main.py` (currently `*` for local development).
- Serve the frontend build (`frontend/dist`) behind the API, or a CDN, with HTTPS.
- Store `GROQ_TRANSCRIBE_API_KEY` and `GEMINI_API_KEY` in a secret manager, never in the client.
- Add rate-limiting and structured logging around the transcription, agent, and payment endpoints.
- Run migrations (`alembic upgrade head`) before deploying a new release.
