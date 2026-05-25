from typing import List, Optional
from proppulse_os.core.database import SessionLocal
from proppulse_os.lead_engine import models

def get_next_agent(brokerage_id: str) -> Optional[int]:
    """
    Simulates a round-robin lead assignment for a brokerage.
    In a real system, this would query agents and their current lead counts.
    """
    # Simple mock: return a random agent ID 1-5
    return (abs(hash(brokerage_id)) % 5) + 1

def route_lead(lead_id: int):
    """
    Routes a lead to an agent based on brokerage-level rules.
    """
    db = SessionLocal()
    try:
        lead = db.query(models.Lead).filter(models.Lead.id == lead_id).first()
        if lead:
            agent_id = get_next_agent(lead.brokerage_id)
            lead.assigned_agent_id = agent_id
            db.commit()
            print(f"Lead {lead_id} routed to Agent {agent_id}")
    finally:
        db.close()
