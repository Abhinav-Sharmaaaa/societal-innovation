import {
  ArrowLeft,
  Building2,
  CalendarDays,
  CheckCircle2,
  Coins,
  GraduationCap,
  Info,
  Loader2,
  Rocket,
  Send,
  Sparkles,
} from "lucide-react";
import type { FormEvent } from "react";
import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import {
  getIndustryCollaborationById,
  type IndustryCollaborationProposal,
} from "../../services/industryCollaborationService";
import {
  createProject,
  type CreateProjectRequest,
} from "../../services/projectService";

import "./ProjectPages.css";

export default function CreateProjectPage() {
  const navigate = useNavigate();
  const location = useLocation();

  const params = new URLSearchParams(location.search);
  const collaborationId = Number(params.get("collaboration_id"));

  const [collaboration, setCollaboration] =
    useState<IndustryCollaborationProposal | null>(null);
  const [loadingCollab, setLoadingCollab] = useState(false);

  const [form, setForm] = useState({
    title: "",
    description: "",
    objectives: "",
    expected_outcomes: "",
    total_budget: "",
    start_date: "",
    target_completion_date: "",
  });

  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (collaborationId && collaborationId > 0) {
      setLoadingCollab(true);
      getIndustryCollaborationById(collaborationId)
        .then((data) => {
          setCollaboration(data);
          setForm((prev) => ({
            ...prev,
            title: prev.title || data.title || "",
            description:
              prev.description || data.collaboration_description || "",
            total_budget:
              prev.total_budget ||
              (data.funding_amount ? String(data.funding_amount) : ""),
          }));
        })
        .catch((err) => {
          console.error("Failed to load collaboration:", err);
        })
        .finally(() => {
          setLoadingCollab(false);
        });
    }
  }, [collaborationId]);

  const updateField = (field: keyof typeof form, value: string) => {
    setForm((current) => ({
      ...current,
      [field]: value,
    }));
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError("");

    if (!collaborationId || collaborationId <= 0) {
      setError("Invalid or missing collaboration ID.");
      return;
    }

    if (form.title.trim().length < 5) {
      setError("Project title must contain at least 5 characters.");
      return;
    }

    try {
      setSubmitting(true);

      const payload: CreateProjectRequest = {
        collaboration_id: collaborationId,
        title: form.title.trim(),
      };

      if (form.description.trim()) {
        payload.description = form.description.trim();
      }
      if (form.objectives.trim()) {
        payload.objectives = form.objectives.trim();
      }
      if (form.expected_outcomes.trim()) {
        payload.expected_outcomes = form.expected_outcomes.trim();
      }
      if (form.total_budget.trim()) {
        const budget = Number(form.total_budget);
        if (Number.isNaN(budget) || budget < 0) {
          setError("Total budget must be a valid non-negative number.");
          return;
        }
        payload.total_budget = budget;
      }
      if (form.start_date) {
        payload.start_date = new Date(form.start_date).toISOString();
      }
      if (form.target_completion_date) {
        payload.target_completion_date = new Date(
          form.target_completion_date
        ).toISOString();
      }

      const project = await createProject(payload);

      navigate(`/government/projects/${project.id}`, { replace: true });
    } catch (err: any) {
      setError(
        err?.response?.data?.detail ||
          "Unable to create project. Please verify inputs."
      );
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <main className="create-project-container">
      {/* Top Header */}
      <header className="create-project-header">
        <button
          type="button"
          className="create-project-back-btn"
          onClick={() => navigate(-1)}
        >
          <ArrowLeft size={18} />
          <span>Back to Collaborations</span>
        </button>

        <div className="create-project-title-area">
          <div className="create-project-badge">
            <Sparkles size={14} />
            <span>Project Initiation Phase</span>
          </div>
          <h1>Create Innovation Project</h1>
          <p>
            Convert the accepted university & industry collaboration into an
            executable societal innovation project with tracked milestones.
          </p>
        </div>
      </header>

      {/* Collaboration Context Banner */}
      {collaborationId > 0 && (
        <section className="collab-context-card">
          <div className="collab-context-header">
            <div className="collab-context-title">
              <CheckCircle2 size={20} className="collab-context-icon" />
              <div>
                <h3>Linked Accepted Collaboration</h3>
                <span className="collab-context-id">
                  Collaboration ID #{collaborationId}
                </span>
              </div>
            </div>

            {loadingCollab ? (
              <div className="collab-context-loading">
                <Loader2 size={16} className="project-spin" />
                <span>Fetching collaboration details...</span>
              </div>
            ) : (
              collaboration && (
                <div className="collab-context-funding">
                  <span className="funding-label">Approved Funding</span>
                  <span className="funding-value">
                    ₹
                    {collaboration.funding_amount
                      ? collaboration.funding_amount.toLocaleString("en-IN")
                      : "Not specified"}
                  </span>
                </div>
              )
            )}
          </div>

          {collaboration && (
            <div className="collab-context-details">
              <h4>{collaboration.title}</h4>
              <p>{collaboration.collaboration_description}</p>
            </div>
          )}
        </section>
      )}

      {/* Alert Error */}
      {error && (
        <div className="create-project-alert error">
          <Info size={18} />
          <span>{error}</span>
        </div>
      )}

      {/* Main Form */}
      <form className="create-project-form" onSubmit={handleSubmit}>
        {/* Section 1: Overview */}
        <section className="create-project-card">
          <div className="card-section-heading">
            <div className="icon-wrapper rocket">
              <Rocket size={20} />
            </div>
            <div>
              <h2>Project Overview</h2>
              <p>
                Define the core details, objectives, and outcomes for project
                execution.
              </p>
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="title">
              Project Title <span className="required">*</span>
            </label>
            <input
              id="title"
              type="text"
              className="form-input"
              value={form.title}
              onChange={(e) => updateField("title", e.target.value)}
              placeholder="e.g. AI-Powered Smart PWD Infrastructure & IoT Traffic System"
              maxLength={255}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="description">Project Description</label>
            <textarea
              id="description"
              className="form-textarea"
              rows={5}
              value={form.description}
              onChange={(e) => updateField("description", e.target.value)}
              placeholder="Describe the full scope, methodology, and implementation approach..."
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="objectives">Key Objectives</label>
              <textarea
                id="objectives"
                className="form-textarea"
                rows={4}
                value={form.objectives}
                onChange={(e) => updateField("objectives", e.target.value)}
                placeholder="List specific targets, KPIs, or technical objectives..."
              />
            </div>

            <div className="form-group">
              <label htmlFor="expected_outcomes">Expected Outcomes</label>
              <textarea
                id="expected_outcomes"
                className="form-textarea"
                rows={4}
                value={form.expected_outcomes}
                onChange={(e) => updateField("expected_outcomes", e.target.value)}
                placeholder="Describe societal impact, deployed hardware, or public metrics..."
              />
            </div>
          </div>
        </section>

        {/* Section 2: Budget & Schedule */}
        <section className="create-project-card">
          <div className="card-section-heading">
            <div className="icon-wrapper coins">
              <Coins size={20} />
            </div>
            <div>
              <h2>Budget & Timeline Schedule</h2>
              <p>
                Set the project financial allocation and execution target dates.
              </p>
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="total_budget">Total Project Budget (₹)</label>
            <div className="input-with-prefix">
              <span className="currency-symbol">₹</span>
              <input
                id="total_budget"
                type="number"
                min="0"
                className="form-input prefixed"
                value={form.total_budget}
                onChange={(e) => updateField("total_budget", e.target.value)}
                placeholder="e.g. 3500000"
              />
            </div>
            <span className="field-hint">
              Defaults to accepted collaboration co-funding amount if available.
            </span>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="start_date">
                <span className="label-icon">
                  <CalendarDays size={15} />
                  Start Date
                </span>
              </label>
              <input
                id="start_date"
                type="datetime-local"
                className="form-input"
                value={form.start_date}
                onChange={(e) => updateField("start_date", e.target.value)}
              />
            </div>

            <div className="form-group">
              <label htmlFor="target_completion_date">
                <span className="label-icon">
                  <CalendarDays size={15} />
                  Target Completion Date
                </span>
              </label>
              <input
                id="target_completion_date"
                type="datetime-local"
                className="form-input"
                value={form.target_completion_date}
                onChange={(e) =>
                  updateField("target_completion_date", e.target.value)
                }
              />
            </div>
          </div>
        </section>

        {/* Section 3: Automatic Milestones */}
        <section className="create-project-card milestones-card">
          <div className="card-section-heading">
            <div className="icon-wrapper sparkles">
              <Sparkles size={20} />
            </div>
            <div>
              <h2>Automated Milestone Tracking Plan</h2>
              <p>
                Initializing this project automatically provisions 6 standardized tracking milestones:
              </p>
            </div>
          </div>

          <div className="milestones-grid">
            <MilestonePreviewCard
              step={1}
              title="Problem Validation"
              desc="Requirement gathering & baseline data verification"
            />
            <MilestonePreviewCard
              step={2}
              title="Research & Architecture"
              desc="System design & technical specification alignment"
            />
            <MilestonePreviewCard
              step={3}
              title="Prototype Development"
              desc="Core model building & lab experimental setup"
            />
            <MilestonePreviewCard
              step={4}
              title="Testing & Validation"
              desc="Field trial testing & stakeholder review"
            />
            <MilestonePreviewCard
              step={5}
              title="Pilot Deployment"
              desc="On-ground pilot execution in target district"
            />
            <MilestonePreviewCard
              step={6}
              title="Final Rollout & Handover"
              desc="Full deployment, user training & final reporting"
            />
          </div>
        </section>

        {/* Action Bar */}
        <div className="create-project-actions">
          <button
            type="button"
            className="btn-cancel"
            onClick={() => navigate(-1)}
            disabled={submitting}
          >
            Cancel
          </button>

          <button type="submit" className="btn-submit" disabled={submitting}>
            {submitting ? (
              <>
                <Loader2 size={18} className="project-spin" />
                <span>Creating Project...</span>
              </>
            ) : (
              <>
                <Send size={18} />
                <span>Create & Initialize Project</span>
              </>
            )}
          </button>
        </div>
      </form>
    </main>
  );
}

function MilestonePreviewCard({
  step,
  title,
  desc,
}: {
  step: number;
  title: string;
  desc: string;
}) {
  return (
    <div className="milestone-preview-card">
      <div className="step-badge">{step}</div>
      <div className="milestone-content">
        <strong>{title}</strong>
        <p>{desc}</p>
      </div>
    </div>
  );
}