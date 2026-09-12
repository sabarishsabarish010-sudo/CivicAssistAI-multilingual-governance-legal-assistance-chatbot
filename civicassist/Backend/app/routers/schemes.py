from typing import List, Optional, Dict, Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.llm_service import generate_response


router = APIRouter(
    prefix="/api/schemes",
    tags=["Government Schemes"],
)


# ============================================================
# Data Models
# ============================================================

class Scheme(BaseModel):
    id: str
    name: str
    description: str
    category: str
    level: str = "Central"
    state: Optional[str] = None
    benefits: List[str] = Field(default_factory=list)
    eligibility: List[str] = Field(default_factory=list)
    documents: List[str] = Field(default_factory=list)
    application_process: List[str] = Field(default_factory=list)
    official_url: Optional[str] = None


class SchemeSearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    state: Optional[str] = None
    category: Optional[str] = None


class EligibilityRequest(BaseModel):
    age: Optional[int] = None
    state: Optional[str] = None
    occupation: Optional[str] = None
    income: Optional[float] = None
    category: Optional[str] = None
    documents_available: Optional[str] = None


class AIEligibilityRequest(BaseModel):
    scheme: Dict[str, Any]
    profile: Dict[str, Any]


# ============================================================
# Initial Scheme Knowledge
# ============================================================
# This is temporary seed data.
#
# Later these schemes will come from:
#   - data/schemes/
#   - database
#   - myScheme
#   - official government sources
#
# We are deliberately keeping the router functional first.
# ============================================================

SCHEMES = [
    Scheme(
        id="pm-kisan",
        name="PM-KISAN",
        description=(
            "Income support scheme for eligible landholding farmer "
            "families, subject to applicable government conditions."
        ),
        category="Farmer",
        level="Central",
        benefits=[
            "Income support through eligible installments"
        ],
        eligibility=[
            "Eligible landholding farmer family",
            "Must satisfy applicable exclusion and eligibility conditions"
        ],
        documents=[
            "Aadhaar",
            "Land records",
            "Bank account details"
        ],
        application_process=[
            "Check eligibility",
            "Verify land and identity details",
            "Complete registration through the official system"
        ],
        official_url="https://pmkisan.gov.in/",
    ),

    Scheme(
        id="ayushman-bharat-pm-jay",
        name="Ayushman Bharat PM-JAY",
        description=(
            "Government health assurance scheme providing eligible "
            "beneficiary families access to covered healthcare services."
        ),
        category="Healthcare",
        level="Central",
        benefits=[
            "Cashless healthcare coverage at empanelled hospitals",
            "Coverage for eligible treatments under the scheme"
        ],
        eligibility=[
            "Eligibility depends on the applicable beneficiary database "
            "and government criteria"
        ],
        documents=[
            "Aadhaar or other accepted identity document",
            "Beneficiary identification details"
        ],
        application_process=[
            "Check beneficiary eligibility",
            "Verify identity",
            "Use the official PM-JAY process for accessing services"
        ],
        official_url="https://pmjay.gov.in/",
    ),

    Scheme(
        id="pmay-u-2",
        name="PMAY-U 2.0",
        description=(
            "Government housing assistance framework for eligible "
            "urban households under applicable components."
        ),
        category="Home",
        level="Central",
        benefits=[
            "Housing assistance under applicable PMAY-U 2.0 components"
        ],
        eligibility=[
            "Eligibility depends on the selected PMAY-U 2.0 component",
            "Household and income conditions may apply",
            "Other government-prescribed conditions apply"
        ],
        documents=[
            "Identity proof",
            "Address proof",
            "Income-related documents",
            "Bank account details",
            "Other component-specific documents"
        ],
        application_process=[
            "Identify the applicable PMAY-U 2.0 component",
            "Check eligibility",
            "Prepare required documents",
            "Apply through the applicable official channel"
        ],
        official_url="https://pmay-urban.gov.in/",
    ),

    Scheme(
        id="mgnrega",
        name="MGNREGA",
        description=(
            "Rural employment programme providing a legal guarantee "
            "of wage employment to eligible rural households."
        ),
        category="Employment",
        level="Central",
        benefits=[
            "Demand-based wage employment under the programme"
        ],
        eligibility=[
            "Adult members of eligible rural households",
            "Applicant must be willing to perform unskilled manual work"
        ],
        documents=[
            "Job card",
            "Identity details",
            "Bank or post-office account details where applicable"
        ],
        application_process=[
            "Approach the appropriate Gram Panchayat",
            "Request employment",
            "Complete the applicable registration and job-card process"
        ],
        official_url="https://nrega.nic.in/",
    ),

    Scheme(
        id="pm-svanidhi",
        name="PM SVANidhi",
        description=(
            "Central government scheme supporting eligible street vendors "
            "through working-capital assistance and related incentives."
        ),
        category="Employment",
        level="Central",
        benefits=[
            "Working-capital support subject to applicable conditions",
            "Other scheme-linked incentives for eligible beneficiaries"
        ],
        eligibility=[
            "Eligible street vendors",
            "Must satisfy applicable scheme requirements"
        ],
        documents=[
            "Identity proof",
            "Street vendor identification or relevant certificate",
            "Bank account details"
        ],
        application_process=[
            "Verify street-vendor eligibility",
            "Prepare required documents",
            "Apply through the official scheme channel"
        ],
        official_url="https://pmsvanidhi.mohua.gov.in/",
    ),
]


# ============================================================
# GET ALL SCHEMES
# ============================================================

@router.get("", response_model=List[Scheme])
async def get_schemes():
    """
    Return all currently loaded schemes.
    """

    return SCHEMES


# ============================================================
# SEARCH SCHEMES
# ============================================================

@router.post("/search", response_model=List[Scheme])
async def search_schemes(request: SchemeSearchRequest):
    """
    Search schemes by:
        - name
        - description
        - category
        - benefit
        - eligibility
        - state
    """

    query = request.query.strip().lower()

    if not query:
        raise HTTPException(
            status_code=400,
            detail="Search query cannot be empty.",
        )

    results = []

    for scheme in SCHEMES:

        searchable_text = " ".join(
            [
                scheme.name,
                scheme.description,
                scheme.category,
                scheme.level,
                scheme.state or "",
                " ".join(scheme.benefits),
                " ".join(scheme.eligibility),
                " ".join(scheme.documents),
            ]
        ).lower()

        if query not in searchable_text:
            continue

        if request.category:
            if scheme.category.lower() != request.category.lower():
                continue

        if request.state:
            if scheme.state and scheme.state.lower() != request.state.lower():
                continue

        results.append(scheme)

    return results


# ============================================================
# GET SCHEME BY ID
# ============================================================

@router.get("/{scheme_id}", response_model=Scheme)
async def get_scheme(scheme_id: str):
    """
    Return detailed information about one scheme.
    """

    scheme_id = scheme_id.strip().lower()

    for scheme in SCHEMES:
        if scheme.id.lower() == scheme_id:
            return scheme

    raise HTTPException(
        status_code=404,
        detail="Scheme not found.",
    )


# ============================================================
# CHECK ELIGIBILITY
# ============================================================

@router.post(
    "/{scheme_id}/eligibility"
)
async def check_eligibility(
    scheme_id: str,
    request: EligibilityRequest,
):
    """
    AI-assisted eligibility explanation. It does not make a final
    government eligibility determination.
    """

    scheme_id = scheme_id.strip().lower()
    scheme = next(
        (item for item in SCHEMES if item.id.lower() == scheme_id),
        None,
    )

    if scheme is None:
        raise HTTPException(status_code=404, detail="Scheme not found.")

    profile = {
        "age": request.age,
        "state": request.state,
        "occupation": request.occupation,
        "annual_family_income": request.income,
        "category": request.category,
        "documents_available": request.documents_available,
    }

    prompt = f"""
Analyze possible eligibility for this government scheme using ONLY the scheme data below.

SCHEME:
Name: {scheme.name}
Description: {scheme.description}
Category: {scheme.category}
Benefits: {scheme.benefits}
Eligibility conditions: {scheme.eligibility}
Required documents: {scheme.documents}
Application process: {scheme.application_process}
Official URL: {scheme.official_url}

CITIZEN PROFILE:
{profile}

Return:
1. A short possible eligibility result ("Likely matches", "Some conditions unclear", or "Likely does not match").
2. Conditions the profile appears to satisfy.
3. Conditions that still need verification.
4. Documents to prepare.
5. Next application step.
Do not invent criteria. Do not request Aadhaar numbers, OTPs, passwords, PINs, or other secrets.
Clearly say that final eligibility must be verified against the current official scheme rules.
""".strip()

    try:
        result = await generate_response(
            message=prompt,
            language="en",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to check eligibility with Gemini: {str(exc)}",
        )

    return {
        "scheme_id": scheme.id,
        "scheme_name": scheme.name,
        "status": "needs_official_verification",
        "message": result.get("response", ""),
        "eligibility_conditions": scheme.eligibility,
        "required_documents": scheme.documents,
        "official_url": scheme.official_url,
    }


@router.post("/eligibility-check")
async def ai_eligibility_check(request: AIEligibilityRequest):
    """Check a frontend scheme against a citizen profile with Gemini."""
    scheme = request.scheme or {}
    profile = request.profile or {}

    if not scheme.get("name"):
        raise HTTPException(status_code=400, detail="Scheme name is required.")

    prompt = f"""
Analyze possible eligibility for this government scheme using ONLY the supplied scheme information.

SCHEME:
{scheme}

CITIZEN PROFILE:
{profile}

Return a concise citizen-friendly answer with:
### Result
Choose: Likely matches / Some conditions unclear / Likely does not match.

### Conditions that match
- List only conditions supported by the scheme data.

### Conditions to verify
- List missing or uncertain requirements.

### Documents
- List documents stated by the scheme.

### Next step
- Give the application step stated by the scheme.

Do not invent eligibility rules. Do not request Aadhaar numbers, OTPs, passwords, PINs, or other secrets.
Final eligibility must be verified against the current official scheme rules.
""".strip()

    try:
        result = await generate_response(message=prompt, language="en")
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to check eligibility with Gemini: {str(exc)}",
        )

    return {
        "status": "needs_official_verification",
        "message": result.get("response", ""),
        "scheme_name": scheme.get("name"),
        "official_url": scheme.get("official_url") or scheme.get("where"),
    }


# ============================================================
# SCHEME ROUTER HEALTH CHECK
# ============================================================

@router.get("/health/status")
async def schemes_health():
    """
    Check whether the schemes router is working.
    """

    return {
        "status": "ok",
        "service": "schemes",
        "scheme_count": len(SCHEMES),
    }
    