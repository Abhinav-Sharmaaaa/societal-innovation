# 🌐 Societal Innovation Platform (SIP)

> **AI-Powered, State-Configurable Societal Innovation Ecosystem**  
> *Connecting Citizens, Government Departments, Municipalities, Universities, Research Labs, and Industry Partners to turn societal challenges into measurable real-world solutions.*

---

## 📑 Table of Contents
1. [🎯 Executive Overview & Vision](#-executive-overview--vision)
2. [🔄 Complete End-to-End Workflow](#-complete-end-to-end-workflow)
3. [🏛️ User Roles & Stakeholder Ecosystem](#-user-roles--stakeholder-ecosystem)
4. [✨ Detailed Feature Specification (Major & Minor)](#-detailed-feature-specification-major--minor)
   - [Citizen Portal & Challenge Crowdsourcing](#1-citizen-portal--challenge-crowdsourcing)
   - [AI Triage & Duplicate Detection Engine](#2-ai-triage--duplicate-detection-engine)
   - [Government & Municipality Control Center](#3-government--municipality-control-center)
   - [Innovation Opportunity & RFP Engine](#4-innovation-opportunity--rfp-engine)
   - [University Matching & Proposal Submissions](#5-university-matching--proposal-submissions)
   - [Proposal Evaluation & Shortlisting](#6-proposal-evaluation--shortlisting)
   - [Industry Collaboration & Funding](#7-industry-collaboration--funding)
   - [Challenge Resolution & Citizen Feedback Loop](#8-challenge-resolution--citizen-feedback-loop)
   - [Real-Time Notification & Alert Engine](#9-real-time-notification--alert-engine)
   - [Super Admin Organisation & User Administration](#10-super-admin-organisation--user-administration)
5. [🤖 AI & Machine Learning Architecture](#-ai--machine-learning-architecture)
6. [🏗️ Technical Stack & System Architecture](#-technical-stack--system-architecture)
7. [📂 Project Structure](#-project-structure)
8. [💾 Database Models & Entity-Relationship Schema](#-database-models--entity-relationship-schema)
9. [🔌 API Endpoint Reference](#-api-endpoint-reference)
10. [🚀 Installation & Setup Guide](#-installation--setup-guide)
11. [🎬 Complete End-to-End Demo Walkthrough](#-complete-end-to-end-demo-walkthrough)

---

## 🎯 Executive Overview & Vision

Societal issues (such as water contamination, road hazards, traffic bottlenecks, waste mismanagement, or agricultural risks) are traditionally fragmented across multiple complaint channels, manually processed, or stalled due to a lack of technical expertise at local municipal levels.

**Societal Innovation Platform (SIP)** bridges this gap by creating an automated, transparent, and scalable pipeline:
1. **Citizens** report challenges with geotagged data and evidence.
2. **AI Engines** instantly triage categories, estimate severity/urgency, check for duplicates, and recommend the competent authority.
3. **Government/Municipalities** resolve routine issues directly or escalate complex problems into **Innovation Opportunities**.
4. **Universities & Labs** submit research proposals backed by faculty and student teams.
5. **Industry Partners** co-fund, mentor, and deploy technologies at scale.
6. **Citizens** are kept in the loop with real-time resolution notifications and proof of work.

---

## 🔄 Complete End-to-End Workflow

```
┌─────────────────────────┐
│     CITIZEN PORTAL      │
│  Reports Challenge with │
│   GPS, Images & Details │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│  AI TRIAGE & DUPLICATE  │ ── Duplicate Found? ──> Link to Master Challenge
│    DETECTION ENGINE     │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│  GOVERNMENT CONTROL     │ ── Routine Issue? ───> Municipal Action & Resolution
│   Review & Routing      │
└────────────┬────────────┘
             │ Innovation Required
             ▼
┌─────────────────────────┐
│ INNOVATION OPPORTUNITY  │
│    & RFP CREATION       │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│   UNIVERSITY MATCHING   │ ── Recommendation Score ──> Invite Top Universities
│     & INVITATIONS       │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│   UNIVERSITY PROPOSAL   │
│   Submission & Team     │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│  GOVERNMENT EVALUATION  │ ── Weighted Scoring ───> Shortlist Proposal
│      & SHORTLIST        │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│  INDUSTRY COLLABORATION │
│  Co-Funding & Mentorship│
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│  PROJECT EXECUTION &    │
│  RESOLUTION NOTIFIER    │ ── Resolution Proof ──> Citizen Notified & Updated
└─────────────────────────┘
```

---

## 🏛️ User Roles & Stakeholder Ecosystem

| Role | Code | Permissions & Scope |
|---|---|---|
| **Super Admin** | `SUPER_ADMIN` | Global platform configuration, creation of organisations (Universities, Municipalities, Departments, Industry), and provisioning official user accounts. |
| **Citizen** | `CITIZEN` | Submit challenges, view duplicate warnings, track submission status in real-time, receive resolution notifications, view public RFPs/projects. |
| **Government Officer** | `GOVERNMENT_OFFICER` | Review state/departmental challenge queues, accept AI recommendations, assign/reassign/escalate, create RFPs, evaluate university proposals, manage projects. |
| **Municipality Officer** | `MUNICIPALITY_OFFICER` | Review district/local challenges, execute field resolutions, submit resolution evidence, request innovation assistance. |
| **Review Officer** | `REVIEW_OFFICER` | Human-in-the-loop reviewer for ambiguous, low-confidence, or flagged AI challenge triages. |
| **University Admin** | `UNIVERSITY_ADMIN` | Institutional dashboard, receive government RFP invitations, delegate proposals to faculty. |
| **Faculty Member** | `FACULTY` | Lead research proposals, manage project milestones, submit progress reports. |
| **Student** | `STUDENT` | Participate in project execution, upload milestone deliverables. |
| **Industry Admin** | `INDUSTRY_ADMIN` | Institutional collaboration dashboard, submit co-funding & mentorship offers for shortlisted university proposals. |
| **Industry Member** | `INDUSTRY_MEMBER` | Co-sponsor individual projects, review tech transfer opportunities. |

---

## ✨ Detailed Feature Specification (Major & Minor)

### 1. Citizen Portal & Challenge Crowdsourcing
- **Multi-Role Registration Selector**: Clean onboarding with dedicated path selection (Citizen vs. Official Institution request).
- **Geotagged Reporting**: Capture location with automatic locality, district, and state extraction.
- **Evidence Attachment**: Support image, video, document uploads (`.png`, `.jpg`, `.pdf`, `.mp4`).
- **Severity & Urgency Metrics**: Self-reported initial impact scores with affected population and economic loss estimates.
- **My Submissions Dashboard**: Real-time progress tracker with visual state badges (`SUBMITTED`, `UNDER_REVIEW`, `IN_PROGRESS`, `RESOLVED`).

### 2. AI Triage & Duplicate Detection Engine
- **Automated Categorization**: TF-IDF & NLP classifier mapping descriptions to core categories (Water, Road Infrastructure, Waste, Energy, Agriculture, Public Health).
- **Duplicate Detection & Clustering**: Calculates cosine similarity against active challenges in the same district.
  - Similarity > 85%: Automatically flagged as duplicate and linked to a **Master Challenge**.
  - Upvote & Escalation Boost: Duplicate reports increment the Master Challenge's priority count instead of cluttering officer queues.
- **Confidence Scoring & Human-in-the-Loop Flagging**: If AI confidence is < 70%, the challenge is automatically routed to a `REVIEW_OFFICER` for validation.

### 3. Government & Municipality Control Center
- **Smart Queue & Filtering**: Filter by district, urgency, severity, AI confidence, or innovation status.
- **Workflow Operations**:
  - **Accept AI Recommendation**: One-click routing to recommended authority.
  - **Manual Override**: Assign to specific local body with custom justification.
  - **Reassign / Transfer**: Shift ownership to neighboring municipality or specialized department.
  - **Escalate**: Elevate critical or stalled challenges to higher state authorities.
- **Complete Audit Trail**: Immutable logging of every status shift, assignment change, officer remark, and timestamp.

### 4. Innovation Opportunity & RFP Engine
- **Convert Challenge to Innovation Call**: If a challenge cannot be resolved by standard municipal protocol, officers convert it into an **Innovation Opportunity**.
- **RFP Creation Wizard**: Define scope, technical constraints, eligibility criteria, budget ceiling, and submission deadlines.
- **State-Wide Publication**: Published RFPs are instantly visible on the public portal and university feeds.

### 5. University Matching & Proposal Submissions
- **AI Competency Matching**: Matches RFP requirements against university department capabilities, past research scores, and location proximity.
- **RFP Invitations**: Top-3 matched universities receive direct invitations with explicit match scores.
- **University Proposal Builder**:
  - Technical approach & methodology description.
  - Team breakdown (Faculty PI, Co-PI, Student Researchers).
  - Detailed milestone plan with deliverables & timelines.
  - Itemized financial budget breakdown.

### 6. Proposal Evaluation & Shortlisting
- **7-Criteria Weighted Evaluation**:
  1. Technical Feasibility (20%)
  2. Innovation Novelty (15%)
  3. Cost Efficiency (15%)
  4. Execution Timeline (15%)
  5. Team Capability (15%)
  6. Societal Impact (10%)
  7. Sustainability & Scalability (10%)
- **Automatic Score Aggregation**: Calculates final weighted score and ranks proposals.
- **Shortlisting & Decisioning**: Officer marks proposal as `SHORTLISTED`, `UNDER_EVALUATION`, or `REJECTED` with official feedback.

### 7. Industry Collaboration & Funding
- **Opportunity Feed**: Industry partners browse government-shortlisted university proposals.
- **Collaboration Offers**: Industry submits support proposals (Co-Funding, Equipment Access, Mentorship, Pilot Deployment, Tech Transfer).
- **University Review**: Universities can Accept, Reject, or Negotiate terms with industry sponsors.

### 8. Challenge Resolution & Citizen Feedback Loop
- **Resolution Control**: Officers/Municipalities mark challenges as `RESOLVED`.
- **Proof of Work Submission**: Upload resolution text and photographic evidence.
- **Citizen Notification**: High-priority alert automatically dispatched to the citizen who filed the original report.
- **Impact & Reputation Points**: Resolving challenges awards reputation points to the participating university, department, and citizen reporter.

### 9. Real-Time Notification & Alert Engine
- **In-App Notification Bell**: Animated unread badge with polling and instant updates.
- **Contextual Deep Linking**: Clicking a notification routes directly to the relevant Challenge, RFP, Proposal, or Project page.
- **Alert Types**: `CHALLENGE_RESOLVED`, `RFP_INVITATION`, `PROPOSAL_STATUS_UPDATE`, `COLLABORATION_OFFER`, `RISK_ALERT`.

### 10. Super Admin Organisation & User Administration
- **Organisation Management Tab**: Register and manage Municipalities, Universities, Industry Orgs, and Government Departments.
- **Official Account Provisioning Tab**: Create credentialed official accounts with role-to-org compatibility enforcement (e.g., `FACULTY` can only be assigned to a `UNIVERSITY`).

---

## 🤖 AI & Machine Learning Architecture

```
                       ┌────────────────────────┐
                       │ Citizen Text & Location│
                       └───────────┬────────────┘
                                   │
                     ┌─────────────┴─────────────┐
                     ▼                           ▼
        ┌────────────────────────┐  ┌────────────────────────┐
        │ TF-IDF / NLP Classifier│  │ District Vector Engine │
        └────────────┬───────────┘  └───────────┬────────────┘
                     │                          │
        ┌────────────┴───────────┐  ┌───────────┴────────────┐
        │ Category & Innovation  │  │ Cosine Similarity      │
        │ Confidence Assessment  │  │ (>85% -> Duplicate)    │
        └────────────┬───────────┘  └───────────┬────────────┘
                     │                          │
                     └─────────────┬────────────┘
                                   ▼
                       ┌────────────────────────┐
                       │   Triage & Routing     │
                       │     Recommendation     │
                       └────────────────────────┘
```

---

## 🏗️ Technical Stack & System Architecture

### Backend
- **Framework**: Python 3.10+ / FastAPI (Async native)
- **Database**: PostgreSQL 14+ with SQLAlchemy 2.0 ORM & Alembic migrations
- **Authentication**: OAuth2 with Password Hashing (Bcrypt) & JWT Tokens
- **Validation**: Pydantic v2
- **Machine Learning**: Scikit-Learn, NumPy, SciPy (TF-IDF vectorizer + Cosine Similarity)

### Frontend
- **Framework**: React 18 / TypeScript / Vite
- **Routing**: React Router v6
- **Styling**: Vanilla CSS (Custom Design Token System, Glassmorphism, Micro-animations)
- **Icons**: Lucide React
- **HTTP Client**: Axios with Interceptors for JWT Refresh & Error Handling

---

## 📂 Project Structure

```
societal-innovation-platform/
├── backend/
│   ├── app/
│   │   ├── api/                   # REST API Endpoints
│   │   │   ├── admin.py
│   │   │   ├── auth.py
│   │   │   ├── challenges.py
│   │   │   ├── dashboards.py
│   │   │   ├── notifications.py
│   │   │   ├── organizations.py
│   │   │   ├── project_outcomes.py
│   │   │   ├── rfps.py
│   │   │   └── university_proposals.py
│   │   ├── core/                  # Security & Database Config
│   │   ├── models/                # SQLAlchemy Database Models
│   │   ├── schemas/               # Pydantic Schemas
│   │   ├── services/              # Business Logic & AI Pipeline
│   │   └── main.py                # FastAPI Application Entrypoint
│   ├── alembic/                   # Database Migrations
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/            # Shared UI (Navbar, NotificationBell, Badges)
│   │   ├── pages/                 # Role-Based Page Views
│   │   │   ├── admin/             # Super Admin Dashboard & Forms
│   │   │   ├── auth/              # Login & Multi-Role Register
│   │   │   ├── citizen/           # Citizen Dashboard & Submit Page
│   │   │   ├── government/        # Officer Queue, Details, RFPs & Resolution
│   │   │   └── university/        # University Invitations & Proposal Builder
│   │   ├── services/              # API Client Services
│   │   ├── types/                 # TypeScript Type Definitions
│   │   └── App.tsx                # Routing Configuration
│   ├── package.json
│   └── vite.config.ts
└── README.md
```

---

## 💾 Database Models & Entity-Relationship Schema

```
Users ──< UserRoles
  │
  ├──< Challenges (submitted_by)
  │       │
  │       ├──< ChallengeEvidence
  │       ├──< ChallengeRouting
  │       └──< ChallengeReviewHistory
  │
  ├──< RFPs (created_by)
  │       │
  │       ├──< RFPInvitations ──> Organizations (University)
  │       └──< UniversityProposals (submitted_by)
  │                 │
  │                 └──< IndustryCollaborations
  │                           │
  │                           └──< Projects ──< ProjectOutcomes
  │
  └──< Notifications (user_id)
```

---

## 🔌 API Endpoint Reference

### Authentication & Admin
- `POST /api/v1/auth/register` — Citizen registration
- `POST /api/v1/auth/login` — Authenticate and receive JWT token
- `GET /api/v1/auth/me` — Fetch current user profile
- `POST /api/v1/admin/organizations` — Register new organisation (Super Admin)
- `GET /api/v1/admin/organizations` — List all registered organisations
- `POST /api/v1/admin/users/official` — Provision official account (Super Admin)

### Challenges & Resolution
- `POST /api/v1/challenges` — Submit new challenge
- `GET /api/v1/challenges/my` — Fetch citizen's submitted challenges
- `GET /api/v1/challenges` — Queue view for government/municipality officers
- `GET /api/v1/challenges/{id}` — Challenge details with AI triage & evidence
- `PATCH /api/v1/challenges/{id}/resolve` — Mark challenge resolved & notify citizen

### RFPs & University Proposals
- `POST /api/v1/rfps` — Create new Request for Proposals
- `GET /api/v1/rfps` — List published RFPs
- `GET /api/v1/rfps/{id}/recommendations` — Fetch AI top-3 matched universities
- `POST /api/v1/university-proposals` — Submit university research proposal
- `GET /api/v1/university-proposals/my` — Fetch user's submitted proposals

### Notifications
- `GET /api/v1/notifications` — Fetch user notifications
- `PATCH /api/v1/notifications/{id}/read` — Mark notification read

---

## 🚀 Installation & Setup Guide

### Prerequisites
- Python 3.10+
- Node.js 18+ & npm
- PostgreSQL 14+

### 1. Backend Setup
```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment (Windows)
.venv\Scripts\Activate.ps1
# (Linux/macOS)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start FastAPI server
uvicorn app.main:app --reload --port 8000
```
*API Swagger Documentation will be available at `http://localhost:8000/docs`.*

### 2. Frontend Setup
```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start Vite dev server
npm run dev
```
*App will be available at `http://localhost:5173`.*

### 3. Production Build Check
```bash
cd frontend
npm run build
```

---

## 🎬 Complete End-to-End Demo Walkthrough

1. **Super Admin Setup**: Log in as Super Admin (`admin@sip.gov.in`), create a University organisation ("IIT Roorkee") and a Municipality ("Dehradun Municipal Corporation"). Provision a `UNIVERSITY_ADMIN` user and a `MUNICIPALITY_OFFICER` user.
2. **Citizen Submission**: Log in as a Citizen, submit a challenge titled *"Water Supply Contamination in Sector 4"*. Observe the instant AI Triage rating and locality tag.
3. **Government Review & RFP**: Log in as a Government Officer, view the challenge, select **"Create Innovation Opportunity"**, and publish an RFP for *"Filtration Tech Solution"*.
4. **University Invitation & Proposal**: Run AI University Matching, invite "IIT Roorkee", log in as University Admin, accept invitation, and submit a research proposal.
5. **Proposal Evaluation**: Government Officer scores the proposal across the 7 weighted criteria and marks it **SHORTLISTED**.
6. **Resolution & Citizen Alert**: Municipality Officer executes field resolution, clicks **"Mark as Resolved"**, and writes the summary. The citizen instantly receives a **"✅ Challenge Resolved"** notification with full evidence.

---

*Societal Innovation Platform (SIP) — Turning societal challenges into measurable real-world solutions.*