import json
import sys

import pandas as pd
from src.rule_engine import kural_motoru_calistir, kurallari_yukle
from src.tfidf_predictor import model_yukle, tfidf_tahmin

# bir kere yükle
tcode_df = pd.read_csv("data/tcode_module_clean.csv")
tcode_dict = dict(zip(tcode_df["tcode"], tcode_df["module"]))
rules = kurallari_yukle()
model = model_yukle()
ml_threshold = (
    rules.get("fallback_behavior", {}).get("ml_confidence_threshold", 0.6)
    if isinstance(rules, dict)
    else 0.6
)


def tahmin_et(ticket):
    # katman 1: kural motoru
    sonuc = kural_motoru_calistir(ticket, tcode_dict, rules)
    if sonuc:
        return sonuc

    # katman 2: tfidf
    sonuc = tfidf_tahmin(ticket, model, threshold=float(ml_threshold))
    if sonuc:
        return sonuc

    # katman 3: llm fallback
    from src.llm_predictor import llm_tahmin

    return llm_tahmin(ticket)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('kullanım: python main.py "ticket metni"')
        sys.exit(1)

    sonuc = tahmin_et(sys.argv[1])
    print(json.dumps(sonuc, ensure_ascii=True))
