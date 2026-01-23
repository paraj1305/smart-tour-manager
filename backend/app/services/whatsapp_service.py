import requests
import os
import logging

logger = logging.getLogger(__name__)

WHATSAPP_API_URL = "https://graph.facebook.com/v17.0"


def send_whatsapp_booking_confirmation(phone_number: str, booking):
    access_token = os.getenv("WHATSAPP_ACCESS_TOKEN")
    phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")

    if not access_token or not phone_number_id:
        raise ValueError("WhatsApp credentials missing")

    url = f"{WHATSAPP_API_URL}/{phone_number_id}/messages"

    payload = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "template",
        "template": {
            "name": "booking_confirmed",
            "language": {"code": "en_US"},
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": booking.guest_name},                 
                        {"type": "text", "text": booking.tour_package.title},         
                        {"type": "text", "text": str(booking.travel_date)},          
                        {"type": "text", "text": str(booking.travel_time or "-")},    
                        {"type": "text", "text": booking.pickup_location or "-"},     
                    ],
                }
            ],
        },
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    response = requests.post(url, json=payload, headers=headers, timeout=10)

    if response.status_code != 200:
        logger.error("WhatsApp error: %s", response.text)
        response.raise_for_status()

    logger.info("WhatsApp booking confirmation sent to %s", phone_number)
    return response.json()

def format_phone(country_code: str, phone: str) -> str:
    phone = phone.replace(" ", "").replace("-", "")
    phone = phone.lstrip("0")
    return f"{country_code}{phone}"
