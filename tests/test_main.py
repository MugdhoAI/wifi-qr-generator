"""
Tests for the WiFi QR code generator.

Run with:
    python -m unittest discover tests
"""

import shutil
import tempfile
import unittest
from pathlib import Path

from src.wifi_string import build_wifi_string
from src.qr_builder import generate_qr_image


class TestBuildWifiString(unittest.TestCase):

    def test_wpa_network_includes_password(self):
        result = build_wifi_string("MyNetwork", "mypassword", "WPA")
        self.assertEqual(result, "WIFI:T:WPA;S:MyNetwork;P:mypassword;;")

    def test_open_network_has_no_password_field(self):
        result = build_wifi_string("OpenCafe", "", "nopass")
        self.assertEqual(result, "WIFI:T:nopass;S:OpenCafe;;")

    def test_special_characters_are_escaped(self):
        result = build_wifi_string("Weird;Name", "pass:word", "WEP")
        self.assertIn("Weird\\;Name", result)
        self.assertIn("pass\\:word", result)

    def test_empty_ssid_raises_error(self):
        with self.assertRaises(ValueError):
            build_wifi_string("", "password", "WPA")

    def test_invalid_encryption_raises_error(self):
        with self.assertRaises(ValueError):
            build_wifi_string("Network", "password", "FAKE")


class TestGenerateQrImage(unittest.TestCase):

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_creates_a_file_at_output_path(self):
        output_path = self.temp_dir / "test.png"
        result = generate_qr_image("WIFI:T:WPA;S:Test;P:pass;;", output_path)
        self.assertTrue(result.exists())

    def test_creates_parent_directories_if_missing(self):
        nested_path = self.temp_dir / "nested" / "folder" / "test.png"
        result = generate_qr_image("some data", nested_path)
        self.assertTrue(result.exists())


if __name__ == "__main__":
    unittest.main()
