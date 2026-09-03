"""
Preva ROI Engine - Deterministic financial calculations.
"""

def safe_divide(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator

def calculate_roi(amount: float, expected_revenue: float) -> float:
    if amount <= 0:
        return 0.0
    return ((expected_revenue - amount) / amount) * 100

def calculate_roas(amount: float, expected_revenue: float) -> float:
    return safe_divide(expected_revenue, amount)

def calculate_break_even_revenue(amount: float) -> float:
    return max(amount, 0.0)

def calculate_break_even_customers(amount: float, revenue_per_customer: float) -> int:
    if amount <= 0 or revenue_per_customer <= 0:
        return 0
    return int((amount / revenue_per_customer) + 0.999999)

def calculate_profit(amount: float, expected_revenue: float) -> float:
    return expected_revenue - amount

def calculate_downside(amount: float, expected_revenue: float, performance_factor: float = 0.5) -> dict:
    factor = max(0.0, min(performance_factor, 1.0))
    downside_revenue = expected_revenue * factor
    downside_profit = downside_revenue - amount
    return {
        "performance_factor": factor,
        "revenue": round(downside_revenue, 2),
        "profit_loss": round(downside_profit, 2),
        "loss": round(max(0.0, -downside_profit), 2)
    }

def calculate_scenarios(amount: float, expected_revenue: float) -> dict:
    factors = {
        "optimistic": 1.20,
        "expected": 1.00,
        "conservative": 0.75,
        "downside": 0.50
    }
    scenarios = {}
    for name, factor in factors.items():
        revenue = expected_revenue * factor
        profit_loss = revenue - amount
        scenarios[name] = {
            "revenue": round(revenue, 2),
            "profit_loss": round(profit_loss, 2),
            "profitable": profit_loss >= 0
        }
    return scenarios

def calculate_recommended_spend(amount: float, expected_revenue: float, minimum_roas: float = 1.2) -> float:
    if amount <= 0:
        return 0.0
    current_roas = calculate_roas(amount, expected_revenue)
    if current_roas <= 0:
        return 0.0
    if current_roas < minimum_roas:
        recommended = expected_revenue / minimum_roas
        return round(min(amount, recommended), 2)
    return round(amount, 2)

def build_roi_report(amount: float, expected_revenue: float, expected_customers: int = 0, revenue_per_customer: float = 0.0) -> dict:
    roi = calculate_roi(amount, expected_revenue)
    roas = calculate_roas(amount, expected_revenue)
    profit = calculate_profit(amount, expected_revenue)
    break_even_revenue = calculate_break_even_revenue(amount)
    
    if revenue_per_customer <= 0 and expected_customers > 0:
        revenue_per_customer = safe_divide(expected_revenue, expected_customers)
    
    break_even_customers = calculate_break_even_customers(amount, revenue_per_customer)
    downside = calculate_downside(amount, expected_revenue, 0.50)
    scenarios = calculate_scenarios(amount, expected_revenue)
    recommended_spend = calculate_recommended_spend(amount, expected_revenue)
    
    return {
        "roi_percent": round(roi, 2),
        "roas": round(roas, 2),
        "expected_profit": round(profit, 2),
        "break_even_revenue": round(break_even_revenue, 2),
        "revenue_per_customer": round(revenue_per_customer, 2),
        "break_even_customers": break_even_customers,
        "downside": downside,
        "scenarios": scenarios,
        "recommended_spend": recommended_spend
    }
