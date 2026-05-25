import requests
from proppulse_os.core.logger import logger

def notify_external_crm(lead_id: int, lead_data: dict, webhook_url: str):
    """
    Simulates notifying an external CRM via an outbound webhook.
    """
    try:
        # In production, this would be a POST request to the CRM
        logger.info(f"CRM Webhook triggered for lead {lead_id} -> {webhook_url}")
        # response = requests.post(webhook_url, json=lead_data, timeout=5)
        # response.raise_for_status()
    except Exception as e:
        logger.error(f"CRM Webhook failed: {e}")
