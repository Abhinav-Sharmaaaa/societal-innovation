import { Plus, Upload } from "lucide-react";
import type { ReactNode } from "react";
import type { ProjectEvidence } from "../../../services/projectService";

const formatDate = (value: string | null): string => {
    if (!value) return "Not specified";

    return new Date(value).toLocaleDateString("en-IN", {
        day: "2-digit",
        month: "short",
        year: "numeric",
    });
};

const label = (value: string): string => {
    return value.replaceAll("_", " ");
};

const badgeClass = (value: string): string => {
    return value.toLowerCase().replaceAll("_", "-");
};

function SectionTitle({
    icon,
    eyebrow,
    title,
    action,
}: {
    icon: ReactNode;
    eyebrow: string;
    title: string;
    action?: ReactNode;
}) {
    return (
        <div className="project-section-heading compact">
            <div className="project-section-title-left">
                <div className="project-section-heading-icon">
                    {icon}
                </div>

                <div>
                    <div className="project-section-eyebrow">
                        {eyebrow}
                    </div>
                    <h2>{title}</h2>
                </div>
            </div>

            {action && (
                <div className="project-section-heading-action">
                    {action}
                </div>
            )}
        </div>
    );
}

function EmptySection({ text }: { text: string }) {
    return (
        <div className="project-section-empty">
            {text}
        </div>
    );
}

export interface ProjectEvidenceProps {
    evidence: ProjectEvidence[];
    onCreate: () => void;
}

export default function ProjectEvidence({
    evidence,
    onCreate,
}: ProjectEvidenceProps) {
    return (
        <section className="project-section project-section-card">
            <SectionTitle
                icon={<Upload size={18} />}
                eyebrow="EVIDENCE"
                title="Project evidence"
                action={
                    <button
                        type="button"
                        className="project-secondary-button project-small-button"
                        onClick={onCreate}
                    >
                        <Plus size={15} />
                        Add Evidence
                    </button>
                }
            />

            {evidence.length === 0 ? (
                <EmptySection text="No evidence has been uploaded yet." />
            ) : (
                <div className="project-list">
                    {evidence.map((item) => (
                        <div
                            key={item.id}
                            className="project-list-item stacked"
                        >
                            <div className="project-list-item-main">
                                <div>
                                    <strong>{item.title}</strong>

                                    {item.description ? (
                                        <p>{item.description}</p>
                                    ) : null}
                                </div>

                                <span
                                    className={`project-mini-badge ${badgeClass(
                                        item.evidence_type,
                                    )}`}
                                >
                                    {label(item.evidence_type)}
                                </span>
                            </div>

                            <div className="project-list-item-bottom">
                                {item.report_id ? (
                                    <span>Report #{item.report_id}</span>
                                ) : (
                                    <span>Project evidence</span>
                                )}

                                <span>
                                    Added {formatDate(item.created_at)}
                                </span>

                                {item.external_url || item.file_url ? (
                                    <a
                                        className="project-link"
                                        href={
                                            item.external_url ||
                                            item.file_url ||
                                            "#"
                                        }
                                        target="_blank"
                                        rel="noreferrer"
                                    >
                                        Open evidence
                                    </a>
                                ) : null}
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </section>
    );
}