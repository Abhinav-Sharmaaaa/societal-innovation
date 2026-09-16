import { CheckCircle2 } from "lucide-react";
import type { ProjectMilestone } from "../../../services/projectService";

type Props = {
    milestones: ProjectMilestone[];
    onUpdate: (milestone: ProjectMilestone) => void;
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

export default function ProjectMilestones({
    milestones,
    onUpdate,
}: Props) {
    return (
        <section className="project-section">
            <div className="project-section-heading">
                <div>
                    <span className="project-section-eyebrow">
                        MILESTONES
                    </span>

                    <h2>Execution timeline</h2>

                    <p>
                        Track and update progress across each automatically
                        planned project milestone.
                    </p>
                </div>
            </div>

            <div className="project-milestone-list">
                {milestones.length === 0 ? (
                    <div className="project-section-empty">
                        <span>
                            No milestones have been created for this project.
                        </span>
                    </div>
                ) : (
                    milestones.map((milestone, index) => (
                        <div
                            key={milestone.id}
                            className="project-milestone-row"
                        >
                            <div className="project-milestone-line">
                                <div
                                    className={`project-milestone-marker ${badgeClass(
                                        milestone.status,
                                    )}`}
                                >
                                    {milestone.status === "COMPLETED" ? (
                                        <CheckCircle2 size={16} />
                                    ) : (
                                        <span>{index + 1}</span>
                                    )}
                                </div>

                                {index !== milestones.length - 1 && (
                                    <div className="project-milestone-connector" />
                                )}
                            </div>

                            <div className="project-milestone-content">
                                <div className="project-milestone-header">
                                    <div>
                                        <h3>{milestone.title}</h3>
                                        <span>{milestone.milestone_type}</span>
                                    </div>

                                    <div className="project-milestone-right">
                                        <strong>
                                            {Math.round(
                                                milestone.progress_percentage,
                                            )}
                                            %
                                        </strong>

                                        <span
                                            className={`project-mini-badge ${badgeClass(
                                                milestone.status,
                                            )}`}
                                        >
                                            {label(milestone.status)}
                                        </span>

                                        <button
                                            type="button"
                                            className="project-milestone-edit-button"
                                            onClick={() => onUpdate(milestone)}
                                        >
                                            Update
                                        </button>
                                    </div>
                                </div>

                                <p>
                                    {milestone.description ||
                                        "No milestone description available."}
                                </p>

                                <div className="project-milestone-meta">
                                    <span>
                                        Start: {formatDate(milestone.start_date)}
                                    </span>

                                    <span>
                                        Due: {formatDate(milestone.due_date)}
                                    </span>

                                    {milestone.completed_at && (
                                        <span>
                                            Completed:{" "}
                                            {formatDate(milestone.completed_at)}
                                        </span>
                                    )}
                                </div>

                                {milestone.deliverables && (
                                    <div className="project-milestone-deliverables">
                                        <strong>Expected deliverables</strong>
                                        <span>{milestone.deliverables}</span>
                                    </div>
                                )}

                                {milestone.completion_remarks && (
                                    <div className="project-milestone-deliverables">
                                        <strong>Latest remarks</strong>
                                        <span>
                                            {milestone.completion_remarks}
                                        </span>
                                    </div>
                                )}
                            </div>
                        </div>
                    ))
                )}
            </div>
        </section>
    );
}