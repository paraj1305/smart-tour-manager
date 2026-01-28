from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def detect_intent_and_extract(text: str) -> dict:
    """
    Detect user intent and extract entities
    """

    system_prompt = """
You are a WhatsApp tour booking assistant.

Classify user intent into ONE of:
- book_tour
- ask_question
- greeting
- unknown

Also extract:
- travel_date (if any)
- city (if any)
- people_count (if any)

Respond ONLY in JSON.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ],
        temperature=0
    )

    return eval(response.choices[0].message.content)
