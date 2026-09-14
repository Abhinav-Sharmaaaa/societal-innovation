import { ArrowLeft, Send } from "lucide-react";
import type { FormEvent } from "react";
import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import {
  createUniversityProposal,
  type CreateUniversityProposalRequest,
} from "../../services/universityProposalService";

import "./UniversityProposalPages.css";

export default function CreateUniversityProposalPage() {
  const navigate = useNavigate();
  const location = useLocation();

  const params = new URLSearchParams(location.search);
  const invitationId = Number(params.get("invitation_id"));
  const rfpId = Number(params.get("rfp_id"));

  const [form, setForm] = useState({
    title: "",
    solution: "",
    technical_approach: "",
    research_methodology: "",
    required_resources: "",
    estimated_cost: "",
    expected_timeline_days: "",
    faculty_team: "",
    expected_outcomes: "",
    technology_requirements: "",
  });

  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const updateField = (
    field: keyof typeof form,
    value: string
  ) => {
    setForm((current) => ({
      ...current,
      [field]: value,
    }));
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    setError("");
    setSuccess("");

    if (!invitationId || invitationId <= 0) {
      setError("Invalid invitation ID.");
      return;
    }

    if (!form.title.trim()) {
      setError("Proposal title is required.");
      return;
    }

    if (form.solution.trim().length < 20) {
      setError("Solution must contain at least 20 characters.");
      return;
    }

    if (form.technical_approach.trim().length < 20) {
      setError(
        "Technical approach must contain at least 20 characters."
      );
      return;
    }

    try {
      setSubmitting(true);

      const payload: CreateUniversityProposalRequest = {
        invitation_id: invitationId,
        title: form.title.trim(),
        solution: form.solution.trim(),
        technical_approach: form.technical_approach.trim(),
      };

      if (form.research_methodology.trim()) {
        payload.research_methodology =
          form.research_methodology.trim();
      }

      if (form.required_resources.trim()) {
        payload.required_resources =
          form.required_resources.trim();
      }

      if (form.estimated_cost.trim()) {
        const estimatedCost = Number(form.estimated_cost);

        if (Number.isNaN(estimatedCost) || estimatedCost < 0) {
          setError("Estimated cost must be a valid positive number.");
          return;
        }

        payload.estimated_cost = estimatedCost;
      }

      if (form.expected_timeline_days.trim()) {
        const timeline = Number(form.expected_timeline_days);

        if (
          Number.isNaN(timeline) ||
          timeline <= 0 ||
          !Number.isInteger(timeline)
        ) {
          setError(
            "Expected timeline must be a positive whole number."
          );
          return;
        }

        payload.expected_timeline_days = timeline;
      }

      if (form.faculty_team.trim()) {
        payload.faculty_team = form.faculty_team.trim();
      }

      if (form.expected_outcomes.trim()) {
        payload.expected_outcomes =
          form.expected_outcomes.trim();
      }

      if (form.technology_requirements.trim()) {
        payload.technology_requirements =
          form.technology_requirements.trim();
      }

      const proposal = await createUniversityProposal(payload);

      setSuccess("Proposal submitted successfully.");

      navigate(`/university/proposals/${proposal.id}`, {
        replace: true,
      });
    } catch (err: any) {
      const message =
        err?.response?.data?.detail ||
        "Failed to submit university proposal.";

      setError(message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="university-proposal-page">
      <div className="proposal-page-header">
        <button
          className="proposal-back-button"
          type="button"
          onClick={() => navigate(-1)}
        >
          <ArrowLeft size={18} />
          Back
        </button>

        <div>
          <p className="proposal-eyebrow">
            UNIVERSITY INNOVATION WORKFLOW
          </p>

          <h1>Submit University Proposal</h1>

          <p>
            Develop a solution proposal for the selected government
            RFP.
          </p>
        </div>
      </div>

      {rfpId > 0 && (
        <div className="proposal-context-card">
          <span>RFP ID</span>
          <strong>#{rfpId}</strong>
        </div>
      )}

      {error && (
        <div className="proposal-alert proposal-alert-error">
          {error}
        </div>
      )}

      {success && (
        <div className="proposal-alert proposal-alert-success">
          {success}
        </div>
      )}

      <form
        className="proposal-form"
        onSubmit={handleSubmit}
      >
        <section className="proposal-section">
          <div className="proposal-section-heading">
            <h2>Proposal Overview</h2>
            <p>Describe your proposed solution.</p>
          </div>

          <label>
            Proposal Title *
            <input
              value={form.title}
              onChange={(event) =>
                updateField("title", event.target.value)
              }
              placeholder="Enter proposal title"
              maxLength={255}
              required
            />
          </label>

          <label>
            Proposed Solution *
            <textarea
              value={form.solution}
              onChange={(event) =>
                updateField("solution", event.target.value)
              }
              placeholder="Explain the proposed solution..."
              rows={6}
              required
            />
          </label>

          <label>
            Technical Approach *
            <textarea
              value={form.technical_approach}
              onChange={(event) =>
                updateField(
                  "technical_approach",
                  event.target.value
                )
              }
              placeholder="Explain how the solution will be technically implemented..."
              rows={6}
              required
            />
          </label>
        </section>

        <section className="proposal-section">
          <div className="proposal-section-heading">
            <h2>Research & Resources</h2>
            <p>
              Provide information about the university's research and
              implementation capabilities.
            </p>
          </div>

          <label>
            Research Methodology
            <textarea
              value={form.research_methodology}
              onChange={(event) =>
                updateField(
                  "research_methodology",
                  event.target.value
                )
              }
              placeholder="Describe the research methodology..."
              rows={5}
            />
          </label>

          <label>
            Required Resources
            <textarea
              value={form.required_resources}
              onChange={(event) =>
                updateField(
                  "required_resources",
                  event.target.value
                )
              }
              placeholder="Mention laboratories, equipment, datasets, infrastructure, etc."
              rows={5}
            />
          </label>

          <label>
            Faculty / Research Team
            <textarea
              value={form.faculty_team}
              onChange={(event) =>
                updateField("faculty_team", event.target.value)
              }
              placeholder="Mention faculty members, researchers, students, or teams."
              rows={4}
            />
          </label>
        </section>

        <section className="proposal-section">
          <div className="proposal-section-heading">
            <h2>Implementation Plan</h2>
            <p>
              Provide estimated cost, duration and expected results.
            </p>
          </div>

          <div className="proposal-grid">
            <label>
              Estimated Cost (₹)
              <input
                type="number"
                min="0"
                value={form.estimated_cost}
                onChange={(event) =>
                  updateField(
                    "estimated_cost",
                    event.target.value
                  )
                }
                placeholder="e.g. 500000"
              />
            </label>

            <label>
              Expected Timeline (Days)
              <input
                type="number"
                min="1"
                step="1"
                value={form.expected_timeline_days}
                onChange={(event) =>
                  updateField(
                    "expected_timeline_days",
                    event.target.value
                  )
                }
                placeholder="e.g. 180"
              />
            </label>
          </div>

          <label>
            Technology Requirements
            <textarea
              value={form.technology_requirements}
              onChange={(event) =>
                updateField(
                  "technology_requirements",
                  event.target.value
                )
              }
              placeholder="Mention required technologies, platforms, hardware, AI/ML models, etc."
              rows={4}
            />
          </label>

          <label>
            Expected Outcomes
            <textarea
              value={form.expected_outcomes}
              onChange={(event) =>
                updateField(
                  "expected_outcomes",
                  event.target.value
                )
              }
              placeholder="Describe measurable expected outcomes and societal impact."
              rows={5}
            />
          </label>
        </section>

        <div className="proposal-submit-bar">
          <button
            type="button"
            className="proposal-secondary-button"
            onClick={() => navigate(-1)}
            disabled={submitting}
          >
            Cancel
          </button>

          <button
            type="submit"
            className="proposal-primary-button"
            disabled={submitting}
          >
            <Send size={18} />

            {submitting
              ? "Submitting..."
              : "Submit Proposal"}
          </button>
        </div>
      </form>
    </div>
  );
}