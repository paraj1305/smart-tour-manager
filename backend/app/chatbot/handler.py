from app.chatbot.states import *
from app.chatbot.replies import *
from app.chatbot.validators import *
from app.chatbot.services import filter_packages
from app.models.chat_session import ChatSession

def handle_message(phone: str, text: str, db):
    text = text.strip()
    session = db.query(ChatSession).filter_by(phone=phone).first()

    if not session:
        session = ChatSession(phone=phone)
        db.add(session)
        db.commit()
        db.refresh(session)

    state = session.state
    data = session.data or {}

    # ---------- GLOBAL COMMANDS ----------
    if text.lower() in ["menu", "start"]:
        session.state = GREETING
        db.commit()
        return greeting()

    # ---------- GREETING ----------
    if state == GREETING:
        session.state = CHOOSE_INTENT
        db.commit()
        return greeting()

    # ---------- INTENT ----------
    if state == CHOOSE_INTENT:
        if text == "1":
            session.state = TRAVEL_DATE
            db.commit()
            return ask_travel_date()
        elif text == "2":
            session.state = FAQ
            db.commit()
            return faq_intro()
        else:
            return "❌ Please reply with 1 or 2."

    # ---------- FAQ ----------
    if state == FAQ:
        q = text.lower()

        if "price" in q:
            return "💰 Prices start from AED 150 per person."
        if "pickup" in q:
            return "🚐 Pickup available from hotels & homes."
        if "payment" in q:
            return "💳 Cash, Card & UPI accepted."
        if "book" in q:
            session.state = TRAVEL_DATE
            db.commit()
            return ask_travel_date()

        return fallback()

    # ---------- BOOKING FLOW ----------
    if state == TRAVEL_DATE:
        if not valid_date(text):
            return "❌ Please enter date as DD/MM/YYYY"
        data["travel_date"] = text
        session.data = data
        session.state = PEOPLE_COUNT
        db.commit()
        return "How many people? (Adults Kids Infants)\nExample: 2 1 0"

    if state == PEOPLE_COUNT:
        try:
            a, k, i = map(int, text.split())
            data["people"] = {"adults": a, "kids": k, "infants": i}
            session.data = data
            session.state = BUDGET
            db.commit()
            return "What is your budget per person? 💰"
        except:
            return "❌ Format: Adults Kids Infants (2 1 0)"

    if state == BUDGET:
        if not valid_int(text):
            return "❌ Enter valid budget number"
        data["budget"] = int(text)
        session.data = data
        session.state = CITY
        db.commit()
        return "Which city? Abu Dhabi / Dubai / Al Ain / Fujairah / ALL"

    if state == CITY:
        packages = filter_packages(db, text.title(), data["budget"])
        if not packages:
            session.state = FALLBACK
            db.commit()
            return "❌ No packages found. Our team will contact you."

        data["packages"] = [
            {"id": p.id, "name": p.title, "price": p.price}
            for p in packages
        ]
        session.data = data
        session.state = SHOW_PACKAGE
        db.commit()

    if state == SHOW_PACKAGE:
        msg = "Available tours:\n"
        for i, p in enumerate(data["packages"], start=1):
            msg += f"{i}️⃣ {p['name']} – AED {p['price']}\n"
        msg += "\nReply with package number."
        session.state = PACKAGE_SELECT
        db.commit()
        return msg

    return fallback()
