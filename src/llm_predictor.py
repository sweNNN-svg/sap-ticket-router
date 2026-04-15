import json

from anthropic import Anthropic
from dotenv import load_dotenv
from src.response_utils import tahmin_cevabi_olustur

load_dotenv()

_client = None


def _client_getir():
    global _client
    if _client is None:
        _client = Anthropic()
    return _client


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
    try:
        response = _client_getir().messages.create(
            model="claude-haiku-4-5",
            max_tokens=200,
            temperature=0.1,
            messages=[
                {
                    "role": "user",
                    "content": (f"Ticket: {ticket}\n\n"),
                }
            ],
            system='You are an SAP support ticket routing expert. Classify this ticket into one SAP module:\'FI, CO, MM, SD, HR, PM, QM, PP, Authorization, E-Solutions, Basis\n\n\'. Respond with raw JSON only, no markdown: {"module": "MODULE_NAME", "confidence": "high/medium/low", "reason": "one sentence"}',
        )
    except Exception as exc:
        raise RuntimeError(f"LLM istegi basarisiz: {exc}") from exc

    if not getattr(response, "content", None):
        raise RuntimeError("LLM bos icerik dondu.")

    block = response.content[0]
    text = getattr(block, "text", None)
    if not text:
        raise RuntimeError(f"LLM text olmayan blok dondurdu: {type(block)}")

    try:
        raw = json_temizle(text)
        sonuc = json.loads(raw)
    except Exception as exc:
        raise RuntimeError(f"LLM JSON parse hatasi: {exc}") from exc

    return tahmin_cevabi_olustur(
        method="llm",
        tcode=None,
        module=sonuc["module"],
        confidence=sonuc["confidence"],
        message=sonuc["reason"],
    )
