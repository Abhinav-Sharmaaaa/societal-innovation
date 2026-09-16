import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import {
  Building2,
  CheckCircle2,
  GraduationCap,
  Landmark,
  PlusCircle,
  ShieldCheck,
  Users,
  XCircle,
} from "lucide-react";
import {
  createOfficialUser,
  createOrganization,
  listOrganizations,
  type OfficialRole,
  type OfficialUserCreate,
  type Organization,
  type OrganizationCreate,
  type OrganizationType,
} from "../../services/adminService";
import "./AdminDashboard.css";


// ============================================================
// Role → org type compatibility (mirrors backend logic)
// ============================================================

const ROLE_ORG_TYPES: Record<OfficialRole, OrganizationType[]> = {
  REVIEW_OFFICER:      ["MUNICIPALITY", "GOVERNMENT_DEPARTMENT"],
  MUNICIPALITY_OFFICER:["MUNICIPALITY"],
  GOVERNMENT_OFFICER:  ["GOVERNMENT_DEPARTMENT"],
  UNIVERSITY_ADMIN:    ["UNIVERSITY"],
  FACULTY:             ["UNIVERSITY"],
  STUDENT:             ["UNIVERSITY"],
  INDUSTRY_ADMIN:      ["INDUSTRY"],
  INDUSTRY_MEMBER:     ["INDUSTRY"],
};

const ROLE_LABELS: Record<OfficialRole, string> = {
  REVIEW_OFFICER:       "Review Officer",
  MUNICIPALITY_OFFICER: "Municipality Officer",
  GOVERNMENT_OFFICER:   "Government Officer",
  UNIVERSITY_ADMIN:     "University Admin",
  FACULTY:              "Faculty",
  STUDENT:              "Student",
  INDUSTRY_ADMIN:       "Industry Admin",
  INDUSTRY_MEMBER:      "Industry Member",
};

const ORG_TYPE_LABELS: Record<OrganizationType, string> = {
  MUNICIPALITY:          "Municipality",
  GOVERNMENT_DEPARTMENT: "Government Department",
  UNIVERSITY:            "University",
  INDUSTRY:              "Industry",
};

const ORG_TYPE_ICON: Record<OrganizationType, React.ElementType> = {
  MUNICIPALITY:          Landmark,
  GOVERNMENT_DEPARTMENT: ShieldCheck,
  UNIVERSITY:            GraduationCap,
  INDUSTRY:              Building2,
};


// ============================================================
// Toast
// ============================================================

interface Toast {
  id: number;
  type: "success" | "error";
  message: string;
}

let toastId = 0;


// ============================================================
// Component
// ============================================================

type ActiveTab = "users" | "organizations";

export default function AdminDashboard() {
  const [tab, setTab] = useState<ActiveTab>("users");

  // ---- Toast ----
  const [toasts, setToasts] = useState<Toast[]>([]);

  function addToast(type: "success" | "error", message: string) {
    const id = ++toastId;
    setToasts((p) => [...p, { id, type, message }]);
    setTimeout(() =>
      setToasts((p) => p.filter((t) => t.id !== id)),
      4000
    );
  }

  // ---- Organizations ----
  const [orgs, setOrgs] = useState<Organization[]>([]);
  const [orgsLoading, setOrgsLoading] = useState(true);

  async function loadOrgs() {
    try {
      setOrgsLoading(true);
      const data = await listOrganizations();
      setOrgs(data);
    } catch {
      addToast("error", "Failed to load organizations.");
    } finally {
      setOrgsLoading(false);
    }
  }

  useEffect(() => { loadOrgs(); }, []);


  // ===========================================================
  // Create Organization Form State
  // ===========================================================

  const [orgForm, setOrgForm] = useState<OrganizationCreate>({
    name: "",
    organization_type: "GOVERNMENT_DEPARTMENT",
    description: "",
    district: "",
    locality: "",
    state: "",
    email: "",
    phone: "",
    website: "",
  });
  const [orgLoading, setOrgLoading] = useState(false);

  async function handleCreateOrg(e: FormEvent) {
    e.preventDefault();
    setOrgLoading(true);
    try {
      const created = await createOrganization({
        ...orgForm,
        description: orgForm.description || undefined,
        district:    orgForm.district    || undefined,
        locality:    orgForm.locality    || undefined,
        state:       orgForm.state       || undefined,
        email:       orgForm.email       || undefined,
        phone:       orgForm.phone       || undefined,
        website:     orgForm.website     || undefined,
      });
      setOrgs((prev) => [created, ...prev]);
      setOrgForm({
        name: "", organization_type: "GOVERNMENT_DEPARTMENT",
        description: "", district: "", locality: "", state: "",
        email: "", phone: "", website: "",
      });
      addToast("success", `Organisation "${created.name}" created successfully.`);
    } catch (err: any) {
      addToast("error", err.response?.data?.detail || "Failed to create organisation.");
    } finally {
      setOrgLoading(false);
    }
  }


  // ===========================================================
  // Create Official User Form State
  // ===========================================================

  const [userForm, setUserForm] = useState<OfficialUserCreate>({
    full_name: "",
    email: "",
    phone: "",
    password: "",
    role: "GOVERNMENT_OFFICER",
    organization_id: 0,
  });
  const [userLoading, setUserLoading] = useState(false);

  // Filter orgs by role compatibility
  const compatibleOrgs = orgs.filter((o) =>
    ROLE_ORG_TYPES[userForm.role]?.includes(o.organization_type)
  );

  async function handleCreateUser(e: FormEvent) {
    e.preventDefault();

    if (!userForm.organization_id) {
      addToast("error", "Please select an organisation for this user.");
      return;
    }

    setUserLoading(true);
    try {
      const created = await createOfficialUser({
        ...userForm,
        phone: userForm.phone || undefined,
      });
      setUserForm({
        full_name: "", email: "", phone: "", password: "",
        role: "GOVERNMENT_OFFICER", organization_id: 0,
      });
      addToast("success", `Official account for "${created.full_name}" created.`);
    } catch (err: any) {
      addToast("error", err.response?.data?.detail || "Failed to create user account.");
    } finally {
      setUserLoading(false);
    }
  }


  // ===========================================================
  // Render
  // ===========================================================

  return (
    <div className="admin-page">

      {/* ---- Toasts ---- */}
      <div className="admin-toasts" aria-live="polite">
        {toasts.map((t) => (
          <div
            key={t.id}
            className={`admin-toast admin-toast--${t.type}`}
          >
            {t.type === "success"
              ? <CheckCircle2 size={16} />
              : <XCircle size={16} />
            }
            {t.message}
          </div>
        ))}
      </div>


      {/* ---- Page Header ---- */}
      <div className="admin-header">
        <div className="admin-header-icon">
          <ShieldCheck size={22} />
        </div>
        <div>
          <h1>Super Admin Panel</h1>
          <p>
            Manage organisations and create official platform accounts.
            Only SUPER_ADMIN can access this area.
          </p>
        </div>
      </div>


      {/* ---- Tabs ---- */}
      <div className="admin-tabs" role="tablist">
        <button
          role="tab"
          id="tab-users"
          aria-selected={tab === "users"}
          className={`admin-tab ${tab === "users" ? "admin-tab--active" : ""}`}
          onClick={() => setTab("users")}
        >
          <Users size={16} />
          Create Official User
        </button>
        <button
          role="tab"
          id="tab-orgs"
          aria-selected={tab === "organizations"}
          className={`admin-tab ${tab === "organizations" ? "admin-tab--active" : ""}`}
          onClick={() => setTab("organizations")}
        >
          <Building2 size={16} />
          Create Organisation
        </button>
      </div>


      <div className="admin-content">

        {/* ============================================
            TAB: Create Official User
        ============================================ */}

        {tab === "users" && (
          <div className="admin-panel">

            <div className="admin-panel-header">
              <h2>Create Official Account</h2>
              <p>
                Assign a role and link the user to an existing organisation.
                The user will be able to log in immediately after creation.
              </p>
            </div>

            <form
              className="admin-form"
              onSubmit={handleCreateUser}
              id="create-user-form"
            >

              {/* Role selector — shown first so org list auto-filters */}
              <div className="admin-form-group">
                <label htmlFor="user-role">Role</label>
                <select
                  id="user-role"
                  value={userForm.role}
                  onChange={(e) =>
                    setUserForm((p) => ({
                      ...p,
                      role: e.target.value as OfficialRole,
                      organization_id: 0,
                    }))
                  }
                  required
                >
                  {(Object.keys(ROLE_LABELS) as OfficialRole[]).map((r) => (
                    <option key={r} value={r}>{ROLE_LABELS[r]}</option>
                  ))}
                </select>
                <span className="admin-form-hint">
                  Compatible org types: {ROLE_ORG_TYPES[userForm.role].map(t => ORG_TYPE_LABELS[t]).join(", ")}
                </span>
              </div>

              {/* Organisation */}
              <div className="admin-form-group">
                <label htmlFor="user-org">Organisation</label>
                <select
                  id="user-org"
                  value={userForm.organization_id || ""}
                  onChange={(e) =>
                    setUserForm((p) => ({
                      ...p,
                      organization_id: Number(e.target.value),
                    }))
                  }
                  required
                >
                  <option value="">— Select organisation —</option>
                  {compatibleOrgs.length === 0 ? (
                    <option disabled>
                      No compatible organisations found. Create one first →
                    </option>
                  ) : (
                    compatibleOrgs.map((o) => (
                      <option key={o.id} value={o.id}>
                        {o.name} ({ORG_TYPE_LABELS[o.organization_type]})
                      </option>
                    ))
                  )}
                </select>
              </div>

              <div className="admin-form-row">
                {/* Full Name */}
                <div className="admin-form-group">
                  <label htmlFor="user-name">Full Name</label>
                  <input
                    id="user-name"
                    type="text"
                    placeholder="Dr. Priya Sharma"
                    value={userForm.full_name}
                    onChange={(e) => setUserForm((p) => ({ ...p, full_name: e.target.value }))}
                    required
                    minLength={2}
                    maxLength={150}
                  />
                </div>

                {/* Email */}
                <div className="admin-form-group">
                  <label htmlFor="user-email">Email</label>
                  <input
                    id="user-email"
                    type="email"
                    placeholder="official@gov.in"
                    value={userForm.email}
                    onChange={(e) => setUserForm((p) => ({ ...p, email: e.target.value }))}
                    required
                  />
                </div>
              </div>

              <div className="admin-form-row">
                {/* Phone */}
                <div className="admin-form-group">
                  <label htmlFor="user-phone">
                    Phone <span className="admin-optional">Optional</span>
                  </label>
                  <input
                    id="user-phone"
                    type="tel"
                    placeholder="9876543210"
                    value={userForm.phone}
                    onChange={(e) => setUserForm((p) => ({ ...p, phone: e.target.value }))}
                    maxLength={20}
                  />
                </div>

                {/* Password */}
                <div className="admin-form-group">
                  <label htmlFor="user-password">
                    Temporary Password
                  </label>
                  <input
                    id="user-password"
                    type="password"
                    placeholder="Min. 8 characters"
                    value={userForm.password}
                    onChange={(e) => setUserForm((p) => ({ ...p, password: e.target.value }))}
                    required
                    minLength={8}
                  />
                </div>
              </div>

              <button
                type="submit"
                className="admin-btn admin-btn--primary"
                disabled={userLoading}
                id="create-user-submit"
              >
                <PlusCircle size={16} />
                {userLoading ? "Creating account…" : "Create Official Account"}
              </button>

            </form>
          </div>
        )}


        {/* ============================================
            TAB: Create Organisation
        ============================================ */}

        {tab === "organizations" && (
          <div className="admin-panel">

            <div className="admin-panel-header">
              <h2>Create Organisation</h2>
              <p>
                Create a government department, municipality, university, or
                industry organisation. You can then assign official users to it.
              </p>
            </div>

            <form
              className="admin-form"
              onSubmit={handleCreateOrg}
              id="create-org-form"
            >

              <div className="admin-form-row">
                {/* Name */}
                <div className="admin-form-group">
                  <label htmlFor="org-name">Organisation Name</label>
                  <input
                    id="org-name"
                    type="text"
                    placeholder="e.g. Pune Municipal Corporation"
                    value={orgForm.name}
                    onChange={(e) => setOrgForm((p) => ({ ...p, name: e.target.value }))}
                    required
                    minLength={2}
                    maxLength={255}
                  />
                </div>

                {/* Type */}
                <div className="admin-form-group">
                  <label htmlFor="org-type">Organisation Type</label>
                  <select
                    id="org-type"
                    value={orgForm.organization_type}
                    onChange={(e) =>
                      setOrgForm((p) => ({
                        ...p,
                        organization_type: e.target.value as OrganizationType,
                      }))
                    }
                    required
                  >
                    {(Object.keys(ORG_TYPE_LABELS) as OrganizationType[]).map((t) => (
                      <option key={t} value={t}>{ORG_TYPE_LABELS[t]}</option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Description */}
              <div className="admin-form-group">
                <label htmlFor="org-description">
                  Description <span className="admin-optional">Optional</span>
                </label>
                <textarea
                  id="org-description"
                  placeholder="Brief description of this organisation…"
                  value={orgForm.description}
                  onChange={(e) => setOrgForm((p) => ({ ...p, description: e.target.value }))}
                  rows={2}
                />
              </div>

              <div className="admin-form-row">
                <div className="admin-form-group">
                  <label htmlFor="org-district">
                    District <span className="admin-optional">Optional</span>
                  </label>
                  <input
                    id="org-district"
                    type="text"
                    placeholder="Pune"
                    value={orgForm.district}
                    onChange={(e) => setOrgForm((p) => ({ ...p, district: e.target.value }))}
                  />
                </div>

                <div className="admin-form-group">
                  <label htmlFor="org-state">
                    State <span className="admin-optional">Optional</span>
                  </label>
                  <input
                    id="org-state"
                    type="text"
                    placeholder="Maharashtra"
                    value={orgForm.state}
                    onChange={(e) => setOrgForm((p) => ({ ...p, state: e.target.value }))}
                  />
                </div>
              </div>

              <div className="admin-form-row">
                <div className="admin-form-group">
                  <label htmlFor="org-email">
                    Email <span className="admin-optional">Optional</span>
                  </label>
                  <input
                    id="org-email"
                    type="email"
                    placeholder="contact@org.gov.in"
                    value={orgForm.email}
                    onChange={(e) => setOrgForm((p) => ({ ...p, email: e.target.value }))}
                  />
                </div>

                <div className="admin-form-group">
                  <label htmlFor="org-phone">
                    Phone <span className="admin-optional">Optional</span>
                  </label>
                  <input
                    id="org-phone"
                    type="tel"
                    placeholder="020-12345678"
                    value={orgForm.phone}
                    onChange={(e) => setOrgForm((p) => ({ ...p, phone: e.target.value }))}
                  />
                </div>
              </div>

              <button
                type="submit"
                className="admin-btn admin-btn--primary"
                disabled={orgLoading}
                id="create-org-submit"
              >
                <PlusCircle size={16} />
                {orgLoading ? "Creating…" : "Create Organisation"}
              </button>

            </form>


            {/* Existing Orgs List */}
            <div className="admin-org-list">
              <h3>Existing Organisations ({orgs.length})</h3>

              {orgsLoading ? (
                <div className="admin-loading">Loading organisations…</div>
              ) : orgs.length === 0 ? (
                <div className="admin-empty">
                  No organisations yet. Create one above.
                </div>
              ) : (
                <div className="admin-org-grid">
                  {orgs.map((org) => {
                    const Icon = ORG_TYPE_ICON[org.organization_type];
                    return (
                      <div key={org.id} className="admin-org-card">
                        <div className="admin-org-card-header">
                          <div className={`admin-org-icon admin-org-icon--${org.organization_type.toLowerCase()}`}>
                            <Icon size={16} />
                          </div>
                          <div>
                            <strong>{org.name}</strong>
                            <span>{ORG_TYPE_LABELS[org.organization_type]}</span>
                          </div>
                          <span className={`admin-org-status ${org.is_active ? "admin-org-status--active" : "admin-org-status--inactive"}`}>
                            {org.is_active ? "Active" : "Inactive"}
                          </span>
                        </div>
                        {(org.district || org.state) && (
                          <p className="admin-org-location">
                            📍 {[org.district, org.state].filter(Boolean).join(", ")}
                          </p>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>

          </div>
        )}

      </div>

    </div>
  );
}
