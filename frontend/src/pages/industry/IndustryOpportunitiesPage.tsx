import {
  ArrowLeft,
  ChevronRight,
  FileText,
  Loader2,
  Search,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  getShortlistedProposals,
  type UniversityProposal,
} from "../../services/industryCollaborationService";

import "./IndustryOpportunitiesPage.css";

export default function IndustryOpportunitiesPage() {
  const navigate = useNavigate();

  const [proposals, setProposals] = useState<
    UniversityProposal[]
  >([]);

  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const load = async () => {
      try {
        setLoading(true);
        setError("");

        const data =
          await getShortlistedProposals();

        setProposals(data);
      } catch (err: any) {
        setError(
          err?.response?.data?.detail ||
            "Unable to load collaboration opportunities."
        );
      } finally {
        setLoading(false);
      }
    };

    void load();
  }, []);

  const filtered = useMemo(() => {
    const query = search.trim().toLowerCase();

    if (!query) {
      return proposals;
    }

    return proposals.filter(
      (proposal) =>
        proposal.title
          .toLowerCase()
          .includes(query) ||
        proposal.solution
          .toLowerCase()
          .includes(query) ||
        proposal.technical_approach
          .toLowerCase()
          .includes(query)
    );
  }, [proposals, search]);

  if (loading) {
    return (
      <main className="industry-opportunities-page">
        <div className="industry-opportunities-state">
          <Loader2
            size={28}
            className="industry-spin"
          />
          Loading collaboration opportunities...
        </div>
      </main>
    );
  }

  return (
    <main className="industry-opportunities-page">

      <header className="industry-opportunities-header">

        <button
          type="button"
          className="industry-back"
          onClick={() =>
            navigate("/industry/dashboard")
          }
        >
          <ArrowLeft size={18} />
          Dashboard
        </button>

        <span>
          INDUSTRY INNOVATION PORTAL
        </span>

        <h1>
          Collaboration Opportunities
        </h1>

        <p>
          Explore shortlisted university proposals
          and contribute funding, technology, expertise
          and deployment support.
        </p>

      </header>

      {error && (
        <div className="industry-opportunity-error">
          {error}
        </div>
      )}

      <div className="industry-search">
        <Search size={18} />

        <input
          value={search}
          onChange={(event) =>
            setSearch(event.target.value)
          }
          placeholder="Search shortlisted proposals..."
        />
      </div>

      {filtered.length === 0 ? (
        <div className="industry-opportunities-state">
          <FileText size={42} />

          <h2>
            No collaboration opportunities
          </h2>

          <p>
            There are currently no shortlisted university
            proposals available for industry collaboration.
          </p>
        </div>
      ) : (
        <div className="industry-opportunity-list">

          {filtered.map((proposal) => (
            <article
              key={proposal.id}
              className="industry-opportunity-card"
            >
              <div className="industry-opportunity-main">

                <div className="industry-opportunity-icon">
                  <FileText size={21} />
                </div>

                <div>
                  <span>
                    UNIVERSITY PROPOSAL #{proposal.id}
                  </span>

                  <h2>
                    {proposal.title}
                  </h2>

                  <p>
                    {proposal.solution.length > 240
                      ? `${proposal.solution.slice(0, 240)}...`
                      : proposal.solution}
                  </p>
                </div>

              </div>

              <div className="industry-opportunity-meta">

                <div>
                  <span>Estimated Cost</span>
                  <strong>
                    {proposal.estimated_cost !== null
                      ? `₹${proposal.estimated_cost.toLocaleString()}`
                      : "Not specified"}
                  </strong>
                </div>

                <div>
                  <span>Timeline</span>
                  <strong>
                    {proposal.expected_timeline_days
                      ? `${proposal.expected_timeline_days} days`
                      : "Not specified"}
                  </strong>
                </div>

                <div>
                  <span>Status</span>
                  <strong>
                    SHORTLISTED
                  </strong>
                </div>

              </div>

              <div className="industry-opportunity-actions">
                <button
                  type="button"
                  onClick={() =>
                    navigate(
                      `/industry/opportunities/${proposal.id}`
                    )
                  }
                >
                  View Opportunity
                  <ChevronRight size={17} />
                </button>
              </div>
            </article>
          ))}

        </div>
      )}

    </main>
  );
}