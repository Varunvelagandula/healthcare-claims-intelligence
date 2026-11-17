import os

FOOTER = "\n\nNote: fictional policy created for a learning project.\n"

docs = {
"physical_therapy.md": """# Physical Therapy Coverage
Physical therapy is covered up to 20 visits per calendar year.
The copay is $30 per visit.
A referral from your primary care physician is required.
Visits beyond 20 need prior authorization with documentation of medical necessity.
Occupational therapy and speech therapy have their own separate 20-visit limits.""",

"emergency_care.md": """# Emergency Care
Emergency room visits are covered 24 hours a day, in-network or out-of-network.
The ER copay is $250, waived if you are admitted to the hospital.
No prior authorization is needed for emergencies.
Ambulance transport is covered with a $100 copay.
A follow-up visit with your primary care physician is recommended within 7 days.""",

"prior_authorization.md": """# Prior Authorization
Prior authorization is required for MRI and CT scans, non-emergency inpatient admissions,
planned surgeries, and specialty drugs.
Standard requests are decided within 5 business days. Urgent requests are decided within 72 hours.
Services that need authorization but do not have it may be denied.
Your provider submits the request on your behalf.""",

"prescription_drugs.md": """# Prescription Drug Coverage
Tier 1 (generic drugs): $10 copay.
Tier 2 (preferred brand drugs): $35 copay.
Tier 3 (non-preferred brand drugs): $70 copay.
Specialty drugs: 20 percent coinsurance, capped at $250 per fill.
Retail pharmacies dispense up to a 30-day supply. Mail order dispenses up to a 90-day supply.
Some drugs require step therapy, which means trying a lower-cost drug first.""",

"mental_health.md": """# Mental Health Coverage
Outpatient therapy visits are covered with a $25 copay, the same as primary care.
There is no annual visit limit.
Telehealth therapy visits are covered at the same rate as in-person visits.
Inpatient psychiatric stays require prior authorization.""",

"preventive_care.md": """# Preventive Care
Annual checkups and recommended vaccinations are covered at 100 percent in-network, with no copay.
Mammograms are covered for members aged 40 and over.
Colon cancer screening is covered for members aged 45 and over.
Preventive services from out-of-network providers are not covered at 100 percent.""",

"claims_and_appeals.md": """# Claims and Appeals
Claims must be filed within 180 days of the date of service.
If a claim is denied, you can file an appeal within 60 days of the denial.
Appeals must be submitted in writing. A decision is made within 30 days.
If the appeal is upheld, you may request an independent external review.""",
}

os.makedirs("policy_docs", exist_ok=True)
for name, text in docs.items():
    with open(os.path.join("policy_docs", name), "w", encoding="utf-8") as f:
        f.write(text.strip() + FOOTER)
    print("wrote", name)