"""
Preva Evidence Service
"""

def calculate_evidence_confidence(
    has_description: bool,
    has_amount: bool,
    has_expected_revenue: bool,
    has_evidence: bool,
    has_historical_data: bool
) -> float:
    score = 0
    if has_description:
        score += 20
    if has_amount:
        score += 20
    if has_expected_revenue:
        score += 20
    if has_evidence:
        score += 20
    if has_historical_data:
        score += 20
    return float(score)

def build_evidence_summary(
    purpose: str,
    amount: float,
    expected_revenue: float,
    has_evidence: bool,
    historical_roas: float | None
) -> dict:
    confidence = calculate_evidence_confidence(
        has_description=bool(purpose.strip()),
        has_amount=amount > 0,
        has_expected_revenue=expected_revenue > 0,
        has_evidence=has_evidence,
        has_historical_data=(historical_roas is not None and historical_roas > 0)
    )
    
    evidence_items = []
    if purpose.strip():
        evidence_items.append("Spending purpose provided.")
    if amount > 0:
        evidence_items.append("Requested amount provided.")
    if expected_revenue > 0:
        evidence_items.append("Expected revenue provided.")
    if has_evidence:
        evidence_items.append("Supporting evidence supplied.")
    else:
        evidence_items.append("No supporting document supplied.")
    if historical_roas is not None and historical_roas > 0:
        evidence_items.append(f"Historical ROAS available: {historical_roas:.2f}x.")
    else:
        evidence_items.append("Historical performance data unavailable.")
    
    return {
        "confidence": confidence,
        "items": evidence_items
    }
