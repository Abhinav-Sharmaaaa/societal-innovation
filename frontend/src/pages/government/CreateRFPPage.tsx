import {
  ArrowLeft,
  FileText,
  Loader2,
  Send,
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


export default function CreateRFPPage() {
  const navigate = useNavigate();

  const [searchParams] =
    useSearchParams();

  const opportunityId =
    Number(
      searchParams.get(
        "opportunity_id",
      ),
    );


  const [title, setTitle] =
    useState("");

  const [description, setDescription] =
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

    if (!opportunityId) {
      setError(
        "A valid innovation opportunity ID is required.",
      );
      return;
    }

    if (
      title.trim().length < 5
    ) {
      setError(
        "RFP title must contain at least 5 characters.",
      );
      return;
    }

    if (
      description.trim().length < 10
    ) {
      setError(
        "RFP description must contain at least 10 characters.",
      );
      return;
    }


    try {
      setLoading(true);

      const rfp =
        await innovationService.createRFP({
          innovation_opportunity_id:
            opportunityId,

          title:
            title.trim(),

          description:
            description.trim(),

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
              ? new Date(
                  deadline,
                ).toISOString()
              : undefined,
        });


      navigate(
        `/government/rfps/${rfp.id}`,
      );

    } catch (err: any) {
      console.error(err);

      setError(
        err.response?.data?.detail ||
          "Unable to create RFP.",
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
              `/government/innovation/${opportunityId}`,
            )
          }
        >
          <ArrowLeft size={16} />
          Opportunity
        </button>

        <span className="innovation-eyebrow">
          RFP MANAGEMENT
        </span>

        <h1>
          Create Request for Proposal
        </h1>

        <p>
          Define the formal proposal request that
          eligible universities can respond to.
        </p>

      </header>


      <div className="innovation-container">

        <form
          className="innovation-form-card"
          onSubmit={handleSubmit}
        >

          <div className="innovation-context">

            <div className="innovation-context-icon">
              <FileText size={20} />
            </div>

            <div>

              <strong>
                Innovation Opportunity #{opportunityId}
              </strong>

              <span>
                The opportunity must already be approved
                before this RFP can be created.
              </span>

            </div>

          </div>


          <FormField
            label="RFP Title"
            required
          >
            <input
              value={title}
              onChange={(event) =>
                setTitle(
                  event.target.value,
                )
              }
              placeholder="e.g. RFP for AI-based Flood Prediction"
              maxLength={255}
            />
          </FormField>


          <FormField
            label="Description"
            required
          >
            <textarea
              value={description}
              onChange={(event) =>
                setDescription(
                  event.target.value,
                )
              }
              placeholder="Describe what universities are being invited to propose..."
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
              placeholder="Objectives of the proposed work..."
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
              placeholder="Technical specifications, research requirements, field conditions..."
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
              placeholder="Expected solution and measurable outcomes..."
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
                  `/government/innovation/${opportunityId}`,
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
                  <Send size={16} />
                  Create RFP
                </>
              )}
            </button>

          </div>

        </form>

      </div>

    </main>
  );
}


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