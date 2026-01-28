from fastapi import APIRouter, Request, Depends
import os
import requests
from app.chatbot.handler import handle_message
from app.database.session import get_db
from sqlalchemy.orm import Session

router = APIRouter()

VERIFY_TOKEN = os.getenv("WHATSAPP_WEBHOOK_VERIFY_TOKEN")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")

# -------------------------------
# Webhook Verification (GET)
# -------------------------------
@router.get("/webhooks/whatsapp")
async def verify_webhook(request: Request):
    hub_mode = request.query_params.get("hub.mode")
    hub_token = request.query_params.get("hub.verify_token")
    hub_challenge = request.query_params.get("hub.challenge")

    if hub_mode == "subscribe" and hub_token == VERIFY_TOKEN:
        return int(hub_challenge)

    return "Invalid token"

# -------------------------------
# Receive WhatsApp Messages (POST)
# -------------------------------
@router.post("/webhooks/whatsapp")
async def receive_message(request: Request, db: Session = Depends(get_db)):
    data = await request.json()

    for entry in data.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            messages = value.get("messages", [])

            print("messages", messages)

            for msg in messages:
                if msg.get("type") != "text":
                    continue

                phone = msg.get("from")
                text = msg.get("text", {}).get("body", "").strip()

                if not text:
                    continue

                reply = handle_message(phone, text, db)
                send_whatsapp_message(phone, reply)

    return {"status": "ok"}

# -------------------------------
# Send WhatsApp Message
# -------------------------------
def send_whatsapp_message(phone: str, text: str):
    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"

    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "text",
        "text": {"body": text}
    }

    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()


@router.post("/test-whatsapp")
async def test_whatsapp(db: Session = Depends(get_db)):
    phone = "+91399399999"
    text = "hi"
    reply = handle_message(phone, text, db)
    return {"reply": reply}