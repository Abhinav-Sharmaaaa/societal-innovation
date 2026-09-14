import {
  ArrowLeft,
  CheckCircle2,
  ClipboardCheck,
  Loader2,
  Send,
  XCircle,
} from "lucide-react";
import type { FormEvent } from "react";
import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import {
  createProposalEvaluation,
  decideProposalEvaluation,
  getUniversityProposal,
  type UniversityProposal,
} from "../../services/proposalEvaluationService";

import "./ProposalEvaluationPage.css";


interface Criterion {
  key:
    | "technical_feasibility_score"
    | "innovation_score"
    | "cost_effectiveness_score"
    | "impact_score"
    | "timeline_score"
    | "scalability_score"
    | "research_capability_score";

  label: string;
  weight: number;
  description: string;
}


const CRITERIA: Criterion[] = [
  {
    key: "technical_feasibility_score",
    label: "Technical Feasibility",
    weight: 20,
    description:
      "How technically practical and implementable is the proposed solution?",
  },
  {
    key: "innovation_score",
    label: "Innovation",
    weight: 15,
    description:
      "How innovative and novel is the proposed approach?",
  },
  {
    key: "cost_effectiveness_score",
    label: "Cost Effectiveness",
    weight: 10,
    description:
      "Does the proposed solution provide strong value for its estimated cost?",
  },
  {
    key: "impact_score",
    label: "Impact",
    weight: 20,
    description:
      "How effectively can the solution address the societal challenge?",
  },
  {
    key: "timeline_score",
    label: "Timeline",
    weight: 10,
    description:
      "How realistic is the proposed implementation timeline?",
  },
  {
    key: "scalability_score",
    label: "Scalability",
    weight: 10,
    description:
      "Can the proposed solution scale beyond the initial implementation?",
  },
  {
    key: "research_capability_score",
    label: "Research Capability",
    weight: 15,
    description:
      "Does the university have the capability to execute the proposed work?",
  },
];


type ScoreState = Record<Criterion["key"], number>;


const INITIAL_SCORES: ScoreState = {
  technical_feasibility_score: 0,
  innovation_score: 0,
  cost_effectiveness_score: 0,
  impact_score: 0,
  timeline_score: 0,
  scalability_score: 0,
  research_capability_score: 0,
};


export default function ProposalEvaluationPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [proposal, setProposal] =
    useState<UniversityProposal | null>(null);

  const [scores, setScores] =
    useState<ScoreState>(INITIAL_SCORES);

  const [remarks, setRemarks] = useState("");

  const [evaluationId, setEvaluationId] =
    useState<number | null>(null);

  const [overallScore, setOverallScore] =
    useState<number | null>(null);

  const [decision, setDecision] =
    useState<string>("UNDER_REVIEW");

  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [deciding, setDeciding] = useState(false);

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");


  useEffect(() => {
    const loadProposal = async () => {
      if (!id) {
        setError("Invalid proposal ID.");
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError("");

        const data = await getUniversityProposal(
          Number(id)
        );

        setProposal(data);
      } catch (err: any) {
        setError(
          err?.response?.data?.detail ||
            "Failed to load university proposal."
        );
      } finally {
        setLoading(false);
      }
    };

    void loadProposal();
  }, [id]);


  const calculatedScore = useMemo(() => {
    return Number(
      (
        scores.technical_feasibility_score * 0.20 +
        scores.innovation_score * 0.15 +
        scores.cost_effectiveness_score * 0.10 +
        scores.impact_score * 0.20 +
        scores.timeline_score * 0.10 +
        scores.scalability_score * 0.10 +
        scores.research_capability_score * 0.15
      ).toFixed(2)
    );
  }, [scores]);


  const updateScore = (
    key: Criterion["key"],
    value: string
  ) => {
    const numericValue = Number(value);

    if (
      Number.isNaN(numericValue) ||
      numericValue < 0 ||
      numericValue > 100
    ) {
      return;
    }

    setScores((current) => ({
      ...current,
      [key]: numericValue,
    }));
  };


  const handleEvaluate = async (
    event: FormEvent<HTMLFormElement>
  ) => {
    event.preventDefault();

    if (!proposal) {
      return;
    }

    try {
      setSubmitting(true);
      setError("");
      setSuccess("");

      const evaluation =
        await createProposalEvaluation({
          proposal_id: proposal.id,

          technical_feasibility_score:
            scores.technical_feasibility_score,

          innovation_score:
            scores.innovation_score,

          cost_effectiveness_score:
            scores.cost_effectiveness_score,

          impact_score:
            scores.impact_score,

          timeline_score:
            scores.timeline_score,

          scalability_score:
            scores.scalability_score,

          research_capability_score:
            scores.research_capability_score,

          remarks:
            remarks.trim() || undefined,
        });

      setEvaluationId(evaluation.id);
      setOverallScore(evaluation.overall_score);
      setDecision(evaluation.decision);
      setSuccess(
        "Proposal evaluation submitted successfully."
      );

      setProposal((current) =>
        current
          ? {
              ...current,
              status: "UNDER_EVALUATION",
            }
          : current
      );
    } catch (err: any) {
      setError(
        err?.response?.data?.detail ||
          "Failed to evaluate proposal."
      );
    } finally {
      setSubmitting(false);
    }
  };


  const handleDecision = async (
    nextDecision: "SHORTLISTED" | "REJECTED"
  ) => {
    if (!evaluationId) {
      return;
    }

    try {
      setDeciding(true);
      setError("");
      setSuccess("");

      const result =
        await decideProposalEvaluation(
          evaluationId,
          {
            decision: nextDecision,
            remarks:
              remarks.trim() || undefined,
          }
        );

      setDecision(result.decision);
      setSuccess(
        nextDecision === "SHORTLISTED"
          ? "Proposal shortlisted successfully."
          : "Proposal rejected successfully."
      );

      setProposal((current) =>
        current
          ? {
              ...current,
              status:
                nextDecision === "SHORTLISTED"
                  ? "SHORTLISTED"
                  : "REJECTED",
            }
          : current
      );
    } catch (err: any) {
      setError(
        err?.response?.data?.detail ||
          "Failed to update proposal decision."
      );
    } finally {
      setDeciding(false);
    }
  };


  if (loading) {
    return (
      <main className="proposal-evaluation-page">
        <div className="evaluation-state">
          <Loader2
            size={28}
            className="evaluation-spinner"
          />
          Loading proposal...
        </div>
      </main>
    );
  }


  if (error && !proposal) {
    return (
      <main className="proposal-evaluation-page">
        <div className="evaluation-state evaluation-state-error">
          <h2>Unable to load proposal</h2>
          <p>{error}</p>

          <button
            type="button"
            className="evaluation-primary-button"
            onClick={() => navigate(-1)}
          >
            <ArrowLeft size={17} />
            Go Back
          </button>
        </div>
      </main>
    );
  }


  if (!proposal) {
    return null;
  }


  return (
    <main className="proposal-evaluation-page">

      <header className="evaluation-header">

        <button
          type="button"
          className="evaluation-back"
          onClick={() =>
            navigate(
              `/government/rfps/${proposal.rfp_id}/proposals`
            )
          }
        >
          <ArrowLeft size={18} />
          Back to Proposals
        </button>

        <div>
          <span className="evaluation-eyebrow">
            GOVERNMENT PROPOSAL EVALUATION
          </span>

          <h1>{proposal.title}</h1>

          <p>
            Proposal #{proposal.id} · RFP #{proposal.rfp_id}
          </p>
        </div>

      </header>


      {error && (
        <div className="evaluation-alert evaluation-alert-error">
          {error}
        </div>
      )}

      {success && (
        <div className="evaluation-alert evaluation-alert-success">
          {success}
        </div>
      )}


      <div className="evaluation-layout">

        {/* ====================================================
            Proposal
        ==================================================== */}

        <section className="evaluation-proposal">

          <div className="evaluation-card">

            <div className="evaluation-card-title">
              <ClipboardCheck size={19} />

              <div>
                <h2>University Proposal</h2>
                <span>
                  Status:{" "}
                  {proposal.status.replaceAll("_", " ")}
                </span>
              </div>
            </div>


            <div className="proposal-content-block">
              <h3>Solution</h3>
              <p>{proposal.solution}</p>
            </div>


            <div className="proposal-content-block">
              <h3>Technical Approach</h3>
              <p>{proposal.technical_approach}</p>
            </div>


            {proposal.research_methodology && (
              <div className="proposal-content-block">
                <h3>Research Methodology</h3>
                <p>
                  {proposal.research_methodology}
                </p>
              </div>
            )}


            {proposal.required_resources && (
              <div className="proposal-content-block">
                <h3>Required Resources</h3>
                <p>{proposal.required_resources}</p>
              </div>
            )}


            {proposal.faculty_team && (
              <div className="proposal-content-block">
                <h3>Faculty / Research Team</h3>
                <p>{proposal.faculty_team}</p>
              </div>
            )}


            {proposal.technology_requirements && (
              <div className="proposal-content-block">
                <h3>Technology Requirements</h3>
                <p>
                  {proposal.technology_requirements}
                </p>
              </div>
            )}


            {proposal.expected_outcomes && (
              <div className="proposal-content-block">
                <h3>Expected Outcomes</h3>
                <p>{proposal.expected_outcomes}</p>
              </div>
            )}


            <div className="proposal-facts">

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

            </div>

          </div>

        </section>


        {/* ====================================================
            Evaluation
        ==================================================== */}

        <section className="evaluation-side">

          <form
            className="evaluation-card"
            onSubmit={handleEvaluate}
          >

            <div className="evaluation-card-title">
              <ClipboardCheck size={19} />

              <div>
                <h2>Evaluation Criteria</h2>
                <span>
                  Score every criterion from 0 to 100.
                </span>
              </div>
            </div>


            <div className="evaluation-score-summary">

              <span>Calculated Overall Score</span>

              <strong>
                {calculatedScore.toFixed(2)}
              </strong>

              <small>
                Based on the official weighted criteria.
              </small>

            </div>


            <div className="evaluation-criteria">

              {CRITERIA.map((criterion) => (

                <div
                  className="evaluation-criterion"
                  key={criterion.key}
                >

                  <div className="criterion-heading">

                    <div>
                      <strong>
                        {criterion.label}
                      </strong>

                      <p>
                        {criterion.description}
                      </p>
                    </div>

                    <span>
                      {criterion.weight}%
                    </span>

                  </div>


                  <div className="criterion-input-row">

                    <input
                      type="range"
                      min="0"
                      max="100"
                      step="1"
                      value={scores[criterion.key]}
                      onChange={(event) =>
                        updateScore(
                          criterion.key,
                          event.target.value
                        )
                      }
                    />

                    <input
                      type="number"
                      min="0"
                      max="100"
                      step="1"
                      value={scores[criterion.key]}
                      onChange={(event) =>
                        updateScore(
                          criterion.key,
                          event.target.value
                        )
                      }
                    />

                  </div>

                </div>

              ))}

            </div>


            <label className="evaluation-remarks">
              Evaluation Remarks

              <textarea
                rows={5}
                value={remarks}
                onChange={(event) =>
                  setRemarks(event.target.value)
                }
                placeholder="Provide evaluation remarks..."
              />
            </label>


            {!evaluationId && (
              <button
                type="submit"
                className="evaluation-primary-button evaluation-submit"
                disabled={submitting}
              >
                {submitting ? (
                  <Loader2
                    size={18}
                    className="evaluation-spinner"
                  />
                ) : (
                  <Send size={18} />
                )}

                {submitting
                  ? "Submitting Evaluation..."
                  : "Submit Evaluation"}
              </button>
            )}

          </form>


          {/* ==================================================
              Decision
          ================================================== */}

          {evaluationId && (
            <section className="evaluation-card decision-card">

              <div className="evaluation-card-title">
                <CheckCircle2 size={19} />

                <div>
                  <h2>Evaluation Decision</h2>
                  <span>
                    Overall Score:{" "}
                    {overallScore?.toFixed(2)}
                  </span>
                </div>
              </div>


              <div
                className={`decision-current decision-${decision.toLowerCase()}`}
              >
                Current Decision:{" "}
                {decision.replaceAll("_", " ")}
              </div>


              {decision === "UNDER_REVIEW" && (
                <div className="decision-actions">

                  <button
                    type="button"
                    className="decision-shortlist"
                    disabled={deciding}
                    onClick={() =>
                      void handleDecision("SHORTLISTED")
                    }
                  >
                    {deciding ? (
                      <Loader2
                        size={17}
                        className="evaluation-spinner"
                      />
                    ) : (
                      <CheckCircle2 size={17} />
                    )}

                    Shortlist
                  </button>


                  <button
                    type="button"
                    className="decision-reject"
                    disabled={deciding}
                    onClick={() =>
                      void handleDecision("REJECTED")
                    }
                  >
                    <XCircle size={17} />
                    Reject
                  </button>

                </div>
              )}

            </section>
          )}

        </section>

      </div>

    </main>
  );
}