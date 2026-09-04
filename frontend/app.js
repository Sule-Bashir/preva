const API_BASE = window.PREVA_API_URL || "https://preva-api.onrender.com";
const form = document.getElementById("decision-form");
const analyzeButton = document.getElementById("analyze-button");
const emptyState = document.getElementById("empty-state");
const result = document.getElementById("result");

function formatMoney(value) {
    return new Intl.NumberFormat("en-NG", {
        style: "currency",
        currency: "NGN",
        maximumFractionDigits: 0
    }).format(value || 0);
}

function showResult(data) {
    emptyState.classList.add("hidden");
    result.classList.remove("hidden");
    
    const decision = data.guardrails.decision;
    const decisionLabel = document.getElementById("decision-label");
    decisionLabel.textContent = decision;
    decisionLabel.className = "decision-" + decision.toLowerCase();
    
    document.getElementById("roi").textContent = data.roi_report.roi_percent + "%";
    document.getElementById("roas").textContent = data.roi_report.roas + "×";
    document.getElementById("risk").textContent = data.guardrails.risk_score + "/100";
    document.getElementById("confidence").textContent = data.guardrails.evidence_confidence + "%";
    document.getElementById("risk-score").textContent = data.guardrails.risk_score;
    document.getElementById("explanation").textContent = data.guardrails.explanation;
    document.getElementById("recommended-spend").textContent = formatMoney(data.guardrails.recommended_spend);
    
    const scenarios = document.getElementById("scenario-list");
    scenarios.innerHTML = "";
    const scenarioData = data.roi_report.scenarios;
    for (const [name, scenario] of Object.entries(scenarioData)) {
        const row = document.createElement("div");
        row.className = "scenario-row";
        const label = name.charAt(0).toUpperCase() + name.slice(1);
        const outcome = scenario.profit_loss >= 0 ? "+" : "";
        row.innerHTML = `<span>${label}</span><strong>${formatMoney(scenario.revenue)}</strong><span>${outcome}${formatMoney(scenario.profit_loss)}</span>`;
        scenarios.appendChild(row);
    }
    
    const ai = data.ai_analysis;
    document.getElementById("ai-assessment").textContent = ai.assessment || "No AI assessment available.";
    document.getElementById("ai-mode").textContent = ai.available ? "AI analysis active" : "Deterministic fallback active";
}

async function loadStats() {
    try {
        const response = await fetch(API_BASE + "/stats");
        if (!response.ok) return;
        const stats = await response.json();
        document.getElementById("stat-total").textContent = stats.total_decisions;
        document.getElementById("stat-amount").textContent = formatMoney(stats.total_amount_analyzed);
        document.getElementById("stat-approved").textContent = stats.approved;
        document.getElementById("stat-review").textContent = stats.needs_review;
        document.getElementById("stat-rejected").textContent = stats.rejected;
    } catch (error) {
        console.log("Stats unavailable:", error);
    }
}

form.addEventListener("submit", async function(event) {
    event.preventDefault();
    analyzeButton.disabled = true;
    analyzeButton.textContent = "Analyzing...";
    
    const purpose = document.getElementById("purpose").value;
    const amount = Number(document.getElementById("amount").value);
    const expectedRevenue = Number(document.getElementById("expected-revenue").value);
    const expectedCustomers = Number(document.getElementById("expected-customers").value) || 0;
    const historicalRoasValue = document.getElementById("historical-roas").value;
    const historicalRoas = historicalRoasValue === "" ? null : Number(historicalRoasValue);
    const hasEvidence = document.getElementById("has-evidence").checked;
    const evidenceDescription = document.getElementById("evidence-description").value;
    
    const payload = {
        purpose, amount,
        expected_revenue: expectedRevenue,
        expected_customers: expectedCustomers,
        evidence_description: evidenceDescription,
        has_evidence: hasEvidence,
        historical_roas: historicalRoas
    };
    
    try {
        const response = await fetch(API_BASE + "/analyze", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || "Analysis failed.");
        showResult(data);
        loadStats();
    } catch (error) {
        alert("Preva error: " + error.message);
    } finally {
        analyzeButton.disabled = false;
        analyzeButton.textContent = "Analyze Decision";
    }
});

loadStats();
