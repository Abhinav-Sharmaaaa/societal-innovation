import { FileCheck2, FileText, Plus } from "lucide-react";
import type { ReactNode } from "react";

import type { ProjectReport } from "../../../services/projectService";

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

export interface ProjectReportsProps {
    reports: ProjectReport[];
    onCreate: () => void;
    onReview: (report: ProjectReport) => void;
}

export default function ProjectReports({
    reports,
    onCreate,
    onReview,
}: ProjectReportsProps) {
    return (
        <section className="project-section project-section-card">
            <SectionTitle
                icon={<FileText size={18} />}
                eyebrow="REPORTING"
                title="Reports"
                action={
                    <button
                        type="button"
                        className="project-secondary-button project-small-button"
                        onClick={onCreate}
                    >
                        <Plus size={15} />
                        Add Report
                    </button>
                }
            />

            {reports.length === 0 ? (
                <EmptySection text="No reports have been submitted yet." />
            ) : (
                <div className="project-list">
                    {reports.map((report) => (
                        <div
                            key={report.id}
                            className="project-list-item stacked"
                        >
                            <div>
                                <div className="project-report-heading-row">
                                    <strong>{report.title}</strong>

                                    <span
                                        className={`project-mini-badge ${badgeClass(
                                            report.status,
                                        )}`}
                                    >
                                        {label(report.status)}
                                    </span>
                                </div>

                                <p>{report.summary}</p>

                                <div className="project-list-item-bottom">
                                    <span>
                                        {label(report.report_type)}
                                    </span>

                                    {report.milestone_id ? (
                                        <span>
                                            Milestone #{report.milestone_id}
                                        </span>
                                    ) : null}

                                    <span>
                                        Created {formatDate(report.created_at)}
                                    </span>
                                </div>

                                {report.review_remarks ? (
                                    <div className="project-form-info">
                                        <strong>Review remarks:</strong>{" "}
                                        {report.review_remarks}
                                    </div>
                                ) : null}
                            </div>

                            {(report.status === "SUBMITTED" ||
                                report.status === "UNDER_REVIEW") && (
                                    <div className="project-list-item-actions">
                                        <button
                                            type="button"
                                            className="project-small-button"
                                            onClick={() => onReview(report)}
                                        >
                                            <FileCheck2 size={14} />
                                            Review
                                        </button>
                                    </div>
                                )}
                        </div>
                    ))}
                </div>
            )}
        </section>
    );
}