import {
  ArrowLeft,
  CheckCircle2,
  ChevronRight,
  Clock3,
  Coins,
  FileText,
  Loader2,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  getUniversityCollaborations,
  type IndustryCollaboration,
} from "../../services/industryCollaborationService";

import "./UniversityCollaborationPages.css";

export default function UniversityCollaborationsPage() {
  const navigate = useNavigate();

  const [collaborations, setCollaborations] =
    useState<IndustryCollaboration[]>([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");

  useEffect(() => {
    const loadCollaborations = async () => {
      try {
        setLoading(true);
        setError("");

        const data =
          await getUniversityCollaborations();

        setCollaborations(data);
      } catch (err: any) {
        setError(
          err?.response?.data?.detail ||
            "Unable to load industry collaborations."
        );
      } finally {
        setLoading(false);
      }
    };

    void loadCollaborations();
  }, []);

  const filteredCollaborations = useMemo(() => {
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

  const getStatusClass = (
    status: IndustryCollaboration["status"]
  ) => {
    switch (status) {
      case "ACCEPTED":
        return "university-collaboration-status accepted";

      case "REJECTED":
        return "university-collaboration-status rejected";

      case "MODIFICATION_REQUESTED":
        return "university-collaboration-status modification";

      case "UNDER_REVIEW":
        return "university-collaboration-status review";

      default:
        return "university-collaboration-status submitted";
    }
  };

  if (loading) {
    return (
      <main className="university-collaborations-page">
        <div className="university-collaborations-state">
          <Loader2
            size={28}
            className="university-collaboration-spin"
          />
          Loading industry collaborations...
        </div>
      </main>
    );
  }

  return (
    <main className="university-collaborations-page">

      <header className="university-collaborations-header">

        <button
          type="button"
          className="university-collaborations-back"
          onClick={() =>
            navigate("/university/dashboard")
          }
        >
          <ArrowLeft size={18} />
          Dashboard
        </button>

        <span>
          UNIVERSITY INDUSTRY COLLABORATION
        </span>

        <h1>Industry Collaborations</h1>

        <p>
          Review funding, technical expertise,
          deployment and commercialization support
          proposed by industry partners.
        </p>

      </header>

      {error && (
        <div className="university-collaboration-error">
          {error}
        </div>
      )}

      <div className="university-collaboration-toolbar">

        <input
          value={search}
          onChange={(event) =>
            setSearch(event.target.value)
          }
          placeholder="Search collaborations..."
        />

        <strong>
          {collaborations.length} collaboration
          {collaborations.length === 1
            ? ""
            : "s"}
        </strong>

      </div>

      {filteredCollaborations.length === 0 ? (
        <div className="university-collaborations-state">

          <FileText size={42} />

          <h2>No collaborations found</h2>

          <p>
            {collaborations.length === 0
              ? "No industry collaboration proposals have been received yet."
              : "No collaborations match your search."}
          </p>

        </div>
      ) : (
        <div className="university-collaboration-list">

          {filteredCollaborations.map(
            (collaboration) => (
              <article
                key={collaboration.id}
                className="university-collaboration-card"
              >

                <div className="university-collaboration-card-main">

                  <div className="university-collaboration-icon">
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
                      {collaboration
                        .collaboration_description
                        .length > 230
                        ? `${collaboration.collaboration_description.slice(
                            0,
                            230
                          )}...`
                        : collaboration.collaboration_description}
                    </p>
                  </div>

                </div>

                <div className="university-collaboration-meta">

                  <div>
                    <span>Status</span>

                    <strong
                      className={getStatusClass(
                        collaboration.status
                      )}
                    >
                      {collaboration.status.replaceAll(
                        "_",
                        " "
                      )}
                    </strong>
                  </div>

                  <div>
                    <span>Funding</span>

                    <strong>
                      <Coins size={15} />

                      {collaboration.funding_amount !==
                      null
                        ? `₹${collaboration.funding_amount.toLocaleString()}`
                        : "Not specified"}
                    </strong>
                  </div>

                  <div>
                    <span>Duration</span>

                    <strong>
                      <Clock3 size={15} />

                      {collaboration
                        .proposed_duration_days
                        ? `${collaboration.proposed_duration_days} days`
                        : "Not specified"}
                    </strong>
                  </div>

                </div>

                {collaboration.status ===
                  "ACCEPTED" && (
                  <div className="university-collaboration-confirmed">
                    <CheckCircle2 size={17} />

                    Collaboration accepted.
                    The project can now move to
                    government project creation.
                  </div>
                )}

                <div className="university-collaboration-card-actions">

                  <button
                    type="button"
                    onClick={() =>
                      navigate(
                        `/university/collaborations/${collaboration.id}`
                      )
                    }
                  >
                    Review Collaboration
                    <ChevronRight size={17} />
                  </button>

                </div>

              </article>
            )
          )}

        </div>
      )}

    </main>
  );
}