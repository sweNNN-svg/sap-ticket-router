# Copyright (c) 2025 Emre Hacımustafaoğlu. All rights reserved.
# Proprietary software. Use, modification, and distribution require explicit written permission.
import re

import yaml
from src.response_utils import tahmin_cevabi_olustur


def kurallari_yukle(yaml_yolu="rules/rule_engine.yaml"):
    with open(yaml_yolu, "r", encoding="utf-8") as f:
        loaded = yaml.safe_load(f) or {}
    loaded.setdefault("overrides", [])
    loaded.setdefault("fallback_behavior", {})
    return loaded


def tcode_bul(metin):
    # büyük harfli kelimeleri yakala, tcode olabilir
    return re.findall(r"\b[A-Z0-9]{2,10}\b", metin.upper())


def _eslesme_var_mi(match_config, title, tcode):
    if not isinstance(match_config, dict):
        return False

    field = match_config.get("field")
    operator = match_config.get("operator")
    value = match_config.get("value", "")
    case_sensitive = bool(match_config.get("case_sensitive", True))

    source_map = {
        "title": title,
        "tcode": tcode,
    }
    source = source_map.get(field)
    if source is None:
        return False

    source_val = source if case_sensitive else source.lower()
    value_val = str(value) if case_sensitive else str(value).lower()

    if operator == "contains":
        return value_val in source_val
    if operator == "startswith":
        return source_val.startswith(value_val)
    if operator == "equals":
        return source_val == value_val
    return False


def kural_motoru_calistir(ticket, tcode_dict, rules):
    title = ticket
    tcodeler = tcode_bul(ticket)
    tcode = tcodeler[0] if tcodeler else ""

    # önce override kurallarına bak
    for kural in rules.get("overrides", []):
        if _eslesme_var_mi(kural.get("match"), title=title, tcode=tcode):
            return tahmin_cevabi_olustur(
                method="rule_override",
                tcode=tcode or None,
                module=kural.get("assign_to"),
                confidence="100%",
                message=kural.get("reason", "Override rule matched."),
            )

    # direkt tcode eşleşmesi
    for tcode in tcodeler:
        if tcode in tcode_dict:
            return tahmin_cevabi_olustur(
                method="rule_direct",
                tcode=tcode,
                module=tcode_dict[tcode],
                confidence="100%",
                message=f"{tcode} -> {tcode_dict[tcode]}",
            )

    return None
