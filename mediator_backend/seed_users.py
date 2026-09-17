"""
Seed script to create ready-to-use official and citizen test credentials for all roles.
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal
from app.models.user import User, UserRole
from app.models.organization import Organization
from app.core.security import hash_password


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


def seed_users():
    db = SessionLocal()
    try:
        print("[SEED] Provisioning test login accounts...")
        added = 0
        updated = 0

        for udata in TEST_USERS:
            org_id = None
            if udata["org_name"]:
                org = (
                    db.query(Organization)
                    .filter(Organization.name == udata["org_name"])
                    .first()
                )
                if org:
                    org_id = org.id

            existing = (
                db.query(User)
                .filter(User.email == udata["email"])
                .first()
            )

            if existing:
                if udata["role"] != UserRole.SUPER_ADMIN or existing.role == UserRole.SUPER_ADMIN:
                    existing.role = udata["role"]
                existing.password_hash = hash_password(udata["password"])
                existing.is_active = True
                if org_id:
                    existing.organization_id = org_id
                updated += 1
            else:
                user = User(
                    email=udata["email"],
                    password_hash=hash_password(udata["password"]),
                    full_name=udata["full_name"],
                    role=udata["role"],
                    phone=udata["phone"],
                    organization_id=org_id,
                    is_active=True,
                )
                db.add(user)
                added += 1

        db.commit()
        print("[SUCCESS] Test accounts ready!")
        print(f"   Created: {added}")
        print(f"   Updated: {updated}")

    except Exception as e:
        db.rollback()
        print(f"[ERROR] Error creating test accounts: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_users()
