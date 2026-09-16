import {
  ArrowLeft,
  CheckCircle2,
  ChevronRight,
  Clock3,
  Coins,
  FileText,
  Loader2,
  Search,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  getAcceptedGovernmentCollaborations,
  type IndustryCollaboration,
} from "../../services/industryCollaborationService";

import "./GovernmentCollaborationPages.css";

export default function GovernmentCollaborationsPage() {
  const navigate = useNavigate();

  const [collaborations, setCollaborations] =
    useState<IndustryCollaboration[]>([]);

  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const loadCollaborations = async () => {
      try {
        setLoading(true);
        setError("");

        const data =
          await getAcceptedGovernmentCollaborations();

        setCollaborations(data);
      } catch (err: any) {
        setError(
          err?.response?.data?.detail ||
            "Unable to load accepted collaborations."
        );
      } finally {
        setLoading(false);
      }
    };

    void loadCollaborations();
  }, []);

  const filtered = useMemo(() => {
    const query = search.trim().toLowerCase();

    if (!query) {
      return collaborations;
    }

    return collaborations.filter(
      (collaboration) =>
        collaboration.title
          .toLowerCase()
          .includes(query) ||
        collaboration.collaboration_description
          .toLowerCase()
          .includes(query)
    );
  }, [collaborations, search]);

  if (loading) {
    return (
      <main className="government-collaborations-page">
        <div className="government-collaborations-state">
          <Loader2
            size={28}
            className="government-collaboration-spin"
          />
          Loading accepted collaborations...
        </div>
      </main>
    );
  }

  return (
    <main className="government-collaborations-page">

      <header className="government-collaborations-header">

        <button
          type="button"
          className="government-collaborations-back"
          onClick={() =>
            navigate("/government/dashboard")
          }
        >
          <ArrowLeft size={18} />
          Dashboard
        </button>

        <span>
          PROJECT INITIATION
        </span>

        <h1>
          Accepted Collaborations
        </h1>

        <p>
          Convert approved university-industry
          partnerships into executable government projects.
        </p>

      </header>

      {error && (
        <div className="government-collaboration-error">
          {error}
        </div>
      )}

      <div className="government-collaboration-toolbar">

        <div className="government-collaboration-search">
          <Search size={18} />

          <input
            value={search}
            onChange={(event) =>
              setSearch(event.target.value)
            }
            placeholder="Search accepted collaborations..."
          />
        </div>

        <strong>
          {collaborations.length} accepted
        </strong>

      </div>

      {filtered.length === 0 ? (
        <div className="government-collaborations-state">

          <CheckCircle2 size={42} />

          <h2>
            No accepted collaborations
          </h2>

          <p>
            No university-industry collaboration has
            been accepted yet.
          </p>

        </div>
      ) : (
        <div className="government-collaboration-list">

          {filtered.map((collaboration) => (
            <article
              key={collaboration.id}
              className="government-collaboration-card"
            >

              <div className="government-collaboration-main">

                <div className="government-collaboration-icon">
                  <FileText size={21} />
                </div>

                <div>

                  <span>
                    COLLABORATION #{collaboration.id}
                  </span>

                  <h2>
                    {collaboration.title}
                  </h2>

                  <p>
                    {collaboration.collaboration_description.length >
                    240
                      ? `${collaboration.collaboration_description.slice(
                          0,
                          240
                        )}...`
                      : collaboration.collaboration_description}
                  </p>

                </div>

              </div>

              <div className="government-collaboration-meta">

                <div>
                  <span>Status</span>

                  <strong className="accepted">
                    <CheckCircle2 size={15} />
                    ACCEPTED
                  </strong>
                </div>

                <div>
                  <span>Funding</span>

                  <strong>
                    <Coins size={15} />

                    {collaboration.funding_amount !== null
                      ? `₹${collaboration.funding_amount.toLocaleString()}`
                      : "Not specified"}
                  </strong>
                </div>

                <div>
                  <span>Duration</span>

                  <strong>
                    <Clock3 size={15} />

                    {collaboration.proposed_duration_days
                      ? `${collaboration.proposed_duration_days} days`
                      : "Not specified"}
                  </strong>
                </div>

              </div>

              <div className="government-collaboration-actions">

                <button
                  type="button"
                  onClick={() =>
                    navigate(
                      `/government/collaborations/${collaboration.id}`
                    )
                  }
                >
                  View Collaboration
                  <ChevronRight size={17} />
                </button>

                <button
                  type="button"
                  className="government-project-button"
                  onClick={() =>
                    navigate(
                      `/government/projects/new?collaboration_id=${collaboration.id}`
                    )
                  }
                >
                  Create Project
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