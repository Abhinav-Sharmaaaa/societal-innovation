import {
  ArrowLeft,
  Loader2,
  Send,
} from "lucide-react";
import type { FormEvent } from "react";
import { useState } from "react";
import {
  useLocation,
  useNavigate,
} from "react-router-dom";

import {
  createIndustryCollaboration,
  type CreateIndustryCollaborationRequest,
} from "../../services/industryCollaborationService";

import "./IndustryCollaborationPages.css";

export default function CreateIndustryCollaborationPage() {
  const navigate = useNavigate();
  const location = useLocation();

  const params = new URLSearchParams(
    location.search
  );

  const universityProposalId = Number(
    params.get("proposal_id")
  );

  const [form, setForm] = useState({
    title: "",
    collaboration_description: "",
    funding_amount: "",
    technical_mentorship: "",
    industry_experts: "",
    infrastructure_resources: "",
    technology_support: "",
    internship_support: "",
    pilot_deployment_support: "",
    commercialization_support: "",
    proposed_duration_days: "",
    response_deadline: "",
    additional_terms: "",
  });

  const [submitting, setSubmitting] =
    useState(false);

  const [error, setError] =
    useState("");

  const updateField = (
    field: keyof typeof form,
    value: string
  ) => {
    setForm((current) => ({
      ...current,
      [field]: value,
    }));
  };

  const handleSubmit = async (
    event: FormEvent<HTMLFormElement>
  ) => {
    event.preventDefault();

    setError("");

    if (
      !universityProposalId ||
      universityProposalId <= 0
    ) {
      setError(
        "Invalid university proposal ID."
      );
      return;
    }

    if (
      form.collaboration_description.trim()
        .length < 20
    ) {
      setError(
        "Collaboration description must contain at least 20 characters."
      );
      return;
    }

    try {
      setSubmitting(true);

      const payload: CreateIndustryCollaborationRequest =
        {
          university_proposal_id:
            universityProposalId,

          title: form.title.trim(),

          collaboration_description:
            form.collaboration_description.trim(),
        };

      if (form.funding_amount.trim()) {
        const amount = Number(
          form.funding_amount
        );

        if (
          Number.isNaN(amount) ||
          amount < 0
        ) {
          setError(
            "Funding amount must be a valid non-negative number."
          );
          return;
        }

        payload.funding_amount = amount;
      }

      if (
        form.technical_mentorship.trim()
      ) {
        payload.technical_mentorship =
          form.technical_mentorship.trim();
      }

      if (form.industry_experts.trim()) {
        payload.industry_experts =
          form.industry_experts.trim();
      }

      if (
        form.infrastructure_resources.trim()
      ) {
        payload.infrastructure_resources =
          form.infrastructure_resources.trim();
      }

      if (form.technology_support.trim()) {
        payload.technology_support =
          form.technology_support.trim();
      }

      if (form.internship_support.trim()) {
        payload.internship_support =
          form.internship_support.trim();
      }

      if (
        form.pilot_deployment_support.trim()
      ) {
        payload.pilot_deployment_support =
          form.pilot_deployment_support.trim();
      }

      if (
        form.commercialization_support.trim()
      ) {
        payload.commercialization_support =
          form.commercialization_support.trim();
      }

      if (
        form.proposed_duration_days.trim()
      ) {
        const days = Number(
          form.proposed_duration_days
        );

        if (
          Number.isNaN(days) ||
          days <= 0 ||
          !Number.isInteger(days)
        ) {
          setError(
            "Proposed duration must be a positive whole number."
          );
          return;
        }

        payload.proposed_duration_days =
          days;
      }

      if (form.response_deadline) {
        payload.response_deadline =
          new Date(
            form.response_deadline
          ).toISOString();
      }

      if (form.additional_terms.trim()) {
        payload.additional_terms =
          form.additional_terms.trim();
      }

      const collaboration =
        await createIndustryCollaboration(
          payload
        );

      navigate(
        `/industry/collaborations/${collaboration.id}`
      );
    } catch (err: any) {
      setError(
        err?.response?.data?.detail ||
          "Failed to submit collaboration proposal."
      );
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <main className="industry-collaboration-page">

      <header className="industry-collaboration-header">

        <button
          type="button"
          className="collaboration-back"
          onClick={() => navigate(-1)}
        >
          <ArrowLeft size={18} />
          Back
        </button>

        <span>
          INDUSTRY COLLABORATION
        </span>

        <h1>
          Submit Collaboration Proposal
        </h1>

        <p>
          Offer funding, technology, expertise and
          deployment support for the shortlisted
          university proposal.
        </p>

      </header>

      {error && (
        <div className="collaboration-error">
          {error}
        </div>
      )}

      <form
        className="collaboration-form"
        onSubmit={handleSubmit}
      >

        <section className="collaboration-section">

          <h2>Collaboration Overview</h2>

          <label>
            Collaboration Title *
            <input
              value={form.title}
              onChange={(event) =>
                updateField(
                  "title",
                  event.target.value
                )
              }
              placeholder="e.g. Industry deployment partnership"
              required
            />
          </label>

          <label>
            Collaboration Description *
            <textarea
              rows={6}
              value={
                form.collaboration_description
              }
              onChange={(event) =>
                updateField(
                  "collaboration_description",
                  event.target.value
                )
              }
              placeholder="Explain how your industry will support the university proposal..."
              required
            />
          </label>

        </section>


        <section className="collaboration-section">

          <h2>Funding & Duration</h2>

          <div className="collaboration-grid">

            <label>
              Funding Amount (₹)
              <input
                type="number"
                min="0"
                value={form.funding_amount}
                onChange={(event) =>
                  updateField(
                    "funding_amount",
                    event.target.value
                  )
                }
                placeholder="e.g. 1000000"
              />
            </label>

            <label>
              Proposed Duration (Days)
              <input
                type="number"
                min="1"
                value={
                  form.proposed_duration_days
                }
                onChange={(event) =>
                  updateField(
                    "proposed_duration_days",
                    event.target.value
                  )
                }
                placeholder="e.g. 180"
              />
            </label>

          </div>

          <label>
            Response Deadline
            <input
              type="datetime-local"
              value={
                form.response_deadline
              }
              onChange={(event) =>
                updateField(
                  "response_deadline",
                  event.target.value
                )
              }
            />
          </label>

        </section>


        <section className="collaboration-section">

          <h2>Industry Support</h2>

          <label>
            Technical Mentorship
            <textarea
              rows={4}
              value={
                form.technical_mentorship
              }
              onChange={(event) =>
                updateField(
                  "technical_mentorship",
                  event.target.value
                )
              }
              placeholder="Describe engineering and technical mentorship."
            />
          </label>

          <label>
            Industry Experts
            <textarea
              rows={4}
              value={
                form.industry_experts
              }
              onChange={(event) =>
                updateField(
                  "industry_experts",
                  event.target.value
                )
              }
              placeholder="Mention experts, specialists, advisors or domain teams."
            />
          </label>

          <label>
            Infrastructure Resources
            <textarea
              rows={4}
              value={
                form.infrastructure_resources
              }
              onChange={(event) =>
                updateField(
                  "infrastructure_resources",
                  event.target.value
                )
              }
              placeholder="Labs, servers, manufacturing facilities, equipment, etc."
            />
          </label>

          <label>
            Technology Support
            <textarea
              rows={4}
              value={
                form.technology_support
              }
              onChange={(event) =>
                updateField(
                  "technology_support",
                  event.target.value
                )
              }
              placeholder="Technology, APIs, hardware, cloud, software, etc."
            />
          </label>

          <label>
            Internship Support
            <textarea
              rows={4}
              value={
                form.internship_support
              }
              onChange={(event) =>
                updateField(
                  "internship_support",
                  event.target.value
                )
              }
              placeholder="Internships and student opportunities."
            />
          </label>

          <label>
            Pilot Deployment Support
            <textarea
              rows={4}
              value={
                form.pilot_deployment_support
              }
              onChange={(event) =>
                updateField(
                  "pilot_deployment_support",
                  event.target.value
                )
              }
              placeholder="How will your company support field/pilot deployment?"
            />
          </label>

          <label>
            Commercialization Support
            <textarea
              rows={4}
              value={
                form.commercialization_support
              }
              onChange={(event) =>
                updateField(
                  "commercialization_support",
                  event.target.value
                )
              }
              placeholder="Manufacturing, market access, commercialization, scaling, etc."
            />
          </label>

        </section>


        <section className="collaboration-section">

          <h2>Additional Terms</h2>

          <textarea
            rows={5}
            value={form.additional_terms}
            onChange={(event) =>
              updateField(
                "additional_terms",
                event.target.value
              )
            }
            placeholder="Any additional conditions, commitments or terms."
          />

        </section>


        <div className="collaboration-submit-bar">

          <button
            type="button"
            className="collaboration-secondary"
            onClick={() => navigate(-1)}
            disabled={submitting}
          >
            Cancel
          </button>

          <button
            type="submit"
            className="collaboration-primary"
            disabled={submitting}
          >
            {submitting ? (
              <Loader2
                size={18}
                className="collaboration-spin"
              />
            ) : (
              <Send size={18} />
            )}

            {submitting
              ? "Submitting..."
              : "Submit Collaboration"}
          </button>

        </div>

      </form>

    </main>
  );
}