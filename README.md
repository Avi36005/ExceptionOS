# ExceptionOS

> **"When policy ends, memory begins."**

ExceptionOS is a multi-tenant organizational decision-intelligence platform that manages business exceptions using AI-powered multi-agent debate, Hindsight Cloud persistent memory, and structured human approval workflows.

## What It Does

- Understands new exception requests (refunds, discounts, SLA compensation, vendor payments, etc.)
- Recalls similar historical decisions from **Hindsight Cloud**
- Runs a structured **multi-agent decision debate** (10 specialized agents)
- Generates an explainable AI recommendation
- Routes to the correct human approver
- Records the final decision and outcome back into Hindsight
- Detects policy drift and repeated exceptions over time

## Tech Stack

### Frontend
- React 18 + Vite + TypeScript
- Tailwind CSS (dark theme, purple accent #5B5BF0)
- Supabase Auth
- React Router v6
- Recharts, Lucide React, Zustand

### Backend
- Python 3.12 + FastAPI
- Supabase PostgreSQL (transactional DB)
- **Hindsight Cloud** (primary memory layer — mandatory)
- Groq (primary LLM) → Gemini → OpenAI (fallback chain)
- ElevenLabs (voice assistant)
- OpenClaw (optional integration, disabled by default)

## Key Features

1. **Exception Inbox** — All cases requiring attention
2. **Conversational Intake** — Chat-based or guided form exception creation
3. **Multi-Agent Debate** — 10 parallel AI agents debate each case
4. **Hindsight Memory** — Retain, Recall, Reflect on every decision
5. **Human Approval Workflow** — Approve, reject, modify, escalate
6. **Precedent Intelligence** — Interactive graph of past decisions
7. **Policy Drift Detection** — Automatic alerts when practice diverges from policy
8. **Training Mode** — New employee decision training scenarios
9. **Voice Assistant** — ElevenLabs conversational intake
10. **Demo Mode** — Judge-optimized 60-90 second presentation flow

## Project Structure

```
ExceptionOS/
├── frontend/          # React + Vite frontend
├── backend/           # FastAPI backend
├── migrations/        # Supabase SQL migrations
└── docs/              # Architecture documentation
```

## Setup

### Frontend
```bash
cd frontend
npm install
cp .env.example .env.local
# Fill in your Supabase and API keys
npm run dev
```

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env
# Fill in your API keys
uvicorn app.main:app --reload
```

## Environment Variables

### Frontend (.env.local)
```
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
VITE_EXCEPTIONOS_API_URL=http://localhost:8000
VITE_APP_ENV=development
VITE_DEMO_MODE_ENABLED=false
```

### Backend (.env)
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
GROQ_API_KEY_PRIMARY=gsk_...
GROQ_API_KEY_SECONDARY=gsk_...
GROQ_API_KEY_TERTIARY=gsk_...
GEMINI_API_KEY=...
OPENAI_API_KEY=sk-...
HINDSIGHT_API_KEY=...
ELEVENLABS_API_KEY=...
ENABLE_OPENCLAW=false
GCP_REGION=asia-south1
```

## Architecture

```
User Request
    ↓
ExceptionOS Frontend (Firebase Hosting)
    ↓
FastAPI Backend (Cloud Run: exceptionos-api)
    ↓
┌─────────────────────────────────────┐
│         Multi-Agent Orchestrator    │
│  ┌──────────┐  ┌─────────────────┐  │
│  │  Intake  │  │   Policy Agent  │  │
│  │  Agent   │  │ Precedent Agent │  │
│  └──────────┘  │  Finance Agent  │  │
│                │  Risk Agent     │  │
│  Hindsight     │  Customer Agent │  │
│  Cloud ←→ ─── │  Critic Agent   │  │
│  (Memory)      │  Final Decision │  │
│                └─────────────────┘  │
└─────────────────────────────────────┘
    ↓
Supabase PostgreSQL (Transactional State)
```

## Demo Flow (Hackathon Judges)

1. Visit `/demo` for the judge launcher
2. Submit **Acme Retail** exception (NovaFlow Systems demo org)
3. Watch **Hindsight Recall** retrieve relevant precedents live
4. View 10-agent **Decision Debate**
5. See AI **Recommendation** with Hindsight evidence
6. **Override** the recommendation as a human approver
7. Watch **Hindsight Retain** store the decision live
8. Record the **Outcome**
9. Submit **PixelWorks** case — watch Acme appear as a new precedent
10. Run **Hindsight Reflect** — see organizational learning
11. View **Policy Improvement** suggestion

## Hackathon

Built for the **AI Agents That Learn Using Hindsight** hackathon.
Required technology: **Hindsight Cloud** by Vectorize (mandatory persistent memory layer).

Google Cloud Project: `mediflow-nexus-2026`
Firebase Hosting: `exceptionos-nexus-2026`
