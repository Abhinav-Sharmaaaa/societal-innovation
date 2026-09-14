import {
    ArrowLeft,
    ChevronRight,
    FileText,
    Loader2,
    Search,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import {
    getRFPProposals,
    type UniversityProposal,
} from "../../services/proposalEvaluationService";

import {
  innovationService,
} from "../../services/innovationService";

import "./RFPProposalsPage.css";

interface RFPBasic {
    id: number;
    title: string;
    status: string;
}

export default function RFPProposalsPage() {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();

    const [rfp, setRfp] = useState<RFPBasic | null>(null);
    const [proposals, setProposals] = useState<UniversityProposal[]>(
        []
    );

    const [search, setSearch] = useState("");
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        const load = async () => {
            if (!id) {
                setError("Invalid RFP ID.");
                setLoading(false);
                return;
            }

            try {
                setLoading(true);
                setError("");

                const rfpId = Number(id);

                const [rfpData, proposalData] = await Promise.all([
                    innovationService.getRFP(rfpId),
                    getRFPProposals(rfpId),
                ]);

                setRfp({
                    id: rfpData.id,
                    title: rfpData.title,
                    status: rfpData.status,
                });

                setProposals(proposalData);
            } catch (err: any) {
                setError(
                    err?.response?.data?.detail ||
                    "Failed to load university proposals."
                );
            } finally {
                setLoading(false);
            }
        };

        void load();
    }, [id]);

    const filteredProposals = useMemo(() => {
        const query = search.trim().toLowerCase();

        if (!query) {
            return proposals;
        }

        return proposals.filter((proposal) => {
            return (
                proposal.title.toLowerCase().includes(query) ||
                proposal.solution.toLowerCase().includes(query) ||
                proposal.technical_approach
                    .toLowerCase()
                    .includes(query)
            );
        });
    }, [proposals, search]);

    if (loading) {
        return (
            <main className="rfp-proposals-page">
                <div className="rfp-proposals-state">
                    <Loader2 className="proposal-spinner" size={28} />
                    <p>Loading university proposals...</p>
                </div>
            </main>
        );
    }

    if (error || !rfp) {
        return (
            <main className="rfp-proposals-page">
                <div className="rfp-proposals-state rfp-proposals-error">
                    <h2>Unable to load proposals</h2>
                    <p>{error || "RFP not found."}</p>

                    <button
                        type="button"
                        onClick={() => navigate(-1)}
                        className="proposal-list-primary"
                    >
                        <ArrowLeft size={17} />
                        Go Back
                    </button>
                </div>
            </main>
        );
    }

    return (
        <main className="rfp-proposals-page">

            <div className="rfp-proposals-header">

                <button
                    type="button"
                    className="proposal-list-back"
                    onClick={() => navigate(`/government/rfps/${rfp.id}`)}
                >
                    <ArrowLeft size={18} />
                    Back to RFP
                </button>

                <div>
                    <span className="proposal-list-eyebrow">
                        PROPOSAL EVALUATION
                    </span>

                    <h1>{rfp.title}</h1>

                    <p>
                        Review university submissions and select the strongest
                        proposal for implementation.
                    </p>
                </div>

            </div>


            <section className="proposal-summary">

                <div>
                    <span>RFP ID</span>
                    <strong>#{rfp.id}</strong>
                </div>

                <div>
                    <span>RFP Status</span>
                    <strong>{rfp.status.replaceAll("_", " ")}</strong>
                </div>

                <div>
                    <span>Total Proposals</span>
                    <strong>{proposals.length}</strong>
                </div>

                <div>
                    <span>Awaiting Evaluation</span>
                    <strong>
                        {
                            proposals.filter(
                                (proposal) =>
                                    proposal.status === "SUBMITTED"
                            ).length
                        }
                    </strong>
                </div>

            </section>


            <div className="proposal-search">

                <Search size={18} />

                <input
                    type="text"
                    value={search}
                    onChange={(event) =>
                        setSearch(event.target.value)
                    }
                    placeholder="Search proposals..."
                />

            </div>


            {filteredProposals.length === 0 ? (
                <div className="rfp-proposals-state">
                    <FileText size={40} />
                    <h2>No proposals found</h2>
                    <p>
                        {proposals.length === 0
                            ? "No university proposals have been submitted for this RFP yet."
                            : "No proposals match your search."}
                    </p>
                </div>
            ) : (
                <div className="proposal-list">

                    {filteredProposals.map((proposal) => (

                        <article
                            key={proposal.id}
                            className="proposal-list-card"
                        >

                            <div className="proposal-list-card-main">

                                <div className="proposal-list-icon">
                                    <FileText size={21} />
                                </div>

                                <div>
                                    <span className="proposal-list-id">
                                        PROPOSAL #{proposal.id}
                                    </span>

                                    <h2>{proposal.title}</h2>

                                    <p>
                                        {proposal.solution.length > 220
                                            ? `${proposal.solution.slice(0, 220)}...`
                                            : proposal.solution}
                                    </p>
                                </div>

                            </div>


                            <div className="proposal-list-meta">

                                <div>
                                    <span>Status</span>

                                    <strong
                                        className={`proposal-status proposal-status-${proposal.status.toLowerCase()}`}
                                    >
                                        {proposal.status.replaceAll("_", " ")}
                                    </strong>
                                </div>

                                <div>
                                    <span>Estimated Cost</span>

                                    <strong>
                                        {proposal.estimated_cost !== null
                                            ? `₹${proposal.estimated_cost.toLocaleString()}`
                                            : "Not specified"}
                                    </strong>
                                </div>

                                <div>
                                    <span>Timeline</span>

                                    <strong>
                                        {proposal.expected_timeline_days
                                            ? `${proposal.expected_timeline_days} days`
                                            : "Not specified"}
                                    </strong>
                                </div>

                            </div>


                            <div className="proposal-list-actions">

                                <button
                                    type="button"
                                    className="proposal-list-primary"
                                    onClick={() =>
                                        navigate(
                                            `/government/proposals/${proposal.id}/evaluate`
                                        )
                                    }
                                >
                                    Review Proposal
                                    <ChevronRight size={17} />
                                </button>

                            </div>

                        </article>

                    ))}

                </div>
            )}

        </main>
    );
}