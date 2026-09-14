import {
  ArrowLeft,
  Building2,
  CheckCircle2,
  Clock3,
  Coins,
  FileText,
  Loader2,
  Send,
  Users,
} from "lucide-react";
import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import {
  getShortlistedProposals,
  type UniversityProposal,
} from "../../services/industryCollaborationService";

import "./IndustryCollaborationPages.css";

export default function IndustryOpportunityDetailsPage() {
  const { proposalId } = useParams<{
    proposalId: string;
  }>();

  const navigate = useNavigate();

  const [proposal, setProposal] =
    useState<UniversityProposal | null>(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const loadProposal = async () => {
      if (!proposalId) {
        setError("Invalid proposal ID.");
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError("");

        const proposals =
          await getShortlistedProposals();

        const found = proposals.find(
          (item) => item.id === Number(proposalId)
        );

        if (!found) {
          setError(
            "This collaboration opportunity could not be found or is no longer shortlisted."
          );
          return;
        }

        setProposal(found);
      } catch (err: any) {
        setError(
          err?.response?.data?.detail ||
            "Unable to load collaboration opportunity."
        );
      } finally {
        setLoading(false);
      }
    };

    void loadProposal();
  }, [proposalId]);

  if (loading) {
    return (
      <main className="industry-collaboration-page">
        <div className="collaboration-state">
          <Loader2
            size={28}
            className="collaboration-spin"
          />
          Loading opportunity...
        </div>
      </main>
    );
  }

  if (error || !proposal) {
    return (
      <main className="industry-collaboration-page">
        <div className="collaboration-state collaboration-state-error">
          <h2>Opportunity unavailable</h2>

          <p>
            {error ||
              "The requested opportunity was not found."}
          </p>

          <button
            type="button"
            className="collaboration-primary"
            onClick={() =>
              navigate("/industry/opportunities")
            }
          >
            <ArrowLeft size={17} />
            Back to Opportunities
          </button>
        </div>
      </main>
    );
  }

  return (
    <main className="industry-collaboration-page">

      <header className="industry-collaboration-header">

        <button
          type="button"
          className="collaboration-back"
          onClick={() =>
            navigate("/industry/opportunities")
          }
        >
          <ArrowLeft size={18} />
          Collaboration Opportunities
        </button>

        <span>
          SHORTLISTED UNIVERSITY PROPOSAL
        </span>

        <h1>{proposal.title}</h1>

        <p>
          Proposal #{proposal.id} · RFP #{proposal.rfp_id}
        </p>

      </header>

      <div className="collaboration-detail-layout">

        <section className="collaboration-detail-main">

          <div className="collaboration-detail-card">

            <div className="collaboration-detail-heading">
              <div className="collaboration-detail-icon">
                <FileText size={20} />
              </div>

              <div>
                <span>PROPOSAL STATUS</span>

                <h2>
                  {proposal.status.replaceAll("_", " ")}
                </h2>
              </div>
            </div>

            <div className="collaboration-detail-section">
              <h3>Proposed Solution</h3>
              <p>{proposal.solution}</p>
            </div>

            <div className="collaboration-detail-section">
              <h3>Technical Approach</h3>
              <p>{proposal.technical_approach}</p>
            </div>

            {proposal.research_methodology && (
              <div className="collaboration-detail-section">
                <h3>Research Methodology</h3>
                <p>
                  {proposal.research_methodology}
                </p>
              </div>
            )}

            {proposal.required_resources && (
              <div className="collaboration-detail-section">
                <h3>Required Resources</h3>
                <p>{proposal.required_resources}</p>
              </div>
            )}

            {proposal.faculty_team && (
              <div className="collaboration-detail-section">
                <h3>Faculty / Research Team</h3>
                <p>{proposal.faculty_team}</p>
              </div>
            )}

            {proposal.technology_requirements && (
              <div className="collaboration-detail-section">
                <h3>Technology Requirements</h3>
                <p>
                  {proposal.technology_requirements}
                </p>
              </div>
            )}

            {proposal.expected_outcomes && (
              <div className="collaboration-detail-section">
                <h3>Expected Outcomes</h3>
                <p>{proposal.expected_outcomes}</p>
              </div>
            )}

          </div>

        </section>


        <aside className="collaboration-detail-side">

          <div className="collaboration-detail-card">

            <div className="collaboration-detail-heading">
              <Building2 size={20} />

              <div>
                <h2>Opportunity Snapshot</h2>
                <span>
                  Industry collaboration
                </span>
              </div>
            </div>

            <div className="collaboration-stat">
              <Coins size={18} />

              <div>
                <span>Estimated University Cost</span>

                <strong>
                  {proposal.estimated_cost !== null
                    ? `₹${proposal.estimated_cost.toLocaleString()}`
                    : "Not specified"}
                </strong>
              </div>
            </div>

            <div className="collaboration-stat">
              <Clock3 size={18} />

              <div>
                <span>Expected Timeline</span>

                <strong>
                  {proposal.expected_timeline_days
                    ? `${proposal.expected_timeline_days} days`
                    : "Not specified"}
                </strong>
              </div>
            </div>

            <div className="collaboration-stat">
              <Users size={18} />

              <div>
                <span>University ID</span>

                <strong>
                  #{proposal.university_id}
                </strong>
              </div>
            </div>

            <div className="collaboration-shortlisted">
              <CheckCircle2 size={18} />

              <span>
                This proposal has been shortlisted by
                the government for industry collaboration.
              </span>
            </div>

            <button
              type="button"
              className="collaboration-primary collaboration-submit-opportunity"
              onClick={() =>
                navigate(
                  `/industry/collaborations/new?proposal_id=${proposal.id}`
                )
              }
            >
              <Send size={18} />
              Submit Collaboration Proposal
            </button>

          </div>

        </aside>

      </div>

    </main>
  );
}