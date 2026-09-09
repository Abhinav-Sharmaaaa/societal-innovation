# 🌐 Societal Innovation Platform (SIP)

An **AI-powered civic technology platform** designed to collect, analyze, triage, and route societal challenges reported by citizens (e.g., infrastructure failures, water contamination, disaster hazards, public safety, healthcare access). The system utilizes machine learning classification alongside rule-based engines to automatically estimate severity, urgency, innovation requirements, and route issues to municipal bodies, government departments, or research institutions/universities.

---

## 📌 Table of Contents
- [Architecture & Tech Stack](#-architecture--tech-stack)
- [Directory Structure](#-directory-structure)
- [Database Schema & Models](#-database-schema--models)
- [API Endpoints Reference](#-api-endpoints-reference)
- [AI & Machine Learning Core](#-ai--machine-learning-core)
- [Frontend User Interface](#-frontend-user-interface)
- [Plugins & External Integration Capabilities](#-plugins--external-integration-capabilities)
- [Setup & Running Locally](#-setup--running-locally)
- [Environment Configuration](#-environment-configuration)

---

## 🏗️ Architecture & Tech Stack

### **Backend**
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python 3.10+)
- **Database**: PostgreSQL with [SQLAlchemy 2.0 ORM](https://www.sqlalchemy.org/)
- **Database Migrations**: [Alembic](https://alembic.sqlalchemy.org/)
- **Authentication**: JWT Bearer Tokens (OAuth2 Password Flow) with Passlib & Argon2 / Bcrypt password hashing
- **Data Validation**: Pydantic v2 & Pydantic Settings

### **Frontend**
- **Framework**: React 19 + TypeScript + [Vite](https://vitejs.dev/)
- **Routing**: [React Router DOM v7](https://reactrouter.com/)
- **State & Data Fetching**: Axios, [TanStack React Query v5](https://tanstack.com/query)
- **Forms & Validation**: React Hook Form + Zod
- **UI & Visualization**: Custom Vanilla CSS (Glassmorphism & Dark Mode styling), Lucide Icons, Recharts

### **Machine Learning & AI Engine**
- **ML Framework**: Scikit-Learn (TF-IDF Vectorization + Logistic Regression Classifier)
- **Model Storage**: Joblib serialization (`ml/models/category/controlled_baselines/B_text_plus_location.joblib`)
- **Triage Pipeline**: Hybrid system combining ML-based category inference with multi-signal heuristic engines for urgency, severity, and innovation routing.

---

## 📂 Directory Structure

```
societal-innovation-platorm/
├── .env                         # Global environment variables
├── backend/                     # FastAPI Backend Application
│   ├── alembic/                 # Alembic DB migration scripts & versions
│   ├── alembic.ini              # Alembic config
│   ├── app/
│   │   ├── ai/                  # AI & ML triage services
│   │   │   ├── category_service.py # Model loading & category prediction
│   │   │   ├── model_loader.py  # Model loader helper
│   │   │   ├── schemas.py       # Pydantic schemas for AI triage
│   │   │   └── triage_service.py# Multi-signal urgency, severity & routing rules
│   │   ├── api/                 # API Routes & Endpoints
│   │   │   ├── ai.py            # AI triage endpoints
│   │   │   ├── auth.py          # User registration, login, profile endpoints
│   │   │   ├── challenges.py    # Challenge CRUD & evidence upload endpoints
│   │   │   └── dependencies.py  # Auth & DB dependency injection
│   │   ├── core/                # Core configurations, JWT, Security utilities
│   │   ├── db/                  # Database session setup
│   │   ├── models/              # SQLAlchemy Database Models
│   │   │   ├── challenge.py
│   │   │   ├── challenge_evidence.py
│   │   │   ├── organization.py
│   │   │   └── user.py
│   │   ├── schemas/             # Pydantic Request/Response schemas
│   │   ├── services/            # Business logic (Auth, Challenge, File Storage)
│   │   └── main.py              # FastAPI Application Entrypoint
│   └── uploads/                 # Storage folder for uploaded challenge evidence files
├── frontend/                    # React + TypeScript Frontend Application
│   ├── src/
│   │   ├── pages/               # Page Components (Landing, Auth, Citizen Dashboard, Submit, Details)
│   │   ├── routes/              # AppRoutes & ProtectedRoute wrapper
│   │   ├── services/            # Axios API client integrations
│   │   ├── types/               # TypeScript interfaces
│   │   ├── App.tsx              # Main App Root
│   │   └── main.tsx             # DOM Rendering Entrypoint
│   ├── package.json             # Frontend dependencies
│   └── vite.config.ts           # Vite Bundler config
└── ml/                          # Machine Learning R&D and Pipelines
    ├── data/                    # Datasets (master, splits, holdout)
    ├── evaluation/              # Category model evaluation & ambiguity audit scripts
    ├── models/                  # Trained Joblib model artifacts
    ├── preprocessing/           # Dataset auditing & cleaning scripts
    └── training/                # Model training pipeline scripts
```

---

## 🗄️ Database Schema & Models

The platform handles four primary relational entities:

### 1. `User` (`users`)
- **Fields**: `id`, `full_name`, `email`, `phone`, `password_hash`, `role`, `organization_id`, `is_active`, `is_verified`, `created_at`, `updated_at`
- **Supported User Roles**:
  - `CITIZEN`: General public submitting challenges
  - `MUNICIPALITY_OFFICER`: Municipal body representative
  - `GOVERNMENT_OFFICER`: State/Central department official
  - `UNIVERSITY_ADMIN` / `FACULTY` / `STUDENT`: Academic R&D team members
  - `INDUSTRY_ADMIN` / `INDUSTRY_MEMBER`: Industry solvers/partners
  - `SUPER_ADMIN`: System administrator

### 2. `Organization` (`organizations`)
- **Fields**: `id`, `name`, `organization_type`, `description`, `district`, `state`, `email`, `phone`, `website`, `is_active`
- **Organization Types**: `MUNICIPALITY`, `GOVERNMENT_DEPARTMENT`, `UNIVERSITY`, `INDUSTRY`

### 3. `Challenge` (`challenges`)
- **Fields**:
  - **Details**: `id`, `title`, `description`, `submitted_by`, `category`, `severity`, `urgency`, `affected_population`, `estimated_economic_loss`
  - **Location**: `address`, `district`, `state`, `latitude`, `longitude`
  - **AI Triage Data**: `innovation_required`, `ai_confidence_score`, `ai_model_version`, `ai_category_confidence`, `ai_second_category`, `ai_second_category_confidence`, `ai_category_margin`, `ai_category_decision`, `ai_requires_human_review`, `ai_category_top_3`, `ai_analysis_at`
  - **Status & Routing**: `routing_type`, `routing_reason`, `status`, `is_master_challenge`, `master_challenge_id`, `duplicate_similarity_score`
- **Challenge Statuses**: `SUBMITTED`, `UNDER_AI_ANALYSIS`, `UNDER_REVIEW`, `ROUTED`, `IN_PROGRESS`, `RESOLVED`, `REJECTED`, `CLOSED`
- **Supported Categories (16)**: `WATER`, `SANITATION`, `WASTE_MANAGEMENT`, `HEALTHCARE`, `EDUCATION`, `AGRICULTURE`, `TRANSPORTATION`, `ENERGY`, `ENVIRONMENT`, `PUBLIC_SAFETY`, `INFRASTRUCTURE`, `DIGITAL_SERVICES`, `EMPLOYMENT`, `SOCIAL_WELFARE`, `DISASTER_MANAGEMENT`, `OTHER`

### 4. `ChallengeEvidence` (`challenge_evidence`)
- **Fields**: `id`, `challenge_id`, `evidence_type`, `original_filename`, `stored_filename`, `content_type`, `file_size`, `file_url`, `uploaded_by`, `created_at`
- **Evidence Types**: `IMAGE`, `VIDEO`, `DOCUMENT`, `OTHER`

---

## 📡 API Endpoints Reference

Base URL Prefix: `/api/v1`

### **1. System & Health**
| Method | Endpoint | Auth Required | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | No | Root endpoint returning application name, status, and version. |
| `GET` | `/api/v1/health` | No | System health check reporting service status and environment. |

### **2. Authentication (`/api/v1/auth`)**
| Method | Endpoint | Auth Required | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/auth/register` | No | Register a new user account (`UserRegister` payload). |
| `POST` | `/api/v1/auth/login` | No | Authenticate with email and password, returning JWT access & refresh tokens. |
| `GET` | `/api/v1/auth/me` | Bearer Token | Fetch profile details of the currently authenticated user. |

### **3. Challenges (`/api/v1/challenges`)**
| Method | Endpoint | Auth Required | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/challenges` | Bearer Token | Submit a new societal challenge. |
| `GET` | `/api/v1/challenges` | No | Retrieve paginated list of public challenges (`skip`, `limit`). |
| `GET` | `/api/v1/challenges/my` | Bearer Token | Retrieve all challenges submitted by the authenticated user. |
| `GET` | `/api/v1/challenges/{id}` | No | Retrieve detailed information for a single challenge. |
| `PATCH` | `/api/v1/challenges/{id}` | Bearer Token | Update a challenge (Submitter only). |
| `POST` | `/api/v1/challenges/{id}/evidence` | Bearer Token | Upload image, video, or PDF document evidence for a challenge. |

### **4. AI Triage (`/api/v1/ai`)**
| Method | Endpoint | Auth Required | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/ai/triage` | Bearer Token | Execute AI category prediction, urgency/severity evaluation, and routing analysis. If `challenge_id` is supplied, verifies ownership and persists triage results into PostgreSQL. |

---

## 🤖 AI & Machine Learning Core

### **1. Primary Category Classification Model**
- **Model Architecture**: TF-IDF Vectorizer + Multinomial Logistic Regression (`B_text_plus_location.joblib`).
- **Feature Engineering**: Concatenates `description`, `problem_context`, `citizen_statement`, `state`, and `district`.
- **Review Policy Engine**:
  - **Confidence Threshold**: `0.50`
  - **Top-1 / Top-2 Margin Threshold**: `0.20`
  - If top prediction confidence is `< 0.50` or top-1/top-2 margin is `< 0.20`, the AI flags `requires_human_review = True` and sets `decision = "HUMAN_REVIEW"`.

### **2. Heuristic Triage Signal Rules**
- **Urgency Signals**: Evaluates critical keywords (e.g. *fatal, life threatening, flood, bridge collapse, oxygen shortage*) and high urgency keywords (e.g. *outage, contamination, leak*) combined with affected population metrics.
- **Severity Signals**: Evaluates affected population thresholds (100, 1,000, 10,000+), economic loss estimates ($100k+, $1M+), and risk indicators to generate a normalized score (0.0 – 1.0).
- **Innovation Detection**: Scans for tech/R&D keywords (*AI, IoT, sensors, satellite, drone, digital twin, prototype, remote sensing*) to identify challenges requiring research or technological intervention.
- **Routing Engine**: Directs challenges to:
  - `MUNICIPALITY`: For civic issues (Water, Sanitation, Waste, Local Roads, Streetlights).
  - `GOVERNMENT`: For state/departmental issues (Healthcare, Education, Energy, Agriculture).
  - `INNOVATION`: For tech/research-driven problem solving (Universities/Industry).
  - `HUMAN_REVIEW`: For high-risk/ambiguous cases requiring manual oversight.

---

## 🖥️ Frontend User Interface

The frontend application provides a modern, responsive web application with dark-mode glassmorphic aesthetics:

- **Landing Page (`/`)**: Hero section, platform feature breakdown, live impact stats, active challenge feed, call-to-action sections.
- **Auth Pages (`/login`, `/register`)**: Form-validated registration and login with automatic JWT token management.
- **Citizen Dashboard (`/citizen/dashboard`)**: Overview of submitted challenges, AI triage status badges, filterable list of civic issues.
- **Submit Challenge Page (`/citizen/challenges/new`)**: Multi-step challenge submission form with real-time AI triage integration.
- **Challenge Details Page (`/citizen/challenges/:id`)**: Comprehensive view of challenge status, location map preview, uploaded media evidence gallery, and AI diagnostic breakdown.

---

## 🔌 Plugins & External Capabilities

The architecture supports several core modules and plugin interfaces:

1. **Static File Upload Plugin**: Fast file server mounted on `/uploads` with MIME-type validation, unique file hashing, and size restrictions (default max 50MB).
2. **Alembic Database Engine Plugin**: Managed database schema evolution tracking.
3. **Machine Learning Model Registry**: Decoupled joblib model loading allowing seamless model swapping without code changes.
4. **Science / Domain Knowledge Integration Ready**: Built-in compatibility structure for integrating domain-specific scientific APIs (biomedical, environmental, geospatial).

---

## ⚙️ Setup & Running Locally

### **Prerequisites**
- Python 3.10+
- Node.js 18+ & npm
- PostgreSQL database instance

### **1. Backend Setup**
```bash
# Navigate to backend folder
cd backend

# Create and activate virtual environment
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt # (or install fastAPI, sqlalchemy, alembic, joblib, scikit-learn, etc.)

# Apply database migrations
alembic upgrade head

# Start FastAPI server
uvicorn app.main:app --reload --port 8000
```
- API Docs available at: `http://localhost:8000/docs`
- ReDoc available at: `http://localhost:8000/redoc`

### **2. Frontend Setup**
```bash
# Navigate to frontend folder
cd frontend

# Install dependencies
npm install

# Run Vite dev server
npm run dev
```
- Frontend application runs at: `http://localhost:5173`

---

## 🔑 Environment Configuration

Create or update the `.env` file in the project root:

```env
APP_NAME="Societal Innovation Platform"
APP_VERSION="1.0.0"
ENVIRONMENT="development"

# PostgreSQL Database Connection
DATABASE_URL="postgresql+psycopg://postgres:your_password@localhost:5432/societal_innovation"

# Security & JWT Configuration
SECRET_KEY="dev-sip-9f4c8a71e2b643a5b6d9c1e7f8a2b4d6"
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
ALGORITHM="HS256"

# Service URLs
FRONTEND_URL="http://localhost:5173"
AI_SERVICE_URL="http://localhost:8001"
MAX_UPLOAD_SIZE_MB=50
```

---

*Societal Innovation Platform — Bridging Citizens, Government, and Innovation Ecosystems.*
