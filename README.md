🌐 Societal Innovation Platform (SIP)

AI-powered, state-configurable societal innovation platform connecting citizens, government, universities, research teams, and industry to turn societal challenges into measurable solutions.

SIP is designed around a complete challenge-to-impact workflow:

Citizen / Community / Government
            ↓
   Societal Challenge
            ↓
       AI Triage
            ↓
 Human Review (when required)
            ↓
Competency-based Authority Routing
            ↓
 ┌───────────────────────────────┐
 │ Routine / Existing Mechanism   │ → Government Resolution
 │ Innovation Required            │ → Innovation Pathway
 └───────────────────────────────┘
            ↓
      Innovation Opportunity
            ↓
             RFP
            ↓
     University Matching
            ↓
   Top-3 University Recommendations
            ↓
       University Invitation
            ↓
       Express Interest
            ↓
      University Proposal
            ↓
   Government Evaluation
            ↓
     SHORTLISTED / REJECTED
            ↓
    Industry Collaboration
            ↓
 University Accepts / Rejects /
 Requests Modification
            ↓
      Government Project
            ↓
 Milestones / Deliverables / Funding
            ↓
 Reports / Evidence / Outcomes
            ↓
      Risk Monitoring
            ↓
      Notifications / Alerts
            ↓
      Reputation / Impact

The implementation is currently demonstrated using Uttarakhand-oriented test organizations and data, while the architecture remains state-configurable and is designed to support other states and jurisdictions without hard-coding the platform to Uttarakhand.

📌 Table of Contents

1. Project Vision

2. Core Design Principles

3. End-to-End Workflow

4. Architecture & Tech Stack

5. Repository Structure

6. User Roles & Responsibilities

7. Organization & Authority Model

8. Challenge Lifecycle

9. AI Triage & Human Review

10. Authority Routing & Escalation

11. Innovation Opportunity & RFP Workflow

12. University Matching

13. University Proposal Workflow

14. Proposal Evaluation

15. Industry Collaboration

16. Project Execution

17. Risk Management & Notifications

18. Reputation System

19. Dashboards & Analytics

20. Database Schema & Models

21. API Endpoints Reference

22. Frontend User Interface

23. AI & Machine Learning

24. Current Completion Status

25. Remaining Work

26. Local Test / Demo Data

27. Setup & Running Locally

28. Environment Configuration

29. Development Workflow

30. Demo Flow

31. Production Hardening

1. 🎯 Project Vision

Societal problems are often reported in fragmented channels, routed manually, and disconnected from research and implementation ecosystems. SIP creates a structured digital pipeline that:

Crowdsources societal challenges from citizens and communities.

Uses AI to triage and explain challenge category, confidence, severity, urgency, innovation requirement, and routing recommendation.

Keeps humans in control for ambiguous, sensitive, or low-confidence decisions.

Routes challenges to the lowest competent authority based on organizational competencies and jurisdiction.

Escalates or reassigns cases when the current authority cannot resolve them or when a higher-level intervention is required.

Converts suitable unresolved challenges into innovation opportunities.

Publishes RFPs and recommends universities based on competencies, capabilities, textual relevance, and location.

Invites selected universities to participate and submit proposals.

Evaluates proposals transparently using explicit weighted criteria.

Connects shortlisted proposals with industry for funding, mentorship, technology, infrastructure, pilot deployment, and commercialization support.

Creates and monitors projects, including milestones, deliverables, funding, reports, evidence, outcomes, risks, and impact.

Builds reputation and analytics around ecosystem participation and results.

2. 🧭 Core Design Principles

AI recommends; authorized humans decide

The platform intentionally separates AI recommendations from official decisions.

AI Recommendation
      ↓
Human Review / Authorized Decision
      ↓
Official Workflow State

AI does not become the final government authority.

Human review is a workflow responsibility

HUMAN_REVIEW is a workflow state, not a physical organization.

A dedicated REVIEW_OFFICER role is used for review responsibilities, scoped to its organization/state/district where applicable.

Lowest competent authority first

Routing is competency and jurisdiction based. A challenge should go to the lowest authority capable of resolving it, with escalation available when necessary.

Reassignment and escalation are different operations

Reassignment: move a case to another eligible authority at the same or different level.

Escalation: explicitly move a case upward or to a higher level because the current authority cannot resolve it, lacks jurisdiction/resources, or higher-level intervention is required.

Full auditability

Routing movements and review actions maintain history including actor, timestamp, action, source, destination, reason, remarks, and resulting state.

State-configurable architecture

State, district, organization, jurisdiction, and competency are data-driven. The platform is not architecturally limited to one state.

3. 🔄 End-to-End Workflow

3.1 Citizen / Community Challenge

A citizen submits:

title

problem description

location

district/state

affected population

estimated economic impact

supporting images/videos/documents

3.2 AI Triage

The AI/rule engine analyzes the challenge and can produce:

primary category

top-2 / top-3 predictions

confidence

top-1/top-2 margin

category decision

severity signals

urgency signals

innovation-required decision

innovation type

human-review requirement

routing recommendation

3.3 Human Review

Low-confidence or ambiguous cases enter the human review queue.

The reviewer can:

accept the AI recommendation

override the recommendation

select/recommend an authority

provide remarks

3.4 Authority Routing

The platform evaluates eligible organizations using competencies, jurisdiction/location and routing logic.

The challenge can then be:

assigned

reassigned

escalated

resolved

forwarded toward the innovation pathway when ordinary mechanisms are insufficient.

3.5 Innovation Pathway

For confirmed innovation challenges:

Challenge
   ↓
Innovation Opportunity
   ↓
Approve
   ↓
RFP
   ↓
Publish
   ↓
University Matching

3.6 University Matching

The platform evaluates universities using a transparent scoring model based on:

competency match

capability match

text relevance

location relevance

The system returns the top 3 recommendations with explanations and component scores.

The current university matching implementation is rule-based and explainable, not a trained ML matching model.

3.7 University Invitation

Government chooses universities from the recommendations and sends invitations.

University-side actions include:

view invitations

express interest

decline

submit proposal after expressing interest

3.8 University Proposal

The university submits:

proposal title

solution

technical approach

research methodology

required resources

estimated cost

expected timeline

faculty/research team

expected outcomes

technology requirements

3.9 Government Evaluation

Government evaluates seven criteria:

Criterion

Weight

Technical Feasibility

20%

Innovation

15%

Cost Effectiveness

10%

Impact

20%

Timeline

10%

Scalability

10%

Research Capability

15%

Total

100%

The evaluation first moves to UNDER_REVIEW. The government then explicitly chooses:

SHORTLISTED

REJECTED

The platform does not automatically shortlist a proposal purely from the calculated score.

3.10 Industry Collaboration

Industry can view shortlisted university proposals and propose:

funding

technical mentorship

industry experts

infrastructure resources

technology support

internship support

pilot deployment support

commercialization support

proposed duration

response deadline

additional terms

University users then review the industry proposal:

ACCEPTED

REJECTED

MODIFICATION_REQUESTED

3.11 Project Execution

After collaboration acceptance, the intended next step is explicit government project creation.

Projects track:

status

health

budget

start/target dates

progress

milestones

deliverables

funding transactions

reports

evidence

outcomes

risks

3.12 Impact & Reputation

Verified outcomes and successful project execution contribute to ecosystem reputation and impact analytics.

4. 🏗️ Architecture & Tech Stack

Backend

Framework: FastAPI

Language: Python 3.10+

Database: PostgreSQL

ORM: SQLAlchemy 2.x

Migrations: Alembic

Authentication: JWT bearer authentication

Validation: Pydantic v2

Scheduling: APScheduler

File Uploads: local upload storage (development/demo)

Frontend

Framework: React + TypeScript

Build Tool: Vite

Routing: React Router

API Client: Axios

Icons: Lucide React

Styling: Custom CSS

AI / ML

ML Framework: scikit-learn

Primary category model: TF-IDF + Logistic Regression

Model serialization: Joblib

Triage: hybrid ML + rule/heuristic engine

University matching: current implementation is transparent rule-based scoring

5. 📂 Repository Structure

societal-innovation-platorm/
│
├── .env
├── backend/
│   ├── alembic/
│   │   └── versions/
│   ├── alembic.ini
│   ├── app/
│   │   ├── ai/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── main.py
│   └── uploads/
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── assets/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── layouts/
│   │   ├── pages/
│   │   │   ├── auth/
│   │   │   ├── citizen/
│   │   │   ├── government/
│   │   │   ├── industry/
│   │   │   ├── public/
│   │   │   └── university/
│   │   ├── routes/
│   │   ├── services/
│   │   ├── store/
│   │   ├── types/
│   │   ├── utils/
│   │   ├── App.css
│   │   ├── index.css
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
│
└── ml/
    ├── data/
    │   ├── instruction/
    │   └── training_views/
    ├── evaluation/
    ├── models/
    ├── preprocessing/
    └── training/

Important current ML data assets

ml/data/instruction/university_matching_training_v2.jsonl
ml/data/instruction/industry_matching_training_v2.jsonl
ml/data/training_views/university_matching_v2.csv
ml/data/training_views/industry_matching_v2.csv

These datasets/views exist for future model-training work. The current university matching production/demo path remains rule-based.

6. 👥 User Roles & Responsibilities

Role

Responsibility

SUPER_ADMIN

Platform-wide administration, official account/org setup, global administration

CITIZEN

Submit and track societal challenges

REVIEW_OFFICER

Human review of AI decisions and ambiguous cases

MUNICIPALITY_OFFICER

Handle/reassign/escalate municipal cases

GOVERNMENT_OFFICER

Government routing, innovation/RFP/proposal/project workflows

UNIVERSITY_ADMIN

University-level participation, invitations, proposals, collaboration review

FACULTY

University proposal/research participation and collaboration review

STUDENT

University-side visibility/participation where permitted

INDUSTRY_ADMIN

Industry collaboration and organization-level participation

INDUSTRY_MEMBER

Industry collaboration participation

SUPER_ADMIN is platform-level and is not tied to a single state/district organization.

7. 🏢 Organization & Authority Model

Organizations represent operational entities and authorities.

Supported organization types:

MUNICIPALITY

GOVERNMENT_DEPARTMENT

UNIVERSITY

INDUSTRY

Organizations can have:

state

district

competencies

capabilities

authority hierarchy/context

Example demo organizations currently used

ID

Organization

Type

Location

1

Dehradun Municipal Authority

MUNICIPALITY

Dehradun, Uttarakhand

2

Dehradun District Disaster Management Authority

GOVERNMENT_DEPARTMENT

Dehradun, Uttarakhand

4

Uttarakhand Innovation University

UNIVERSITY

Dehradun, Uttarakhand

5

Uttarakhand Innovation Technologies

INDUSTRY

Dehradun, Uttarakhand

A test organization #3 also exists and is intended to be cleaned up when test data is finalized.

University demo capabilities

Computer Science

Artificial Intelligence

AI Innovation Lab

Industry demo capabilities

Internet of Things

Field Deployment

Pilot Funding

Product Engineering Mentorship

8. 🧾 Challenge Lifecycle

Supported challenge statuses include:

SUBMITTED
    ↓
UNDER_AI_ANALYSIS
    ↓
UNDER_REVIEW   ← ambiguity / low confidence
    ↓
ROUTED
    ↓
IN_PROGRESS
    ↓
RESOLVED
    ↓
CLOSED

Other possible terminal/exception states include REJECTED.

The challenge model also supports duplicate/master challenge tracking through:

is_master_challenge

master_challenge_id

duplicate_similarity_score

9. 🤖 AI Triage & Human Review

Category classification

The current category engine uses ML classification with a confidence and ambiguity policy.

Primary supported categories:

WATER
SANITATION
WASTE_MANAGEMENT
HEALTHCARE
EDUCATION
AGRICULTURE
TRANSPORTATION
ENERGY
ENVIRONMENT
PUBLIC_SAFETY
INFRASTRUCTURE
DIGITAL_SERVICES
EMPLOYMENT
SOCIAL_WELFARE
DISASTER_MANAGEMENT
OTHER

Human-review policy

The category review policy uses:

top-1 confidence threshold: 0.50

top-1 vs top-2 margin threshold: 0.20

Low confidence or low separation can result in:

category_decision = HUMAN_REVIEW
requires_human_review = true

Example

A vague challenge such as:

“Potholes are there on the roads.”

can produce a low confidence/margin situation and enter human review instead of being blindly routed.

The demonstrated workflow then allows a REVIEW_OFFICER to accept the recommendation or override it.

10. 🧭 Authority Routing & Escalation

Routing uses authority competency rather than simply sending every challenge to a high-level department.

Current logic concept

Challenge
   ↓
Eligible authorities
   ↓
Competency / jurisdiction / location scoring
   ↓
Recommended authority
   ↓
Human review when required
   ↓
Assignment

Available operations

Accept recommendation

Override recommendation

Assign

Auto-route

Reassign

Escalate

Audit history

Routing movement is retained in assignment history.

A demonstrated test flow has included:

Human Review
   ↓
Government Authority #2
   ↓
Reassigned to Municipality #1
   ↓
Escalated back to Government Authority #2

This proves the platform can represent bidirectional authorized workflow movement rather than only upward escalation.

11. 💡 Innovation Opportunity & RFP Workflow

Innovation Opportunity

Statuses:

DRAFT
APPROVED
RFP_CREATED
ACTIVE
CLOSED
CANCELLED

An innovation opportunity is intended to be created after the innovation requirement has been confirmed through the governance workflow.

RFP

Statuses:

DRAFT
PUBLISHED
CLOSED
CANCELLED

Typical sequence:

Innovation Opportunity
       ↓
Approve
       ↓
Create RFP
       ↓
Publish
       ↓
Match Universities
       ↓
Send Invitations

12. 🎓 University Matching

The current university matching engine is rule-based and explainable.

Scoring components:

Signal

Weight

Competency match

35%

Capability match

40%

Text relevance

15%

Location

10%

The API returns the top 3 recommendations with:

rank

organization ID/name

total score

competency score

capability score

text relevance score

location score

matched competencies

matched capabilities

explanation

The current architecture intentionally allows a trained university-matching model to be introduced later without replacing the surrounding workflow.

13. 🎓 University Proposal Workflow

Invitation statuses:

INVITED
VIEWED
INTERESTED
DECLINED
PROPOSAL_SUBMITTED
EXPIRED

Workflow:

Invitation
   ↓
INTERESTED
   ↓
Create Proposal
   ↓
SUBMITTED

Backend enforcement includes:

university association check

correct university ownership of invitation

invitation must be INTERESTED

RFP must be PUBLISHED

proposal deadline must not have passed

duplicate proposal prevention

Proposal statuses:

DRAFT
SUBMITTED
UNDER_EVALUATION
SHORTLISTED
REJECTED
WITHDRAWN

14. 🧮 Proposal Evaluation

Authorized government users evaluate proposals using seven weighted criteria.

Technical Feasibility       × 0.20
Innovation                  × 0.15
Cost Effectiveness          × 0.10
Impact                      × 0.20
Timeline                    × 0.10
Scalability                 × 0.10
Research Capability         × 0.15
-----------------------------------
Overall Score                 100%

Each criterion is scored from 0–100.

The backend calculates and stores the authoritative overall_score.

Important governance behavior:

Evaluate
   ↓
UNDER_REVIEW
   ↓
Explicit human decision
   ├── SHORTLISTED
   └── REJECTED

The system does not silently auto-shortlist based on score.

15. 🤝 Industry Collaboration

Industry collaboration is enabled only for shortlisted university proposals.

Industry contribution fields

funding amount

technical mentorship

industry experts

infrastructure resources

technology support

internship support

pilot deployment support

commercialization support

proposed duration

response deadline

additional terms

Collaboration statuses

DRAFT
SUBMITTED
UNDER_REVIEW
MODIFICATION_REQUESTED
ACCEPTED
REJECTED
WITHDRAWN

Industry-side workflow currently implemented

Industry Dashboard
      ↓
Collaboration Opportunities
      ↓
Shortlisted University Proposals
      ↓
Opportunity Details
      ↓
Submit Collaboration Proposal

University-side decision workflow

The backend supports:

SUBMITTED / UNDER_REVIEW / MODIFICATION_REQUESTED
                    ↓
       ┌────────────┼────────────┐
       ↓            ↓            ↓
   ACCEPTED     REJECTED   MODIFICATION_REQUESTED

The university reviewer must belong to the university associated with the proposal.

16. 🚀 Project Execution

Once an industry collaboration is accepted, project creation is intended to be an explicit government action rather than an automatic side effect of accepting collaboration.

Project statuses

PLANNING
ACTIVE
ON_HOLD
COMPLETED
CANCELLED

Project health

ON_TRACK
AT_RISK
DELAYED
CRITICAL

Automatic milestone generation

A project currently has a six-stage milestone model:

Problem Validation

Research Planning

Prototype Development

Testing & Validation

Pilot Deployment

Final Solution Deployment

Each milestone supports status and progress tracking.

17. ⚠️ Risk Management & Notifications

Risk model

Risk levels:

LOW
MEDIUM
HIGH
CRITICAL

Risk lifecycle:

OPEN
  ↓
ACKNOWLEDGED
  ↓
MITIGATED
  ↓
CLOSED

Risk scoring signals

The risk engine combines signals such as:

delayed milestones

blocked milestones

overdue milestones

overdue deliverables

rejected reports

schedule gaps

high funding utilization with low project progress

verified outcomes below target

Scores are capped at 100 and mapped to risk levels.

Notification priorities

LOW
MEDIUM
HIGH
CRITICAL

Notification types include:

RISK_ALERT

DEADLINE_ALERT

PROJECT_UPDATE

MILESTONE_UPDATE

FUNDING_ALERT

The backend also contains scheduled scans for project risk and deadlines using APScheduler.

Deadline thresholds

Current deadline scanning uses:

7 days → MEDIUM

3 days → HIGH

1 day → HIGH

due today → HIGH

overdue → CRITICAL

18. 🏆 Reputation System

The reputation system tracks contributions for:

citizens

universities

industry organizations

Event types

CHALLENGE_SUBMITTED

CHALLENGE_VALIDATED

UNIVERSITY_PROPOSAL

PROJECT_CONTRIBUTION

MILESTONE_COMPLETED

DELIVERABLE_APPROVED

FUNDING_CONTRIBUTION

PROJECT_COMPLETED

POSITIVE_PROJECT_OUTCOME

Current point values

Event

Points

Challenge submitted

5

Challenge validated

15

University proposal

20

Project contribution

15

Milestone completed

10

Deliverable approved

10

Funding contribution

25

Project completed

50

Positive project outcome

75

The implementation includes idempotency checks to prevent duplicate reputation events from being repeatedly counted.

19. 📊 Dashboards & Analytics

Current backend dashboard services include:

Government Dashboard

University Dashboard

Industry Dashboard

Citizen Dashboard

Action Center

Analytics Overview

District Analytics

University Leaderboard / Reputation

Industry Leaderboard / Reputation

Government dashboard

Provides visibility into:

challenges

routing/review workload

innovation pipeline

projects

impact/risk signals

University dashboard

Tracks:

invitations

proposals

collaboration status

projects

milestones

deliverables

outcomes

reputation

action-center notifications

Industry dashboard

Tracks:

collaborations

projects

milestones

deliverables

funding

impact

reputation

The current Industry dashboard includes an entry point to browse collaboration opportunities.

Citizen dashboard

Tracks a citizen's submitted challenges and status information.

20. 🗄️ Database Schema & Models

The platform currently contains the following major SQLAlchemy model areas.

Identity & organizations

User

Organization

OrganizationCompetency

OrganizationCapability

Challenge ecosystem

Challenge

ChallengeEvidence

ChallengeAssignment

ChallengeReview

Innovation/RFP

InnovationOpportunity

RFP

RFPInvitation

UniversityProposal

ProposalEvaluation

IndustryCollaborationProposal

Project execution

Project

ProjectMilestone

ProjectDeliverable

ProjectFundingTransaction

ProjectReport

ProjectEvidence

ProjectOutcome

ProjectRisk

Platform services

Notification

ReputationEvent

ReputationScore

Important relationship note

ProjectMilestone.deliverables is a text description field. The SQLAlchemy relationship to ProjectDeliverable is intentionally named:

deliverable_items

This avoids collision between the text field and relationship property.

21. 📡 API Endpoints Reference

Base prefix:

/api/v1

This list reflects the currently implemented backend workflow. Exact response fields should be checked against the corresponding Pydantic schema when extending the platform.

21.1 Authentication

Method

Endpoint

Description

POST

/api/v1/auth/register

Public citizen registration

POST

/api/v1/auth/login

Login and JWT issuance

GET

/api/v1/auth/me

Current authenticated user

POST

/api/v1/auth/setup-super-admin

One-time super-admin setup

POST

/api/v1/admin/users

SUPER_ADMIN creates official users

21.2 Challenges

Method

Endpoint

Description

GET

/api/v1/challenges

Challenge list

GET

/api/v1/challenges/my

Current user's challenges

GET

/api/v1/challenges/{id}

Challenge details

POST

/api/v1/challenges

Submit challenge

POST

/api/v1/challenges/{id}/evidence

Upload evidence

POST

/api/v1/challenges/{id}/assign

Assign authority

POST

/api/v1/challenges/{id}/auto-route

Auto-route

POST

/api/v1/challenges/{id}/reassign

Reassign authority

POST

/api/v1/challenges/{id}/escalate

Escalate

GET

/api/v1/challenges/{id}/assignment-history

Assignment audit history

21.3 AI & routing

Method

Endpoint

Description

POST

/api/v1/ai/triage

Run AI triage

GET

/api/v1/routing/challenges/{challenge_id}/recommendation

Authority recommendation

21.4 Human review

Method

Endpoint

Description

GET

/api/v1/reviews/queue

Review queue

POST

/api/v1/reviews/{challenge_id}/accept

Accept AI recommendation

POST

/api/v1/reviews/{challenge_id}/override

Override AI recommendation

GET

/api/v1/reviews/{challenge_id}/history

Review history

21.5 Innovation opportunities

Method

Endpoint

Description

POST

/api/v1/innovation-opportunities

Create innovation opportunity

GET

/api/v1/innovation-opportunities/{id}

Get opportunity

POST

/api/v1/innovation-opportunities/{id}/approve

Approve opportunity

21.6 RFPs

Method

Endpoint

Description

POST

/api/v1/rfps

Create RFP

GET

/api/v1/rfps/{id}

Get RFP

POST

/api/v1/rfps/{id}/publish

Publish RFP

POST

/api/v1/rfps/{id}/close

Close RFP

POST

/api/v1/rfps/{id}/match-universities

Get top university matches

21.7 RFP Invitations

Method

Endpoint

Description

POST

/api/v1/rfp-invitations

Government sends invitation

GET

/api/v1/rfp-invitations/rfp/{rfp_id}

RFP invitation list

GET

/api/v1/rfp-invitations/my

University invitation list

POST

/api/v1/rfp-invitations/{id}/interest

Express interest

POST

/api/v1/rfp-invitations/{id}/decline

Decline invitation

21.8 University proposals

Method

Endpoint

Description

POST

/api/v1/university-proposals

Submit university proposal

GET

/api/v1/university-proposals/{id}

Get proposal

GET

/api/v1/university-proposals/rfp/{rfp_id}

List RFP proposals

GET

/api/v1/university-proposals/shortlisted

Shortlisted proposals for industry

21.9 Proposal evaluations

Method

Endpoint

Description

POST

/api/v1/proposal-evaluations

Create evaluation

POST

/api/v1/proposal-evaluations/{id}/decision

Shortlist/reject

21.10 Industry collaboration

Method

Endpoint

Description

POST

/api/v1/industry-collaboration

Submit collaboration

GET

/api/v1/industry-collaboration/my

Industry's collaborations

GET

/api/v1/industry-collaboration/university

University's received collaborations

POST

/api/v1/industry-collaboration/{id}/decision

University decision

21.11 Dashboards

GET /api/v1/dashboard/government
GET /api/v1/university-dashboard
GET /api/v1/industry-dashboard
GET /api/v1/citizen-dashboard
GET /api/v1/action-center
GET /api/v1/analytics/overview
GET /api/v1/analytics/districts
GET /api/v1/analytics/universities
GET /api/v1/analytics/industries
GET /api/v1/analytics/reputation

22. 🖥️ Frontend User Interface

Public

Landing page

Login

Citizen registration

Citizen

Citizen dashboard

Challenge submission

Challenge details

Government

Government dashboard

Challenges list

Challenge details/control center

Human review queue

Innovation opportunity creation/details

RFP creation/details

University matching

RFP proposal list

Proposal evaluation

Government challenge control center

Provides:

AI triage visibility

category/confidence/top predictions

innovation assessment

authority recommendation

candidate authorities

accept/override

assign/reassign/escalate/auto-route

review history

assignment history

evidence

University

University dashboard

RFP invitations

Express interest / decline

Create university proposal

Proposal details

Industry

Industry dashboard

Collaboration opportunities

Opportunity details

Collaboration submission

Current protected routing

CITIZEN
  → /citizen/*

SUPER_ADMIN / REVIEW_OFFICER /
GOVERNMENT_OFFICER / MUNICIPALITY_OFFICER
  → /government/*

UNIVERSITY_ADMIN / FACULTY / STUDENT
  → /university/*

INDUSTRY_ADMIN / INDUSTRY_MEMBER
  → /industry/*

The frontend uses an Outlet-based ProtectedRoute for authorization-aware route groups.

23. 🤖 AI & Machine Learning

Category model

The core classification path uses a scikit-learn model based on TF-IDF + logistic regression and a serialized Joblib artifact.

The model is designed to consider challenge text and location context.

Hybrid triage

The platform does not rely only on the classifier. Triage combines ML output with deterministic/rule-based signals for:

urgency

severity

affected-population impact

economic impact

innovation requirement

routing decisions

Current limitation

University matching is presently rule-based. The existing training datasets can support future experiments with a trained matching model, but such a model is not currently part of the active matching path.

24. ✅ Current Completion Status

The project is in a working integrated-demo stage, not yet a finished production release.

Backend status

Module

Status

PostgreSQL database

✅ Working

Alembic migrations

✅ Established / linear migration chain

JWT authentication

✅

Citizen registration/login

✅

SUPER_ADMIN setup

✅

Official account creation

✅

Organization competencies

✅

Organization capabilities

✅

Challenge submission

✅

Challenge evidence

✅

AI triage

✅

Human review

✅

Authority assignment

✅

Reassignment

✅

Escalation

✅

Assignment/review audit history

✅

Innovation opportunities

✅

RFP workflow

✅

University matching

✅ Rule-based

RFP invitations

✅

University proposals

✅

Proposal evaluation

✅

Industry collaboration

✅

Project model

✅

Milestones

✅

Deliverables

✅

Funding transactions

✅

Reports

✅

Evidence

✅

Outcomes

✅

Risks

✅

Notifications

✅

Scheduled risk scan

✅

Scheduled deadline scan

✅

Reputation

✅

Dashboards

✅

Analytics services

✅

Frontend status

Module

Status

Landing

✅

Login/register

✅

Citizen dashboard

✅

Citizen challenge flow

✅

Government dashboard

✅

Government challenge management

✅

Human review queue

✅

Innovation Opportunity UI

✅

RFP UI

✅

University matching UI

✅

University invitations UI

✅

University proposal UI

✅

Government proposal list

✅

Government proposal evaluation

✅

Industry dashboard

✅

Industry opportunity list

✅

Industry opportunity details

✅

Industry collaboration submission

✅

University collaboration review UI

⏳ Remaining

Project creation UI

⏳ Remaining

Project dashboard

⏳ Remaining

Milestone UI

⏳ Remaining

Deliverable UI

⏳ Remaining

Funding UI

⏳ Remaining

Report UI

⏳ Remaining

Evidence UI

⏳ Remaining

Outcomes UI

⏳ Remaining

Risk UI

⏳ Remaining

Notification center UI

⏳ Remaining

Advanced analytics UI

⏳ Remaining

Build status

The frontend has repeatedly been compiled successfully after the current feature integrations. The latest recorded production build completed successfully with Vite after approximately 2,011 modules were transformed.

A successful frontend build confirms TypeScript/Vite compilation; it does not by itself prove every runtime/API authorization path has been end-to-end tested.

25. 🚧 Remaining Work

Priority 1 — Finish collaboration workflow

University collaboration review

Still required on the frontend:

University Dashboard
      ↓
Industry Collaborations
      ↓
Collaboration Details
      ↓
ACCEPTED / REJECTED / MODIFICATION_REQUESTED

Industry collaboration history/details

The industry side needs a dedicated list/details view for previously submitted collaborations and response state.

Priority 2 — Project creation

Once collaboration is accepted:

Accepted Collaboration
        ↓
Government project creation
        ↓
Project created

Project creation should remain an explicit authorized action.

Priority 3 — Project execution UI

Build frontend modules for:

project dashboard

milestone management

deliverables

funding transactions

reports

evidence

outcomes

risks

health/progress indicators

Priority 4 — Notification center

Add a complete frontend notification inbox and action routing.

Priority 5 — Analytics visualization

Add richer frontend analytics for:

district comparison

category trends

university performance

industry participation

reputation

impact outcomes

risk patterns

Priority 6 — Production hardening

Before deployment:

tighten notification recipient targeting

validate all route-level authorization in integration tests

remove temporary/test organizations and users

validate all environment variables and secrets

configure production file storage

add proper CORS/origin policy

add database backup strategy

add observability/logging

add API rate limiting where appropriate

add automated backend tests

add browser/e2e workflow tests

Not currently planned for immediate integration

A trained university-matching ML model exists as a future option but is intentionally postponed until the transparent baseline workflow is fully validated.

26. 🧪 Local Test / Demo Data

Current demo ecosystem includes:

Government / authority

Dehradun Municipal Authority

Dehradun District Disaster Management Authority

University

Uttarakhand Innovation University

Industry

Uttarakhand Innovation Technologies

Capabilities

University:

Computer Science
Artificial Intelligence
AI Innovation Lab

Industry:

Internet of Things
Field Deployment
Pilot Funding
Product Engineering Mentorship

Example challenge flow

A previously validated test challenge demonstrated:

Potholes are there on the roads.
        ↓
Low AI category confidence
        ↓
Human Review
        ↓
Recommendation accepted
        ↓
Government authority assigned
        ↓
Reassigned to municipality
        ↓
Escalated to government authority

This test case is useful for demonstrating review, assignment, reassignment, escalation and audit history.

27. ⚙️ Setup & Running Locally

Prerequisites

Python 3.10+

Node.js + npm

PostgreSQL

Git

Backend

cd backend

python -m venv .venv

# Windows PowerShell
.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Apply migrations
alembic upgrade head

# Run backend
uvicorn app.main:app --reload --port 8000

Backend documentation:

http://localhost:8000/docs
http://localhost:8000/redoc

Frontend

cd frontend
npm install
npm run dev

Frontend:

http://localhost:5173

Frontend production build

npm run build

The expected successful output includes:

✓ built in ...

28. 🔑 Environment Configuration

Use a development .env with values appropriate for your local machine.

Example:

APP_NAME="Societal Innovation Platform"
APP_VERSION="1.0.0"
ENVIRONMENT="development"

DATABASE_URL="postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/societal_innovation"

SECRET_KEY="CHANGE_THIS_IN_DEVELOPMENT_AND_PRODUCTION"
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
ALGORITHM="HS256"

FRONTEND_URL="http://localhost:5173"

MAX_UPLOAD_SIZE_MB=50

# Only set this if your active deployment actually uses a separate AI service.
AI_SERVICE_URL="http://localhost:8001"

Security warning

Do not commit real secrets, database passwords, production JWT secrets, API keys, or private credentials to Git.

29. 🛠️ Development Workflow

Recommended workflow for changes:

1. Update backend model/schema/service if required
2. Create or update Alembic migration
3. Run alembic check
4. Run backend compile/tests
5. Update frontend service contract
6. Update frontend page/routes
7. npm run build
8. Run API/runtime smoke tests
9. Test the role-specific UI workflow
10. Commit changes

Useful checks:

# Backend syntax
python -m compileall app

# Migration consistency
alembic check

# Run migrations
alembic upgrade head

# Frontend build
cd ..\frontend
npm run build

30. 🎬 Demo Flow

For a strong end-to-end demonstration, use the following sequence.

Stage 1 — Citizen

Register/login as a citizen.

Submit a societal challenge.

Attach supporting evidence.

Run/display AI triage.

Show category confidence and review decision.

Stage 2 — Government

Login as REVIEW_OFFICER.

Open human review queue.

Accept or override AI recommendation.

Show authority candidates.

Assign the case.

Demonstrate reassignment/escalation if useful.

Show audit history.

Stage 3 — Innovation

Create innovation opportunity.

Approve it.

Create RFP.

Publish RFP.

Run university matching.

Show top 3 recommendations and transparent score breakdown.

Send invitation to selected university.

Stage 4 — University

Login as university admin.

Open RFP Invitations.

Express interest.

Create and submit proposal.

Show submitted proposal.

Stage 5 — Government evaluation

Return to government.

Open RFP → View Proposals.

Open submitted proposal.

Score the seven criteria.

Show weighted overall score.

Submit evaluation.

Explicitly shortlist the proposal.

Stage 6 — Industry

Login as industry user.

Open Collaboration Opportunities.

Open shortlisted proposal.

Submit collaboration proposal including funding/mentorship/deployment support.

Stage 7 — University collaboration decision

University opens received collaboration.

Accept, reject, or request modification.

Stage 8 — Project

Government creates the project from the accepted collaboration.

Track milestones, deliverables and funding.

Add reports/evidence/outcomes.

Demonstrate risk/notification behavior.

Show reputation and impact analytics.

Stages 38–42 describe the intended final demo once the remaining frontend project modules are completed.

31. 🔐 Production Hardening

Before production deployment, complete the following:

Security

rotate all development secrets

enforce secure password policies

configure secure JWT/refresh-token handling

restrict CORS

enforce HTTPS

validate upload file types and content

move uploads to durable object storage

add rate limiting

audit privileged endpoints

Data integrity

add comprehensive foreign-key/ownership checks

add transactional tests around workflow transitions

protect duplicate submissions

verify deadline/timezone handling

test concurrent actions

Authorization

Verify every workflow action for:

current user role

organization ownership

organization type

state/district scope where required

challenge/proposal/project ownership

Operations

production PostgreSQL backups

structured logging

error tracking

application metrics

scheduler monitoring

health/readiness endpoints

deployment automation

🏁 Current Product Position

SIP has progressed beyond a basic issue-reporting application into a multi-stakeholder societal innovation workflow platform.

The core chain is already implemented across backend and frontend:

Citizen
  ↓
Challenge
  ↓
AI Triage
  ↓
Human Review
  ↓
Authority Routing
  ↓
Innovation Opportunity
  ↓
RFP
  ↓
University Matching
  ↓
University Invitation
  ↓
University Proposal
  ↓
Government Evaluation
  ↓
Shortlisting
  ↓
Industry Collaboration

The remaining major work is to finish the University Collaboration Review → Government Project Creation → Project Execution → Impact/Notification UI chain and then perform comprehensive end-to-end testing and production hardening.

📄 License / Ownership

Add the project's final license and organization/author information before public release.

Societal Innovation Platform — Bridging Citizens, Government, Universities, and Industry to turn societal challenges into measurable real-world impact.