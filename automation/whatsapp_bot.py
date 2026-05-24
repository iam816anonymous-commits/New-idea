import time
import random
from sqlalchemy.orm import Session
from core.database import SessionLocal
from api import models
from core.scoring import calculate_lead_score

def trigger_whatsapp_qualification(lead_id: int):
    """
    Simulates triggering a WhatsApp qualification bot.
    """
    start_time = time.time()
    print(f"DEBUG: Starting WhatsApp qualification for lead {lead_id}...")

    db = SessionLocal()
    try:
        lead = db.query(models.Lead).filter(models.Lead.id == lead_id).first()
        if not lead:
            return

        # Record response time (simulated 2-5 seconds for the "instant" feel)
        delay = random.randint(2, 5)
        time.sleep(delay)
        lead.response_time_seconds = int(time.time() - start_time)

        # Simulate sending the first message
        message1 = f"Hi {lead.name}, noticed you're exploring luxury properties in {lead.project.micro_market if lead.project else 'Bangalore'}. To share the exclusive pricing matrix, are you looking for self-use or an investment asset?"

        # Update status
        lead.status = "Contacted"
        lead.chat_history = f"Bot: {message1}\n"
        db.commit()

        # Simulate lead replying
        replies = ["Investment", "Self-use", "Just checking prices"]
        user_reply = random.choice(replies)

        lead.chat_history += f"User: {user_reply}\n"

        # Dynamic Scoring logic
        has_budget = user_reply in ["Investment", "Self-use"]
        score = calculate_lead_score(user_reply, True, has_budget)

        lead.qualification_score = score

        if score >= 75:
            lead.status = "Qualified"
            lead.budget_range = "1.5Cr - 2.5Cr"
            response = "Great! I've sent the pricing matrix to your email. Would you like to schedule a site visit this weekend?"
        elif score >= 40:
            lead.status = "Interested"
            response = "Understood. I'll share the floor plans for your reference. Any specific budget you have in mind?"
        else:
            lead.status = "Low Intent"
            response = "No problem. I'll send you our monthly market newsletter instead."

        lead.chat_history += f"Bot: {response}\n"
        db.commit()

    except Exception as e:
        print(f"ERROR: WhatsApp Loop failed: {e}")
    finally:
        db.close()

    return True
