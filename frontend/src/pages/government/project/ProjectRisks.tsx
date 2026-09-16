import { ShieldAlert } from "lucide-react";

import type { ProjectRisk } from "../../../services/projectService";

import type { ReactNode } from "react";

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
  icon: ReactNode;
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

interface ProjectRisksProps {
  latestRisk: ProjectRisk | null;
}

export default function ProjectRisks({
  latestRisk,
}: ProjectRisksProps) {
  return (
    <section className="project-section">
      <SectionTitle
        icon={<ShieldAlert size={18} />}
        eyebrow="RISK MONITORING"
        title="Execution risk"
      />

      {!latestRisk ? (
        <div className="project-risk-empty">
          <ShieldAlert size={24} />

          <div>
            <strong>No risk assessment available</strong>

            <p>
              A project risk assessment has not been generated
              yet.
            </p>
          </div>
        </div>
      ) : (
        <div className="project-risk-card">
          <div className="project-risk-score">
            <span>Risk Score</span>

            <strong>
              {Math.round(latestRisk.risk_score)}
              <small>/100</small>
            </strong>
          </div>

          <div className="project-risk-content">
            <div className="project-risk-header">
              <div>
                <span className="project-risk-eyebrow">
                  CURRENT LEVEL
                </span>

                <h3>
                  {label(latestRisk.risk_level)}
                </h3>
              </div>

              <span
                className={`project-health-badge ${badgeClass(
                  latestRisk.risk_level,
                )}`}
              >
                {label(latestRisk.status)}
              </span>
            </div>

            <p>{latestRisk.description}</p>

            {latestRisk.detected_factors && (
              <div className="project-risk-factors">
                <strong>Detected factors</strong>

                <pre>
                  {latestRisk.detected_factors}
                </pre>
              </div>
            )}

            {latestRisk.recommended_action && (
              <div className="project-risk-action">
                <strong>Recommended action</strong>

                <p>
                  {latestRisk.recommended_action}
                </p>
              </div>
            )}
          </div>
        </div>
      )}
    </section>
  );
}