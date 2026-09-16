import { FileCheck2, Plus } from "lucide-react";
import type {
    Project,
    ProjectDeliverable,
    ProjectMilestone,
} from "../../../services/projectService";

type Props = {
    project: Project;
    milestones: ProjectMilestone[];
    deliverables: ProjectDeliverable[];
    onCreate: () => void;
    onSubmit: (deliverable: ProjectDeliverable) => void;
    onReview: (deliverable: ProjectDeliverable) => void;
};

function formatDate(value: string | null): string {
    if (!value) return "Not specified";

    return new Date(value).toLocaleDateString("en-IN", {
        day: "2-digit",
        month: "short",
        year: "numeric",
    });
}

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
    action,
}: {
    icon: React.ReactNode;
    eyebrow: string;
    title: string;
    action?: React.ReactNode;
}) {
    return (
        <div className="project-section-heading compact">
            <div className="project-section-title-left">
                <div className="project-section-heading-icon">{icon}</div>

                <div>
                    <span className="project-section-eyebrow">{eyebrow}</span>
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
            <span>{text}</span>
        </div>
    );
}

export default function ProjectDeliverables({
    project,
    milestones,
    deliverables,
    onCreate,
    onSubmit,
    onReview,
}: Props) {
    const canCreate =
        milestones.length > 0 &&
        project.status !== "COMPLETED" &&
        project.status !== "CANCELLED";

    return (
        <section className="project-section project-section-card">
            <SectionTitle
                icon={<FileCheck2 size={18} />}
                eyebrow="DELIVERABLES"
                title="Project deliverables"
                action={
                    <button
                        type="button"
                        className="project-primary-button project-section-action"
                        onClick={onCreate}
                        disabled={!canCreate}
                    >
                        <Plus size={16} />
                        Add Deliverable
                    </button>
                }
            />

            {deliverables.length === 0 ? (
                <EmptySection text="No deliverables have been created yet." />
            ) : (
                <div className="project-list">
                    {deliverables.map((item) => (
                        <div
                            key={item.id}
                            className="project-deliverable-item"
                        >
                            <div className="project-deliverable-main">
                                <div>
                                    <strong>{item.title}</strong>

                                    <span>
                                        Due {formatDate(item.due_date)}
                                    </span>

                                    {item.description && (
                                        <p>{item.description}</p>
                                    )}
                                </div>

                                <span
                                    className={`project-mini-badge ${badgeClass(
                                        item.status,
                                    )}`}
                                >
                                    {label(item.status)}
                                </span>
                            </div>

                            <div className="project-deliverable-actions">
                                <div className="project-deliverable-meta">
                                    <span>
                                        {item.is_mandatory
                                            ? "Mandatory"
                                            : "Optional"}
                                    </span>

                                    {item.submitted_at && (
                                        <span>
                                            Submitted{" "}
                                            {formatDate(item.submitted_at)}
                                        </span>
                                    )}

                                    {item.approved_at && (
                                        <span>
                                            Approved{" "}
                                            {formatDate(item.approved_at)}
                                        </span>
                                    )}
                                </div>

                                {(item.status === "PENDING" ||
                                    item.status === "IN_PROGRESS" ||
                                    item.status === "REJECTED") && (
                                        <button
                                            type="button"
                                            className="project-secondary-button project-action-button"
                                            onClick={() => onSubmit(item)}
                                        >
                                            Submit
                                        </button>
                                    )}

                                {(item.status === "SUBMITTED" ||
                                    item.status === "OVERDUE") && (
                                        <button
                                            type="button"
                                            className="project-primary-button project-action-button"
                                            onClick={() => onReview(item)}
                                        >
                                            Review
                                        </button>
                                    )}
                            </div>

                            {item.submission_reference && (
                                <div className="project-deliverable-reference">
                                    <strong>Submission reference</strong>
                                    <span>{item.submission_reference}</span>
                                </div>
                            )}

                            {item.review_remarks && (
                                <div className="project-deliverable-reference">
                                    <strong>Review remarks</strong>
                                    <span>{item.review_remarks}</span>
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            )}
        </section>
    );
}