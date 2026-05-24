import time
import random
from sqlalchemy.orm import Session
from core.database import SessionLocal
from api import models

def trigger_whatsapp_qualification(lead_id: int):
    """
    Simulates triggering a WhatsApp qualification bot.
    In a real system, this would interact with a WhatsApp Business API.
    """
    print(f"DEBUG: Starting WhatsApp qualification for lead {lead_id}...")

    db = SessionLocal()
    try:
        lead = db.query(models.Lead).filter(models.Lead.id == lead_id).first()
        if not lead:
            print(f"ERROR: Lead {lead_id} not found")
            return

        # Simulate sending the first message
        message1 = f"Hi {lead.name}, noticed you're exploring luxury properties in {lead.project.micro_market if lead.project else 'Bangalore'}. To share the exclusive pricing matrix, are you looking for self-use or an investment asset?"
        print(f"DEBUG: WhatsApp SENT to {lead.phone_number}: {message1}")

        # Update status
        lead.status = "Contacted"
        lead.chat_history = f"Bot: {message1}\n"
        db.commit()

        # Simulate lead replying after some time
        time.sleep(1) # simulate "thinking" or waiting for reply

        replies = ["Investment", "Self-use", "Just checking prices"]
        user_reply = random.choice(replies)
        print(f"DEBUG: WhatsApp RECEIVED from {lead.phone_number}: {user_reply}")

        lead.chat_history += f"User: {user_reply}\n"

        # Automated scoring logic
        if user_reply in ["Investment", "Self-use"]:
            lead.qualification_score = 80
            lead.status = "Qualified"
            lead.budget_range = "1.5Cr - 2.5Cr" # extracted from context in real LLM
            response = "Great! I've sent the pricing matrix to your email. Would you like to schedule a site visit this weekend?"
        else:
            lead.qualification_score = 30
            lead.status = "Interested"
            response = "Understood. I'll share the brochure for your reference."

        print(f"DEBUG: WhatsApp SENT to {lead.phone_number}: {response}")
        lead.chat_history += f"Bot: {response}\n"
        db.commit()

    except Exception as e:
        print(f"ERROR: WhatsApp Loop failed: {e}")
    finally:
        db.close()

    return True

if __name__ == "__main__":
    # Test logic manually if needed
    pass
