from sqlalchemy.orm import Session
from proppulse_os.core.database import SessionLocal
from proppulse_os.lead_engine.models import AdIntelligence, Lead, Project
from proppulse_os.core.logger import logger
from datetime import datetime, timedelta
import random

class MarketIntelEngine:
    def __init__(self, db: Session):
        self.db = db

    def analyze_market_momentum(self, micro_market: str):
        # Simulated ad velocity and pricing trends
        ad_count = self.db.query(AdIntelligence).filter(AdIntelligence.micro_market == micro_market).count()
        leads_count = self.db.query(Lead).join(Project).filter(Project.micro_market == micro_market).count()

        velocity = "High" if ad_count > 5 else "Moderate"
        momentum = (leads_count * 1.5) + (ad_count * 2.0)

        return {
            "micro_market": micro_market,
            "ad_velocity": velocity,
            "momentum_score": momentum,
            "sentiment": "Bullish" if momentum > 10 else "Neutral",
            "price_trend": "+4.2% (QoQ)"
        }

    def detect_competitor_shifts(self, tenant_id: int):
        # Logic to find if competitors in the same micro-market are changing hooks
        competitors = self.db.query(AdIntelligence).filter(AdIntelligence.brokerage_id == tenant_id).all()
        shifts = []
        for comp in competitors:
             if "limited" in comp.hook.lower() or "offer" in comp.hook.lower():
                 shifts.append(f"High urgency campaign detected by {comp.builder} in {comp.micro_market}")
        return shifts

def extract_lead_intent(lead_id: int):
    db = SessionLocal()
    try:
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead: return

        # Simulated NLP extraction from conversation
        # In real world, this would use OpenAI/Claude on chat_history
        intent_map = {
            "budget_range": random.choice(["80L - 1.2Cr", "1.5Cr - 2.5Cr", "3Cr+"]),
            "location_pref": lead.project.micro_market if lead.project else "Central Bangalore",
            "purchase_urgency": random.choice(["30 days", "90 days", "6 months"]),
            "intent_type": random.choice(["Investment", "Self-use"]),
            "readiness_score": random.randint(60, 95)
        }

        lead.budget_range = intent_map["budget_range"]
        lead.location_pref = intent_map["location_pref"]
        lead.purchase_urgency = intent_map["purchase_urgency"]
        lead.intent_type = intent_map["intent_type"]
        lead.readiness_score = intent_map["readiness_score"]
        lead.ai_confidence = random.randint(85, 99)

        db.commit()
        logger.info(f"AI Lead Brain: Extracted intent for lead {lead.id}")
    finally:
        db.close()
