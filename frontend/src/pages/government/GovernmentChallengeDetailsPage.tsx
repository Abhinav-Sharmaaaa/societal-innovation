import {
  AlertCircle,
  ArrowLeft,
  ArrowUpRight,
  CheckCircle2,
  FileText,
  GitBranch,
  Lightbulb,
  MapPin,
  RefreshCw,
  ShieldCheck,
  Sparkles,
  UserCheck,
  Users,
} from "lucide-react";
import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import {
  challengeService,
  type AssignmentHistoryItem,
  type Challenge,
  type ReviewHistoryItem,
  type RoutingRecommendation,
  type TransferAuthority,
} from "../../services/challengeService";

import "./GovernmentChallengeDetailsPage.css";

export default function GovernmentChallengeDetailsPage() {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();

  const challengeId = Number(id);

  const [challenge, setChallenge] = useState<Challenge | null>(null);
  const [routing, setRouting] = useState<RoutingRecommendation | null>(null);
  const [assignmentHistory, setAssignmentHistory] =
    useState<AssignmentHistoryItem[]>([]);
  const [reviewHistory, setReviewHistory] =
    useState<ReviewHistoryItem[]>([]);
  const [transferAuthorities, setTransferAuthorities] =
    useState<TransferAuthority[]>([]);

  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);

  const [error, setError] = useState("");
  const [actionMessage, setActionMessage] = useState("");

  // Used for Accept / Override / initial Assign.
  const [selectedAuthorityId, setSelectedAuthorityId] =
    useState<number | null>(null);

  // Used only for Reassign / Escalate.
  const [destinationAuthorityId, setDestinationAuthorityId] =
    useState<number | null>(null);

  const [remarks, setRemarks] = useState("");
  const [reason, setReason] = useState("");
  const [resolutionSummary, setResolutionSummary] = useState("");
  const [showResolveModal, setShowResolveModal] = useState(false);

  async function loadData() {
    try {
      setLoading(true);
      setError("");

      const [
        challengeData,
        routingData,
        assignmentData,
        reviewData,
      ] = await Promise.all([
        challengeService.getChallenge(challengeId),
        challengeService.getRoutingRecommendation(challengeId),
        challengeService.getAssignmentHistory(challengeId),
        challengeService.getReviewHistory(challengeId),
      ]);

      let transferAuthoritiesData: TransferAuthority[] = [];

      if (challengeData.current_authority_id !== null) {
        try {
          const transferData =
            await challengeService.getTransferAuthorities(
              challengeId,
            );

          transferAuthoritiesData =
            transferData.authorities;
        } catch (transferErr: any) {
          // Transfer destinations are intentionally restricted to the
          // authorized officer of the current authority. A REVIEW_OFFICER
          // or another government user must still be able to open and
          // review the challenge even when this endpoint returns 403.
          console.warn(
            "Transfer authorities unavailable for current user:",
            transferErr?.response?.data?.detail ||
              transferErr,
          );

          transferAuthoritiesData = [];
        }
      }

      setChallenge(challengeData);
      setRouting(routingData);
      setAssignmentHistory(assignmentData);
      setReviewHistory(reviewData);
      setTransferAuthorities(transferAuthoritiesData);

      setSelectedAuthorityId(
        routingData.recommended_authority_id ?? null,
      );
      setDestinationAuthorityId(null);
    } catch (err: any) {
      console.error(err);

      setError(
        err?.response?.data?.detail ||
        "Unable to load challenge details.",
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (!Number.isFinite(challengeId)) {
      setError("Invalid challenge ID.");
      setLoading(false);
      return;
    }

    void loadData();
  }, [challengeId]);

  async function refreshData() {
    await loadData();
  }

  async function runAction(
    action: () => Promise<Challenge>,
    successMessage: string,
  ) {
    try {
      setActionLoading(true);
      setActionMessage("");
      setError("");

      await action();

      setActionMessage(successMessage);

      await loadData();
    } catch (err: any) {
      console.error(err);

      setError(
        err?.response?.data?.detail ||
        "The requested action could not be completed.",
      );
    } finally {
      setActionLoading(false);
    }
  }

  async function handleAcceptRecommendation() {
    await runAction(
      () => challengeService.acceptRecommendation(challengeId),
      "AI recommendation accepted successfully.",
    );
  }

  async function handleOverride() {
    if (!selectedAuthorityId) {
      setError(
        "Select an authority before overriding the recommendation.",
      );
      return;
    }

    if (reason.trim().length < 5) {
      setError(
        "Override reason must contain at least 5 characters.",
      );
      return;
    }

    await runAction(
      () =>
        challengeService.overrideRecommendation(challengeId, {
          authority_id: selectedAuthorityId,
          reason: reason.trim(),
        }),
      "AI recommendation overridden successfully.",
    );

    setReason("");
  }

  async function handleAssign() {
    if (!selectedAuthorityId) {
      setError("Select an authority first.");
      return;
    }

    if (challenge?.current_authority_id != null) {
      setError(
        "This challenge is already assigned. Use Reassign or Escalate instead.",
      );
      return;
    }

    await runAction(
      () =>
        challengeService.assignChallenge(challengeId, {
          authority_id: selectedAuthorityId,
          remarks: remarks.trim() || undefined,
        }),
      "Challenge assigned successfully.",
    );

    setRemarks("");
  }

  async function handleReassign() {
    if (!destinationAuthorityId) {
      setError("Select a destination authority.");
      return;
    }

    if (
      destinationAuthorityId === challenge?.current_authority_id
    ) {
      setError(
        "Destination authority must be different from the current authority.",
      );
      return;
    }

    if (reason.trim().length < 5) {
      setError(
        "Reassignment reason must contain at least 5 characters.",
      );
      return;
    }

    await runAction(
      () =>
        challengeService.reassignChallenge(challengeId, {
          authority_id: destinationAuthorityId,
          reason: reason.trim(),
          remarks: remarks.trim() || undefined,
        }),
      "Challenge reassigned successfully.",
    );

    setReason("");
    setRemarks("");
    setDestinationAuthorityId(null);
  }

  async function handleEscalate() {
    if (!destinationAuthorityId) {
      setError("Select a destination authority.");
      return;
    }

    if (
      destinationAuthorityId === challenge?.current_authority_id
    ) {
      setError(
        "Destination authority must be different from the current authority.",
      );
      return;
    }

    if (reason.trim().length < 5) {
      setError(
        "Escalation reason must contain at least 5 characters.",
      );
      return;
    }

    await runAction(
      () =>
        challengeService.escalateChallenge(challengeId, {
          authority_id: destinationAuthorityId,
          reason: reason.trim(),
          remarks: remarks.trim() || undefined,
        }),
      "Challenge escalated successfully.",
    );

    setReason("");
    setRemarks("");
    setDestinationAuthorityId(null);
  }

  async function handleAutoRoute() {
    await runAction(
      () => challengeService.autoRouteChallenge(challengeId),
      "Automatic routing completed successfully.",
    );
  }

  async function handleResolve() {
    if (!resolutionSummary.trim() || resolutionSummary.trim().length < 20) {
      setError("Resolution summary must be at least 20 characters long.");
      return;
    }
    await runAction(
      () => challengeService.resolveChallenge(challengeId, resolutionSummary.trim()),
      "Challenge marked as RESOLVED! Notification sent to citizen.",
    );
    setShowResolveModal(false);
    setResolutionSummary("");
  }

  if (loading) {
    return (
      <main className="challenge-details-page">
        <div className="challenge-details-loading">
          <div className="details-spinner" />
          Loading challenge...
        </div>
      </main>
    );
  }

  if (!challenge) {
    return (
      <main className="challenge-details-page">
        <div className="challenge-details-error">
          <AlertCircle size={22} />

          <div>
            <strong>Challenge unavailable</strong>

            <p>
              {error ||
                "The requested challenge could not be found."}
            </p>
          </div>

          <button
            type="button"
            onClick={() => navigate("/government/challenges")}
          >
            Back
          </button>
        </div>
      </main>
    );
  }

  const needsHumanReview =
    challenge.ai_requires_human_review === true ||
    challenge.ai_innovation_requires_human_review === true ||
    challenge.ai_innovation_type_requires_human_review === true;

  const currentAuthorityId =
    challenge.current_authority_id ?? null;

  const hasCurrentAuthority =
    currentAuthorityId !== null;

  const canInitialAssign = !hasCurrentAuthority;
  const canTransfer =
    hasCurrentAuthority &&
    transferAuthorities.length > 0;

  return (
    <main className="challenge-details-page">
      <header className="details-header">
        <div className="details-header-top">
          <button
            type="button"
            className="details-back-button"
            onClick={() => navigate("/government/challenges")}
          >
            <ArrowLeft size={17} />
            Challenge Queue
          </button>

          <button
            type="button"
            className="details-refresh-button"
            onClick={() => void refreshData()}
            disabled={actionLoading}
          >
            <RefreshCw size={16} />
            Refresh
          </button>
        </div>

        <div className="details-heading">
          <div>
            <span className="details-eyebrow">
              CHALLENGE CH-{challenge.id}
            </span>

            <h1>{challenge.title}</h1>

            <p>
              Submitted on {formatDate(challenge.created_at)}
            </p>
          </div>

          <div className="details-status-group">
            <StatusBadge status={challenge.status} />
            <UrgencyBadge urgency={challenge.urgency} />
          </div>
        </div>
      </header>

      <div className="details-container">
        {error && (
          <div className="details-alert details-alert-error">
            <AlertCircle size={18} />
            <span>{error}</span>

            <button
              type="button"
              onClick={() => setError("")}
              aria-label="Close error"
            >
              ×
            </button>
          </div>
        )}

        {actionMessage && (
          <div className="details-alert details-alert-success">
            <CheckCircle2 size={18} />
            <span>{actionMessage}</span>

            <button
              type="button"
              onClick={() => setActionMessage("")}
              aria-label="Close message"
            >
              ×
            </button>
          </div>
        )}

        {needsHumanReview && (
          <section className="human-review-banner">
            <div className="human-review-icon">
              <ShieldCheck size={21} />
            </div>

            <div>
              <strong>Human review required</strong>

              <p>
                The AI analysis does not meet the automatic
                decision threshold. An authorized officer should
                validate the recommendation before routing this
                challenge.
              </p>
            </div>
          </section>
        )}

        <section className="details-main-grid">
          <div className="details-card details-card-wide">
            <CardHeader
              icon={<FileText size={18} />}
              title="Challenge Information"
              subtitle="Citizen-submitted problem details"
            />

            <div className="challenge-information">
              <div className="challenge-description">
                <label>Description</label>
                <p>{challenge.description}</p>
              </div>

              <InfoGrid>
                <InfoItem
                  label="Category"
                  value={formatValue(challenge.category)}
                />

                <InfoItem
                  label="Severity"
                  value={formatValue(challenge.severity)}
                />

                <InfoItem
                  label="Urgency"
                  value={formatValue(challenge.urgency)}
                />

                <InfoItem
                  label="Affected Population"
                  value={
                    challenge.affected_population != null
                      ? challenge.affected_population.toLocaleString()
                      : "Not provided"
                  }
                />

                <InfoItem
                  label="Economic Loss"
                  value={
                    challenge.estimated_economic_loss != null
                      ? `₹${challenge.estimated_economic_loss.toLocaleString()}`
                      : "Not provided"
                  }
                />

                <InfoItem
                  label="Innovation Required"
                  value={challenge.innovation_required ? "Yes" : "No"}
                />
              </InfoGrid>
            </div>
          </div>

          <div className="details-card">
            <CardHeader
              icon={<MapPin size={18} />}
              title="Location"
              subtitle="Resolved challenge location"
            />

            <div className="location-details">
              <InfoItem
                label="Locality"
                value={challenge.locality || "Not provided"}
              />

              <InfoItem
                label="District"
                value={challenge.district || "Not provided"}
              />

              <InfoItem
                label="State"
                value={challenge.state || "Not provided"}
              />

              <InfoItem
                label="Address"
                value={challenge.address || "Not provided"}
              />

              <InfoItem
                label="Location Source"
                value={formatValue(challenge.location_source)}
              />

              <InfoItem
                label="Verified"
                value={challenge.location_verified ? "Yes" : "No"}
              />
            </div>

            {challenge.latitude != null &&
              challenge.longitude != null && (
                <div className="coordinates-box">
                  <span>Coordinates</span>

                  <strong>
                    {challenge.latitude}, {challenge.longitude}
                  </strong>
                </div>
              )}
          </div>

          <div className="details-card">
            <CardHeader
              icon={<Sparkles size={18} />}
              title="AI Triage"
              subtitle="Machine-assisted analysis"
            />

            <div className="ai-analysis">
              <AIResult
                label="Category"
                value={formatValue(challenge.category)}
                confidence={challenge.ai_category_confidence}
              />

              <AIResult
                label="Second Category"
                value={
                  challenge.ai_second_category
                    ? formatValue(challenge.ai_second_category)
                    : "—"
                }
                confidence={challenge.ai_second_category_confidence}
              />

              <AIResult
                label="Category Margin"
                value={
                  challenge.ai_category_margin != null
                    ? `${(challenge.ai_category_margin * 100).toFixed(2)}%`
                    : "—"
                }
              />

              <AIResult
                label="Overall AI Confidence"
                value={
                  challenge.ai_confidence_score != null
                    ? `${(challenge.ai_confidence_score * 100).toFixed(1)}%`
                    : "—"
                }
              />

              <AIResult
                label="Innovation"
                value={
                  challenge.innovation_required
                    ? "Required"
                    : "Not Required"
                }
              />

              <AIResult
                label="Innovation Type"
                value={
                  challenge.ai_innovation_type
                    ? formatValue(challenge.ai_innovation_type)
                    : "—"
                }
                confidence={challenge.ai_innovation_type_confidence}
              />

              <AIResult
                label="Innovation Decision"
                value={
                  challenge.ai_innovation_decision
                    ? formatValue(
                      challenge.ai_innovation_decision,
                    )
                    : "—"
                }
              />

              <AIResult
                label="Model Version"
                value={challenge.ai_model_version || "—"}
              />
            </div>

            {challenge.ai_category_top_3 &&
              challenge.ai_category_top_3.length > 0 && (
                <div className="top-predictions">
                  <h3>Top Category Predictions</h3>

                  {challenge.ai_category_top_3.map(
                    (prediction, index) => (
                      <div
                        className="prediction-row"
                        key={index}
                      >
                        <span>
                          {String(
                            prediction.category ??
                            prediction.label ??
                            "Prediction",
                          )}
                        </span>

                        <strong>
                          {formatPredictionConfidence(
                            prediction,
                          )}
                        </strong>
                      </div>
                    ),
                  )}
                </div>
              )}
          </div>

          <div className="details-card details-card-wide">
            <CardHeader
              icon={<GitBranch size={18} />}
              title="Authority Routing"
              subtitle="AI-assisted authority recommendation"
            />

            <div className="routing-overview">
              <div className="routing-recommended">
                <span>Recommended Authority</span>

                <strong>
                  {routing?.recommended_authority_name ||
                    "No recommendation"}
                </strong>

                <small>
                  Score:{" "}
                  {routing?.score != null
                    ? routing.score.toFixed(2)
                    : "—"}
                </small>

                {routing?.reason && <p>{routing.reason}</p>}
              </div>

              <div className="routing-current">
                <span>Current Authority</span>

                <strong>
                  {currentAuthorityId != null
                    ? `Organization #${currentAuthorityId}`
                    : "Not assigned"}
                </strong>

                {challenge.routing_reason && (
                  <p>
                    {formatValue(challenge.routing_reason)}
                  </p>
                )}
              </div>
            </div>

            {routing?.candidates &&
              routing.candidates.length > 0 && (
                <div className="authority-candidates">
                  <h3>Recommended Authority Candidates</h3>

                  <div className="candidate-list">
                    {routing.candidates.map((candidate) => (
                      <button
                        type="button"
                        key={candidate.organization_id}
                        className={`candidate-card ${selectedAuthorityId ===
                          candidate.organization_id
                          ? "selected"
                          : ""
                          }`}
                        onClick={() =>
                          setSelectedAuthorityId(
                            candidate.organization_id,
                          )
                        }
                      >
                        <div className="candidate-main">
                          <div className="candidate-radio">
                            {selectedAuthorityId ===
                              candidate.organization_id ? (
                              <CheckCircle2 size={17} />
                            ) : (
                              <Users size={16} />
                            )}
                          </div>

                          <div>
                            <strong>
                              {candidate.organization_name}
                            </strong>

                            <span>
                              {formatValue(
                                candidate.organization_type,
                              )}
                            </span>
                          </div>
                        </div>

                        <div className="candidate-score">
                          <strong>
                            {candidate.score.toFixed(1)}
                          </strong>

                          <span>Match score</span>
                        </div>

                        <p>{candidate.reason}</p>
                      </button>
                    ))}
                  </div>
                </div>
              )}
          </div>

          <div className="details-card details-card-wide">
            <CardHeader
              icon={<UserCheck size={18} />}
              title="Officer Control Center"
              subtitle="Authorized workflow actions"
            />

            <div className="control-form">
              <div className="form-field">
                <label htmlFor="selected-authority">
                  Selected authority
                </label>

                <select
                  id="selected-authority"
                  value={selectedAuthorityId ?? ""}
                  onChange={(event) =>
                    setSelectedAuthorityId(
                      event.target.value
                        ? Number(event.target.value)
                        : null,
                    )
                  }
                >
                  <option value="">Select authority</option>

                  {routing?.candidates.map((candidate) => (
                    <option
                      key={candidate.organization_id}
                      value={candidate.organization_id}
                    >
                      {candidate.organization_name}
                    </option>
                  ))}
                </select>

                <small>
                  Used for Accept, Override, and initial Assign.
                </small>
              </div>

              {hasCurrentAuthority && (
                <div className="form-field">
                  <label htmlFor="transfer-authority">
                    Transfer destination
                  </label>

                  <select
                    id="transfer-authority"
                    value={destinationAuthorityId ?? ""}
                    onChange={(event) =>
                      setDestinationAuthorityId(
                        event.target.value
                          ? Number(event.target.value)
                          : null,
                      )
                    }
                  >
                    <option value="">
                      Select destination authority
                    </option>

                    {transferAuthorities.map(
                      (authority) => (
                        <option
                          key={authority.id}
                          value={authority.id}
                        >
                          {authority.name} —{" "}
                          {formatValue(
                            authority.organization_type,
                          )}
                        </option>
                      ),
                    )}
                  </select>

                  <small>
                    Current authority:{" "}
                    {currentAuthorityId != null
                      ? `Organization #${currentAuthorityId}`
                      : "Not assigned"}
                  </small>

                  {!canTransfer && (
                    <small>
                      No eligible transfer destinations are
                      currently available.
                    </small>
                  )}
                </div>
              )}

              <div className="form-field">
                <label htmlFor="routing-reason">
                  Reason
                </label>

                <textarea
                  id="routing-reason"
                  value={reason}
                  onChange={(event) =>
                    setReason(event.target.value)
                  }
                  placeholder="Explain why this decision is being made..."
                  rows={3}
                />
              </div>

              <div className="form-field">
                <label htmlFor="routing-remarks">
                  Remarks
                </label>

                <textarea
                  id="routing-remarks"
                  value={remarks}
                  onChange={(event) =>
                    setRemarks(event.target.value)
                  }
                  placeholder="Optional remarks for the audit trail..."
                  rows={3}
                />
              </div>

              <div className="control-actions">
                {challenge.innovation_required && (
                  <button
                    type="button"
                    className="action-button action-auto"
                    onClick={() =>
                      navigate(
                        `/government/innovation/new?challenge_id=${challenge.id}&organization_id=${challenge.current_authority_id ?? 0}`,
                      )
                    }
                    disabled={
                      actionLoading ||
                      !challenge.current_authority_id
                    }
                  >
                    <Lightbulb size={16} />
                    Create Innovation Opportunity
                  </button>
                )}

                <button
                  type="button"
                  className="action-button action-primary"
                  onClick={() =>
                    void handleAcceptRecommendation()
                  }
                  disabled={
                    actionLoading ||
                    !routing?.recommended_authority_id
                  }
                >
                  <CheckCircle2 size={16} />
                  Accept AI Recommendation
                </button>

                <button
                  type="button"
                  className="action-button action-secondary"
                  onClick={() => void handleOverride()}
                  disabled={
                    actionLoading ||
                    !selectedAuthorityId
                  }
                >
                  <ShieldCheck size={16} />
                  Override
                </button>

                <button
                  type="button"
                  className="action-button action-secondary"
                  onClick={() => void handleAssign()}
                  disabled={
                    actionLoading ||
                    !canInitialAssign ||
                    !selectedAuthorityId
                  }
                >
                  <UserCheck size={16} />
                  Assign
                </button>

                <button
                  type="button"
                  className="action-button action-warning"
                  onClick={() => void handleReassign()}
                  disabled={
                    actionLoading ||
                    !canTransfer ||
                    !destinationAuthorityId
                  }
                >
                  <RefreshCw size={16} />
                  Reassign
                </button>

                <button
                  type="button"
                  className="action-button action-danger"
                  onClick={() => void handleEscalate()}
                  disabled={
                    actionLoading ||
                    !canTransfer ||
                    !destinationAuthorityId
                  }
                >
                  <ArrowUpRight size={16} />
                  Escalate
                </button>

                <button
                  type="button"
                  className="action-button action-auto"
                  onClick={() => void handleAutoRoute()}
                  disabled={
                    actionLoading ||
                    hasCurrentAuthority ||
                    needsHumanReview
                  }
                >
                  <Sparkles size={16} />
                  Auto Route
                </button>

                {challenge.status !== "RESOLVED" ? (
                  <button
                    type="button"
                    className="action-button"
                    style={{ backgroundColor: "#10b981", color: "#ffffff" }}
                    onClick={() => setShowResolveModal(true)}
                    disabled={actionLoading}
                  >
                    <CheckCircle2 size={16} />
                    Mark as Resolved
                  </button>
                ) : (
                  <div style={{ padding: "8px 16px", borderRadius: "8px", background: "#d1fae5", color: "#065f46", fontWeight: 600, display: "flex", alignItems: "center", gap: "6px" }}>
                    <CheckCircle2 size={16} /> Resolved & Citizen Notified
                  </div>
                )}
              </div>
            </div>
          </div>

          {showResolveModal && (
            <div style={{ position: "fixed", inset: 0, backgroundColor: "rgba(0,0,0,0.5)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 1000, padding: "20px" }}>
              <div style={{ background: "#ffffff", borderRadius: "16px", padding: "28px", maxWidth: "560px", width: "100%", boxShadow: "0 20px 25px -5px rgba(0,0,0,0.1)" }}>
                <h2 style={{ fontSize: "1.25rem", fontWeight: 700, marginBottom: "8px", color: "#1e293b" }}>Mark Challenge as Resolved</h2>
                <p style={{ fontSize: "0.875rem", color: "#64748b", marginBottom: "20px" }}>
                  Describe how this citizen's issue was addressed and resolved. This explanation will be sent directly to the citizen who filed the challenge.
                </p>
                <div style={{ marginBottom: "20px" }}>
                  <label style={{ display: "block", fontSize: "0.875rem", fontWeight: 600, color: "#334155", marginBottom: "6px" }}>
                    Resolution Summary (min 20 characters) *
                  </label>
                  <textarea
                    rows={4}
                    value={resolutionSummary}
                    onChange={(e) => setResolutionSummary(e.target.value)}
                    placeholder="E.g., Pothole repair team deployed on 15th Sept. Road surface repaved and inspected by municipal engineer."
                    style={{ width: "100%", padding: "10px 14px", borderRadius: "8px", border: "1px solid #cbd5e1", fontSize: "0.875rem" }}
                  />
                </div>
                <div style={{ display: "flex", justifyContent: "flex-end", gap: "12px" }}>
                  <button
                    type="button"
                    onClick={() => setShowResolveModal(false)}
                    style={{ padding: "10px 18px", borderRadius: "8px", border: "1px solid #cbd5e1", background: "#f8fafc", color: "#475569", fontWeight: 600, cursor: "pointer" }}
                  >
                    Cancel
                  </button>
                  <button
                    type="button"
                    onClick={() => void handleResolve()}
                    disabled={actionLoading || resolutionSummary.trim().length < 20}
                    style={{ padding: "10px 20px", borderRadius: "8px", border: "none", background: "#10b981", color: "#ffffff", fontWeight: 600, cursor: "pointer", opacity: resolutionSummary.trim().length < 20 ? 0.6 : 1 }}
                  >
                    {actionLoading ? "Resolving..." : "Confirm & Notify Citizen"}
                  </button>
                </div>
              </div>
            </div>
          )}

          <div className="details-card details-card-wide">
            <CardHeader
              icon={<FileText size={18} />}
              title="Submitted Evidence"
              subtitle="Files attached to this challenge"
            />

            {challenge.evidence &&
              challenge.evidence.length > 0 ? (
              <div className="evidence-list">
                {challenge.evidence.map((item) => (
                  <div key={item.id} style={{ display: "flex", flexDirection: "column", gap: "12px", marginBottom: "12px" }}>
                    {item.evidence_type === "IMAGE" && item.file_url && (
                      <img 
                        src={item.file_url} 
                        alt={item.original_filename} 
                        style={{ width: "100%", maxHeight: "350px", objectFit: "cover", borderRadius: "8px" }} 
                      />
                    )}
                    <a
                      className="evidence-item"
                      href={item.file_url || "#"}
                      target="_blank"
                      rel="noreferrer"
                      style={{ marginBottom: 0 }}
                    >
                      <FileText size={18} />

                      <div>
                        <strong>
                          {item.original_filename}
                        </strong>

                        <span>
                          {item.content_type ||
                            item.evidence_type}
                          {" • "}
                          {formatFileSize(item.file_size)}
                        </span>
                      </div>
                    </a>
                  </div>
                ))}
              </div>
            ) : (
              <div className="details-empty">
                No evidence has been submitted.
              </div>
            )}
          </div>

          <HistoryCard
            title="Review History"
            subtitle="Human review decisions"
            icon={<ShieldCheck size={18} />}
            emptyMessage="No review decisions recorded."
          >
            {reviewHistory.map((item) => (
              <div
                className="history-item"
                key={item.id}
              >
                <div className="history-marker">
                  <ShieldCheck size={14} />
                </div>

                <div className="history-content">
                  <div className="history-top">
                    <strong>
                      {formatValue(String(item.decision))}
                    </strong>

                    <span>
                      {formatDate(item.created_at)}
                    </span>
                  </div>

                  <p>
                    Reviewer #{item.reviewer_id}
                  </p>

                  {item.reason && (
                    <small>{item.reason}</small>
                  )}
                </div>
              </div>
            ))}
          </HistoryCard>

          <HistoryCard
            title="Assignment History"
            subtitle="Complete routing audit trail"
            icon={<GitBranch size={18} />}
            emptyMessage="No assignment history recorded."
          >
            {assignmentHistory.map((item) => (
              <div
                className="history-item"
                key={item.id}
              >
                <div className="history-marker">
                  <GitBranch size={14} />
                </div>

                <div className="history-content">
                  <div className="history-top">
                    <strong>
                      {formatValue(String(item.action))}
                    </strong>

                    <span>
                      {formatDate(item.created_at)}
                    </span>
                  </div>

                  <p>
                    Organization{" "}
                    {item.from_authority_id ?? "—"}
                    {" → "}
                    Organization {item.to_authority_id}
                  </p>

                  {item.reason && (
                    <small>
                      Reason: {item.reason}
                    </small>
                  )}

                  {item.remarks && (
                    <small>
                      Remarks: {item.remarks}
                    </small>
                  )}
                </div>
              </div>
            ))}
          </HistoryCard>
        </section>
      </div>
    </main>
  );
}

/* ============================================================
   COMPONENTS
============================================================ */

function CardHeader({
  icon,
  title,
  subtitle,
}: {
  icon: React.ReactNode;
  title: string;
  subtitle: string;
}) {
  return (
    <div className="details-card-header">
      <div className="details-card-icon">{icon}</div>

      <div>
        <h2>{title}</h2>
        <p>{subtitle}</p>
      </div>
    </div>
  );
}

function InfoGrid({
  children,
}: {
  children: React.ReactNode;
}) {
  return <div className="info-grid">{children}</div>;
}

function InfoItem({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div className="info-item">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function AIResult({
  label,
  value,
  confidence,
}: {
  label: string;
  value: string;
  confidence?: number | null;
}) {
  return (
    <div className="ai-result">
      <span>{label}</span>

      <strong>{value}</strong>

      {confidence != null && (
        <small>
          {(confidence * 100).toFixed(1)}% confidence
        </small>
      )}
    </div>
  );
}

function HistoryCard({
  title,
  subtitle,
  icon,
  children,
  emptyMessage,
}: {
  title: string;
  subtitle: string;
  icon: React.ReactNode;
  children: React.ReactNode;
  emptyMessage: string;
}) {
  const hasChildren = Array.isArray(children)
    ? children.length > 0
    : Boolean(children);

  return (
    <div className="details-card">
      <CardHeader
        icon={icon}
        title={title}
        subtitle={subtitle}
      />

      <div className="history-list">
        {hasChildren ? (
          children
        ) : (
          <div className="details-empty">
            {emptyMessage}
          </div>
        )}
      </div>
    </div>
  );
}

function StatusBadge({
  status,
}: {
  status: string;
}) {
  return (
    <span
      className={`details-status details-status-${status.toLowerCase()}`}
    >
      {formatValue(status)}
    </span>
  );
}

function UrgencyBadge({
  urgency,
}: {
  urgency: string;
}) {
  return (
    <span
      className={`details-urgency details-urgency-${urgency.toLowerCase()}`}
    >
      {urgency}
    </span>
  );
}

function formatValue(value?: string | null): string {
  if (!value) {
    return "—";
  }

  return value
    .replaceAll("_", " ")
    .replace(/\b\w/g, (character) =>
      character.toUpperCase(),
    );
}

function formatDate(value?: string): string {
  if (!value) {
    return "—";
  }

  return new Date(value).toLocaleString(
    "en-IN",
    {
      dateStyle: "medium",
      timeStyle: "short",
    },
  );
}

function formatPredictionConfidence(
  prediction: Record<string, unknown>,
): string {
  const raw =
    prediction.confidence ??
    prediction.probability ??
    prediction.score;

  if (typeof raw !== "number") {
    return "—";
  }

  return `${(raw * 100).toFixed(1)}%`;
}

function formatFileSize(
  size?: number | null,
): string {
  if (!size) {
    return "Unknown size";
  }

  if (size < 1024) {
    return `${size} B`;
  }

  if (size < 1024 * 1024) {
    return `${(size / 1024).toFixed(1)} KB`;
  }

  return `${(
    size /
    (1024 * 1024)
  ).toFixed(1)} MB`;
}
