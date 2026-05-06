# Copyright (c) 2025 Emre Hacımustafaoğlu. All rights reserved.
# Proprietary software. Use, modification, and distribution require explicit written permission.
import hashlib
import logging
import warnings
from pathlib import Path

import joblib
from src.response_utils import tahmin_cevabi_olustur

logger = logging.getLogger(__name__)


def _verify_model_hash(model_yolu: str) -> None:
    """SHA256 doğrulaması. Hash dosyası yoksa yüklemeyi engelleme ama yüksek sesle uyar."""
    hash_path = Path(model_yolu).with_suffix(".sha256")
    if not hash_path.exists():
        logger.warning(
            "GUVENLIK UYARISI: Model hash dosyasi bulunamadi (%s). "
            "Modelin butunlugu dogrulanamadi. "
            "Hash olusturmak icin: python -c "
            "\"from src.tfidf_predictor import model_hash_olustur; model_hash_olustur()\"",
            hash_path,
        )
        return

    expected = hash_path.read_text(encoding="utf-8").strip()
    sha256 = hashlib.sha256()
    with open(model_yolu, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha256.update(chunk)
    actual = sha256.hexdigest()

    if actual != expected:
        raise RuntimeError(
            f"Model hash dogrulamasi BASARISIZ. "
            f"Beklenen: {expected[:16]}... | Gercek: {actual[:16]}... "
            "Model dosyasi degistirilmis veya bozulmus olabilir."
        )
    logger.info("Model hash dogrulandi: %s", actual[:16])


def model_hash_olustur(model_yolu: str = "models/ticket_module_predictor.pkl") -> None:
    """Model .pkl dosyasının SHA256 hash'ini .sha256 dosyasına yazar."""
    sha256 = hashlib.sha256()
    with open(model_yolu, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha256.update(chunk)
    hash_path = Path(model_yolu).with_suffix(".sha256")
    hash_path.write_text(sha256.hexdigest(), encoding="utf-8")
    print(f"Hash kaydedildi: {hash_path} -> {sha256.hexdigest()}")


def model_yukle(model_yolu: str = "models/ticket_module_predictor.pkl"):
    _verify_model_hash(model_yolu)
    # Sadece sklearn UserWarning'leri kapat; diğer uyarılar görünür kalır.
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")
        return joblib.load(model_yolu)


def tfidf_tahmin(ticket, model, threshold=0.6):
    tahmin = model.predict([ticket])[0]
    olasiliklar = model.predict_proba([ticket])[0]
    confidence = max(olasiliklar)

    if confidence < threshold:
        # düşük confidence, LLM'e git
        return None

    return tahmin_cevabi_olustur(
        method="tfidf",
        tcode=None,
        module=tahmin,
        confidence=f"{confidence:.2%}",
        message=f"TF-IDF tahmini: {tahmin} ({confidence:.2%})",
    )
