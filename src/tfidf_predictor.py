import warnings

import joblib

warnings.filterwarnings("ignore")


def model_yukle(model_yolu="models/ticket_module_predictor.pkl"):
    # pkl'den modeli yükle
    return joblib.load(model_yolu)


def tfidf_tahmin(ticket, model, threshold=0.6):
    tahmin = model.predict([ticket])[0]
    olasiliklar = model.predict_proba([ticket])[0]
    confidence = max(olasiliklar)

    if confidence < threshold:
        # düşük confidence, LLM'e git
        return None

    return {
        "method": "tfidf",
        "tcode": None,
        "module": tahmin,
        "confidence": f"{confidence:.2%}",
        "message": f"TF-IDF tahmini: {tahmin} ({confidence:.2%})",
    }
