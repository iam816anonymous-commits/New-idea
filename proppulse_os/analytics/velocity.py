from sqlalchemy.orm import Session
from proppulse_os.lead_engine.models import Lead, Project
from proppulse_os.core.database import SessionLocal
from datetime import datetime, timedelta

def get_conversion_rate(tenant_id: int):
    db = SessionLocal()
    try:
        total = db.query(Lead).filter(Lead.brokerage_id == tenant_id).count()
        qualified = db.query(Lead).filter(Lead.brokerage_id == tenant_id, Lead.status == "Qualified").count()
        return (qualified / total * 100) if total > 0 else 0
    finally:
        db.close()

def get_lead_velocity(tenant_id: int):
    # Leads per day in the last 7 days
    db = SessionLocal()
    try:
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        count = db.query(Lead).filter(Lead.brokerage_id == tenant_id, Lead.created_at >= seven_days_ago).count()
        return count / 7
    finally:
        db.close()

def get_market_inventory_status(micro_market: str):
    # Simulated prediction
    if micro_market == "Sarjapur":
        return "Critical (Exhausting in 4 months)"
    return "Stable"
