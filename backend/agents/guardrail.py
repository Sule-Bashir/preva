"""
Preva Guardrail Engine - Deterministic rules, NOT LLM
"""

def calculate_risk_score(
    roi_percent: float,
    roas: float,
    evidence_confidence: float,
    downside_loss: float,
    amount: float,
    historical_roas: float | None = None
) -> int:
    score = 0
    
    if roi_percent < 0:
        score += 30
    elif roi_percent < 10:
        score += 20
    elif roi_percent < 30:
        score += 10
    
    if roas < 1.0:
        score += 20
    elif roas < 1.2:
        score += 10
    
    if evidence_confidence < 40:
        score += 25
    elif evidence_confidence < 60:
        score += 15
    elif evidence_confidence < 75:
        score += 5
    
    if downside_loss > amount * 0.50:
        score += 20
    elif downside_loss > amount * 0.25:
        score += 10
    elif downside_loss > 0:
        score += 5
    
    if historical_roas is not None and historical_roas > 0:
        if roas > historical_roas * 2:
            score += 15
        elif roas > historical_roas * 1.5:
            score += 8
    
    return min(100, max(0, score))

def determine_decision(
    risk_score: int,
    roi_percent: float,
    evidence_confidence: float,
    roas: float,
    amount: float,
    recommended_spend: float,
    historical_roas: float | None = None
) -> str:
    if amount <= 0:
        return "REJECT"
    if roi_percent < 0:
        return "REJECT"
    if roas < 0.8:
        return "REJECT"
    
    if evidence_confidence < 40:
        return "REVIEW"
    
    if risk_score >= 75:
        return "REJECT"
    
    if historical_roas is not None:
        if historical_roas > 0 and roas < historical_roas * 0.7:
            return "REVIEW"
    
    if risk_score >= 50:
        return "CONDITIONAL"
    
    if recommended_spend > 0:
        if recommended_spend < amount * 0.70:
            return "CONDITIONAL"
    
    if evidence_confidence < 70:
        return "CONDITIONAL"
    
    return "APPROVE"

def decision_explanation(decision: str, risk_score: int, roi_percent: float, evidence_confidence: float, recommended_spend: float, amount: float) -> str:
    if decision == "REJECT":
        return "Preva recommends rejecting this spending request because the financial risk is too high under the current assumptions."
    if decision == "REVIEW":
        return "Preva recommends human review because there is not enough reliable evidence to safely approve the request."
    if decision == "CONDITIONAL":
        if recommended_spend < amount:
            return f"Preva recommends a controlled approval with a maximum initial spend of {recommended_spend:,.2f}. The requested amount is higher than the evidence currently supports."
        return "Preva recommends conditional approval because the opportunity may be viable, but additional evidence or monitoring is required."
    return "Preva found the proposal financially reasonable under the supplied assumptions and evidence."

def evaluate_guardrails(
    roi_report: dict,
    evidence_confidence: float,
    amount: float,
    historical_roas: float | None = None
) -> dict:
    roi_percent = roi_report["roi_percent"]
    roas = roi_report["roas"]
    downside_loss = roi_report["downside"]["loss"]
    recommended_spend = roi_report["recommended_spend"]
    
    risk_score = calculate_risk_score(
        roi_percent=roi_percent,
        roas=roas,
        evidence_confidence=evidence_confidence,
        downside_loss=downside_loss,
        amount=amount,
        historical_roas=historical_roas
    )
    
    decision = determine_decision(
        risk_score=risk_score,
        roi_percent=roi_percent,
        evidence_confidence=evidence_confidence,
        roas=roas,
        amount=amount,
        recommended_spend=recommended_spend,
        historical_roas=historical_roas
    )
    
    explanation = decision_explanation(
        decision=decision,
        risk_score=risk_score,
        roi_percent=roi_percent,
        evidence_confidence=evidence_confidence,
        recommended_spend=recommended_spend,
        amount=amount
    )
    
    return {
        "decision": decision,
        "risk_score": risk_score,
        "explanation": explanation,
        "evidence_confidence": evidence_confidence,
        "recommended_spend": recommended_spend
    }
