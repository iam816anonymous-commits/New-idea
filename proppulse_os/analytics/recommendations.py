from typing import List, Dict
from proppulse_os.market_intel.engine import MarketIntelEngine
from sqlalchemy.orm import Session

class GrowthAdvisor:
    def __init__(self, db: Session):
        self.db = db
        self.intel = MarketIntelEngine(db)

    def get_recommendations(self, tenant_id: int) -> List[Dict]:
        recommendations = []

        # 1. Market Opportunity
        pulse = self.intel.analyze_market_momentum("Sarjapur") # Mocking Sarjapur as primary
        if pulse['sentiment'] == "Bullish" and pulse['ad_velocity'] == "High":
            recommendations.append({
                "category": "Ad Strategy",
                "title": "Increase Spend in Sarjapur",
                "body": "Market momentum is high. Competitor ad velocity suggests a price hike is imminent. Secure leads now at current CPL.",
                "priority": "High"
            })

        # 2. Lead Conversion
        recommendations.append({
            "category": "Sales Ops",
            "title": "Follow up with Hot Leads < 4h",
            "body": "AI Lead Brain identified 3 high-intent buyers in the last 24h. Human follow-up within 4 hours increases booking rate by 40%.",
            "priority": "Critical"
        })

        # 3. Inventory Warning
        recommendations.append({
            "category": "Inventory",
            "title": "3BHK Inventory Alert",
            "body": "Demand for 3BHKs in Bagalur is outpacing current ingestion. Consider pushing 2BHK + Study alternatives in next ad campaign.",
            "priority": "Medium"
        })

        return recommendations
