#!/usr/bin/env python3
"""Fail-closed JSON loading tests; synthetic input is never Unreal runtime proof."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Scripts"))
import cp1_gate_runtime as gate


class CP1GateJSONLoaderTests(unittest.TestCase):
    def load_bytes(self, payload: bytes):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "cp1.json"
            path.write_bytes(payload)
            return gate.load_json_file(path)

    def test_valid_object_preserves_exact_raw_bytes(self):
        payload = b'{"status":"GREEN","nested":{"value":1}}\n'
        data, raw, error = self.load_bytes(payload)
        self.assertIsNone(error)
        self.assertEqual(data, {"status": "GREEN", "nested": {"value": 1}})
        self.assertEqual(raw, payload)

    def test_duplicate_root_and_nested_keys_fail_closed(self):
        for payload in (
            b'{"status":"RED","status":"GREEN"}',
            b'{"status":"GREEN","nested":{"x":1,"x":2}}',
        ):
            with self.subTest(payload=payload):
                data, raw, error = self.load_bytes(payload)
                self.assertIsNone(data)
                self.assertIsNone(raw)
                self.assertIn("duplicate JSON key", error)

    def test_non_finite_constants_fail_closed_even_when_nested(self):
        for token in ("NaN", "Infinity", "-Infinity"):
            with self.subTest(token=token):
                payload = ('{"status":"GREEN","nested":[' + token + ']}').encode()
                data, raw, error = self.load_bytes(payload)
                self.assertIsNone(data)
                self.assertIsNone(raw)
                self.assertIn("non-finite JSON constant", error)

    def test_invalid_utf8_fails_closed(self):
        data, raw, error = self.load_bytes(b'{"status":"GREEN","bad":"\xff"}')
        self.assertIsNone(data)
        self.assertIsNone(raw)
        self.assertIn("invalid JSON file", error)

    def test_non_object_root_is_rejected(self):
        data, raw, error = self.load_bytes(b'["GREEN"]')
        self.assertIsNone(data)
        self.assertEqual(raw, b'["GREEN"]')
        self.assertIn("not an object", error)

    def test_oversized_json_is_rejected_without_unbounded_read(self):
        data, raw, error = self.load_bytes(b" " * (gate.MAX_JSON_BYTES + 1))
        self.assertIsNone(data)
        self.assertIsNone(raw)
        self.assertIn("exceeds", error)

    def test_symlink_to_valid_json_is_not_followed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "actual.json"
            target.write_text('{"status":"GREEN"}', encoding="utf-8")
            link = root / "cp1.json"
            try:
                link.symlink_to(target)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks unavailable")
            data, raw, error = gate.load_json_file(link)
            self.assertIsNone(data)
            self.assertIsNone(raw)
            self.assertIn("symbolic link", error)

    def test_missing_file_is_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            data, raw, error = gate.load_json_file(Path(tmp) / "missing.json")
            self.assertIsNone(data)
            self.assertIsNone(raw)
            self.assertIn("missing file", error)


if __name__ == "__main__":
    unittest.main()
