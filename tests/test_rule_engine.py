import tempfile
import unittest

from src.rule_engine import kural_motoru_calistir, kurallari_yukle


class RuleEngineTests(unittest.TestCase):
    def test_case_insensitive_override_match(self):
        rules = {
            "overrides": [
                {
                    "match": {
                        "field": "title",
                        "operator": "contains",
                        "value": "#SanctionTrace",
                        "case_sensitive": False,
                    },
                    "assign_to": "SD",
                    "reason": "override test",
                }
            ]
        }
        sonuc = kural_motoru_calistir("#sanctiontrace task var", {}, rules)
        self.assertIsNotNone(sonuc)
        self.assertEqual(sonuc["method"], "rule_override")
        self.assertEqual(sonuc["module"], "SD")

    def test_direct_rule_message_ascii_safe(self):
        rules = {"overrides": []}
        sonuc = kural_motoru_calistir("MIGO hata veriyor", {"MIGO": "MM"}, rules)
        self.assertIsNotNone(sonuc)
        self.assertEqual(sonuc["method"], "rule_direct")
        self.assertIn("->", sonuc["message"])

    def test_rule_loader_defaults_missing_keys(self):
        with tempfile.NamedTemporaryFile("w+", suffix=".yaml", delete=False) as f:
            f.write("{}")
            path = f.name
        loaded = kurallari_yukle(path)
        self.assertIn("overrides", loaded)
        self.assertIn("fallback_behavior", loaded)


if __name__ == "__main__":
    unittest.main()
