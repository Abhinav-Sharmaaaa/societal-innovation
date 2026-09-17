import {
  ArrowLeft,
  ArrowRight,
  FileText,
  Handshake,
  Loader2,
  Search,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  getMyIndustryCollaborations,
  type IndustryCollaboration,
  type IndustryCollaborationStatus,
} from "../../services/industryCollaborationService";

import "./IndustryMyCollaborationsPage.css";


const STATUS_LABELS: Record<
  IndustryCollaborationStatus,
  string
> = {
  DRAFT: "Draft",
  SUBMITTED: "Submitted",
  UNDER_REVIEW: "Under Review",
  MODIFICATION_REQUESTED: "Modification Requested",
  ACCEPTED: "Accepted",
  REJECTED: "Rejected",
  WITHDRAWN: "Withdrawn",
};


export default function IndustryMyCollaborationsPage() {
  const navigate = useNavigate();

  const [collaborations, setCollaborations] = useState<
    IndustryCollaboration[]
  >([]);

  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");


  useEffect(() => {
    const load = async () => {
      try {
        setLoading(true);
        setError("");

        const data = await getMyIndustryCollaborations();
        setCollaborations(data);
      } catch (err: any) {
        setError(
          err?.response?.data?.detail ||
            "Unable to load your collaboration proposals."
        );
      } finally {
        setLoading(false);
      }
    };

    void load();
  }, []);


  const filtered = useMemo(() => {
    const query = search.trim().toLowerCase();
    if (!query) return collaborations;

    return collaborations.filter(
      (c) =>
        c.title.toLowerCase().includes(query) ||
        c.collaboration_description
          .toLowerCase()
          .includes(query)
    );
  }, [collaborations, search]);


  if (loading) {
    return (
      <main className="my-collab-page">
        <div className="my-collab-state">
          <Loader2 size={28} className="my-collab-spin" />
          Loading your collaborations...
        </div>
      </main>
    );
  }


  return (
    <main className="my-collab-page">

      <header className="my-collab-header">

        <button
          type="button"
          className="my-collab-back"
          onClick={() => navigate("/industry/dashboard")}
        >
          <ArrowLeft size={18} />
          Dashboard
        </button>

        <span>INDUSTRY COLLABORATION PORTAL</span>

        <h1>My Collaboration Proposals</h1>

        <p>
          All collaboration proposals you have submitted to
          shortlisted university projects.
        </p>

      </header>


      {error && (
        <div className="my-collab-error">{error}</div>
      )}


      <div className="my-collab-toolbar">
        <div className="my-collab-search">
          <Search size={17} />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search collaborations..."
          />
        </div>

        <button
          type="button"
          className="my-collab-new-btn"
          onClick={() => navigate("/industry/opportunities")}
        >
          <Handshake size={17} />
          Browse Opportunities
        </button>
      </div>


      {filtered.length === 0 ? (
        <div className="my-collab-state">
          <FileText size={46} />

          <h2>
            {collaborations.length === 0
              ? "No collaborations yet"
              : "No matching collaborations"}
          </h2>

          <p>
            {collaborations.length === 0
              ? "Browse shortlisted university proposals and submit your first collaboration offer."
              : "Try a different search term."}
          </p>

          {collaborations.length === 0 && (
            <button
              type="button"
              className="my-collab-primary"
              onClick={() =>
                navigate("/industry/opportunities")
              }
            >
              <Handshake size={17} />
              Browse Opportunities
            </button>
          )}
        </div>
      ) : (
        <div className="my-collab-list">
          {filtered.map((collab) => (
            <CollaborationRow
              key={collab.id}
              collab={collab}
              onClick={() =>
                navigate(
                  `/industry/collaborations/${collab.id}`
                )
              }
            />
          ))}
        </div>
      )}

    </main>
  );
}


/* ============================================================
   ROW COMPONENT
============================================================ */

function CollaborationRow({
  collab,
  onClick,
}: {
  collab: IndustryCollaboration;
  onClick: () => void;
}) {
  return (
    <article
      className="my-collab-row"
      onClick={onClick}
      role="button"
      tabIndex={0}
      onKeyDown={(e) =>
        (e.key === "Enter" || e.key === " ") && onClick()
      }
    >
      <div className="my-collab-row-icon">
        <Handshake size={20} />
      </div>

      <div className="my-collab-row-body">
        <span>
          COLLABORATION #{collab.id} · Proposal #
          {collab.university_proposal_id}
        </span>

        <h2>{collab.title}</h2>

        <p>
          {collab.collaboration_description.length > 180
            ? `${collab.collaboration_description.slice(
                0,
                180
              )}…`
            : collab.collaboration_description}
        </p>

        <div className="my-collab-row-meta">
          {collab.funding_amount !== null && (
            <span className="my-collab-meta-chip">
              ₹{collab.funding_amount.toLocaleString()}{" "}
              Funding
            </span>
          )}

          {collab.proposed_duration_days && (
            <span className="my-collab-meta-chip">
              {collab.proposed_duration_days} days
            </span>
          )}

          <span
            className={`my-collab-status my-collab-status-${collab.status.toLowerCase()}`}
          >
            {STATUS_LABELS[collab.status] ?? collab.status}
          </span>
        </div>
      </div>

      <div className="my-collab-row-arrow">
        <ArrowRight size={18} />
      </div>
    </article>
  );
}
