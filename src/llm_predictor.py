import json
import os

from anthropic import Anthropic
from anthropic.types import TextBlock
from dotenv import load_dotenv

load_dotenv()

# client bir kere açılıyor
client = Anthropic()


def json_temizle(raw):
    # bazen markdown ile geliyor, temizle
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()
    return raw


def llm_tahmin(ticket):
    # kural ve tfidf tutmadı, claude'a sor
    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=200,
        messages=[
            {
                "role": "user",
                "content": (f"Ticket: {ticket}\n\n"),
            }
        ],
        system='You are an SAP support ticket routing expert. Classify this ticket into one SAP module:\'FI, CO, MM, SD, HR, PM, QM, PP, Authorization, E-Solutions, Basis\n\n\'. Respond with raw JSON only, no markdown: {"module": "MODULE_NAME", "confidence": "high/medium/low", "reason": "one sentence"}',
    )

    block = response.content[0]
    assert isinstance(block, TextBlock), f"beklenmedik tip: {type(block)}"

    try:
        raw = json_temizle(block.text)
        sonuc = json.loads(raw)
    except:
        print("json parse olmadı kanka")
        print("raw geldi:", block.text)
        raise

    return {
        "method": "llm",
        "tcode": None,
        "module": sonuc["module"],
        "confidence": sonuc["confidence"],
        "message": sonuc["reason"],
    }
