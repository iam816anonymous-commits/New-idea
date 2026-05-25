def calculate_lead_score(intent: str, micro_market_match: bool, budget_provided: bool) -> int:
    """
    Calculates a weighted qualification score for a lead.
    """
    score = 0

    # Intent weight (50%)
    intent_scores = {
        "Investment": 50,
        "Self-use": 40,
        "Just checking prices": 10
    }
    score += intent_scores.get(intent, 0)

    # Micro-market match weight (25%)
    if micro_market_match:
        score += 25

    # Budget provision weight (25%)
    if budget_provided:
        score += 25

    return score
