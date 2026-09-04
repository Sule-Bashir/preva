"""
Preva API - AI-powered business spending decision engine.
"""

from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from database import init_database, save_decision, get_decisions, get_stats
from services.roi import build_roi_report
from services.evidence import build_evidence_summary
from agents.guardrail import evaluate_guardrails
from agents.analyst import analyze_with_ai

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR.parent / "frontend"

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_database()
    yield

app = FastAPI(
    title="Preva",
    description="Preva evaluates proposed business spending before money is committed.",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://preva-sand.vercel.app", "https://preva.vercel.app", "http://localhost:8000", "https://preva-api.onrender.com", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DecisionRequest(BaseModel):
    purpose: str = Field(..., min_length=2, max_length=500)
    amount: float = Field(..., gt=0)
    expected_revenue: float = Field(..., ge=0)
    expected_customers: int = Field(default=0, ge=0)
    evidence_description: str = Field(default="No supporting evidence supplied.", max_length=3000)
    has_evidence: bool = False
    historical_roas: float | None = Field(default=None, ge=0)

@app.get("/")
def root():
    return {
        "product": "Preva",
        "tagline": "Prove it before you spend.",
        "status": "online",
        "version": "1.0.0"
    }

@app.get("/health")
def health():
    return {"status": "healthy", "database": "connected", "product": "Preva"}

@app.post("/analyze")
async def analyze_decision(request: DecisionRequest):
    evidence = build_evidence_summary(
        purpose=request.purpose,
        amount=request.amount,
        expected_revenue=request.expected_revenue,
        has_evidence=request.has_evidence,
        historical_roas=request.historical_roas
    )
    evidence_confidence = evidence["confidence"]
    
    revenue_per_customer = 0.0
    if request.expected_customers > 0:
        revenue_per_customer = request.expected_revenue / request.expected_customers
    
    roi_report = build_roi_report(
        amount=request.amount,
        expected_revenue=request.expected_revenue,
        expected_customers=request.expected_customers,
        revenue_per_customer=revenue_per_customer
    )
    
    guardrails = evaluate_guardrails(
        roi_report=roi_report,
        evidence_confidence=evidence_confidence,
        amount=request.amount,
        historical_roas=request.historical_roas
    )
    
    ai_analysis = await analyze_with_ai(
        purpose=request.purpose,
        amount=request.amount,
        expected_revenue=request.expected_revenue,
        expected_customers=request.expected_customers,
        evidence_summary=request.evidence_description + "\n" + "\n".join(evidence["items"]),
        evidence_confidence=evidence_confidence
    )
    
    result = {
        "purpose": request.purpose,
        "amount": request.amount,
        "expected_revenue": request.expected_revenue,
        "expected_customers": request.expected_customers,
        "evidence": evidence,
        "roi_report": roi_report,
        "guardrails": guardrails,
        "ai_analysis": ai_analysis
    }
    
    decision_id = save_decision(result)
    result["decision_id"] = decision_id
    
    return result

@app.get("/decisions")
def decisions():
    return {"decisions": get_decisions()}

@app.get("/stats")
def stats():
    return get_stats()

if FRONTEND_DIR.exists():
    app.mount("/app", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
