# Copyright (c) 2025 Emre Hacımustafaoğlu. All rights reserved.
# Proprietary software. Use, modification, and distribution require explicit written permission.
def tahmin_cevabi_olustur(method, module, confidence, message, tcode=None):
    return {
        "method": method,
        "tcode": tcode,
        "module": module,
        "confidence": confidence,
        "message": message,
    }
