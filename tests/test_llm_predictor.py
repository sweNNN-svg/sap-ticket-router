# Copyright (c) 2025 Emre Hacımustafaoğlu. All rights reserved.
# Proprietary software. Use, modification, and distribution require explicit written permission.
import unittest

import src.llm_predictor as llm_predictor


class _FakeMessages:
    def __init__(self, response):
        self._response = response

    def create(self, **kwargs):
        return self._response


class _FakeClient:
    def __init__(self, response):
        self.messages = _FakeMessages(response)


class _FakeBlock:
    def __init__(self, text):
        self.text = text


class _FakeResponse:
    def __init__(self, content):
        self.content = content


class LlmPredictorTests(unittest.TestCase):
    def setUp(self):
        self._original_client_getir = llm_predictor._client_getir

    def tearDown(self):
        llm_predictor._client_getir = self._original_client_getir

    def test_json_temizle_markdown_block(self):
        raw = "```json\n{\"module\":\"MM\",\"confidence\":\"high\",\"reason\":\"ok\"}\n```"
        temiz = llm_predictor.json_temizle(raw)
        self.assertTrue(temiz.startswith("{"))
        self.assertIn("\"module\":\"MM\"", temiz)

    def test_llm_tahmin_success(self):
        response = _FakeResponse(
            [_FakeBlock('{"module":"MM","confidence":"high","reason":"test"}')]
        )
        llm_predictor._client_getir = lambda: _FakeClient(response)
        sonuc = llm_predictor.llm_tahmin("ticket")
        self.assertEqual(sonuc["method"], "llm")
        self.assertEqual(sonuc["module"], "MM")
        self.assertEqual(sonuc["confidence"], "high")

    def test_llm_tahmin_empty_content_raises(self):
        response = _FakeResponse([])
        llm_predictor._client_getir = lambda: _FakeClient(response)
        with self.assertRaises(RuntimeError):
            llm_predictor.llm_tahmin("ticket")


if __name__ == "__main__":
    unittest.main()
