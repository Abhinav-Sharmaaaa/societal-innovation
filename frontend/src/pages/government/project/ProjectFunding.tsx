import {
    AlertCircle,
    CheckCircle2,
    Landmark,
    Loader2,
    Plus,
} from "lucide-react";
import type { ReactNode } from "react";
import type {
    ProjectFundingSummary,
    ProjectFundingTransaction,
} from "../../../services/projectService";

const formatDate = (value: string | null): string => {
    if (!value) return "Not specified";

    return new Date(value).toLocaleDateString("en-IN", {
        day: "2-digit",
        month: "short",
        year: "numeric",
    });
};

const formatBudget = (value: number | null): string => {
    if (value == null) return "Not specified";

    return new Intl.NumberFormat("en-IN", {
        style: "currency",
        currency: "INR",
        maximumFractionDigits: 0,
    }).format(value);
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

function FundingMetric({
    label: metricLabel,
    value,
    highlight = false,
}: {
    label: string;
    value: number;
    highlight?: boolean;
}) {
    return (
        <div
            className={`project-funding-metric ${highlight ? "highlight" : ""
                }`}
        >
            <span>{metricLabel}</span>
            <strong>{formatBudget(value)}</strong>
        </div>
    );
}

export interface ProjectFundingProps {
    projectStatus: string;
    funding: ProjectFundingSummary | null;
    transactions: ProjectFundingTransaction[];
    fundingError: string;
    actionId: number | null;
    onCreate: () => void;
    onApprove: (id: number) => void | Promise<void>;
    onReject: (id: number) => void | Promise<void>;
    onComplete: (id: number) => void | Promise<void>;
}

export default function ProjectFunding({
    projectStatus,
    funding,
    transactions,
    fundingError,
    actionId,
    onCreate,
    onApprove,
    onReject,
    onComplete,
}: ProjectFundingProps) {
    const isProjectClosed =
        projectStatus === "COMPLETED" ||
        projectStatus === "CANCELLED";

    return (
        <section className="project-section project-section-card">
            <SectionTitle
                icon={<Landmark size={18} />}
                eyebrow="FUNDING"
                title="Funding management"
                action={
                    <button
                        type="button"
                        className="project-primary-button project-section-action"
                        onClick={onCreate}
                        disabled={isProjectClosed}
                    >
                        <Plus size={16} />
                        Add Transaction
                    </button>
                }
            />

            {!funding ? (
                <EmptySection text="Funding information unavailable." />
            ) : (
                <>
                    <div className="project-funding-grid">
                        <FundingMetric
                            label="Allocated"
                            value={funding.allocated}
                        />

                        <FundingMetric
                            label="Disbursed"
                            value={funding.disbursed}
                        />

                        <FundingMetric
                            label="Utilized"
                            value={funding.utilized}
                        />

                        <FundingMetric
                            label="Refunded"
                            value={funding.refunded}
                        />

                        <FundingMetric
                            label="Remaining"
                            value={funding.remaining}
                            highlight
                        />
                    </div>

                    <div className="project-funding-transactions">
                        <div className="project-subsection-heading">
                            <div>
                                <span className="project-section-eyebrow">
                                    TRANSACTIONS
                                </span>
                                <h3>Funding activity</h3>
                            </div>
                        </div>

                        {fundingError && (
                            <div className="project-inline-error">
                                <AlertCircle size={16} />
                                <span>{fundingError}</span>
                            </div>
                        )}

                        {transactions.length === 0 ? (
                            <EmptySection text="No funding transactions have been recorded yet." />
                        ) : (
                            <div className="project-list">
                                {transactions.map((transaction) => (
                                    <div
                                        key={transaction.id}
                                        className="project-funding-transaction"
                                    >
                                        <div className="project-funding-transaction-main">
                                            <div className="project-funding-transaction-title">
                                                <strong>
                                                    {label(transaction.transaction_type)}
                                                </strong>

                                                <span>
                                                    {formatBudget(transaction.amount)}
                                                </span>
                                            </div>

                                            <p>
                                                {transaction.description ||
                                                    "No transaction description provided."}
                                            </p>

                                            <div className="project-funding-meta">
                                                <span>
                                                    Ref:{" "}
                                                    {transaction.reference_number ||
                                                        "Not provided"}
                                                </span>

                                                <span>
                                                    {formatDate(
                                                        transaction.transaction_date,
                                                    )}
                                                </span>

                                                <span>
                                                    Created by user #
                                                    {transaction.created_by}
                                                </span>
                                            </div>
                                        </div>

                                        <div className="project-funding-transaction-actions">
                                            <span
                                                className={`project-mini-badge ${badgeClass(
                                                    transaction.status,
                                                )}`}
                                            >
                                                {label(transaction.status)}
                                            </span>

                                            {transaction.status === "PENDING" && (
                                                <>
                                                    <button
                                                        type="button"
                                                        className="project-small-button"
                                                        onClick={() =>
                                                            void onApprove(transaction.id)
                                                        }
                                                        disabled={actionId === transaction.id}
                                                    >
                                                        {actionId === transaction.id ? (
                                                            <Loader2
                                                                size={14}
                                                                className="spin"
                                                            />
                                                        ) : (
                                                            <CheckCircle2 size={14} />
                                                        )}
                                                        Approve
                                                    </button>

                                                    <button
                                                        type="button"
                                                        className="project-small-button danger"
                                                        onClick={() =>
                                                            void onReject(transaction.id)
                                                        }
                                                        disabled={actionId === transaction.id}
                                                    >
                                                        Reject
                                                    </button>
                                                </>
                                            )}

                                            {transaction.status === "APPROVED" && (
                                                <button
                                                    type="button"
                                                    className="project-small-button"
                                                    onClick={() =>
                                                        void onComplete(transaction.id)
                                                    }
                                                    disabled={actionId === transaction.id}
                                                >
                                                    {actionId === transaction.id ? (
                                                        <Loader2
                                                            size={14}
                                                            className="spin"
                                                        />
                                                    ) : (
                                                        <CheckCircle2 size={14} />
                                                    )}
                                                    Complete
                                                </button>
                                            )}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </>
            )}
        </section>
    );
}