import {
  ArrowRight,
  Building2,
  GraduationCap,
  Handshake,
  Lightbulb,
  MapPin,
  ShieldCheck,
  Users,
} from "lucide-react";
import { useNavigate } from "react-router-dom";

import "./LandingPage.css";

export default function LandingPage() {
  const navigate = useNavigate();

  return (
    <div className="landing-page">

      {/* ======================================================
          Navigation
      ====================================================== */}

      <header className="navbar">
        <div className="navbar-container">

          <button
            className="brand"
            onClick={() => navigate("/")}
          >
            <div className="brand-icon">
              <Lightbulb size={22} />
            </div>

            <div>
              <div className="brand-name">
                Societal Innovation
              </div>

              <div className="brand-subtitle">
                Platform
              </div>
            </div>
          </button>

          <nav className="nav-links">
            <a href="#how-it-works">
              How It Works
            </a>

            <a href="#ecosystem">
              Ecosystem
            </a>

            <a href="#impact">
              Impact
            </a>
          </nav>

          <div className="nav-actions">
            <button
              className="btn btn-secondary"
              onClick={() => navigate("/login")}
            >
              Login
            </button>

            <button
              className="btn btn-primary"
              onClick={() => navigate("/register")}
            >
              Get Started
            </button>
          </div>

        </div>
      </header>


      {/* ======================================================
          Hero
      ====================================================== */}

      <main>

        <section className="hero">
          <div className="hero-container">

            <div className="hero-content">

              <div className="hero-badge">
                <span className="hero-badge-dot" />
                AI-powered societal problem solving
              </div>

              <h1>
                Turn
                <span className="hero-highlight">
                  {" societal challenges "}
                </span>
                into measurable impact.
              </h1>

              <p className="hero-description">
                A collaborative platform connecting citizens,
                governments, universities, and industry to
                identify real-world problems, discover the right
                expertise, develop solutions, and create lasting
                social impact.
              </p>

              <div className="hero-actions">

                <button
                  className="btn btn-primary btn-large"
                  onClick={() => navigate("/register")}
                >
                  Report a Challenge
                  <ArrowRight size={19} />
                </button>

                <button
                  className="btn btn-outline btn-large"
                  onClick={() => navigate("/login")}
                >
                  Explore Platform
                </button>

              </div>

              <div className="hero-trust">

                <ShieldCheck size={18} />

                <span>
                  Transparent workflows •
                  Human-reviewed decisions •
                  Measurable outcomes
                </span>

              </div>

            </div>


            {/* ==================================================
                Hero Visual
            ================================================== */}

            <div className="hero-visual">

              <div className="innovation-card">

                <div className="innovation-header">
                  <div>
                    <span className="card-label">
                      LIVE INNOVATION PIPELINE
                    </span>

                    <h3>
                      From Problem to Impact
                    </h3>
                  </div>

                  <div className="live-indicator">
                    <span />
                    Live
                  </div>
                </div>


                <div className="pipeline">

                  <PipelineItem
                    number="01"
                    icon={<Users size={18} />}
                    title="Community"
                    description="Real-world challenge submitted"
                    active
                  />

                  <PipelineConnector />

                  <PipelineItem
                    number="02"
                    icon={<Lightbulb size={18} />}
                    title="AI Triage"
                    description="Classify, prioritize & route"
                    active
                  />

                  <PipelineConnector />

                  <PipelineItem
                    number="03"
                    icon={<GraduationCap size={18} />}
                    title="University"
                    description="Expertise matched to challenge"
                  />

                  <PipelineConnector />

                  <PipelineItem
                    number="04"
                    icon={<Handshake size={18} />}
                    title="Industry"
                    description="Funding, mentoring & deployment"
                  />

                  <PipelineConnector />

                  <PipelineItem
                    number="05"
                    icon={<MapPin size={18} />}
                    title="Impact"
                    description="Verified outcome on ground"
                  />

                </div>

              </div>

            </div>

          </div>
        </section>


        {/* ======================================================
            Ecosystem
        ====================================================== */}

        <section
          id="ecosystem"
          className="section ecosystem-section"
        >

          <div className="section-container">

            <div className="section-heading">
              <span className="section-eyebrow">
                ONE CONNECTED ECOSYSTEM
              </span>

              <h2>
                Everyone has a role in solving
                <br />
                societal challenges.
              </h2>

              <p>
                The platform brings every stakeholder into one
                transparent workflow instead of keeping problems,
                expertise, funding, and implementation disconnected.
              </p>
            </div>


            <div className="ecosystem-grid">

              <EcosystemCard
                icon={<Users size={23} />}
                title="Citizens & Communities"
                text="Report local challenges with location, evidence, and context."
              />

              <EcosystemCard
                icon={<Building2 size={23} />}
                title="Government"
                text="Route issues, assign officers, verify solutions, and track outcomes."
              />

              <EcosystemCard
                icon={<GraduationCap size={23} />}
                title="Universities"
                text="Match societal challenges with faculty, students, labs, and expertise."
              />

              <EcosystemCard
                icon={<Handshake size={23} />}
                title="Industry"
                text="Provide funding, technology, mentorship, manufacturing, and deployment."
              />

            </div>

          </div>

        </section>


        {/* ======================================================
            How It Works
        ====================================================== */}

        <section
          id="how-it-works"
          className="section workflow-section"
        >

          <div className="section-container">

            <div className="section-heading centered">

              <span className="section-eyebrow">
                HOW IT WORKS
              </span>

              <h2>
                One pipeline.
                <br />
                Multiple stakeholders.
                <br />
                Measurable impact.
              </h2>

            </div>


            <div className="workflow-grid">

              <WorkflowStep
                number="01"
                title="Report"
                text="A citizen, community organization, or local body submits a real-world societal challenge."
              />

              <WorkflowStep
                number="02"
                title="Understand"
                text="AI analyses the challenge, identifies its category, severity, urgency, and innovation requirement."
              />

              <WorkflowStep
                number="03"
                title="Route"
                text="The challenge is intelligently routed to the municipality, government, or innovation pipeline."
              />

              <WorkflowStep
                number="04"
                title="Match"
                text="Relevant universities and industry partners are matched based on expertise and capability."
              />

              <WorkflowStep
                number="05"
                title="Build"
                text="Teams develop solutions through proposals, projects, milestones, and real-world testing."
              />

              <WorkflowStep
                number="06"
                title="Measure"
                text="Government verification and impact metrics track whether the solution actually helped."
              />

            </div>

          </div>

        </section>


        {/* ======================================================
            Impact CTA
        ====================================================== */}

        <section
          id="impact"
          className="section cta-section"
        >

          <div className="cta-container">

            <div>
              <span className="section-eyebrow">
                START THE PIPELINE
              </span>

              <h2>
                Have a problem worth solving?
              </h2>

              <p>
                Put it in front of the people who can help turn
                it into a real solution.
              </p>
            </div>

            <button
              className="btn btn-primary btn-large"
              onClick={() => navigate("/register")}
            >
              Report a Challenge
              <ArrowRight size={19} />
            </button>

          </div>

        </section>

      </main>


      {/* ======================================================
          Footer
      ====================================================== */}

      <footer className="footer">

        <div className="footer-container">

          <div>
            <div className="footer-brand">
              Societal Innovation Platform
            </div>

            <p>
              Connecting problems with people,
              technology, and resources.
            </p>
          </div>

          <div className="footer-meta">
            Built for collaborative societal innovation
          </div>

        </div>

      </footer>

    </div>
  );
}


/* ============================================================
   Pipeline Item
   ============================================================ */

interface PipelineItemProps {
  number: string;
  icon: React.ReactNode;
  title: string;
  description: string;
  active?: boolean;
}


function PipelineItem({
  number,
  icon,
  title,
  description,
  active = false,
}: PipelineItemProps) {
  return (
    <div
      className={`pipeline-item ${
        active ? "pipeline-item-active" : ""
      }`}
    >
      <div className="pipeline-number">
        {number}
      </div>

      <div className="pipeline-icon">
        {icon}
      </div>

      <div className="pipeline-content">
        <h4>{title}</h4>
        <p>{description}</p>
      </div>
    </div>
  );
}


/* ============================================================
   Pipeline Connector
   ============================================================ */

function PipelineConnector() {
  return (
    <div className="pipeline-connector">
      <div />
    </div>
  );
}


/* ============================================================
   Ecosystem Card
   ============================================================ */

interface EcosystemCardProps {
  icon: React.ReactNode;
  title: string;
  text: string;
}


function EcosystemCard({
  icon,
  title,
  text,
}: EcosystemCardProps) {
  return (
    <div className="ecosystem-card">

      <div className="ecosystem-icon">
        {icon}
      </div>

      <h3>{title}</h3>

      <p>{text}</p>

    </div>
  );
}


/* ============================================================
   Workflow Step
   ============================================================ */

interface WorkflowStepProps {
  number: string;
  title: string;
  text: string;
}


function WorkflowStep({
  number,
  title,
  text,
}: WorkflowStepProps) {
  return (
    <div className="workflow-step">

      <span className="workflow-number">
        {number}
      </span>

      <h3>{title}</h3>

      <p>{text}</p>

    </div>
  );
}