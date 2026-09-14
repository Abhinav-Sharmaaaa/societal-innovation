import {
  ArrowLeft,
  CheckCircle2,
  Lightbulb,
  Loader2,
} from "lucide-react";
import { useState } from "react";
import type { FormEvent } from "react";
import {
  useNavigate,
  useSearchParams,
} from "react-router-dom";

import {
  innovationService,
} from "../../services/innovationService";

import "./InnovationPages.css";


export default function CreateInnovationOpportunityPage() {
  const navigate = useNavigate();
  const [searchParams] =
    useSearchParams();

  const challengeId = Number(
    searchParams.get("challenge_id"),
  );

  const organizationId = Number(
    searchParams.get("organization_id"),
  );


  const [title, setTitle] =
    useState("");

  const [problemStatement, setProblemStatement] =
    useState("");

  const [objectives, setObjectives] =
    useState("");

  const [technicalRequirements, setTechnicalRequirements] =
    useState("");

  const [expectedOutcomes, setExpectedOutcomes] =
    useState("");

  const [budget, setBudget] =
    useState("");

  const [duration, setDuration] =
    useState("");

  const [deadline, setDeadline] =
    useState("");

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");


  async function handleSubmit(
    event: FormEvent,
  ) {
    event.preventDefault();

    setError("");

    if (!challengeId) {
      setError(
        "A valid challenge ID is required.",
      );
      return;
    }

    if (!organizationId) {
      setError(
        "A sponsoring organization ID is required.",
      );
      return;
    }

    if (
      title.trim().length < 5
    ) {
      setError(
        "Title must contain at least 5 characters.",
      );
      return;
    }

    if (
      problemStatement.trim().length < 10
    ) {
      setError(
        "Problem statement must contain at least 10 characters.",
      );
      return;
    }


    try {
      setLoading(true);

      const opportunity =
        await innovationService.createOpportunity({
          challenge_id:
            challengeId,

          sponsoring_organization_id:
            organizationId,

          title:
            title.trim(),

          problem_statement:
            problemStatement.trim(),

          objectives:
            objectives.trim() ||
            undefined,

          technical_requirements:
            technicalRequirements.trim() ||
            undefined,

          expected_outcomes:
            expectedOutcomes.trim() ||
            undefined,

          estimated_budget:
            budget
              ? Number(budget)
              : undefined,

          expected_duration_days:
            duration
              ? Number(duration)
              : undefined,

          proposal_deadline:
            deadline
              ? new Date(deadline).toISOString()
              : undefined,
        });


      navigate(
        `/government/innovation/${opportunity.id}`,
      );

    } catch (err: any) {
      console.error(err);

      setError(
        err.response?.data?.detail ||
          "Unable to create innovation opportunity.",
      );
    } finally {
      setLoading(false);
    }
  }


  return (
    <main className="innovation-page">

      <header className="innovation-header">

        <button
          className="innovation-back"
          onClick={() =>
            navigate(
              `/government/challenges/${challengeId}`,
            )
          }
        >
          <ArrowLeft size={16} />
          Back to Challenge
        </button>

        <span className="innovation-eyebrow">
          INNOVATION PIPELINE
        </span>

        <h1>
          Create Innovation Opportunity
        </h1>

        <p>
          Convert an eligible societal challenge into
          a structured opportunity for universities,
          research institutions and industry partners.
        </p>

      </header>


      <div className="innovation-container">

        <section className="innovation-context">

          <div className="innovation-context-icon">
            <Lightbulb size={21} />
          </div>

          <div>
            <strong>
              Challenge #{challengeId}
            </strong>

            <span>
              This opportunity will remain in draft
              until it is approved by an authorized
              government officer.
            </span>
          </div>

        </section>


        <form
          className="innovation-form-card"
          onSubmit={handleSubmit}
        >

          <FormField
            label="Opportunity Title"
            required
          >
            <input
              value={title}
              onChange={(event) =>
                setTitle(event.target.value)
              }
              placeholder="e.g. Smart Flood Early Warning System"
              maxLength={255}
            />
          </FormField>


          <FormField
            label="Problem Statement"
            required
          >
            <textarea
              value={problemStatement}
              onChange={(event) =>
                setProblemStatement(
                  event.target.value,
                )
              }
              placeholder="Describe the societal problem that requires an innovative solution..."
              rows={6}
            />
          </FormField>


          <FormField label="Objectives">

            <textarea
              value={objectives}
              onChange={(event) =>
                setObjectives(
                  event.target.value,
                )
              }
              placeholder="What should the proposed solution achieve?"
              rows={4}
            />

          </FormField>


          <FormField label="Technical Requirements">

            <textarea
              value={technicalRequirements}
              onChange={(event) =>
                setTechnicalRequirements(
                  event.target.value,
                )
              }
              placeholder="Technology, research, hardware, AI, field-testing or other requirements..."
              rows={4}
            />

          </FormField>


          <FormField label="Expected Outcomes">

            <textarea
              value={expectedOutcomes}
              onChange={(event) =>
                setExpectedOutcomes(
                  event.target.value,
                )
              }
              placeholder="Expected measurable outcomes and societal impact..."
              rows={4}
            />

          </FormField>


          <div className="innovation-form-grid">

            <FormField label="Estimated Budget">

              <input
                type="number"
                min="0"
                value={budget}
                onChange={(event) =>
                  setBudget(
                    event.target.value,
                  )
                }
                placeholder="₹"
              />

            </FormField>


            <FormField label="Expected Duration (days)">

              <input
                type="number"
                min="1"
                value={duration}
                onChange={(event) =>
                  setDuration(
                    event.target.value,
                  )
                }
                placeholder="e.g. 180"
              />

            </FormField>

          </div>


          <FormField label="Proposal Deadline">

            <input
              type="datetime-local"
              value={deadline}
              onChange={(event) =>
                setDeadline(
                  event.target.value,
                )
              }
            />

          </FormField>


          {error && (
            <div className="innovation-error">
              {error}
            </div>
          )}


          <div className="innovation-form-actions">

            <button
              type="button"
              className="innovation-secondary-button"
              onClick={() =>
                navigate(
                  `/government/challenges/${challengeId}`,
                )
              }
              disabled={loading}
            >
              Cancel
            </button>


            <button
              type="submit"
              className="innovation-primary-button"
              disabled={loading}
            >
              {loading ? (
                <>
                  <Loader2
                    size={16}
                    className="button-spin"
                  />
                  Creating...
                </>
              ) : (
                <>
                  <CheckCircle2 size={16} />
                  Create Opportunity
                </>
              )}
            </button>

          </div>

        </form>

      </div>

    </main>
  );
}


/* ============================================================
   FORM FIELD
============================================================ */

function FormField({
  label,
  required = false,
  children,
}: {
  label: string;
  required?: boolean;
  children: React.ReactNode;
}) {
  return (
    <div className="innovation-field">

      <label>
        {label}

        {required && (
          <span> *</span>
        )}
      </label>

      {children}

    </div>
  );
}