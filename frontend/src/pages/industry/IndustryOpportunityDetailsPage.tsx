import {
  ArrowLeft,
  BookOpen,
  Building2,
  Calendar,
  CheckCircle2,
  Clock3,
  Coins,
  FileText,
  Loader2,
  Send,
  Target,
  Users,
} from "lucide-react";
import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import {
  getProposalWithRfp,
  type ProposalWithRfp,
} from "../../services/industryCollaborationService";

import "./IndustryCollaborationPages.css";


export default function IndustryOpportunityDetailsPage() {
  const { proposalId } = useParams<{
    proposalId: string;
  }>();

  const navigate = useNavigate();

  const [data, setData] =
    useState<ProposalWithRfp | null>(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");


  useEffect(() => {
    const load = async () => {
      if (!proposalId) {
        setError("Invalid proposal ID.");
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError("");

        const result = await getProposalWithRfp(
          Number(proposalId)
        );

        // Guard: must be shortlisted
        if (result.proposal.status !== "SHORTLISTED") {
          setError(
            "This proposal is not currently shortlisted for industry collaboration."
          );
          return;
        }

        setData(result);
      } catch (err: any) {
        setError(
          err?.response?.data?.detail ||
            "Unable to load collaboration opportunity."
        );
      } finally {
        setLoading(false);
      }
    };

    void load();
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


  if (error || !data) {
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


  const { proposal, rfp } = data;


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


      {/* =====================================================
          RFP OVERVIEW CARD  (what the government issued)
      ===================================================== */}

      <div className="collaboration-rfp-banner">
        <div className="collaboration-rfp-banner-header">
          <div className="collaboration-rfp-banner-icon">
            <BookOpen size={20} />
          </div>

          <div>
            <span>GOVERNMENT REQUEST FOR PROPOSAL</span>
            <h2>{rfp.title}</h2>
          </div>
        </div>

        {rfp.description && (
          <p className="collaboration-rfp-description">
            {rfp.description}
          </p>
        )}

        {rfp.objectives && (
          <div className="collaboration-rfp-section">
            <Target size={16} />
            <div>
              <strong>Objectives</strong>
              <p>{rfp.objectives}</p>
            </div>
          </div>
        )}

        {rfp.technical_requirements && (
          <div className="collaboration-rfp-section">
            <FileText size={16} />
            <div>
              <strong>Technical Requirements</strong>
              <p>{rfp.technical_requirements}</p>
            </div>
          </div>
        )}

        {rfp.expected_outcomes && (
          <div className="collaboration-rfp-section">
            <CheckCircle2 size={16} />
            <div>
              <strong>Expected Outcomes</strong>
              <p>{rfp.expected_outcomes}</p>
            </div>
          </div>
        )}

        <div className="collaboration-rfp-meta">

          <div className="collaboration-rfp-meta-item">
            <Coins size={16} />
            <div>
              <span>Estimated Budget</span>
              <strong>
                {rfp.estimated_budget !== null
                  ? `₹${rfp.estimated_budget.toLocaleString()}`
                  : "Not specified"}
              </strong>
            </div>
          </div>

          <div className="collaboration-rfp-meta-item">
            <Clock3 size={16} />
            <div>
              <span>Duration</span>
              <strong>
                {rfp.expected_duration_days
                  ? `${rfp.expected_duration_days} days`
                  : "Not specified"}
              </strong>
            </div>
          </div>

          <div className="collaboration-rfp-meta-item">
            <Calendar size={16} />
            <div>
              <span>Proposal Deadline</span>
              <strong>
                {rfp.proposal_deadline
                  ? new Date(
                      rfp.proposal_deadline
                    ).toLocaleDateString("en-IN", {
                      day: "numeric",
                      month: "long",
                      year: "numeric",
                    })
                  : "Not specified"}
              </strong>
            </div>
          </div>

          <div className="collaboration-rfp-meta-item">
            <span
              className={`collaboration-rfp-status collaboration-rfp-status-${rfp.status.toLowerCase()}`}
            >
              {rfp.status}
            </span>
          </div>

        </div>
      </div>


      {/* =====================================================
          PROPOSAL + SIDEBAR LAYOUT
      ===================================================== */}

      <div className="collaboration-detail-layout">

        {/* === MAIN: University Proposal === */}
        <section className="collaboration-detail-main">

          <div className="collaboration-detail-card">

            <div className="collaboration-detail-heading">
              <div className="collaboration-detail-icon">
                <FileText size={20} />
              </div>

              <div>
                <span>UNIVERSITY PROPOSAL</span>

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


        {/* === SIDEBAR: Snapshot + CTA === */}
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
                <span>University Cost Estimate</span>

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