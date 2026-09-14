import {
  ArrowLeft,
  CheckCircle2,
  ChevronRight,
  Loader2,
  RefreshCw,
  Send,
  Sparkles,
} from "lucide-react";
import {
  useEffect,
  useMemo,
  useState,
} from "react";
import {
  useNavigate,
  useParams,
} from "react-router-dom";

import {
  innovationService,
  type RFP,
} from "../../services/innovationService";

import {
  universityMatchingService,
  type RFPInvitation,
  type UniversityMatchRecommendation,
  type UniversityMatchingResponse,
} from "../../services/universityMatchingService";

import "./RFPUniversityMatchingPage.css";


export default function RFPUniversityMatchingPage() {
  const navigate = useNavigate();
  const { id } = useParams();

  const rfpId = Number(id);

  const [rfp, setRfp] =
    useState<RFP | null>(null);

  const [matching, setMatching] =
    useState<UniversityMatchingResponse | null>(
      null,
    );

  const [invitations, setInvitations] =
    useState<RFPInvitation[]>([]);

  const [selectedUniversityIds, setSelectedUniversityIds] =
    useState<number[]>([]);

  const [loading, setLoading] =
    useState(true);

  const [matchingLoading, setMatchingLoading] =
    useState(false);

  const [invitationLoading, setInvitationLoading] =
    useState(false);

  const [error, setError] =
    useState("");

  const [message, setMessage] =
    useState("");


  async function loadData() {
    try {
      setLoading(true);
      setError("");

      const [
        rfpData,
        invitationData,
      ] = await Promise.all([
        innovationService.getRFP(rfpId),
        universityMatchingService.getRFPInvitations(
          rfpId,
        ),
      ]);

      setRfp(rfpData);
      setInvitations(invitationData);

    } catch (err: any) {
      console.error(err);

      setError(
        err.response?.data?.detail ||
          "Unable to load RFP matching data.",
      );
    } finally {
      setLoading(false);
    }
  }


  useEffect(() => {
    if (!Number.isFinite(rfpId)) {
      setError("Invalid RFP ID.");
      setLoading(false);
      return;
    }

    loadData();
  }, [rfpId]);


  async function handleMatchUniversities() {
    try {
      setMatchingLoading(true);
      setError("");
      setMessage("");

      const result =
        await universityMatchingService.matchUniversities(
          rfpId,
        );

      setMatching(result);

      setSelectedUniversityIds([]);

      setMessage(
        `${result.recommendations.length} university recommendations generated.`,
      );

    } catch (err: any) {
      console.error(err);

      setError(
        err.response?.data?.detail ||
          "Unable to generate university recommendations.",
      );
    } finally {
      setMatchingLoading(false);
    }
  }


  function toggleUniversity(
    universityId: number,
  ) {
    setSelectedUniversityIds(
      (current) =>
        current.includes(universityId)
          ? current.filter(
              (id) => id !== universityId,
            )
          : [...current, universityId],
    );
  }


  async function handleSendInvitations() {
    if (
      selectedUniversityIds.length === 0
    ) {
      setError(
        "Select at least one university.",
      );
      return;
    }

    if (!matching) {
      setError(
        "Generate university recommendations first.",
      );
      return;
    }


    try {
      setInvitationLoading(true);
      setError("");
      setMessage("");

      const results =
        await Promise.all(
          selectedUniversityIds.map(
            (universityId) =>
              universityMatchingService.sendInvitation(
                {
                  rfp_id: rfpId,
                  university_id:
                    universityId,
                },
              ),
          ),
        );


      setInvitations(
        (current) => [
          ...current,
          ...results,
        ],
      );

      setSelectedUniversityIds([]);

      setMessage(
        `${results.length} university invitation${
          results.length > 1
            ? "s"
            : ""
        } sent successfully.`,
      );

    } catch (err: any) {
      console.error(err);

      setError(
        err.response?.data?.detail ||
          "Unable to send university invitation.",
      );
    } finally {
      setInvitationLoading(false);
    }
  }


  const invitedUniversityIds = useMemo(
    () =>
      new Set(
        invitations.map(
          (invitation) =>
            invitation.university_id,
        ),
      ),
    [invitations],
  );


  const availableRecommendations =
    matching?.recommendations.filter(
      (recommendation) =>
        !invitedUniversityIds.has(
          recommendation.organization_id,
        ),
    ) ?? [];


  if (loading) {
    return (
      <main className="matching-page">
        <div className="matching-loading">
          <Loader2
            size={20}
            className="matching-spin"
          />

          Loading RFP...
        </div>
      </main>
    );
  }


  if (!rfp) {
    return (
      <main className="matching-page">

        <div className="matching-error-page">

          <strong>
            RFP unavailable
          </strong>

          <p>
            {error ||
              "The requested RFP could not be found."}
          </p>

          <button
            onClick={() =>
              navigate(
                "/government/dashboard",
              )
            }
          >
            Dashboard
          </button>

        </div>

      </main>
    );
  }


  return (
    <main className="matching-page">

      {/* =====================================================
          HEADER
      ===================================================== */}

      <header className="matching-header">

        <div className="matching-header-top">

          <button
            className="matching-back"
            onClick={() =>
              navigate(
                `/government/rfps/${rfp.id}`,
              )
            }
          >
            <ArrowLeft size={16} />
            Back to RFP
          </button>

          <button
            className="matching-refresh"
            onClick={loadData}
            disabled={
              matchingLoading ||
              invitationLoading
            }
          >
            <RefreshCw size={15} />
            Refresh
          </button>

        </div>


        <span className="matching-eyebrow">
          UNIVERSITY MATCHING
        </span>

        <h1>
          Select University Partners
        </h1>

        <p>
          {rfp.title}
        </p>

      </header>


      <div className="matching-container">

        {/* ===================================================
            STATUS
        =================================================== */}

        {error && (
          <div className="matching-alert matching-alert-error">
            {error}
          </div>
        )}


        {message && (
          <div className="matching-alert matching-alert-success">
            <CheckCircle2 size={16} />
            {message}
          </div>
        )}


        {/* ===================================================
            RFP SUMMARY
        =================================================== */}

        <section className="matching-summary">

          <div className="matching-summary-main">

            <div className="matching-summary-icon">
              <Sparkles size={22} />
            </div>

            <div>

              <span>
                RFP #{rfp.id}
              </span>

              <strong>
                {formatValue(rfp.status)}
              </strong>

            </div>

          </div>


          <div className="matching-summary-stats">

            <SummaryItem
              label="Candidates Evaluated"
              value={
                matching?.total_candidates_evaluated ??
                "—"
              }
            />

            <SummaryItem
              label="Recommendations"
              value={
                matching?.recommendations
                  .length ?? "—"
              }
            />

            <SummaryItem
              label="Invitations Sent"
              value={invitations.length}
            />

            <SummaryItem
              label="Selected"
              value={
                selectedUniversityIds.length
              }
            />

          </div>

        </section>


        {/* ===================================================
            MATCH ACTION
        =================================================== */}

        <section className="matching-action-card">

          <div>

            <div className="matching-action-title">

              <Sparkles size={18} />

              <strong>
                Generate AI University Recommendations
              </strong>

            </div>

            <p>
              The matching engine evaluates university
              competencies, capabilities, text relevance,
              and location. The government retains final
              authority over invitations.
            </p>

          </div>


          <button
            className="matching-primary-button"
            onClick={
              handleMatchUniversities
            }
            disabled={
              matchingLoading ||
              invitationLoading
            }
          >

            {matchingLoading ? (
              <Loader2
                size={16}
                className="matching-spin"
              />
            ) : (
              <Sparkles size={16} />
            )}

            {matching
              ? "Regenerate Recommendations"
              : "Match Universities"}

          </button>

        </section>


        {/* ===================================================
            RECOMMENDATIONS
        =================================================== */}

        {matching && (
          <section className="recommendation-section">

            <div className="section-heading">

              <div>

                <h2>
                  Recommended Universities
                </h2>

                <span>
                  Top-ranked matches generated by
                  the matching engine
                </span>

              </div>

              {selectedUniversityIds.length >
                0 && (
                <button
                  className="matching-invite-button"
                  onClick={
                    handleSendInvitations
                  }
                  disabled={
                    invitationLoading
                  }
                >
                  {invitationLoading ? (
                    <Loader2
                      size={15}
                      className="matching-spin"
                    />
                  ) : (
                    <Send size={15} />
                  )}

                  Invite{" "}
                  {selectedUniversityIds.length}
                  {" "}
                  University
                  {selectedUniversityIds.length >
                  1
                    ? "ies"
                    : ""}
                </button>
              )}

            </div>


            <div className="recommendation-grid">

              {availableRecommendations.length ===
              0 ? (

                <div className="matching-empty">
                  All recommended universities have
                  already been invited.
                </div>

              ) : (

                availableRecommendations.map(
                  (recommendation) => (

                    <UniversityCard
                      key={
                        recommendation.organization_id
                      }
                      recommendation={
                        recommendation
                      }
                      selected={selectedUniversityIds.includes(
                        recommendation.organization_id,
                      )}
                      onSelect={() =>
                        toggleUniversity(
                          recommendation.organization_id,
                        )
                      }
                    />

                  ),
                )
              )}

            </div>

          </section>
        )}


        {/* ===================================================
            INVITATIONS
        =================================================== */}

        <section className="invitation-section">

          <div className="section-heading">

            <div>

              <h2>
                Invitation History
              </h2>

              <span>
                Universities already invited to this RFP
              </span>

            </div>

          </div>


          {invitations.length === 0 ? (

            <div className="matching-empty">
              No invitations have been sent yet.
            </div>

          ) : (

            <div className="invitation-table-wrapper">

              <table className="invitation-table">

                <thead>
                  <tr>
                    <th>University</th>
                    <th>Rank</th>
                    <th>Match Score</th>
                    <th>Status</th>
                    <th>Invited</th>
                  </tr>
                </thead>

                <tbody>

                  {invitations.map(
                    (invitation) => (

                      <tr
                        key={
                          invitation.id
                        }
                      >

                        <td>
                          University #
                          {
                            invitation.university_id
                          }
                        </td>

                        <td>
                          {invitation.recommendation_rank ??
                            "—"}
                        </td>

                        <td>
                          {invitation.match_score !=
                          null
                            ? invitation.match_score.toFixed(
                                1,
                              )
                            : "—"}
                        </td>

                        <td>
                          <InvitationStatus
                            status={
                              invitation.status
                            }
                          />
                        </td>

                        <td>
                          {formatDate(
                            invitation.invited_at,
                          )}
                        </td>

                      </tr>

                    ),
                  )}

                </tbody>

              </table>

            </div>

          )}

        </section>

      </div>

    </main>
  );
}


/* ============================================================
   UNIVERSITY CARD
============================================================ */

function UniversityCard({
  recommendation,
  selected,
  onSelect,
}: {
  recommendation:
    UniversityMatchRecommendation;

  selected: boolean;

  onSelect: () => void;
}) {
  return (
    <button
      type="button"
      className={`university-match-card ${
        selected
          ? "selected"
          : ""
      }`}
      onClick={onSelect}
    >

      <div className="university-card-top">

        <div className="rank-badge">
          #{recommendation.rank}
        </div>

        <div className="university-card-title">

          <strong>
            {recommendation.organization_name}
          </strong>

          <span>
            University / HEI
          </span>

        </div>

        <div className="match-score">

          <strong>
            {recommendation.score.toFixed(1)}
          </strong>

          <span>
            Match
          </span>

        </div>

      </div>


      <div className="score-bars">

        <ScoreBar
          label="Competency"
          value={
            recommendation.competency_match_score
          }
        />

        <ScoreBar
          label="Capability"
          value={
            recommendation.capability_match_score
          }
        />

        <ScoreBar
          label="Relevance"
          value={
            recommendation.text_relevance_score
          }
        />

        <ScoreBar
          label="Location"
          value={
            recommendation.location_score
          }
        />

      </div>


      <div className="matched-section">

        <div className="matched-heading">
          <CheckCircle2 size={14} />
          Matched competencies
        </div>

        <div className="tag-list">

          {recommendation.matched_competencies
            .length > 0 ? (
            recommendation.matched_competencies.map(
              (item) => (
                <span key={item}>
                  {item}
                </span>
              ),
            )
          ) : (
            <small>
              None identified
            </small>
          )}

        </div>

      </div>


      <div className="matched-section">

        <div className="matched-heading">
          <CheckCircle2 size={14} />
          Matched capabilities
        </div>

        <div className="tag-list">

          {recommendation.matched_capabilities
            .length > 0 ? (
            recommendation.matched_capabilities.map(
              (item) => (
                <span key={item}>
                  {item}
                </span>
              ),
            )
          ) : (
            <small>
              None identified
            </small>
          )}

        </div>

      </div>


      <div className="university-explanation">

        <span>
          Why this university?
        </span>

        <p>
          {recommendation.explanation}
        </p>

      </div>


      <div className="university-card-footer">

        <span>
          {selected
            ? "Selected for invitation"
            : "Click to select"}
        </span>

        <ChevronRight size={16} />

      </div>

    </button>
  );
}


/* ============================================================
   SCORE BAR
============================================================ */

function ScoreBar({
  label,
  value,
}: {
  label: string;
  value: number;
}) {
  return (
    <div className="score-bar-row">

      <div className="score-bar-label">

        <span>
          {label}
        </span>

        <strong>
          {value.toFixed(0)}%
        </strong>

      </div>

      <div className="score-bar-track">

        <div
          className="score-bar-fill"
          style={{
            width: `${Math.min(
              Math.max(value, 0),
              100,
            )}%`,
          }}
        />

      </div>

    </div>
  );
}


/* ============================================================
   SUMMARY
============================================================ */

function SummaryItem({
  label,
  value,
}: {
  label: string;
  value: number | string;
}) {
  return (
    <div className="summary-item">

      <span>
        {label}
      </span>

      <strong>
        {value}
      </strong>

    </div>
  );
}


/* ============================================================
   INVITATION STATUS
============================================================ */

function InvitationStatus({
  status,
}: {
  status: string;
}) {
  return (
    <span
      className={`invitation-status invitation-status-${status.toLowerCase()}`}
    >
      {formatValue(status)}
    </span>
  );
}


/* ============================================================
   HELPERS
============================================================ */

function formatValue(
  value: string,
) {
  return value
    .replaceAll("_", " ")
    .replace(
      /\b\w/g,
      (character) =>
        character.toUpperCase(),
    );
}


function formatDate(
  value: string,
) {
  return new Date(value).toLocaleString(
    "en-IN",
    {
      dateStyle: "medium",
      timeStyle: "short",
    },
  );
}