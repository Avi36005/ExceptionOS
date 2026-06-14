<div align="center">

<img src="https://img.shields.io/badge/ExceptionOS-When%20Policy%20Ends%2C%20Memory%20Begins-5B5BF0?style=for-the-badge&logoColor=white" alt="ExceptionOS" />

# ExceptionOS

### *"When policy ends, memory begins."*

**The world's first AI-native organizational decision-intelligence platform.**  
Every business exception — remembered, analyzed, and learned from. Forever.

<br/>

[![Live Demo](https://img.shields.io/badge/🚀%20Live%20Demo-exceptionos.web.app-5B5BF0?style=for-the-badge)](https://exceptionos.web.app)
[![API Docs](https://img.shields.io/badge/📡%20API%20Docs-FastAPI%20Swagger-009688?style=for-the-badge)](https://exceptionos-backend-m477e5mida-el.a.run.app/docs)
[![GitHub](https://img.shields.io/badge/GitHub-Avi36005%2FExceptionOS-181717?style=for-the-badge&logo=github)](https://github.com/Avi36005/ExceptionOS)

<br/>

![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6?style=flat-square&logo=typescript&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react&logoColor=black)
![Vite](https://img.shields.io/badge/Vite-5-646CFF?style=flat-square&logo=vite&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=flat-square&logo=fastapi&logoColor=white)
![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E?style=flat-square&logo=supabase&logoColor=white)
![Google Cloud](https://img.shields.io/badge/Google%20Cloud-Cloud%20Run-4285F4?style=flat-square&logo=googlecloud&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-Primary%20LLM-F55036?style=flat-square)
![Hindsight](https://img.shields.io/badge/Hindsight%20Cloud-Memory%20Layer-7C3AED?style=flat-square)

<br/>

![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Hackathon](https://img.shields.io/badge/Hackathon-AI%20Agents%20That%20Learn%20Using%20Hindsight-orange?style=flat-square)
![Status](https://img.shields.io/badge/Status-Active%20Development-brightgreen?style=flat-square)
![Branch](https://img.shields.io/badge/Branch-feat%2Fexceptionos--frontend-5B5BF0?style=flat-square)

</div>

---

## 🧠 What Is ExceptionOS?

Most organizations handle business exceptions — refund requests, discount approvals, contract cancellations, SLA compensation — through **tribal knowledge and gut instinct**. Decisions are inconsistent, reasoning is undocumented, and every new exception is decided in a vacuum.

**ExceptionOS changes that.**

It's a multi-tenant decision-intelligence platform that:

- 📥 **Captures** every exception with full context
- 🔍 **Recalls** similar historical decisions from Hindsight Cloud memory
- 🤖 **Debates** the case with 10 specialized AI agents simultaneously
- 📋 **Recommends** a decision with full explainable reasoning
- ✅ **Routes** to the correct human approver based on authority
- 💾 **Retains** the final decision and outcome to long-term memory
- 📈 **Learns** patterns, detects policy drift, and proposes improvements

The result: **consistent, fair, explainable decisions** that get smarter over time.

---

## 🌐 Live URLs

| Service | URL | Status |
|---------|-----|--------|
| **Frontend App** | [exceptionos.web.app](https://exceptionos.web.app) | ![Firebase](https://img.shields.io/badge/Firebase-Hosting-orange?style=flat-square&logo=firebase) |
| **API (Cloud Run)** | [exceptionos-api.run.app/docs](https://exceptionos-backend-m477e5mida-el.a.run.app/docs) | ![Cloud Run](https://img.shields.io/badge/Cloud%20Run-asia--south1-4285F4?style=flat-square) |
| **Supabase DB** | [ardxmhsajkhfegiyzomr.supabase.co](https://ardxmhsajkhfegiyzomr.supabase.co) | ![Supabase](https://img.shields.io/badge/PostgreSQL-Active-3ECF8E?style=flat-square) |
| **GitHub Repo** | [Avi36005/ExceptionOS](https://github.com/Avi36005/ExceptionOS) | ![GitHub](https://img.shields.io/badge/Branch-feat%2Fexceptionos--frontend-181717?style=flat-square) |

---

## ⚡ The Hackathon Problem

> **"AI Agents That Learn Using Hindsight"**  
> Build AI-powered applications using **Hindsight by Vectorize** — a memory system that allows AI agents to remember, recall, and improve over time.

ExceptionOS uses Hindsight Cloud as its **mandatory primary memory layer** for:

| Memory Type | What Gets Stored |
|-------------|-----------------|
| 📜 **Policy Memory** | Policy versions, thresholds, exception paths, approval authorities |
| 📁 **Case Memory** | Exception request, extracted facts, root cause, evidence, resolution |
| ⚖️ **Decision Memory** | Recommendation, human decision, approver, override reasoning, conditions |
| 📊 **Outcome Memory** | Actual outcome, financial result, customer retention, repeat issues |
| 🔭 **Observation Memory** | Organizational learning, patterns, policy drift signals |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    ExceptionOS Platform                          │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │          React + Vite Frontend (Firebase Hosting)        │    │
│  │  Landing │ Auth │ Dashboard │ Exceptions │ Demo Mode     │    │
│  └──────────────────────┬──────────────────────────────────┘    │
│                         │ REST + SSE                             │
│  ┌──────────────────────▼──────────────────────────────────┐    │
│  │         FastAPI Backend (Cloud Run: exceptionos-api)     │    │
│  │                                                          │    │
│  │  ┌─────────────────────────────────────────────────┐    │    │
│  │  │           Multi-Agent Orchestrator               │    │    │
│  │  │                                                  │    │    │
│  │  │  [Intake] → [Policy] → [Precedent]               │    │    │
│  │  │       ↓                                          │    │    │
│  │  │  [Finance] [Risk] [Customer] [Counter-Precedent] │    │    │
│  │  │       ↓                                          │    │    │
│  │  │  [Consistency] → [Critic] → [Final Decision]     │    │    │
│  │  │       ↓                                          │    │    │
│  │  │  [Outcome Learning] → [Policy Drift]             │    │    │
│  │  └─────────────────────────────────────────────────┘    │    │
│  │                         │                                │    │
│  │  ┌──────────────────────▼──────────────┐                │    │
│  │  │      LLM Provider Router            │                │    │
│  │  │  Groq Primary → Groq 2 → Groq 3    │                │    │
│  │  │  → Gemini → OpenAI → Demo Fixture   │                │    │
│  │  └─────────────────────────────────────┘                │    │
│  └──────────┬──────────────────────────────────────────────┘    │
│             │                                                    │
│  ┌──────────▼────────────┐   ┌──────────────────────────────┐  │
│  │   Supabase PostgreSQL  │   │      Hindsight Cloud          │  │
│  │   (Transactional DB)   │   │   (Persistent Memory Layer)   │  │
│  │   18 tables + RLS      │   │  Retain │ Recall │ Reflect    │  │
│  └───────────────────────┘   └──────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🤖 The 10-Agent Debate System

Every exception triggers a parallel multi-agent debate before any recommendation is made:

| # | Agent | Role | LLM |
|---|-------|------|-----|
| 1 | 📥 **Intake Agent** | Extracts facts, identifies missing info, assesses urgency | Groq Fast |
| 2 | 📋 **Policy Agent** | Finds applicable policy version, maps exception paths | Groq Primary |
| 3 | 🔍 **Precedent Agent** | Recalls similar historical cases from Hindsight | Groq Primary |
| 4 | 💰 **Finance Agent** | Direct cost, budget impact, financial alternatives | Groq Secondary |
| 5 | 👥 **Customer Impact Agent** | Churn risk, relationship impact, strategic importance | Groq Primary |
| 6 | ⚠️ **Risk Agent** | Policy risk, consistency risk, evidence risk, operational risk | Gemini |
| 7 | ⚖️ **Counter-Precedent Agent** | Finds cases opposing the emerging recommendation | Groq Secondary |
| 8 | 📊 **Consistency Agent** | Approval/rejection distribution, consistency score | Groq Primary |
| 9 | 🔬 **Critic Agent** | Weak assumptions, missing evidence, excessive confidence | OpenAI |
| 10 | 🎯 **Final Decision Agent** | Synthesizes all inputs → structured recommendation | Groq Primary |

**+ Async Agents:**
- 🎓 **Outcome Learning Agent** — Records outcome lessons to Hindsight after resolution
- 📈 **Policy Drift Agent** — Detects divergence between decisions and stated policy

---

## 🎯 25 Advanced Features

<details>
<summary><b>Click to expand all 25 features</b></summary>

| # | Feature | Route |
|---|---------|-------|
| 1 | 🎬 Decision Replay | `/app/exceptions/:id/replay` |
| 2 | 🕸️ Precedent Graph | `/app/precedents/graph` |
| 3 | 🎯 Memory Confidence Score | Per recalled memory |
| 4 | ❓ Missing Information Agent | `/app/exceptions/:id/intake` |
| 5 | 🔄 Decision Consistency Checker | `/app/insights/consistency` |
| 6 | 💰 Exception Budget Tracker | `/app/admin/budgets` |
| 7 | 🔁 Repeated Exception Detector | `/app/insights/repeated-exceptions` |
| 8 | 🌳 Root-Cause Intelligence | `/app/insights/root-causes` |
| 9 | 🤖 Policy Autopilot Drafting | `/app/policies/autopilot` |
| 10 | 🔮 Policy Impact Simulator | `/app/policies/simulator` |
| 11 | 📊 Outcome Prediction | Per recommendation |
| 12 | 🔄 What Changed Explanation | `/app/exceptions/:id/what-changed` |
| 13 | ↩️ Counter-Precedent Agent | Debate view |
| 14 | 🎙️ Decision Debate Mode | `/app/exceptions/:id/debate` |
| 15 | 📤 Escalation Routing | Auto-resolved by amount + role |
| 16 | ⏱️ Decision Deadline & SLA | Per case header |
| 17 | 🔗 Similarity Explanation | Per precedent card |
| 18 | ⚡ Memory Contradiction Detector | `/app/precedents/contradictions` |
| 19 | 🕰️ Memory Aging & Relevance | Per recalled memory |
| 20 | 📅 Outcome Follow-up Agent | `/app/my-approvals` queue |
| 21 | ⭐ Exception Success Score | `/app/insights/success` |
| 22 | 🏥 Organizational Memory Health | `/app/insights/memory-health` |
| 23 | 💬 "What Would We Usually Do?" | `/app/precedents/ask` |
| 24 | 🎓 New Employee Training Mode | `/app/training` |
| 25 | 📈 Anonymous Cross-Company Benchmarking | `/app/insights/benchmarks` |

</details>

---

## 🗺️ Route Map

<details>
<summary><b>View all 60+ routes</b></summary>

### Public & Auth
```
/                          Landing page
/login                     Supabase Auth login
/signup                    New account
/forgot-password           Password reset request
/reset-password            Complete reset
/auth/callback             OAuth / magic link callback
/accept-invite             Organization invitation
/unauthorized              Permission denied
/service-unavailable       Provider outage state
```

### Onboarding
```
/onboarding/company        Company setup wizard
/onboarding/policies       Upload initial policies
/onboarding/team           Invite team members
/onboarding/hindsight      Hindsight bank setup status
/select-organization       Multi-org switcher
```

### Core App (/app/*)
```
/app                       Executive dashboard
/app/inbox                 Exception inbox
/app/my-requests           My submitted exceptions
/app/my-approvals          Waiting for my decision
/app/exceptions/new        New exception (form + chat modes)
/app/exceptions/:id        Case workspace
/app/exceptions/:id/intake         Conversational intake
/app/exceptions/:id/evidence       Evidence & attachments
/app/exceptions/:id/policy         Applicable policy
/app/exceptions/:id/precedents     Hindsight precedents
/app/exceptions/:id/debate         Multi-agent debate
/app/exceptions/:id/recommendation AI recommendation
/app/exceptions/:id/decision       Human approval workflow
/app/exceptions/:id/outcome        Outcome recording
/app/exceptions/:id/replay         Decision replay timeline
/app/exceptions/:id/memory         Hindsight evidence drawer
/app/exceptions/:id/audit          Full audit trail
```

### Policies, Precedents, Intelligence
```
/app/policies              Policy library
/app/policies/new          Create policy
/app/policies/:id          Policy detail
/app/policies/:id/drift    Policy-vs-practice analysis
/app/policies/simulator    Impact simulator
/app/policies/autopilot    AI-generated policy drafts
/app/precedents            Precedent search
/app/precedents/graph      Interactive precedent graph
/app/precedents/ask        "What would we usually do?"
/app/insights              Organizational intelligence
/app/insights/policy-drift Policy drift findings
/app/insights/memory-health Memory health dashboard
/app/insights/provider-usage LLM cost & latency analytics
```

### Demo Mode (Hackathon Judges)
```
/demo                      Judge launcher
/demo/story                Guided 13-step demo
/demo/hindsight-live       Live Retain/Recall/Reflect feed
/demo/before-after         Stateless LLM vs Hindsight comparison
/demo/reset                Reset demo organization only
```

</details>

---

## 🛠️ Tech Stack

### Frontend
| Technology | Version | Purpose |
|------------|---------|---------|
| **React** | 18 | UI framework |
| **Vite** | 5 | Build tool |
| **TypeScript** | 5 | Type safety |
| **Tailwind CSS** | 3 | Styling (light theme: white canvas, purple-black sidebar, `#5B5BF0` accent) |
| **React Router** | v6 | Client-side routing |
| **Supabase JS** | 2 | Auth + real-time |
| **Zustand** | 4 | State management |
| **Recharts** | 2 | Analytics charts |
| **Lucide React** | latest | Icon system |
| **React Hot Toast** | 2 | Notifications |
| **TanStack Query** | 5 | Server state + caching |

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.12 | Runtime |
| **FastAPI** | 0.111 | REST API framework |
| **Pydantic** | v2 | Schema validation |
| **Supabase Python** | 2 | DB + auth client |
| **httpx** | async | HTTP client |
| **structlog** | latest | Structured logging |
| **Groq SDK** | latest | Primary LLM |
| **google-generativeai** | latest | Gemini fallback |
| **openai** | latest | Final fallback |
| **uvicorn** | latest | ASGI server |

### Infrastructure
| Service | Provider | Purpose |
|---------|----------|---------|
| **Database** | Supabase PostgreSQL | Transactional state (18 tables, RLS) |
| **Auth** | Supabase Auth | JWT, magic link, OAuth |
| **Memory** | Hindsight Cloud (Vectorize) | Retain / Recall / Reflect |
| **Backend API** | Google Cloud Run | `exceptionos-backend` (asia-south1) |
| **Frontend** | Firebase Hosting | `exceptionos` (exceptionos.web.app) |
| **Secrets** | Google Secret Manager | All API keys |
| **Voice** | ElevenLabs | Conversational voice assistant |
| **Region** | `asia-south1` | Primary Cloud Run region |

Deployment safety checklist: see [docs/deployment/readiness-runbook.md](docs/deployment/readiness-runbook.md) before running any GCP or Firebase deployment commands.

### LLM Fallback Chain
```
Groq (Primary Key)
    ↓ [rate limit / error]
Groq (Secondary Key)
    ↓ [rate limit / error]
Groq (Tertiary Key)
    ↓ [rate limit / error]
Gemini
    ↓ [rate limit / error]
OpenAI
    ↓ [only when DEMO_MODE=true]
Labeled Demo Fixture (clearly marked, never silent)
```

---

## 🚀 Quick Start

### Prerequisites
- Node.js 20+
- Python 3.12+
- Supabase project
- Hindsight Cloud account (promo: `MEMHACK6` for $50 free credits)
- Groq API key (free tier available)

### Frontend
```bash
cd frontend
npm install
cp .env.example .env.local

# Set your keys in .env.local:
# VITE_SUPABASE_URL=https://your-project.supabase.co
# VITE_SUPABASE_ANON_KEY=your-anon-key
# VITE_EXCEPTIONOS_API_URL=http://localhost:8000

npm run dev
# → http://localhost:5173
```

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env

# Set your keys in .env (see Environment Variables section)

uvicorn app.main:app --reload --port 8000
# → http://localhost:8000/docs
```

### Database Migration
```bash
# Run in your Supabase SQL editor:
# backend/migrations/001_initial.sql
# Creates all 18 tables with RLS policies
```

---

## ⚙️ Environment Variables

### Frontend (`.env.local`)
```env
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=eyJ...
VITE_EXCEPTIONOS_API_URL=http://localhost:8000
VITE_EXCEPTIONOS_WS_URL=ws://localhost:8000
VITE_APP_ENV=development
VITE_DEMO_MODE_ENABLED=false
```

### Backend (`.env`)
```env
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_ROLE_KEY=eyJ...

# LLM Providers (fallback chain)
GROQ_API_KEY_PRIMARY=gsk_...
GROQ_API_KEY_SECONDARY=gsk_...
GROQ_API_KEY_TERTIARY=gsk_...
GROQ_PRIMARY_MODEL=llama-3.3-70b-versatile
GROQ_FAST_MODEL=llama-3.1-8b-instant

GEMINI_API_KEY=...
GEMINI_MODEL=gemini-2.0-flash

OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini

# Memory (mandatory)
HINDSIGHT_API_KEY=hsk_...
HINDSIGHT_BASE_URL=https://api.hindsight.vectorize.io

# Voice (optional)
ELEVENLABS_API_KEY=...

# Feature flags
ENABLE_OPENCLAW=false
ENABLE_MULTI_PROVIDER_DEBATE=false
DEMO_MODE=false

# Infrastructure
GCP_REGION=asia-south1
APP_ENV=development
```

> ⚠️ **Never commit `.env` files.** All secrets are in `.gitignore`.

---

## 🗄️ Database Schema

18 tables with Row-Level Security (multi-tenant isolation):

```
organizations          → Core org config + Hindsight bank ID
profiles               → User profiles (linked to Supabase Auth)
organization_memberships → Role-based org access
departments            → Org departments + manager
exception_categories   → Configurable exception types + SLA defaults
exception_cases        → Core case entity (full lifecycle)
case_facts             → Extracted structured facts per case
case_evidence          → Uploaded files + extracted text
case_events            → Immutable audit event log
policies               → Policy registry
policy_versions        → Versioned policy content + Hindsight doc ID
recommendations        → AI recommendation per case version
agent_runs             → Agent orchestration run metadata
agent_outputs          → Per-agent structured output
precedent_links        → Hindsight-sourced precedent relationships
human_decisions        → Human approve/reject/modify/escalate record
outcomes               → Actual business outcome after decision
hindsight_operations   → Retain/Recall/Reflect operation log
llm_usage              → Token usage + cost tracking per call
notifications          → User notification queue
voice_sessions         → ElevenLabs session records
openclaw_sessions      → OpenClaw integration sessions (optional)
escalation_rules       → Amount + role escalation config
sla_rules              → SLA duration + urgency config
exception_budgets      → Org/dept exception budget tracking
policy_drift_findings  → Detected policy drift events
training_scenarios     → Masked historical training cases
benchmark_cohorts      → Synthetic anonymous benchmarks
```

---

## 🎬 Hackathon Demo Flow

The 13-step judge demo at `/demo/story`:

```
Step 1  → Show stateless LLM answer (no memory context)
Step 2  → Submit Acme Retail exception (NovaFlow Systems)
Step 3  → Watch Hindsight RECALL live ← precedents retrieved
Step 4  → View Policy + Retrieved Precedents
Step 5  → Watch 10-agent Decision Debate run
Step 6  → Read AI Recommendation (with Hindsight evidence)
Step 7  → Human Override (Manager changes the decision)
Step 8  → Watch Hindsight RETAIN live ← decision stored
Step 9  → Record outcome (customer retained, revenue saved)
Step 10 → Submit PixelWorks exception (similar scenario)
Step 11 → Watch Acme appear as NEW precedent in Recall ✨
Step 12 → Run Hindsight REFLECT ← organizational learning
Step 13 → View suggested policy improvement
```

**The money moment:** Step 11 proves the system actually learned during the demo.

---

## 🔒 Security

- ✅ Supabase JWT verified on every backend request
- ✅ Organization membership resolved per request (RBAC)
- ✅ Row-Level Security on all multi-tenant tables
- ✅ Hindsight API key never exposed to frontend
- ✅ ElevenLabs key never in frontend bundle (session token pattern)
- ✅ Service-role key backend-only
- ✅ Rate limiting on all endpoints
- ✅ MIME type validation on file uploads
- ✅ OpenClaw webhook signature verification
- ✅ No silent demo mode — always labeled when fixture data is shown

---

## 👥 User Roles

| Role | Access Level |
|------|-------------|
| `platform_super_admin` | All organizations, all data |
| `organization_admin` | Full org control |
| `policy_admin` | Create and manage policies |
| `decision_manager` | Approve/reject within authority |
| `reviewer` | View assigned + department cases |
| `requester` | Create exceptions, view own cases |
| `auditor` | Read-only access to cases + audit |
| `trainee` | Training scenarios only |
| `read_only` | View-only access |

---

## 📁 Project Structure

```
ExceptionOS/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── layout/          # AppShell, Sidebar, TopBar
│   │   │   ├── ui/              # Button, Card, Badge, Modal, Table
│   │   │   └── hindsight/       # HindsightActivityPanel, EvidenceDrawer
│   │   ├── pages/
│   │   │   ├── public/          # Landing, Login, Signup
│   │   │   ├── onboarding/      # Company, Policies, Team, Hindsight
│   │   │   └── app/
│   │   │       ├── exceptions/  # NewException, Detail, Debate, Decision
│   │   │       ├── policies/    # Library, Simulator, Autopilot
│   │   │       ├── precedents/  # Search, Graph, Ask
│   │   │       ├── insights/    # Dashboard, PolicyDrift, MemoryHealth
│   │   │       ├── training/    # Scenarios, History
│   │   │       ├── voice/       # VoiceAssistant
│   │   │       ├── integrations/# OpenClaw (isolated, disabled by default)
│   │   │       ├── admin/       # Orgs, Users, Roles, SLA, Budgets
│   │   │       ├── settings/    # Profile, Org, Security, Demo
│   │   │       └── demo/        # Judge launcher, Story, BeforeAfter
│   │   ├── lib/                 # supabase.ts, api.ts, auth.ts
│   │   ├── store/               # Zustand: authStore, orgStore
│   │   └── hooks/               # useSSE, useHindsightActivity
│   └── ...config files
│
├── backend/
│   ├── app/
│   │   ├── agents/              # 11 AI agents + orchestrator
│   │   ├── llm/                 # Provider router + 3 providers
│   │   ├── memory/              # Hindsight client + retain/recall/reflect
│   │   ├── api/v1/routes/       # 16 REST route modules
│   │   ├── domain/              # Org, Exception, Policy domain logic
│   │   ├── integrations/openclaw/ # Isolated OpenClaw handler
│   │   └── middleware/          # JWT auth middleware
│   ├── migrations/
│   │   └── 001_initial.sql      # Complete schema + RLS
│   └── tests/
│
└── README.md
```

---

## 🤝 Contributing

This project was built for the **AI Agents That Learn Using Hindsight** hackathon.

**Git conventions:**
```bash
feat(scope): description      # New feature
fix(scope): description       # Bug fix
feat(hindsight): description  # Hindsight memory features
feat(agents): description     # Agent system changes
feat(ui): description         # Frontend changes
```

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">

**Built with ❤️ using [Hindsight Cloud](https://hindsight.vectorize.io) by Vectorize**

*The AI memory layer that makes every decision smarter than the last.*

[![Hindsight](https://img.shields.io/badge/Powered%20by-Hindsight%20Cloud-7C3AED?style=for-the-badge)](https://hindsight.vectorize.io)
[![Vectorize](https://img.shields.io/badge/Memory%20by-Vectorize-5B5BF0?style=for-the-badge)](https://vectorize.io)
[![Groq](https://img.shields.io/badge/LLM%20by-Groq-F55036?style=for-the-badge)](https://groq.com)
[![Supabase](https://img.shields.io/badge/Database%20by-Supabase-3ECF8E?style=for-the-badge)](https://supabase.com)

<br/>

*ExceptionOS — Where every exception becomes institutional memory.*

</div>
