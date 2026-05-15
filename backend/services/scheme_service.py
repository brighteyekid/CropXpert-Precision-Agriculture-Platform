"""
CropXpert — Government scheme seeding + eligibility service.
Seeds 17 real schemes. Eligibility is checked against farmer profile (acreage, state).
"""
import json
from datetime import date
from sqlalchemy.orm import Session
from models.government_scheme import GovernmentScheme
from models.loan_program import LoanProgram


SEED_SCHEMES = [
    # ── Welfare / Income Support ───────────────────────────────────────────────
    {
        "name": "PM-KISAN Samman Nidhi",
        "description": "Direct income support of ₹6,000/year to landholding farmer families, paid in three installments of ₹2,000 every four months.",
        "benefit_amount": "₹6,000/year",
        "eligibility": "Landholding below 2 hectares; Aadhaar-linked farm records; Not a government employee or income-tax payer",
        "documents_required": "Aadhaar Card; Land ownership records (7/12 Extract); Bank passbook",
        "apply_url": "https://pmkisan.gov.in",
        "scheme_type": "welfare",
        "applicable_states": json.dumps(["all"]),
        "max_acreage_ha": 2.0,
    },
    {
        "name": "PM Fasal Bima Yojana (PMFBY)",
        "description": "Comprehensive crop insurance at subsidised premiums: 2% for Kharif, 1.5% for Rabi, 5% for commercial crops. Covers natural disasters, pest attacks, post-harvest losses.",
        "benefit_amount": "Premium: 2% Kharif / 1.5% Rabi",
        "eligibility": "Any farmer with a notified crop in a notified area; No acreage limit",
        "documents_required": "Sowing declaration; Bank details; Land records; Aadhaar",
        "apply_url": "https://pmfby.gov.in",
        "scheme_type": "welfare",
        "applicable_states": json.dumps(["all"]),
        "max_acreage_ha": None,
    },
    {
        "name": "Soil Health Card Scheme",
        "description": "Free soil testing every 2 years with personalised fertilizer recommendations issued as a digital card within 30 days of sampling.",
        "benefit_amount": "Free soil testing",
        "eligibility": "All farmers with cultivable land; No acreage limit",
        "documents_required": "Aadhaar Card; Land survey number; Mobile number",
        "apply_url": "https://soilhealth.dac.gov.in",
        "scheme_type": "welfare",
        "applicable_states": json.dumps(["all"]),
        "max_acreage_ha": None,
    },
    {
        "name": "PM Krishi Sinchayee Yojana (PMKSY)",
        "description": "Micro-irrigation subsidies of 55–80% on drip and sprinkler systems plus watershed development grants for rain-fed farmers.",
        "benefit_amount": "55–80% subsidy on micro-irrigation",
        "eligibility": "Any farmer with irrigable land; Priority to drought-prone districts",
        "documents_required": "Land records; Bank account; Aadhaar; Vendor quotation",
        "apply_url": "https://pmksy.gov.in",
        "scheme_type": "welfare",
        "applicable_states": json.dumps(["all"]),
        "max_acreage_ha": None,
    },
    {
        "name": "PM Formalization of Micro Food Processing (PMFME)",
        "description": "35% credit-linked capital subsidy (max ₹10 lakh) for micro food-processing units under One District One Product (ODOP) categories.",
        "benefit_amount": "35% capital subsidy (max ₹10L)",
        "eligibility": "Existing micro food processing units; New units in ODOP categories; SHGs",
        "documents_required": "Udyam registration; Project report; Bank loan sanction; Aadhaar",
        "apply_url": "https://pmfme.mofpi.gov.in",
        "scheme_type": "welfare",
        "applicable_states": json.dumps(["all"]),
        "max_acreage_ha": None,
    },
    {
        "name": "National Food Security Mission (NFSM)",
        "description": "Input subsidies (certified seeds, biofertilisers, micronutrients, irrigation tools) for rice, wheat, pulses, coarse cereals and nutri-cereals farmers.",
        "benefit_amount": "Seed & input subsidies",
        "eligibility": "Farmers growing NFSM target crops in notified districts; No acreage limit",
        "documents_required": "Land records; Aadhaar; Bank account",
        "apply_url": "https://nfsm.gov.in",
        "scheme_type": "welfare",
        "applicable_states": json.dumps(["all"]),
        "max_acreage_ha": None,
    },
    {
        "name": "Rashtriya Krishi Vikas Yojana (RKVY)",
        "description": "Flexible district-level grants for agriculture infrastructure: custom hiring centres, FPO formation, precision farming pilots and agri-startups.",
        "benefit_amount": "Grant-based (varies by project)",
        "eligibility": "FPOs, SHGs, individual farmers in selected districts; Project approval from district office",
        "documents_required": "Project proposal; Land records; Organisation certificate",
        "apply_url": "https://rkvy.nic.in",
        "scheme_type": "welfare",
        "applicable_states": json.dumps(["all"]),
        "max_acreage_ha": None,
    },
    {
        "name": "Pradhan Mantri Annadata Aay SanraksHan Abhiyan (PM-AASHA)",
        "description": "Price support scheme ensuring farmers receive MSP for oilseeds, pulses and copra via direct procurement and price deficiency payments.",
        "benefit_amount": "MSP guaranteed on oilseeds & pulses",
        "eligibility": "Farmers producing oilseeds, pulses, copra in notified states; Registration with local mandi",
        "documents_required": "Land records; Bank account; Aadhaar; Crop registration slip",
        "apply_url": "https://agricoop.nic.in/pm-aasha",
        "scheme_type": "welfare",
        "applicable_states": json.dumps(["all"]),
        "max_acreage_ha": None,
    },
    {
        "name": "Market Intervention Scheme (MIS)",
        "description": "State-specific scheme providing procurement at declared intervention price for perishable horticulture crops when open market prices fall below production cost.",
        "benefit_amount": "Intervention price support",
        "eligibility": "Horticulture farmers in states where intervention is declared; Perishable crop growers",
        "documents_required": "Land records; Crop inspection certificate; Bank account",
        "apply_url": "https://agricoop.nic.in",
        "scheme_type": "welfare",
        "applicable_states": json.dumps(["all"]),
        "max_acreage_ha": None,
    },
    {
        "name": "Sub-Mission on Agricultural Mechanization (SMAM)",
        "description": "50–80% subsidy on farm machinery (tractors, harvesters, tillers) for small and marginal farmers and Custom Hiring Centres (CHC).",
        "benefit_amount": "50–80% machinery subsidy",
        "eligibility": "Small and marginal farmers (below 5 ha); SC/ST farmers get higher subsidy; CHC applicants",
        "documents_required": "Land records; Aadhaar; Bank account; Quotation from dealer",
        "apply_url": "https://agrimachinery.nic.in",
        "scheme_type": "welfare",
        "applicable_states": json.dumps(["all"]),
        "max_acreage_ha": 5.0,
    },
    {
        "name": "e-NAM (National Agriculture Market)",
        "description": "Online platform connecting 1,260+ mandis across India. Enables farmers to list produce, receive competitive bids and get transparent electronic payments.",
        "benefit_amount": "Better market price realisation",
        "eligibility": "Any farmer registered at an e-NAM enabled mandi; No acreage limit",
        "documents_required": "Aadhaar; Bank account; Mandi trader licence (for traders)",
        "apply_url": "https://enam.gov.in",
        "scheme_type": "welfare",
        "applicable_states": json.dumps(["all"]),
        "max_acreage_ha": None,
    },
    {
        "name": "Paramparagat Krishi Vikas Yojana (PKVY)",
        "description": "Organic farming promotion: ₹50,000/ha over 3 years for cluster-based organic conversion, on-farm input production, and certification and marketing support.",
        "benefit_amount": "₹50,000/ha over 3 years",
        "eligibility": "Farmers willing to convert to organic; Cluster of minimum 20 ha; No acreage limit per farmer",
        "documents_required": "Land records; Aadhaar; Cluster formation consent",
        "apply_url": "https://pgsindia-ncof.gov.in",
        "scheme_type": "welfare",
        "applicable_states": json.dumps(["all"]),
        "max_acreage_ha": None,
    },
    # ── Loan / Credit ─────────────────────────────────────────────────────────
    {
        "name": "Kisan Credit Card (KCC)",
        "description": "Short-term crop loan up to ₹3 lakh at 0% effective interest (4% nominal − 2% interest subvention − 2% prompt repayment rebate). ATM-enabled debit card.",
        "benefit_amount": "0% effective interest up to ₹3L",
        "eligibility": "Any farmer with cultivable land; Animal husbandry and fisheries farmers eligible",
        "documents_required": "Identity proof; Land records; Two passport photos; Bank KYC",
        "apply_url": "https://nabard.org/kcc",
        "scheme_type": "loan",
        "applicable_states": json.dumps(["all"]),
        "max_acreage_ha": None,
    },
    {
        "name": "Agriculture Infrastructure Fund (AIF)",
        "description": "₹1 lakh crore credit facility at 3% interest subvention for post-harvest infrastructure: cold storage, primary processing, assaying labs, e-marketing under one scheme.",
        "benefit_amount": "3% interest subvention on loans",
        "eligibility": "FPOs, PACS, SHGs, agri-entrepreneurs; Individual farmers for infrastructure above ₹2 crore",
        "documents_required": "Project DPR; Organisation registration; Bank loan sanction letter",
        "apply_url": "https://agriinfra.dac.gov.in",
        "scheme_type": "loan",
        "applicable_states": json.dumps(["all"]),
        "max_acreage_ha": None,
    },
    {
        "name": "NABARD Long-Term Rural Credit Fund",
        "description": "Low-interest term loans (4–7%) up to ₹10 lakh for land development, orchard establishment, farm mechanisation and allied activities.",
        "benefit_amount": "4–7% interest rate",
        "eligibility": "Farmers with minimum 1 acre; State-compliant project plan",
        "documents_required": "Land records; Project plan; Bank KYC",
        "apply_url": "https://nabard.org",
        "scheme_type": "loan",
        "applicable_states": json.dumps(["all"]),
        "max_acreage_ha": None,
    },
    {
        "name": "Modified Interest Subvention Scheme (MISS)",
        "description": "2% interest subvention on short-term crop loans up to ₹3 lakh. Additional 2% prompt repayment incentive, making effective rate 0%.",
        "benefit_amount": "Up to 4% interest subvention",
        "eligibility": "Farmers with short-term crop loans up to ₹3L from scheduled banks",
        "documents_required": "KCC/loan account; Aadhaar; Land records",
        "apply_url": "https://agricoop.nic.in/miss",
        "scheme_type": "loan",
        "applicable_states": json.dumps(["all"]),
        "max_acreage_ha": None,
    },
    {
        "name": "PM SVANidhi (Vendor Credit for Agri-produce sellers)",
        "description": "Collateral-free working capital loans of ₹10,000–₹50,000 at subsidised rates for street vendors and micro-traders of agricultural produce.",
        "benefit_amount": "₹10K–₹50K collateral-free",
        "eligibility": "Street vendors and micro-traders certified by urban local bodies",
        "documents_required": "Vendor certificate; Aadhaar; Bank account",
        "apply_url": "https://pmsvanidhi.mohua.gov.in",
        "scheme_type": "loan",
        "applicable_states": json.dumps(["all"]),
        "max_acreage_ha": None,
    },
]


SEED_LOANS = [
    {
        "name": "Kisan Credit Card — Crop Loan",
        "provider": "Any scheduled commercial bank",
        "interest_rate": 0.0,
        "max_amount": 300000,
        "tenure_months_max": 12,
        "eligibility": "Any farmer with cultivable land",
        "apply_url": "https://nabard.org/kcc",
    },
    {
        "name": "NABARD Long-Term Farm Loan",
        "provider": "NABARD partner banks",
        "interest_rate": 4.0,
        "max_amount": 1000000,
        "tenure_months_max": 60,
        "eligibility": "Farmers with minimum 1 acre landholding",
        "apply_url": "https://nabard.org",
    },
    {
        "name": "Agriculture Infrastructure Fund",
        "provider": "Scheduled commercial banks, NABARD",
        "interest_rate": 4.0,
        "max_amount": 20000000,
        "tenure_months_max": 84,
        "eligibility": "FPOs, PACS, SHGs, agri-entrepreneurs, individual farmers",
        "apply_url": "https://agriinfra.dac.gov.in",
    },
]


def seed_schemes(db: Session):
    """Re-seed government schemes — updates if count differs from SEED_SCHEMES."""
    existing_count = db.query(GovernmentScheme).count()
    if existing_count == len(SEED_SCHEMES):
        return  # already up to date

    # Wipe and re-seed to pick up new/changed schemes
    db.query(GovernmentScheme).delete()
    db.query(LoanProgram).delete()

    for s in SEED_SCHEMES:
        scheme = GovernmentScheme(
            name=s["name"],
            description=s["description"],
            benefit_amount=s["benefit_amount"],
            eligibility=s["eligibility"],
            documents_required=s["documents_required"],
            apply_url=s["apply_url"],
            scheme_type=s["scheme_type"],
            applicable_states=s["applicable_states"],
            last_updated=date.today(),
        )
        db.add(scheme)

    for loan_data in SEED_LOANS:
        db.add(LoanProgram(**loan_data))

    db.commit()


def get_schemes(db: Session, state: str | None = None, acreage_ha: float | None = None) -> list[dict]:
    """Return schemes filtered by state and farmer acreage with eligibility flag."""
    schemes = db.query(GovernmentScheme).all()
    results = []

    for s in schemes:
        # State filter
        states = json.loads(s.applicable_states) if s.applicable_states else ["all"]
        if state and "all" not in states and state not in states:
            continue

        # Acreage eligibility — look up max_acreage from SEED data by name
        seed = next((x for x in SEED_SCHEMES if x["name"] == s.name), {})
        max_ha = seed.get("max_acreage_ha")  # None = no limit

        if acreage_ha is not None and max_ha is not None:
            is_eligible = acreage_ha <= max_ha
        else:
            is_eligible = True  # no limit or unknown acreage → show as eligible

        results.append({
            "id": s.id,
            "name": s.name,
            "description": s.description,
            "benefit_amount": s.benefit_amount,
            "eligibility": s.eligibility,
            "documents_required": s.documents_required,
            "apply_url": s.apply_url,
            "scheme_type": s.scheme_type,
            "last_updated": s.last_updated.isoformat() if s.last_updated else None,
            "is_eligible": is_eligible,
            "max_acreage_ha": max_ha,
        })

    return results


def get_loans(db: Session) -> list[LoanProgram]:
    return db.query(LoanProgram).all()


def calculate_emi(principal: float, rate: float, tenure_months: int) -> dict:
    """Standard EMI formula. Rate=0 → flat division."""
    if rate == 0:
        monthly = principal / tenure_months
        return {
            "monthly_emi": round(monthly, 2),
            "total_payment": round(principal, 2),
            "total_interest": 0,
            "principal": principal,
            "rate": rate,
            "tenure_months": tenure_months,
        }
    r = rate / 100 / 12
    n = tenure_months
    emi = principal * r * ((1 + r) ** n) / (((1 + r) ** n) - 1)
    total = emi * n
    return {
        "monthly_emi": round(emi, 2),
        "total_payment": round(total, 2),
        "total_interest": round(total - principal, 2),
        "principal": principal,
        "rate": rate,
        "tenure_months": tenure_months,
    }
