"""
Seed script to create ready-to-use official and citizen test credentials for all roles.
Supports:
- Auto-seeding organizations if missing so organization_id is always linked
- Full user attributes including is_active=True and is_verified=True
- Safe single SUPER_ADMIN enforcement (demoting previous if a new one is assigned)
- Phone collision safety
- Flexible database targeting via --db-url or DATABASE_URL
- Custom user creation via CLI arguments (--email, --password, --role, etc.)
"""

import sys
import os
import argparse
from typing import Optional

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.db.database import Base, SessionLocal as DefaultSessionLocal, engine as default_engine
from app.models.user import User, UserRole
from app.models.organization import Organization
from app.core.security import hash_password
from app.core.config import settings


TEST_USERS = [
    {
        "email": "sa@platfom.com",
        "password": "12345678",
        "full_name": "Super Administrator",
        "role": UserRole.SUPER_ADMIN,
        "phone": "9876543200",
        "org_name": None,
    },
    {
        "email": "citizen@gmail.com",
        "password": "12345678",
        "full_name": "Anil Kumar (Citizen)",
        "role": UserRole.CITIZEN,
        "phone": "9876543211",
        "org_name": None,
    },
    {
        "email": "abhinav2654@gmail.com",
        "password": "11111111",
        "full_name": "Abhinav Sharma",
        "role": UserRole.CITIZEN,
        "phone": "9876543299",
        "org_name": None,
    },
    {
        "email": "abhinav@gmail.com",
        "password": "11111111",
        "full_name": "Abhinav Sharma",
        "role": UserRole.CITIZEN,
        "phone": "9876543298",
        "org_name": None,
    },
    {
        "email": "pwd.dehradun@gov.in",
        "password": "12345678",
        "full_name": "Er. Rajesh Verma (PWD Officer)",
        "role": UserRole.GOVERNMENT_OFFICER,
        "phone": "9876543212",
        "org_name": "Public Works Department (PWD) Dehradun Division",
    },
    {
        "email": "dehradun.officer@nagar.gov.in",
        "password": "12345678",
        "full_name": "Sanjay Rawat (Dehradun Municipal Officer)",
        "role": UserRole.MUNICIPALITY_OFFICER,
        "phone": "9876543213",
        "org_name": "Dehradun Municipal Corporation (Nagar Nigam Dehradun)",
    },
    {
        "email": "haridwar.officer@nagar.gov.in",
        "password": "12345678",
        "full_name": "Vikram Singh (Haridwar Municipal Officer)",
        "role": UserRole.MUNICIPALITY_OFFICER,
        "phone": "9876543214",
        "org_name": "Haridwar Municipal Corporation (Nagar Nigam Haridwar)",
    },
    {
        "email": "haldwani.officer@nagar.gov.in",
        "password": "12345678",
        "full_name": "Deepak Joshi (Haldwani Municipal Officer)",
        "role": UserRole.MUNICIPALITY_OFFICER,
        "phone": "9876543215",
        "org_name": "Haldwani-Kathgodam Municipal Corporation (Nagar Nigam Haldwani)",
    },
    {
        "email": "reviewer@sip.gov.in",
        "password": "12345678",
        "full_name": "Sunita Bisht (AI Review Officer)",
        "role": UserRole.REVIEW_OFFICER,
        "phone": "9876543216",
        "org_name": "Public Works Department (PWD) Dehradun Division",
    },
    {
        "email": "admin@iitr.ac.in",
        "password": "12345678",
        "full_name": "Prof. R. D. Sharma (IIT Roorkee Admin)",
        "role": UserRole.UNIVERSITY_ADMIN,
        "phone": "9876543217",
        "org_name": "Indian Institute of Technology (IIT) Roorkee",
    },
    {
        "email": "faculty@iitr.ac.in",
        "password": "12345678",
        "full_name": "Dr. Meenakshi Sundaram (IIT Roorkee Faculty)",
        "role": UserRole.FACULTY,
        "phone": "9876543218",
        "org_name": "Indian Institute of Technology (IIT) Roorkee",
    },
    {
        "email": "admin@gbpuat.ac.in",
        "password": "12345678",
        "full_name": "Dr. K. P. Pant (GB Pant Univ Admin)",
        "role": UserRole.UNIVERSITY_ADMIN,
        "phone": "9876543219",
        "org_name": "G. B. Pant University of Agriculture and Technology",
    },
    {
        "email": "admin@geu.ac.in",
        "password": "12345678",
        "full_name": "Dr. Kamal Ghanshala (Graphic Era Admin)",
        "role": UserRole.UNIVERSITY_ADMIN,
        "phone": "9876543220",
        "org_name": "Graphic Era Deemed to be University",
    },
    {
        "email": "admin@tcs.com",
        "password": "12345678",
        "full_name": "Amitabh Kant (TCS Innovation Head)",
        "role": UserRole.INDUSTRY_ADMIN,
        "phone": "9876543221",
        "org_name": "Tata Consultancy Services (TCS) Social Innovation Lab",
    },
    {
        "email": "admin@infosys.com",
        "password": "12345678",
        "full_name": "Sudha Murty (Infosys Foundation Lead)",
        "role": UserRole.INDUSTRY_ADMIN,
        "phone": "9876543222",
        "org_name": "Infosys Foundation & Social Innovation Hub",
    },
    {
        "email": "water.dept@uk.gov.in",
        "password": "12345678",
        "full_name": "Ramesh Chandra (Water & Sanitation Head)",
        "role": UserRole.GOVERNMENT_OFFICER,
        "phone": "9876543223",
        "org_name": "Department of Water Resources & Sanitation (Jal Sansthan)",
    },
    {
        "email": "waste.mgmt@uk.gov.in",
        "password": "12345678",
        "full_name": "Anuradha Sharma (Waste & Environment Officer)",
        "role": UserRole.GOVERNMENT_OFFICER,
        "phone": "9876543224",
        "org_name": "Department of Waste Management & Environment",
    },
    {
        "email": "health.dept@uk.gov.in",
        "password": "12345678",
        "full_name": "Dr. Vivek Anand (Health & Welfare Director)",
        "role": UserRole.GOVERNMENT_OFFICER,
        "phone": "9876543225",
        "org_name": "Department of Healthcare & Social Welfare",
    },
    {
        "email": "infra.transport@uk.gov.in",
        "password": "12345678",
        "full_name": "Sunil Dutt (Infrastructure & Transport Officer)",
        "role": UserRole.GOVERNMENT_OFFICER,
        "phone": "9876543226",
        "org_name": "Department of Public Works, Transport & Digital Infrastructure",
    },
    {
        "email": "disaster.mgmt@uk.gov.in",
        "password": "12345678",
        "full_name": "Col. Ajay Tyagi (USDMA Disaster & Energy Chief)",
        "role": UserRole.GOVERNMENT_OFFICER,
        "phone": "9876543227",
        "org_name": "Uttarakhand State Disaster Management & Energy Authority (USDMA)",
    },
]


def get_db_session(db_url: Optional[str] = None):
    """
    Returns an engine and sessionmaker. If a custom db_url is supplied,
    creates a dedicated engine; otherwise uses default SessionLocal.
    """
    if db_url and db_url != settings.DATABASE_URL:
        connect_args = {}
        if db_url.startswith("sqlite"):
            connect_args["check_same_thread"] = False
        custom_engine = create_engine(db_url, connect_args=connect_args, pool_pre_ping=True)
        custom_session = sessionmaker(bind=custom_engine, autoflush=False, autocommit=False)
        return custom_engine, custom_session
    return default_engine, DefaultSessionLocal


def ensure_organizations(db: Session) -> None:
    """
    Checks if organizations exist. If not, auto-seeds them using seed_uttarakhand.
    """
    count = db.query(Organization).count()
    if count == 0:
        print("[INFO] No organizations found in DB. Auto-seeding organizations from seed_uttarakhand...")
        try:
            from seed_uttarakhand import seed as seed_orgs
            seed_orgs(db=db)
        except Exception as e:
            print(f"[WARN] Could not auto-seed organizations: {e}")


def resolve_organization(db: Session, org_name: Optional[str]) -> Optional[int]:
    """
    Finds organization ID by name or case-insensitive partial match.
    """
    if not org_name:
        return None

    org = db.query(Organization).filter(Organization.name == org_name).first()
    if org:
        return org.id

    # Fallback to case-insensitive partial match
    org = db.query(Organization).filter(Organization.name.ilike(f"%{org_name}%")).first()
    if org:
        return org.id

    print(f"[WARN] Organization not found: '{org_name}'")
    return None


def upsert_user(db: Session, udata: dict) -> str:
    """
    Upserts a single user dictionary into the DB.
    Returns 'created' or 'updated'.
    """
    email = udata["email"].strip().lower()
    full_name = udata.get("full_name", email.split("@")[0]).strip()
    password = str(udata.get("password", "12345678"))
    raw_role = udata.get("role", UserRole.CITIZEN)
    if isinstance(raw_role, str):
        role = UserRole[raw_role.upper()] if raw_role.upper() in UserRole.__members__ else UserRole(raw_role)
    else:
        role = raw_role

    phone = udata.get("phone")
    if phone:
        phone = phone.strip()

    org_id = udata.get("organization_id")
    if not org_id and udata.get("org_name"):
        org_id = resolve_organization(db, udata["org_name"])

    # Protect single SUPER_ADMIN constraint:
    # If this user is being set as SUPER_ADMIN, ensure any other existing SUPER_ADMIN is demoted
    if role == UserRole.SUPER_ADMIN:
        existing_sa = db.query(User).filter(User.role == UserRole.SUPER_ADMIN, User.email != email).first()
        if existing_sa:
            print(f"[INFO] Demoting previous SUPER_ADMIN '{existing_sa.email}' to CITIZEN to enforce single super admin rule.")
            existing_sa.role = UserRole.CITIZEN
            db.flush()

    # Avoid phone uniqueness collision with a different user
    if phone:
        phone_conflict = db.query(User).filter(User.phone == phone, User.email != email).first()
        if phone_conflict:
            print(f"[WARN] Phone '{phone}' already registered to '{phone_conflict.email}'. Clearing phone for '{email}' to prevent constraint violation.")
            phone = None

    existing = db.query(User).filter(User.email == email).first()

    if existing:
        existing.full_name = full_name
        existing.role = role
        existing.password_hash = hash_password(password)
        existing.is_active = True
        existing.is_verified = True
        if phone is not None:
            existing.phone = phone
        if org_id is not None:
            existing.organization_id = org_id
        return "updated"
    else:
        user = User(
            email=email,
            password_hash=hash_password(password),
            full_name=full_name,
            role=role,
            phone=phone,
            organization_id=org_id,
            is_active=True,
            is_verified=True,
        )
        db.add(user)
        return "created"


def seed_users(
    db_url: Optional[str] = None,
    custom_user: Optional[dict] = None,
    seed_all: bool = True,
):
    """
    Main seeding routine.
    """
    engine, SessionMaker = get_db_session(db_url)

    # Ensure tables exist
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"[WARN] Table creation check failed or already managed by Alembic: {e}")

    db = SessionMaker()
    try:
        ensure_organizations(db)

        added = 0
        updated = 0

        users_to_process = []
        if seed_all:
            users_to_process.extend(TEST_USERS)

        if custom_user:
            # Overwrite or append custom user
            existing_entry_idx = next(
                (i for i, u in enumerate(users_to_process) if u["email"].strip().lower() == custom_user["email"].strip().lower()),
                None
            )
            if existing_entry_idx is not None:
                users_to_process[existing_entry_idx] = custom_user
            else:
                users_to_process.append(custom_user)

        print(f"[SEED] Provisioning {len(users_to_process)} user accounts...")

        for udata in users_to_process:
            res = upsert_user(db, udata)
            if res == "created":
                added += 1
            else:
                updated += 1

        db.commit()
        print("\n[SUCCESS] Users seeded successfully!")
        print(f"   Created: {added}")
        print(f"   Updated: {updated}")
        print(f"   Total Accounts in Run: {len(users_to_process)}")

        print("\n[KEY] Ready-to-use Sample Logins:")
        print("   - Super Admin:          sa@platfom.com             / 12345678")
        print("   - Citizen:              citizen@gmail.com          / 12345678")
        print("   - Citizen (Abhinav):    abhinav2654@gmail.com      / 11111111")
        print("   - PWD Officer:          pwd.dehradun@gov.in        / 12345678")
        print("   - Municipal Officer:    dehradun.officer@nagar.gov.in / 12345678")
        print("   - Review Officer:       reviewer@sip.gov.in        / 12345678")
        print("   - University Admin:     admin@iitr.ac.in           / 12345678")
        print("   - Industry Admin:       admin@tcs.com              / 12345678\n")

    except Exception as e:
        db.rollback()
        print(f"\n[ERROR] Error seeding users: {e}")
        raise
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description="Seed users into the platform database.")
    parser.add_argument("--db-url", type=str, default=os.getenv("DATABASE_URL"), help="Custom Database URL")
    parser.add_argument("--email", type=str, help="Specific user email to seed/update")
    parser.add_argument("--password", type=str, default="12345678", help="Password for custom user")
    parser.add_argument("--name", "--full-name", dest="full_name", type=str, help="Full name for custom user")
    parser.add_argument(
        "--role",
        type=str,
        default="CITIZEN",
        choices=[r.value for r in UserRole],
        help="Role for custom user"
    )
    parser.add_argument("--phone", type=str, help="Phone for custom user")
    parser.add_argument("--org", "--org-name", dest="org_name", type=str, help="Organization name for custom user")
    parser.add_argument("--only-custom", action="store_true", help="Only seed the custom user, skip default TEST_USERS")

    args = parser.parse_args()

    custom_user = None
    if args.email:
        custom_user = {
            "email": args.email,
            "password": args.password,
            "full_name": args.full_name or args.email.split("@")[0],
            "role": args.role,
            "phone": args.phone,
            "org_name": args.org_name,
        }

    seed_all = not args.only_custom

    seed_users(
        db_url=args.db_url,
        custom_user=custom_user,
        seed_all=seed_all,
    )


if __name__ == "__main__":
    main()
