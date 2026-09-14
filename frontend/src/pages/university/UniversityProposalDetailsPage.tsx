import {
  ArrowLeft,
  CalendarDays,
  CheckCircle2,
  Clock3,
  Coins,
  FileText,
  FlaskConical,
  Users,
} from "lucide-react";
import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import {
  getUniversityProposal,
  type UniversityProposal,
} from "../../services/universityProposalService";

import "./UniversityProposalPages.css";

export default function UniversityProposalDetailsPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [proposal, setProposal] =
    useState<UniversityProposal | null>(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const loadProposal = async () => {
      if (!id) {
        setError("Invalid proposal ID.");
        setLoading(false);
        return;
      }

      try {
        setLoading(true);

        const data = await getUniversityProposal(
          Number(id)
        );

        setProposal(data);
      } catch (err: any) {
        setError(
          err?.response?.data?.detail ||
            "Failed to load proposal."
        );
      } finally {
        setLoading(false);
      }
    };

    void loadProposal();
  }, [id]);

  if (loading) {
    return (
      <div className="proposal-state">
        Loading proposal...
      </div>
    );
  }

  if (error || !proposal) {
    return (
      <div className="proposal-state proposal-state-error">
        <h2>Unable to load proposal</h2>
        <p>{error || "Proposal not found."}</p>

        <button
          type="button"
          onClick={() => navigate(-1)}
          className="proposal-primary-button"
        >
          <ArrowLeft size={18} />
          Go Back
        </button>
      </div>
    );
  }

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
            UNIVERSITY PROPOSAL
          </p>

          <h1>{proposal.title}</h1>

          <p>
            Proposal #{proposal.id} · RFP #{proposal.rfp_id}
          </p>
        </div>
      </div>

      <div className="proposal-status-row">
        <div className="proposal-status-card">
          <span>Status</span>

          <strong>
            <CheckCircle2 size={18} />
            {proposal.status.replaceAll("_", " ")}
          </strong>
        </div>

        <div className="proposal-status-card">
          <span>Submitted</span>

          <strong>
            {proposal.submitted_at
              ? new Date(
                  proposal.submitted_at
                ).toLocaleDateString()
              : "Not submitted"}
          </strong>
        </div>

        <div className="proposal-status-card">
          <span>Estimated Cost</span>

          <strong>
            <Coins size={18} />
            {proposal.estimated_cost !== null
              ? `₹${proposal.estimated_cost.toLocaleString()}`
              : "Not specified"}
          </strong>
        </div>

        <div className="proposal-status-card">
          <span>Timeline</span>

          <strong>
            <Clock3 size={18} />
            {proposal.expected_timeline_days !== null
              ? `${proposal.expected_timeline_days} days`
              : "Not specified"}
          </strong>
        </div>
      </div>

      <div className="proposal-details-grid">
        <section className="proposal-detail-card proposal-detail-wide">
          <div className="proposal-detail-heading">
            <FileText size={20} />
            <h2>Proposed Solution</h2>
          </div>

          <p>{proposal.solution}</p>
        </section>

        <section className="proposal-detail-card proposal-detail-wide">
          <div className="proposal-detail-heading">
            <FlaskConical size={20} />
            <h2>Technical Approach</h2>
          </div>

          <p>{proposal.technical_approach}</p>
        </section>

        {proposal.research_methodology && (
          <section className="proposal-detail-card">
            <h2>Research Methodology</h2>
            <p>{proposal.research_methodology}</p>
          </section>
        )}

        {proposal.required_resources && (
          <section className="proposal-detail-card">
            <h2>Required Resources</h2>
            <p>{proposal.required_resources}</p>
          </section>
        )}

        {proposal.faculty_team && (
          <section className="proposal-detail-card">
            <div className="proposal-detail-heading">
              <Users size={20} />
              <h2>Faculty / Research Team</h2>
            </div>

            <p>{proposal.faculty_team}</p>
          </section>
        )}

        {proposal.technology_requirements && (
          <section className="proposal-detail-card">
            <h2>Technology Requirements</h2>
            <p>{proposal.technology_requirements}</p>
          </section>
        )}

        {proposal.expected_outcomes && (
          <section className="proposal-detail-card proposal-detail-wide">
            <div className="proposal-detail-heading">
              <CalendarDays size={20} />
              <h2>Expected Outcomes</h2>
            </div>

            <p>{proposal.expected_outcomes}</p>
          </section>
        )}
      </div>
    </div>
  );
}