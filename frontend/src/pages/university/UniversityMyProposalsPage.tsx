import {
  ArrowRight,
  CheckCircle2,
  Clock3,
  FileText,
  IndianRupee,
  Loader2,
  PlusCircle,
  XCircle,
} from "lucide-react";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  getMyProposals,
  type UniversityProposal,
} from "../../services/universityProposalService";

import "./UniversityProposalPages.css";
import "./UniversityMyProposalsPage.css";

// ============================================================
// Status helpers
// ============================================================

function statusMeta(status: string): {
  label: string;
  cls: string;
  icon: React.ReactNode;
} {
  switch (status) {
    case "SUBMITTED":
      return { label: "Submitted", cls: "mps-submitted", icon: <Clock3 size={13} /> };
    case "UNDER_EVALUATION":
      return { label: "Under Evaluation", cls: "mps-evaluating", icon: <Loader2 size={13} /> };
    case "SHORTLISTED":
      return { label: "Shortlisted", cls: "mps-shortlisted", icon: <CheckCircle2 size={13} /> };
    case "REJECTED":
      return { label: "Rejected", cls: "mps-rejected", icon: <XCircle size={13} /> };
    case "WITHDRAWN":
      return { label: "Withdrawn", cls: "mps-withdrawn", icon: <XCircle size={13} /> };
    default:
      return { label: status, cls: "mps-draft", icon: <FileText size={13} /> };
  }
}


// ============================================================
// Component
// ============================================================

export default function UniversityMyProposalsPage() {
  const navigate = useNavigate();

  const [proposals, setProposals] = useState<UniversityProposal[]>([]);
  const [loading, setLoading]     = useState(true);
  const [error, setError]         = useState("");

  useEffect(() => {
    async function load() {
      try {
        setLoading(true);
        const data = await getMyProposals();
        setProposals(data);
      } catch (err: any) {
        setError(
          err?.response?.data?.detail ||
            "Unable to load your proposals."
        );
      } finally {
        setLoading(false);
      }
    }

    void load();
  }, []);


  // ----------------------------------------------------------
  // Loading
  // ----------------------------------------------------------

  if (loading) {
    return (
      <div className="mpp-page">
        <div className="mpp-loading">
          <Loader2 size={28} className="mpp-spin" />
          <span>Loading your proposals…</span>
        </div>
      </div>
    );
  }


  // ----------------------------------------------------------
  // Error
  // ----------------------------------------------------------

  if (error) {
    return (
      <div className="mpp-page">
        <div className="mpp-error">
          <XCircle size={24} />
          <p>{error}</p>
          <button onClick={() => window.location.reload()}>
            Retry
          </button>
        </div>
      </div>
    );
  }


  // ----------------------------------------------------------
  // Render
  // ----------------------------------------------------------

  return (
    <div className="mpp-page">

      {/* Header */}
      <div className="mpp-header">
        <div>
          <span className="mpp-eyebrow">UNIVERSITY PORTAL</span>
          <h1>My Submitted Proposals</h1>
          <p>
            Track the status of all proposals your university has
            submitted in response to government RFPs.
          </p>
        </div>

        <button
          className="mpp-new-btn"
          onClick={() => navigate("/university/invitations")}
        >
          <PlusCircle size={16} />
          Submit New Proposal
        </button>
      </div>


      {/* Empty State */}
      {proposals.length === 0 ? (

        <div className="mpp-empty">
          <FileText size={40} strokeWidth={1.2} />
          <h2>No proposals yet</h2>
          <p>
            Express interest in an RFP invitation to unlock the
            proposal submission form.
          </p>
          <button
            className="mpp-empty-cta"
            onClick={() => navigate("/university/invitations")}
          >
            View RFP Invitations
            <ArrowRight size={15} />
          </button>
        </div>

      ) : (

        <div className="mpp-list">
          {proposals.map((proposal) => {
            const meta = statusMeta(proposal.status);

            return (
              <div
                key={proposal.id}
                className={`mpp-card mpp-card--${proposal.status.toLowerCase()}`}
              >

                <div className="mpp-card-body">

                  {/* Left */}
                  <div className="mpp-card-left">
                    <div className="mpp-card-badges">
                      <span className={`mpp-status ${meta.cls}`}>
                        {meta.icon}
                        {meta.label}
                      </span>
                      <span className="mpp-rfp-ref">
                        RFP #{proposal.rfp_id}
                      </span>
                    </div>

                    <h2 className="mpp-card-title">
                      {proposal.title}
                    </h2>

                    <p className="mpp-card-solution">
                      {proposal.solution.length > 160
                        ? proposal.solution.slice(0, 160) + "…"
                        : proposal.solution}
                    </p>

                    <div className="mpp-card-meta">
                      {proposal.estimated_cost != null && (
                        <span>
                          <IndianRupee size={12} />
                          ₹{proposal.estimated_cost.toLocaleString()}
                        </span>
                      )}
                      {proposal.expected_timeline_days != null && (
                        <span>
                          <Clock3 size={12} />
                          {proposal.expected_timeline_days} days
                        </span>
                      )}
                      {proposal.submitted_at && (
                        <span>
                          <FileText size={12} />
                          Submitted{" "}
                          {new Date(proposal.submitted_at).toLocaleDateString(
                            "en-IN",
                            { day: "numeric", month: "short", year: "numeric" }
                          )}
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Right */}
                  <div className="mpp-card-right">
                    <button
                      className="mpp-view-btn"
                      onClick={() =>
                        navigate(`/university/proposals/${proposal.id}`)
                      }
                    >
                      View Details
                      <ArrowRight size={15} />
                    </button>
                  </div>

                </div>

              </div>
            );
          })}
        </div>

      )}

    </div>
  );
}
