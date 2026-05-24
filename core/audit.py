from core.database import SessionLocal
from api import models

def log_event(tenant_id: int, event_type: str, details: str):
    """Logs critical business events for B2B auditing."""
    db = SessionLocal()
    try:
        log = models.AuditLog(
            brokerage_id=tenant_id,
            event_type=event_type,
            details=details
        )
        db.add(log)
        db.commit()
    finally:
        db.close()
