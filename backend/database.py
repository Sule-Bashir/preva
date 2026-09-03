"""
Preva SQLite database.
"""

import sqlite3
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "preva.db"

def get_connection():
    connection = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    return connection

def init_database():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS decisions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            purpose TEXT NOT NULL,
            amount REAL NOT NULL,
            expected_revenue REAL NOT NULL,
            expected_customers INTEGER DEFAULT 0,
            roi_percent REAL,
            roas REAL,
            risk_score INTEGER,
            evidence_confidence REAL,
            recommended_spend REAL,
            decision TEXT,
            explanation TEXT,
            created_at TEXT NOT NULL
        )
    """)
    connection.commit()
    connection.close()

def save_decision(data: dict) -> int:
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO decisions (
            purpose, amount, expected_revenue, expected_customers,
            roi_percent, roas, risk_score, evidence_confidence,
            recommended_spend, decision, explanation, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["purpose"],
        data["amount"],
        data["expected_revenue"],
        data.get("expected_customers", 0),
        data["roi_report"]["roi_percent"],
        data["roi_report"]["roas"],
        data["guardrails"]["risk_score"],
        data["guardrails"]["evidence_confidence"],
        data["guardrails"]["recommended_spend"],
        data["guardrails"]["decision"],
        data["guardrails"]["explanation"],
        datetime.utcnow().isoformat()
    ))
    decision_id = cursor.lastrowid
    connection.commit()
    connection.close()
    return decision_id

def get_decisions(limit: int = 50) -> list:
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM decisions ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    connection.close()
    return [dict(row) for row in rows]

def get_stats() -> dict:
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) AS total FROM decisions")
    total = cursor.fetchone()["total"]
    cursor.execute("SELECT COALESCE(SUM(amount), 0) AS amount FROM decisions")
    total_amount = cursor.fetchone()["amount"]
    cursor.execute("SELECT COUNT(*) AS count FROM decisions WHERE decision = 'APPROVE'")
    approved = cursor.fetchone()["count"]
    cursor.execute("SELECT COUNT(*) AS count FROM decisions WHERE decision = 'REJECT'")
    rejected = cursor.fetchone()["count"]
    cursor.execute("SELECT COUNT(*) AS count FROM decisions WHERE decision IN ('REVIEW', 'CONDITIONAL')")
    review = cursor.fetchone()["count"]
    connection.close()
    return {
        "total_decisions": total,
        "total_amount_analyzed": round(total_amount, 2),
        "approved": approved,
        "rejected": rejected,
        "needs_review": review
    }
