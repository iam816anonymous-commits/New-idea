import random
import time

def scrape_competitor_ads(micro_market: str):
    """
    Simulates scraping Meta/TikTok ads for competitor projects.
    """
    print(f"DEBUG: Monitoring ads in {micro_market}...")
    time.sleep(1)

    competitors = [
        {"builder": "Prestige Group", "project": "Prestige Sanctuary", "offer": "No Pre-EMI until 2025", "hook": "Luxury living in the lap of nature"},
        {"builder": "Sobha", "project": "Sobha Oakshire", "offer": "₹2 Lakhs worth gold voucher on booking", "hook": "Tudor style row houses"},
        {"builder": "Assetz", "project": "Assetz Bloom & Dell", "offer": "Special pricing for first 50 units", "hook": "Sustainability meets luxury"}
    ]

    results = random.sample(competitors, random.randint(1, 3))
    print(f"DEBUG: Found {len(results)} active competitor ads.")
    return results

if __name__ == "__main__":
    ads = scrape_competitor_ads("Sarjapur")
    for ad in ads:
        print(f"Builder: {ad['builder']} | Project: {ad['project']} | Offer: {ad['offer']}")
