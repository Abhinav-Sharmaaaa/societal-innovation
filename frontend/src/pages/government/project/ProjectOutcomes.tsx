import { Target } from "lucide-react";

import type { ProjectOutcome } from "../../../services/projectService";

function label(value: string): string {
  return value.replaceAll("_", " ");
}

function badgeClass(value: string): string {
  return value.toLowerCase().replaceAll("_", "-");
}

function SectionTitle({
  icon,
  eyebrow,
  title,
}: {
  icon: React.ReactNode;
  eyebrow: string;
  title: string;
}) {
  return (
    <div className="project-section-heading compact">
      <div className="project-section-title-left">
        <div className="project-section-heading-icon">
          {icon}
        </div>

        <div>
          <span className="project-section-eyebrow">
            {eyebrow}
          </span>

          <h2>{title}</h2>
        </div>
      </div>
    </div>
  );
}

function EmptySection({ text }: { text: string }) {
  return (
    <div className="project-section-empty">
      <span>{text}</span>
    </div>
  );
}

interface ProjectOutcomesProps {
  outcomes: ProjectOutcome[];
}

export default function ProjectOutcomes({
  outcomes,
}: ProjectOutcomesProps) {
  return (
    <section className="project-section">
      <SectionTitle
        icon={<Target size={18} />}
        eyebrow="IMPACT"
        title="Project outcomes"
      />

      {outcomes.length === 0 ? (
        <EmptySection
          text="No project outcomes have been submitted yet."
        />
      ) : (
        <div className="project-outcome-grid">
          {outcomes.map((outcome) => (
            <div
              key={outcome.id}
              className="project-outcome-card"
            >
              <div className="project-outcome-top">
                <div>
                  <h3>{outcome.title}</h3>
                  <p>{outcome.description}</p>
                </div>

                <span
                  className={`project-mini-badge ${badgeClass(
                    outcome.status,
                  )}`}
                >
                  {label(outcome.status)}
                </span>
              </div>

              <div className="project-outcome-metrics">
                {outcome.beneficiary_count !== null && (
                  <div>
                    <span>Beneficiaries</span>

                    <strong>
                      {outcome.beneficiary_count.toLocaleString(
                        "en-IN",
                      )}
                    </strong>
                  </div>
                )}

                {outcome.baseline_value !== null && (
                  <div>
                    <span>Baseline</span>
                    <strong>
                      {outcome.baseline_value}
                    </strong>
                  </div>
                )}

                {outcome.target_value !== null && (
                  <div>
                    <span>Target</span>
                    <strong>
                      {outcome.target_value}
                    </strong>
                  </div>
                )}

                {outcome.achieved_value !== null && (
                  <div>
                    <span>Achieved</span>
                    <strong>
                      {outcome.achieved_value}
                    </strong>
                  </div>
                )}

                {outcome.impact_score !== null && (
                  <div>
                    <span>Impact Score</span>

                    <strong>
                      {outcome.impact_score}/100
                    </strong>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}