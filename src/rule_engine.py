import re

import yaml


def kurallari_yukle(yaml_yolu="rules/rule_engine.yaml"):
    with open(yaml_yolu, "r") as f:
        return yaml.safe_load(f)


def tcode_bul(metin):
    # büyük harfli kelimeleri yakala, tcode olabilir
    return re.findall(r"\b[A-Z0-9]{2,10}\b", metin.upper())


def kural_motoru_calistir(ticket, tcode_dict, rules):
    baslik = ticket.lower()
    title = baslik
    tcodeler = tcode_bul(ticket)
    tcode = tcodeler[0] if tcodeler else ""

    # önce override kurallarına bak
    for kural in rules["overrides"]:
        try:
            if eval(kural["condition"]):
                return {
                    "method": "rule_override",
                    "tcode": tcode or None,
                    "module": kural["assign_to"],
                    "confidence": "100%",
                    "message": kural["reason"],
                }
        except:
            continue

    # direkt tcode eşleşmesi
    for tcode in tcodeler:
        if tcode in tcode_dict:
            return {
                "method": "rule_direct",
                "tcode": tcode,
                "module": tcode_dict[tcode],
                "confidence": "100%",
                "message": f"{tcode} → {tcode_dict[tcode]}",
            }

    return None
