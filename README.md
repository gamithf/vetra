# 🐾 Vetra — AI-Assisted Veterinary Clinic Operating System

Vetra is an **intelligent operating system for modern veterinary clinics**. It unifies the front desk, the exam room, and the billing counter into one real-time platform — then **wraps the entire visit in an AI agent** that handles the paperwork so clinicians can focus on medicine.

A veterinarian dictates a consultation into the built-in AI co-pilot, and a real multi-agent pipeline (Gemini 2.5 Flash) **reasons through the exam, writes the medical record, checks drug interactions, reconciles inventory, generates the bill, notifies the owner, and auto-books the follow-up** — before the client even reaches the counter.

---

## ✨ Core Features

### Front Desk — Staff
- Today's overview dashboard with live stats (appointments, checked-in, low stock, pending invoices).
- Grouped calendar view of the day's appointments.
- One-click **check-in** that pushes the patient into the vet's queue in real time.
- **Emergency intake** wizard for urgent walk-ins, surfaced for triage.
- **Pending checkout** — completed visits still owing payment are surfaced automatically, with a checkout modal and payment methods.

### Exam Room — Vet
- Urgency-sorted patient queue (urgent cases flagged red).
- Full **EMR timeline** — species, breed, weight, microchip, vaccination and treatment history.
- Floating **AI Co-Pilot** that **auto-locks to the active patient** (no manual patient-ID entry), with **voice-to-text** via Groq Cloud Whisper Large V3.
- On submit, an **8-agent pipeline streams live** over a WebSocket — each agent's thinking and tool actions visible in real time.

### Owner Portal — Secure Magic Link
- Every pet is reachable through a secure, tokenized public link sent to the owner.
- **Visit Summary & Bill** — diagnosis, treatment, and the invoice produced by the AI pipeline.
- **Appointments & Booking** — view scheduled visits (including the auto-scheduled follow-up), pick any free 30-minute clinic slot, and reschedule upcoming appointments.

### Platform
- **JWT authentication** (bcrypt-hashed passwords) with **role-based access** (`vet` / `staff` / `admin`).
- **WebSockets** for real-time cross-role updates (queue, dashboard, appointments).
- **Agentic AI** — a dedicated Gemini service that performs real database actions (records, inventory, invoices, booking) on the clinic's behalf.

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
├── agent/                       # Gemini agentic service
│   ├── app/
│   │   ├── main.py              # FastAPI app + WebSocket /agent
│   │   ├── orchestrator.py      # 8-agent pipeline
│   │   ├── gemini.py            # Gemini client (streaming reasoning + structured plan)
│   │   ├── tools.py             # real actions against the Vetra backend
│   │   └── config.py            # settings (env-driven)
│   ├── requirements.txt
│   └── .env.example
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── deps.py          # auth dependencies + role guards
│   │   │   └── v1/
│   │   │       ├── router.py    # router registration
│   │   │       └── endpoints/   # auth, users, owners, pets, rooms, appointments,
│   │   │                        # medical_records, vaccinations, lab_results,
│   │   │                        # clinical_notes, inventory, prescriptions,
│   │   │                        # invoices, weight_records, dashboard,
│   │   │                        # transcription, public_booking
│   │   ├── core/                # security, exceptions, config
│   │   ├── models/              # SQLModel models
│   │   ├── services/            # business logic (scheduling, magic_link, ...)
│   │   ├── schemas/             # Pydantic request/response schemas
│   │   ├── config.py            # settings (env-driven)
│   │   ├── database.py          # async engine + session factory
│   │   ├── main.py              # FastAPI app, CORS, WebSocket
│   │   └── enums.py             # shared enums
│   ├── alembic/                 # migrations
│   ├── scripts/seed.py          # demo seed
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── lib/                 # API client + realtime constants
│       ├── components/          # UI primitives, copilot, agent-stream, checkout, booking
│       ├── context/             # auth context
│       ├── pages/               # landing, login, dashboards, public portal
│       └── App.tsx              # routing
└── DEMO_SCRIPT.md               # 5-minute narrated product walkthrough
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Node.js 20+
- PostgreSQL 14+ running locally
- API keys: `GROQ_TRANSCRIBE_API_KEY` (optional, voice) and `GEMINI_API_KEY` (required, AI pipeline)

### 1. Backend

```bash
cd backend
python -m venv venv
# activate:  Windows → venv\Scripts\activate  |  macOS/Linux → source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # then edit DATABASE_URL / SECRET_KEY
```

Run migrations and seed the demo data:

```bash
alembic upgrade head
python scripts/seed.py
```

Start the API:

```bash
uvicorn app.main:app --reload
```

Interactive API docs are available at `http://localhost:8000/docs`.

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
pip install -r requirements.txt
cp .env.example .env         # set GEMINI_API_KEY
```

Start the agent service:

```bash
uvicorn app.main:app --port 8001 --reload
```

---

## ⚙️ Configuration

### Backend (`backend/.env`)
| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Async PostgreSQL connection string | `postgresql+asyncpg://postgres:postgres@localhost:5432/vetra` |
| `SECRET_KEY` | JWT signing secret (change it in production) | — |
| `GROQ_TRANSCRIBE_API_KEY` | Groq Cloud key for Whisper Large V3 transcription (free) | — |
| `FRONTEND_URL` | Origin used in owner links / notifications | `http://localhost:5173` |
| `AK_WHATSAPP__*` | Meta Cloud API WhatsApp credentials (optional owner notifications) | — |
| `AK_WHATSAPP__TEMPLATE_NAME` | Pre-approved WhatsApp template for visit summaries (optional) | — |

Get a Groq key at [console.groq.com](https://console.groq.com). Without it, voice transcription is simply unavailable.

### Agent Service (`agent/.env`)
| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google AI Studio key for Gemini 2.5 Flash | — |
| `GEMINI_MODEL` | Gemini model name | `gemini-2.5-flash` |
| `VETRA_API_URL` | Backend API base the agents call to act | `http://localhost:8000/api/v1` |
| `HOST` / `PORT` | Service bind address | `0.0.0.0` / `8001` |

### Frontend (`frontend/.env`)
| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API origin | `http://localhost:8000` |
| `VITE_WS_URL` | Main realtime WebSocket | `ws://localhost:8000/ws` |
| `VITE_AGENT_URL` | Agent pipeline WebSocket | `ws://localhost:8001/agent` |

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

The AI Co-Pilot records audio via the MediaRecorder API (`audio/webm`) and POSTs it to `POST /api/v1/transcribe`. The backend streams the file to Groq's **Whisper Large v3** and returns the transcript, which the vet edits before submitting.

---

## 🧠 Agentic AI Pipeline (Gemini 2.5 Flash) — Open Category

This is the core differentiator. When the vet submits a transcript, the frontend opens a WebSocket to the agent service (`/agent`) and the orchestrator runs an **8-agent pipeline**, streaming each step's status, live "thinking" text, and tool results back to the UI.

| # | Agent | Responsibility |
|---|-------|----------------|
| 1 | **Patient Context** | Loads the patient, reason, and the vet's active patient from the backend. |
| 2 | **Medical Reasoning** | Gemini 2 streams its clinical analysis of the transcript word-by-word. |
| 3 | **Clinical Safety (RAG)** | Semantic vector search over an embedded veterinary drug-interaction index; compares current prescriptions (e.g. Meloxicam/NSAID) against newly-prescribed medication (e.g. Amoxicillin) and flags interactions. |
| 4 | **Clinical Note** | Saves the raw transcript + a structured SOAP note. |
| 5 | **Medical Record** | Writes the diagnosis and treatment to the pet's EMR timeline. |
| 6 | **Inventory** | Matches consumed supplies by name and deducts stock. |
| 7 | **Billing** | Generates itemized invoice lines from the visit. |
| 8 | **Finalize** | Marks the visit complete, notifies the owner (best-effort), and **auto-schedules a follow-up appointment** when the structured plan calls for one. |

**Tool actions** (records, inventory, invoices, follow-up booking) are executed against the backend with the logged-in vet's JWT, preserving role-based permissions. Nothing is simulated — every step mutates real data.

Read more in the narrated **[DEMO_SCRIPT.md](./DEMO_SCRIPT.md)**.

---

## 🔗 Secure Owner Portal (Magic Link)

Every pet has a tokenized public portal shared with the owner. It is generated server-side, requires no login, and is scoped to that owner's data only.

- **Appointments & Booking** — the visit list (including AI-booked follow-ups), free 30-minute slot picker within clinic hours, and rescheduling of future appointments.
- **Visit Summary & Bill** — the diagnosis, treatment, and invoice line items produced by the AI pipeline.

Public endpoints (`/api/v1/public/*`) authenticate via the magic-link token and are restricted to that owner's records.

---

## 📡 API Overview (v1)

| Group | Endpoints |
|-------|-----------|
| Auth | `POST /auth/login`, `POST /auth/register`, `GET /auth/me` |
| Owners / Pets | CRUD + pets `medical-records`, `vaccinations`, `lab-results`, `weight-history` |
| Appointments | CRUD, `today`, `pending-checkout`, `emergency`, `{id}/check-in`, `{id}/start`, `{id}/complete`, `{id}/create-invoice`, `followup` |
| Clinical Notes | CRUD (agents handle record/inventory/billing) |
| Inventory | CRUD, `low-stock`, `{id}/adjust` |
| Invoices | CRUD, `{id}/items`, `{id}/pay` |
| Dashboard | `GET /vet`, `GET /staff` |
| Transcription | `POST /transcribe` (Groq Whisper) |
| Public (owner portal) | `GET /public/portal/{token}`, `GET /public/slots/{token}/{vet}/{date}`, `POST /public/appointments`, `PATCH /public/appointments/{id}` |
| Realtime | WebSocket `ws://localhost:8000/ws` (main app), `ws://localhost:8001/agent` (agent) |

Most endpoints require `Authorization: Bearer <token>`; the `public/*` endpoints authenticate via the magic-link token.

---

## 🔄 Appointment Lifecycle

`SCHEDULED → CHECKED_IN → IN_PROGRESS → COMPLETED`

1. **Staff** checks a patient in.
2. The change reflects in the **vet queue in real time**.
3. The **vet** opens the patient (co-pilot auto-locks), starts the visit, and dictates.
4. Submitting the transcript runs the **agent pipeline** — reasoning, medical record, safety check, inventory deduction, billing — then marks the visit **COMPLETED** and schedules the follow-up if ordered.
5. **Staff** sees the completed visit under **Pending Checkout**, and processes payment.

---

## ✅ Lint & Build

```bash
# Frontend
cd frontend
npm run lint     # oxlint
npm run build    # tsc -b && vite build

# Backend / Agent service
cd backend && python -m py_compile app
cd agent && python -m py_compile app
```

---

## 🌍 Demo / Presentation

For a polished, timed 5-minute narrated walkthrough (what to click + exactly what to say), see **[DEMO_SCRIPT.md](./DEMO_SCRIPT.md)**.

---

## 🔒 Production Notes

- Set a strong `SECRET_KEY` and rotate it in production.
- Restrict CORS origins and serve everything over HTTPS.
- Store API keys in a secret manager — never in the client.
- Run migrations (`alembic upgrade head`) before every deployment.