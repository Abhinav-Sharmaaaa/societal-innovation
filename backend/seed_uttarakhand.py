"""
Seed script to register:
- 10 Universities in Uttarakhand/India
- 10 Industry Organizations
- All 13 Districts of Uttarakhand with their Municipal Corporations/Boards and Government Departments.
"""

import sys
import os

# Ensure backend directory is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal
from app.models.organization import Organization, OrganizationType


UNIVERSITIES = [
    {
        "name": "Indian Institute of Technology (IIT) Roorkee",
        "organization_type": OrganizationType.UNIVERSITY,
        "description": "Premier premier engineering and technology institute specializing in civil, water resources, AI, and disaster mitigation research.",
        "district": "Haridwar",
        "locality": "Roorkee",
        "state": "Uttarakhand",
        "email": "director@iitr.ac.in",
        "phone": "+91-1332-285311",
        "website": "https://www.iitr.ac.in",
    },
    {
        "name": "G. B. Pant University of Agriculture and Technology",
        "organization_type": OrganizationType.UNIVERSITY,
        "description": "First agricultural university in India, leading research in sustainable agriculture, crop disease, and rural hydrology.",
        "district": "Udham Singh Nagar",
        "locality": "Pantnagar",
        "state": "Uttarakhand",
        "email": "vc@gbpuat.ac.in",
        "phone": "+91-5944-233333",
        "website": "https://www.gbpuat.ac.in",
    },
    {
        "name": "Hemvati Nandan Bahuguna Garhwal University",
        "organization_type": OrganizationType.UNIVERSITY,
        "description": "Central University focusing on Himalayan ecology, forestry, environmental sciences, and renewable energy.",
        "district": "Pauri Garhwal",
        "locality": "Srinagar Garhwal",
        "state": "Uttarakhand",
        "email": "registrar@hnbgu.ac.in",
        "phone": "+91-1370-267093",
        "website": "https://www.hnbgu.ac.in",
    },
    {
        "name": "Kumaun University",
        "organization_type": OrganizationType.UNIVERSITY,
        "description": "Premier state university in Nainital specialized in environmental monitoring, geology, and biotechnology.",
        "district": "Nainital",
        "locality": "Nainital",
        "state": "Uttarakhand",
        "email": "info@kunainital.ac.in",
        "phone": "+91-5942-235563",
        "website": "https://www.kunainital.ac.in",
    },
    {
        "name": "Graphic Era Deemed to be University",
        "organization_type": OrganizationType.UNIVERSITY,
        "description": "Top private university in Dehradun with dedicated labs for Computer Science, Robotics, and IoT sensor deployment.",
        "district": "Dehradun",
        "locality": "Clement Town",
        "state": "Uttarakhand",
        "email": "enquiry@geu.ac.in",
        "phone": "+91-135-2643421",
        "website": "https://www.geu.ac.in",
    },
    {
        "name": "University of Petroleum and Energy Studies (UPES)",
        "organization_type": OrganizationType.UNIVERSITY,
        "description": "Specialized institution focusing on smart grids, renewable energy, clean transportation, and infrastructure engineering.",
        "district": "Dehradun",
        "locality": "Bidholi",
        "state": "Uttarakhand",
        "email": "enrollments@upes.ac.in",
        "phone": "+91-135-2776091",
        "website": "https://www.upes.ac.in",
    },
    {
        "name": "All India Institute of Medical Sciences (AIIMS) Rishikesh",
        "organization_type": OrganizationType.UNIVERSITY,
        "description": "Apex healthcare and medical research university specializing in public health, telemedicine, and epidemic surveillance.",
        "district": "Dehradun",
        "locality": "Rishikesh",
        "state": "Uttarakhand",
        "email": "admin@aiimsrishikesh.edu.in",
        "phone": "+91-135-2462940",
        "website": "https://www.aiimsrishikesh.edu.in",
    },
    {
        "name": "Forest Research Institute (FRI) Deemed University",
        "organization_type": OrganizationType.UNIVERSITY,
        "description": "World-renowned institute in forestry, watershed management, soil erosion control, and bio-resource management.",
        "district": "Dehradun",
        "locality": "Kaulagarh",
        "state": "Uttarakhand",
        "email": "registrarfri@icfre.org",
        "phone": "+91-135-2755277",
        "website": "http://fri.icfre.gov.in",
    },
    {
        "name": "Doon University",
        "organization_type": OrganizationType.UNIVERSITY,
        "description": "State university specializing in School of Environment and Natural Resources, Social Sciences, and Sustainable Development.",
        "district": "Dehradun",
        "locality": "Kedarpur",
        "state": "Uttarakhand",
        "email": "registrar@doonuniversity.ac.in",
        "phone": "+91-135-2607012",
        "website": "https://doonuniversity.ac.in",
    },
    {
        "name": "National Institute of Technology (NIT) Uttarakhand",
        "organization_type": OrganizationType.UNIVERSITY,
        "description": "Institute of National Importance working on structural dynamics, disaster management electronics, and GIS mapping.",
        "district": "Pauri Garhwal",
        "locality": "Srinagar Garhwal",
        "state": "Uttarakhand",
        "email": "nituttarakhand@nituk.ac.in",
        "phone": "+91-1346-257404",
        "website": "https://www.nituk.ac.in",
    },
]


INDUSTRIES = [
    {
        "name": "Tata Consultancy Services (TCS) Social Innovation Lab",
        "organization_type": OrganizationType.INDUSTRY,
        "description": "Technology and CSR arm of TCS co-funding smart governance, civic analytics, and AI public solutions.",
        "district": "Dehradun",
        "locality": "IT Park",
        "state": "Uttarakhand",
        "email": "innovation.lab@tcs.com",
        "phone": "+91-135-6677000",
        "website": "https://www.tcs.com",
    },
    {
        "name": "Infosys Foundation & Social Innovation Hub",
        "organization_type": OrganizationType.INDUSTRY,
        "description": "Corporate foundation deploying grants, technology mentorship, and IoT hardware for municipal projects.",
        "district": "Dehradun",
        "locality": "Rajpur Road",
        "state": "Uttarakhand",
        "email": "foundation@infosys.com",
        "phone": "+91-80-28520261",
        "website": "https://www.infosys.com/infosys-foundation",
    },
    {
        "name": "Bharat Electronics Limited (BEL) Kotdwar Complex",
        "organization_type": OrganizationType.INDUSTRY,
        "description": "Navratna PSU providing hardware engineering, telemetry sensors, and automated flood alert systems.",
        "district": "Pauri Garhwal",
        "locality": "Kotdwar",
        "state": "Uttarakhand",
        "email": "belkot@bel.co.in",
        "phone": "+91-1382-222601",
        "website": "https://bel-india.in",
    },
    {
        "name": "Bharat Heavy Electricals Limited (BHEL) Haridwar Plant",
        "organization_type": OrganizationType.INDUSTRY,
        "description": "Maharatna PSU supporting heavy machinery innovation, clean energy turbines, and industrial waste management.",
        "district": "Haridwar",
        "locality": "Ranipur",
        "state": "Uttarakhand",
        "email": "contact@bhelhwr.co.in",
        "phone": "+91-1334-281313",
        "website": "https://www.bhelhwr.co.in",
    },
    {
        "name": "Wipro EcoEnergy & Smart Cities Division",
        "organization_type": OrganizationType.INDUSTRY,
        "description": "Industry leader in smart street lighting, energy efficiency monitoring, and urban waste analytics.",
        "district": "Dehradun",
        "locality": "IT Park",
        "state": "Uttarakhand",
        "email": "smartcities@wipro.com",
        "phone": "+91-80-28440011",
        "website": "https://www.wipro.com",
    },
    {
        "name": "Tech Mahindra Public Sector & IoT Practice",
        "organization_type": OrganizationType.INDUSTRY,
        "description": "Enterprise IT consultancy backing digital twin initiatives, municipal GIS, and civic complaint automation.",
        "district": "Dehradun",
        "locality": "Patel Nagar",
        "state": "Uttarakhand",
        "email": "publicsector@techmahindra.com",
        "phone": "+91-120-4923000",
        "website": "https://www.techmahindra.com",
    },
    {
        "name": "ITC Limited Sustainable Agriculture & CSR Division",
        "organization_type": OrganizationType.INDUSTRY,
        "description": "Conglomerate supporting watershed development, farmer soil health labs, and rural organic waste recycling.",
        "district": "Haridwar",
        "locality": "SIIDCUL Industrial Area",
        "state": "Uttarakhand",
        "email": "sustainability@itc.in",
        "phone": "+91-1334-239100",
        "website": "https://www.itcportal.com",
    },
    {
        "name": "Larsen & Toubro (L&T) Public Infrastructure Group",
        "organization_type": OrganizationType.INDUSTRY,
        "description": "Engineering & construction giant co-sponsoring bridge safety monitors, road durability R&D, and slope stability tech.",
        "district": "Dehradun",
        "locality": "Vasant Vihar",
        "state": "Uttarakhand",
        "email": "infra@larsentoubro.com",
        "phone": "+91-22-67525656",
        "website": "https://www.larsentoubro.com",
    },
    {
        "name": "Hero MotoCorp Manufacturing & Innovation Center",
        "organization_type": OrganizationType.INDUSTRY,
        "description": "Automotive leader investing in green mobility solutions, road safety tech, and EV charging infrastructure.",
        "district": "Haridwar",
        "locality": "SIIDCUL Haridwar",
        "state": "Uttarakhand",
        "email": "csr@heromotocorp.com",
        "phone": "+91-1334-238800",
        "website": "https://www.heromotocorp.com",
    },
    {
        "name": "Patanjali Bio Research & Development Institute",
        "organization_type": OrganizationType.INDUSTRY,
        "description": "Research division focusing on herbal bio-remediation, organic waste composting, and clean river initiatives.",
        "district": "Haridwar",
        "locality": "Bahadrabad",
        "state": "Uttarakhand",
        "email": "research@patanjaliayurved.org",
        "phone": "+91-1334-240008",
        "website": "https://www.patanjaliayurved.net",
    },
]


DISTRICT_ORGANIZATIONS = [
    # 1. Dehradun
    {
        "name": "Dehradun Municipal Corporation (Nagar Nigam Dehradun)",
        "organization_type": OrganizationType.MUNICIPALITY,
        "description": "Primary urban local body responsible for sanitation, road maintenance, waste management, and civic amenities in Dehradun.",
        "district": "Dehradun",
        "locality": "Dehradun City",
        "state": "Uttarakhand",
        "email": "nagarnigam.ddn@gmail.com",
        "phone": "+91-135-2653572",
        "website": "https://nagarnigamdehradun.com",
    },
    {
        "name": "Public Works Department (PWD) Dehradun Division",
        "organization_type": OrganizationType.GOVERNMENT_DEPARTMENT,
        "description": "State department managing arterial road construction, bridge engineering, and structural safety across Dehradun district.",
        "district": "Dehradun",
        "locality": "Yamuna Colony",
        "state": "Uttarakhand",
        "email": "ee.pwd.dehradun@uk.gov.in",
        "phone": "+91-135-2531201",
        "website": "https://pwd.uk.gov.in",
    },
    {
        "name": "Uttarakhand Jal Sansthan Dehradun",
        "organization_type": OrganizationType.GOVERNMENT_DEPARTMENT,
        "description": "State water supply authority monitoring potable water pipelines, chlorination treatment plants, and sewer networks in Dehradun.",
        "district": "Dehradun",
        "locality": "Dalanwala",
        "state": "Uttarakhand",
        "email": "cgujs.dehradun@gmail.com",
        "phone": "+91-135-2673238",
        "website": "https://ujs.uk.gov.in",
    },
    {
        "name": "Dehradun Chief Medical Office & Public Health Dept",
        "organization_type": OrganizationType.GOVERNMENT_DEPARTMENT,
        "description": "District health office managing epidemic prevention, vector control, primary health centers, and emergency response.",
        "district": "Dehradun",
        "locality": "Chander Nagar",
        "state": "Uttarakhand",
        "email": "cmo.dehradun@gmail.com",
        "phone": "+91-135-2623327",
        "website": "https://health.uk.gov.in",
    },

    # 2. Haridwar
    {
        "name": "Haridwar Municipal Corporation (Nagar Nigam Haridwar)",
        "organization_type": OrganizationType.MUNICIPALITY,
        "description": "Municipal authority governing sanitation, pilgrim crowd infrastructure, riverbank cleanliness, and solid waste in Haridwar.",
        "district": "Haridwar",
        "locality": "Haridwar City",
        "state": "Uttarakhand",
        "email": "nagarnigamharidwar@gmail.com",
        "phone": "+91-1334-227008",
        "website": "https://haridwarnagarnigam.com",
    },
    {
        "name": "Public Works Department (PWD) Haridwar Circle",
        "organization_type": OrganizationType.GOVERNMENT_DEPARTMENT,
        "description": "Government roads department overseeing highway connectivity, bypasses, and drainage works in Haridwar.",
        "district": "Haridwar",
        "locality": "Roshnabad",
        "state": "Uttarakhand",
        "email": "ee.pwd.haridwar@uk.gov.in",
        "phone": "+91-1334-239011",
        "website": "https://pwd.uk.gov.in",
    },

    # 3. Nainital
    {
        "name": "Haldwani-Kathgodam Municipal Corporation (Nagar Nigam Haldwani)",
        "organization_type": OrganizationType.MUNICIPALITY,
        "description": "Largest civic body in Kumaun region responsible for Haldwani urban development, drainage, and waste management.",
        "district": "Nainital",
        "locality": "Haldwani",
        "state": "Uttarakhand",
        "email": "nagarnigamhaldwani@gmail.com",
        "phone": "+91-5946-220042",
        "website": "https://haldwaninagarnigam.com",
    },
    {
        "name": "Nainital Municipal Board (Nagar Palika Parishad Nainital)",
        "organization_type": OrganizationType.MUNICIPALITY,
        "description": "Heritage municipal authority governing Naini Lake conservation, hill town sanitation, and eco-tourism infrastructure.",
        "district": "Nainital",
        "locality": "Nainital Town",
        "state": "Uttarakhand",
        "email": "nppnainital@gmail.com",
        "phone": "+91-5942-235025",
        "website": "https://nainital.gov.in",
    },

    # 4. Udham Singh Nagar
    {
        "name": "Rudrapur Municipal Corporation (Nagar Nigam Rudrapur)",
        "organization_type": OrganizationType.MUNICIPALITY,
        "description": "Industrial hub civic body managing industrial effluent monitoring, civic roads, and street lighting in Rudrapur.",
        "district": "Udham Singh Nagar",
        "locality": "Rudrapur",
        "state": "Uttarakhand",
        "email": "nnrudrapur@gmail.com",
        "phone": "+91-5944-242200",
        "website": "https://usnagar.nic.in",
    },
    {
        "name": "Kashipur Municipal Corporation (Nagar Nigam Kashipur)",
        "organization_type": OrganizationType.MUNICIPALITY,
        "description": "Urban local body managing public amenities, storm drains, and civic maintenance in Kashipur area.",
        "district": "Udham Singh Nagar",
        "locality": "Kashipur",
        "state": "Uttarakhand",
        "email": "nnkashipur@gmail.com",
        "phone": "+91-5947-275100",
        "website": "https://usnagar.nic.in",
    },

    # 5. Pauri Garhwal
    {
        "name": "Kotdwar Municipal Corporation (Nagar Nigam Kotdwar)",
        "organization_type": OrganizationType.MUNICIPALITY,
        "description": "Gateway municipality to Garhwal hills overseeing riverbed protection, municipal solid waste, and urban transport.",
        "district": "Pauri Garhwal",
        "locality": "Kotdwar",
        "state": "Uttarakhand",
        "email": "nnkotdwar@gmail.com",
        "phone": "+91-1382-220015",
        "website": "https://pauri.nic.in",
    },
    {
        "name": "Pauri Municipal Board (Nagar Palika Parishad Pauri)",
        "organization_type": OrganizationType.MUNICIPALITY,
        "description": "District headquarters municipal council regulating hill slopes, public parks, and water distribution oversight.",
        "district": "Pauri Garhwal",
        "locality": "Pauri Town",
        "state": "Uttarakhand",
        "email": "npppauri@gmail.com",
        "phone": "+91-1368-222010",
        "website": "https://pauri.nic.in",
    },

    # 6. Tehri Garhwal
    {
        "name": "Tehri Municipal Board (Nagar Palika Parishad New Tehri)",
        "organization_type": OrganizationType.MUNICIPALITY,
        "description": "Planned hill city municipal authority managing reservoir town civic infrastructure, waste, and green belts.",
        "district": "Tehri Garhwal",
        "locality": "New Tehri",
        "state": "Uttarakhand",
        "email": "nppnewtehri@gmail.com",
        "phone": "+91-1376-232014",
        "website": "https://tehri.nic.in",
    },

    # 7. Uttarkashi
    {
        "name": "Uttarkashi Municipal Board (Nagar Palika Parishad Uttarkashi)",
        "organization_type": OrganizationType.MUNICIPALITY,
        "description": "High-altitude municipal council managing Bhagirathi riverbank sanitation, landslide alert awareness, and civic services.",
        "district": "Uttarkashi",
        "locality": "Uttarkashi Town",
        "state": "Uttarakhand",
        "email": "npputtarkashi@gmail.com",
        "phone": "+91-1374-222018",
        "website": "https://uttarkashi.nic.in",
    },

    # 8. Chamoli
    {
        "name": "Gopeshwar Municipal Board (Nagar Palika Parishad Gopeshwar)",
        "organization_type": OrganizationType.MUNICIPALITY,
        "description": "District headquarters civic council managing alpine town waste collection, civic roads, and street lights.",
        "district": "Chamoli",
        "locality": "Gopeshwar",
        "state": "Uttarakhand",
        "email": "nppgopeshwar@gmail.com",
        "phone": "+91-1372-252110",
        "website": "https://chamoli.gov.in",
    },
    {
        "name": "Joshimath Municipal Board (Nagar Palika Parishad Joshimath)",
        "organization_type": OrganizationType.MUNICIPALITY,
        "description": "Strategic border hill town municipal council handling land subsidence monitoring assistance and tourist sanitation.",
        "district": "Chamoli",
        "locality": "Joshimath",
        "state": "Uttarakhand",
        "email": "nppjoshimath@gmail.com",
        "phone": "+91-1389-222005",
        "website": "https://chamoli.gov.in",
    },

    # 9. Rudraprayag
    {
        "name": "Rudraprayag Municipal Board (Nagar Palika Parishad Rudraprayag)",
        "organization_type": OrganizationType.MUNICIPALITY,
        "description": "Sacred confluence town municipal authority focused on Yatra pilgrim waste management and river ghat cleanliness.",
        "district": "Rudraprayag",
        "locality": "Rudraprayag Town",
        "state": "Uttarakhand",
        "email": "npprudraprayag@gmail.com",
        "phone": "+91-1364-233300",
        "website": "https://rudraprayag.gov.in",
    },

    # 10. Almora
    {
        "name": "Almora Municipal Board (Nagar Palika Parishad Almora)",
        "organization_type": OrganizationType.MUNICIPALITY,
        "description": "Cultural center municipal council managing historic hill bazaar heritage roads, solid waste, and water distribution.",
        "district": "Almora",
        "locality": "Almora Town",
        "state": "Uttarakhand",
        "email": "nppalmora@gmail.com",
        "phone": "+91-5962-230015",
        "website": "https://almora.nic.in",
    },

    # 11. Bageshwar
    {
        "name": "Bageshwar Municipal Board (Nagar Palika Parishad Bageshwar)",
        "organization_type": OrganizationType.MUNICIPALITY,
        "description": "Saryu river valley municipal body managing valley drainage, civic maintenance, and waste segregation.",
        "district": "Bageshwar",
        "locality": "Bageshwar Town",
        "state": "Uttarakhand",
        "email": "nppbageshwar@gmail.com",
        "phone": "+91-5963-220025",
        "website": "https://bageshwar.nic.in",
    },

    # 12. Pithoragarh
    {
        "name": "Pithoragarh Municipal Board (Nagar Palika Parishad Pithoragarh)",
        "organization_type": OrganizationType.MUNICIPALITY,
        "description": "Eastern border district civic authority governing Soar valley municipal roads, street lighting, and sanitation.",
        "district": "Pithoragarh",
        "locality": "Pithoragarh Town",
        "state": "Uttarakhand",
        "email": "npppithoragarh@gmail.com",
        "phone": "+91-5964-225010",
        "website": "https://pithoragarh.nic.in",
    },

    # 13. Champawat
    {
        "name": "Champawat Municipal Board (Nagar Palika Parishad Champawat)",
        "organization_type": OrganizationType.MUNICIPALITY,
        "description": "Historic Kumaun capital municipal council regulating eco-sanitation, local roads, and public health amenities.",
        "district": "Champawat",
        "locality": "Champawat Town",
        "state": "Uttarakhand",
        "email": "nppchampawat@gmail.com",
        "phone": "+91-5965-230020",
        "website": "https://champawat.nic.in",
    },
]

CATEGORY_DEPARTMENTS = [
    {
        "name": "Department of Water Resources & Sanitation (Jal Sansthan)",
        "organization_type": OrganizationType.GOVERNMENT_DEPARTMENT,
        "description": "Specialized state department handling water supply, pipeline infrastructure, chlorination, and urban sanitation (Categories: WATER, SANITATION).",
        "district": "Dehradun",
        "locality": "Dalanwala",
        "state": "Uttarakhand",
        "email": "water.dept@uk.gov.in",
        "phone": "+91-135-2673001",
        "website": "https://ujs.uk.gov.in",
    },
    {
        "name": "Department of Waste Management & Environment",
        "organization_type": OrganizationType.GOVERNMENT_DEPARTMENT,
        "description": "Specialized municipal body overseeing solid waste management, landfill processing, environmental protection, and recycling (Categories: WASTE_MANAGEMENT, ENVIRONMENT).",
        "district": "Dehradun",
        "locality": "Rajpur Road",
        "state": "Uttarakhand",
        "email": "waste.mgmt@uk.gov.in",
        "phone": "+91-135-2673002",
        "website": "https://ueppcb.uk.gov.in",
    },
    {
        "name": "Department of Healthcare & Social Welfare",
        "organization_type": OrganizationType.GOVERNMENT_DEPARTMENT,
        "description": "State department managing public health centers, epidemic control, hospital amenities, and social welfare programs (Categories: HEALTHCARE, SOCIAL_WELFARE, PUBLIC_SAFETY).",
        "district": "Dehradun",
        "locality": "Chander Nagar",
        "state": "Uttarakhand",
        "email": "health.dept@uk.gov.in",
        "phone": "+91-135-2673003",
        "website": "https://health.uk.gov.in",
    },
    {
        "name": "Department of Public Works, Transport & Digital Infrastructure",
        "organization_type": OrganizationType.GOVERNMENT_DEPARTMENT,
        "description": "State infrastructure authority overseeing road construction, public transit, bridges, traffic signals, and smart digital services (Categories: INFRASTRUCTURE, TRANSPORTATION, DIGITAL_SERVICES).",
        "district": "Dehradun",
        "locality": "Yamuna Colony",
        "state": "Uttarakhand",
        "email": "infra.transport@uk.gov.in",
        "phone": "+91-135-2673004",
        "website": "https://pwd.uk.gov.in",
    },
    {
        "name": "Uttarakhand State Disaster Management & Energy Authority (USDMA)",
        "organization_type": OrganizationType.GOVERNMENT_DEPARTMENT,
        "description": "Apex emergency response authority managing landslide alerts, disaster mitigation, clean energy grid stability, and public safety (Categories: DISASTER_MANAGEMENT, ENERGY, PUBLIC_SAFETY).",
        "district": "Dehradun",
        "locality": "Secretariat",
        "state": "Uttarakhand",
        "email": "disaster.mgmt@uk.gov.in",
        "phone": "+91-135-2673005",
        "website": "https://usdma.uk.gov.in",
    },
]


def seed():
    db = SessionLocal()
    try:
        print("[SEED] Starting seeding of Uttarakhand Organizations...")
        added_count = 0
        skipped_count = 0

        all_records = UNIVERSITIES + INDUSTRIES + DISTRICT_ORGANIZATIONS + CATEGORY_DEPARTMENTS

        for data in all_records:
            existing = (
                db.query(Organization)
                .filter(Organization.name == data["name"])
                .first()
            )
            if existing:
                skipped_count += 1
                continue

            org = Organization(
                name=data["name"],
                organization_type=data["organization_type"],
                description=data.get("description"),
                district=data.get("district"),
                locality=data.get("locality"),
                state=data.get("state", "Uttarakhand"),
                email=data.get("email"),
                phone=data.get("phone"),
                website=data.get("website"),
                is_active=True,
            )
            db.add(org)
            added_count += 1

        db.commit()
        print("[SUCCESS] Seeding Complete!")
        print(f"   Added: {added_count} new organizations")
        print(f"   Skipped (already exists): {skipped_count} organizations")
        print(f"   Total Registered Orgs: {added_count + skipped_count}")

    except Exception as e:
        db.rollback()
        print(f"[ERROR] Error during seeding: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
