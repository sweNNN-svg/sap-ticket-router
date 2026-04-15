def tahmin_cevabi_olustur(method, module, confidence, message, tcode=None):
    return {
        "method": method,
        "tcode": tcode,
        "module": module,
        "confidence": confidence,
        "message": message,
    }
