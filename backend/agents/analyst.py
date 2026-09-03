"""
Preva AI Analyst
"""

import json
import os
import httpx

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

def fallback_analysis(purpose: str, amount: float, expected_revenue: float, evidence_confidence: float) -> dict:
    if expected_revenue > amount:
        assessment = "The proposal has positive expected revenue, but the assumptions should be verified."
    else:
        assessment = "The proposal does not currently demonstrate positive expected revenue."
    
    return {
        "available": False,
        "mode": "deterministic_fallback",
        "assessment": assessment,
        "assumptions": [
            "Expected revenue is accurate.",
            "The requested amount represents the full relevant cost.",
            "No major hidden costs have been omitted."
        ],
        "missing_information": ["Historical performance"] if evidence_confidence < 70 else [],
        "confidence": round(evidence_confidence, 2)
    }

async def analyze_with_ai(
    purpose: str,
    amount: float,
    expected_revenue: float,
    expected_customers: int,
    evidence_summary: str,
    evidence_confidence: float
) -> dict:
    api_key = os.getenv("GROQ_API_KEY")
    
    if not api_key:
        return fallback_analysis(purpose, amount, expected_revenue, evidence_confidence)
    
    prompt = f"""
You are Preva, an AI business decision analyst.

Proposal:
Purpose: {purpose}
Amount: {amount}
Expected revenue: {expected_revenue}
Expected customers: {expected_customers}

Evidence:
{evidence_summary}

Evidence confidence: {evidence_confidence}

Return ONLY valid JSON with:
{{
  "assessment": "short assessment",
  "assumptions": ["..."],
  "missing_information": ["..."],
  "risk_factors": ["..."],
  "recommended_questions": ["..."]
}}
"""
    
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": "You are a careful business analyst. Return JSON only."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1,
        "max_tokens": 800
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(GROQ_API_URL, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            parsed = json.loads(content)
            return {
                "available": True,
                "mode": "groq",
                **parsed
            }
    except Exception as exc:
        fallback = fallback_analysis(purpose, amount, expected_revenue, evidence_confidence)
        fallback["ai_error"] = str(exc)
        return fallback
