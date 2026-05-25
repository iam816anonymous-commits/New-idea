import random
import time
from proppulse_os.core.database import SessionLocal
from proppulse_os.lead_engine import models

def scrape_competitor_ads(micro_market: str):
    """
    Simulates scraping Meta/TikTok ads for competitor projects.
    """
    print(f"DEBUG: Monitoring ads in {micro_market}...")
    time.sleep(1)

    competitors = [
        {"builder": "Prestige Group", "project_name": "Prestige Sanctuary", "offer": "No Pre-EMI until 2025", "hook": "Luxury living in the lap of nature", "micro_market": micro_market},
        {"builder": "Sobha", "project_name": "Sobha Oakshire", "offer": "₹2 Lakhs worth gold voucher on booking", "hook": "Tudor style row houses", "micro_market": micro_market},
        {"builder": "Assetz", "project_name": "Assetz Bloom & Dell", "offer": "Special pricing for first 50 units", "hook": "Sustainability meets luxury", "micro_market": micro_market}
    ]

    results = random.sample(competitors, random.randint(1, 3))

    # Persist to DB
    db = SessionLocal()
    try:
        for res in results:
            # Check if ad already exists (simple builder + project check)
            exists = db.query(models.AdIntelligence).filter(
                models.AdIntelligence.builder == res["builder"],
                models.AdIntelligence.project_name == res["project_name"]
            ).first()
            if not exists:
                db_ad = models.AdIntelligence(**res)
                db.add(db_ad)
        db.commit()
        print(f"Saved {len(results)} ad intelligence records.")
    finally:
        db.close()

    return results

if __name__ == "__main__":
    scrape_competitor_ads("Sarjapur")
    scrape_competitor_ads("Whitefield")
