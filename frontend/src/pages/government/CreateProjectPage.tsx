import {
  ArrowLeft,
  CalendarDays,
  Coins,
  Loader2,
  Rocket,
  Send,
} from "lucide-react";
import type { FormEvent } from "react";
import { useState } from "react";
import {
  useLocation,
  useNavigate,
} from "react-router-dom";

import {
  createProject,
  type CreateProjectRequest,
} from "../../services/projectService";

import "./ProjectPages.css";

export default function CreateProjectPage() {
  const navigate = useNavigate();
  const location = useLocation();

  const params = new URLSearchParams(
    location.search
  );

  const collaborationId = Number(
    params.get("collaboration_id")
  );

  const [form, setForm] = useState({
    title: "",
    description: "",
    objectives: "",
    expected_outcomes: "",
    total_budget: "",
    start_date: "",
    target_completion_date: "",
  });

  const [submitting, setSubmitting] =
    useState(false);

  const [error, setError] =
    useState("");

  const updateField = (
    field: keyof typeof form,
    value: string
  ) => {
    setForm((current) => ({
      ...current,
      [field]: value,
    }));
  };

  const handleSubmit = async (
    event: FormEvent<HTMLFormElement>
  ) => {
    event.preventDefault();

    setError("");

    if (
      !collaborationId ||
      collaborationId <= 0
    ) {
      setError(
        "Invalid collaboration ID."
      );
      return;
    }

    if (form.title.trim().length < 5) {
      setError(
        "Project title must contain at least 5 characters."
      );
      return;
    }

    try {
      setSubmitting(true);

      const payload: CreateProjectRequest = {
        collaboration_id: collaborationId,
        title: form.title.trim(),
      };

      if (form.description.trim()) {
        payload.description =
          form.description.trim();
      }

      if (form.objectives.trim()) {
        payload.objectives =
          form.objectives.trim();
      }

      if (form.expected_outcomes.trim()) {
        payload.expected_outcomes =
          form.expected_outcomes.trim();
      }

      if (form.total_budget.trim()) {
        const budget = Number(
          form.total_budget
        );

        if (
          Number.isNaN(budget) ||
          budget < 0
        ) {
          setError(
            "Total budget must be a valid non-negative number."
          );
          return;
        }

        payload.total_budget = budget;
      }

      if (form.start_date) {
        payload.start_date =
          new Date(
            form.start_date
          ).toISOString();
      }

      if (form.target_completion_date) {
        payload.target_completion_date =
          new Date(
            form.target_completion_date
          ).toISOString();
      }

      const project =
        await createProject(payload);

      navigate(
        `/government/projects/${project.id}`,
        {
          replace: true,
        }
      );
    } catch (err: any) {
      setError(
        err?.response?.data?.detail ||
          "Unable to create project."
      );
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <main className="project-page">

      <header className="project-header">

        <button
          type="button"
          className="project-back"
          onClick={() => navigate(-1)}
        >
          <ArrowLeft size={18} />
          Back
        </button>

        <span className="project-eyebrow">
          PROJECT INITIATION
        </span>

        <h1>
          Create Innovation Project
        </h1>

        <p>
          Convert the accepted industry
          collaboration into an executable
          societal innovation project.
        </p>

      </header>

      {error && (
        <div className="project-alert project-alert-error">
          {error}
        </div>
      )}

      <form
        className="project-form"
        onSubmit={handleSubmit}
      >

        <section className="project-section">

          <div className="project-section-heading">
            <Rocket size={20} />

            <div>
              <h2>Project Overview</h2>
              <p>
                Define the project that will be
                executed by the university and
                industry partners.
              </p>
            </div>
          </div>

          <label>
            Project Title *
            <input
              value={form.title}
              onChange={(event) =>
                updateField(
                  "title",
                  event.target.value
                )
              }
              placeholder="Enter the project title"
              maxLength={255}
              required
            />
          </label>

          <label>
            Project Description
            <textarea
              rows={6}
              value={form.description}
              onChange={(event) =>
                updateField(
                  "description",
                  event.target.value
                )
              }
              placeholder="Describe the project scope and implementation approach."
            />
          </label>

          <label>
            Objectives
            <textarea
              rows={5}
              value={form.objectives}
              onChange={(event) =>
                updateField(
                  "objectives",
                  event.target.value
                )
              }
              placeholder="Define the key project objectives."
            />
          </label>

          <label>
            Expected Outcomes
            <textarea
              rows={5}
              value={
                form.expected_outcomes
              }
              onChange={(event) =>
                updateField(
                  "expected_outcomes",
                  event.target.value
                )
              }
              placeholder="Describe the measurable expected outcomes."
            />
          </label>

        </section>


        <section className="project-section">

          <div className="project-section-heading">
            <Coins size={20} />

            <div>
              <h2>
                Budget & Schedule
              </h2>

              <p>
                You may leave these blank to
                use backend defaults.
              </p>
            </div>
          </div>

          <label>
            Total Project Budget (₹)
            <input
              type="number"
              min="0"
              value={form.total_budget}
              onChange={(event) =>
                updateField(
                  "total_budget",
                  event.target.value
                )
              }
              placeholder="Defaults to accepted collaboration funding"
            />
          </label>


          <div className="project-grid">

            <label>
              <span className="project-label-icon">
                <CalendarDays size={15} />
                Start Date
              </span>

              <input
                type="datetime-local"
                value={form.start_date}
                onChange={(event) =>
                  updateField(
                    "start_date",
                    event.target.value
                  )
                }
              />
            </label>


            <label>
              <span className="project-label-icon">
                <CalendarDays size={15} />
                Target Completion Date
              </span>

              <input
                type="datetime-local"
                value={
                  form.target_completion_date
                }
                onChange={(event) =>
                  updateField(
                    "target_completion_date",
                    event.target.value
                  )
                }
              />
            </label>

          </div>

        </section>


        <section className="project-milestone-preview">

          <h2>
            Automatic Milestone Plan
          </h2>

          <p>
            Creating this project will automatically
            generate these six mandatory milestones:
          </p>

          <div className="project-milestones">

            <MilestonePreview
              number={1}
              title="Problem Validation"
            />

            <MilestonePreview
              number={2}
              title="Research & Planning"
            />

            <MilestonePreview
              number={3}
              title="Prototype Development"
            />

            <MilestonePreview
              number={4}
              title="Testing & Validation"
            />

            <MilestonePreview
              number={5}
              title="Pilot Deployment"
            />

            <MilestonePreview
              number={6}
              title="Final Solution / Deployment"
            />

          </div>

        </section>


        <div className="project-submit-bar">

          <button
            type="button"
            className="project-secondary"
            onClick={() => navigate(-1)}
            disabled={submitting}
          >
            Cancel
          </button>

          <button
            type="submit"
            className="project-primary"
            disabled={submitting}
          >
            {submitting ? (
              <Loader2
                size={18}
                className="project-spin"
              />
            ) : (
              <Send size={18} />
            )}

            {submitting
              ? "Creating Project..."
              : "Create Project"}
          </button>

        </div>

      </form>

    </main>
  );
}


function MilestonePreview({
  number,
  title,
}: {
  number: number;
  title: string;
}) {
  return (
    <div className="project-milestone-preview-item">

      <span>
        {number}
      </span>

      <strong>
        {title}
      </strong>

    </div>
  );
}