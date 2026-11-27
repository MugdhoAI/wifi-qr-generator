"""
Tests for the WiFi QR code generator.

Run with:
    python -m unittest discover tests
"""

import contextlib
import io
import shutil
import tempfile
import unittest
from pathlib import Path

from src.wifi_string import build_wifi_string
from src.qr_builder import generate_qr_image, print_qr_to_terminal


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

    def test_double_quotes_are_escaped(self):
        result = build_wifi_string('My "Home" Net', 'say "hi" now', "WPA")
        self.assertEqual(
            result,
            'WIFI:T:WPA;S:My \\"Home\\" Net;P:say \\"hi\\" now;;',
        )

    def test_all_reserved_characters_are_escaped(self):
        result = build_wifi_string("Net", 'a\\b;c,d:e"f', "WPA")
        self.assertIn('P:a\\\\b\\;c\\,d\\:e\\"f', result)

    def test_hidden_network_adds_hidden_field(self):
        result = build_wifi_string("MyNetwork", "mypassword", "WPA", hidden=True)
        self.assertEqual(result, "WIFI:T:WPA;S:MyNetwork;P:mypassword;H:true;;")

    def test_hidden_open_network_adds_hidden_field(self):
        result = build_wifi_string("OpenCafe", "", "nopass", hidden=True)
        self.assertEqual(result, "WIFI:T:nopass;S:OpenCafe;H:true;;")

    def test_empty_password_raises_error_for_wpa(self):
        with self.assertRaises(ValueError):
            build_wifi_string("Network", "", "WPA")

    def test_empty_password_raises_error_for_wep(self):
        with self.assertRaises(ValueError):
            build_wifi_string("Network", "", "WEP")

    def test_wep_network_format(self):
        result = build_wifi_string("OldRouter", "wepkey123", "WEP")
        self.assertEqual(result, "WIFI:T:WEP;S:OldRouter;P:wepkey123;;")

    def test_open_network_ignores_password(self):
        result = build_wifi_string("OpenCafe", "shouldbeignored", "nopass")
        self.assertEqual(result, "WIFI:T:nopass;S:OpenCafe;;")

    def test_empty_ssid_raises_error(self):
        with self.assertRaises(ValueError):
            build_wifi_string("", "password", "WPA")

    def test_whitespace_only_ssid_raises_error(self):
        with self.assertRaises(ValueError):
            build_wifi_string("   ", "password", "WPA")

    def test_invalid_encryption_raises_error(self):
        with self.assertRaises(ValueError):
            build_wifi_string("Network", "password", "FAKE")

    def test_ssid_of_exactly_32_bytes_is_accepted(self):
        result = build_wifi_string("A" * 32, "mypassword", "WPA")
        self.assertIn("S:" + "A" * 32, result)

    def test_ssid_longer_than_32_bytes_raises_error(self):
        with self.assertRaises(ValueError):
            build_wifi_string("A" * 33, "mypassword", "WPA")

    def test_ssid_length_counts_utf8_bytes_not_characters(self):
        # 16 accented characters are 32 bytes, 17 are 34 bytes.
        result = build_wifi_string("é" * 16, "mypassword", "WPA")
        self.assertIn("S:" + "é" * 16, result)
        with self.assertRaises(ValueError):
            build_wifi_string("é" * 17, "mypassword", "WPA")

    def test_wpa_password_shorter_than_8_raises_error(self):
        with self.assertRaises(ValueError):
            build_wifi_string("Network", "short12", "WPA")

    def test_wpa_password_of_8_characters_is_accepted(self):
        result = build_wifi_string("Network", "12345678", "WPA")
        self.assertIn("P:12345678", result)

    def test_wpa_password_of_63_characters_is_accepted(self):
        result = build_wifi_string("Network", "a" * 63, "WPA")
        self.assertIn("P:" + "a" * 63, result)

    def test_wpa_password_of_64_hex_characters_is_accepted(self):
        result = build_wifi_string("Network", "0123456789abcdef" * 4, "WPA")
        self.assertIn("P:" + "0123456789abcdef" * 4, result)

    def test_wpa_password_of_64_non_hex_characters_raises_error(self):
        with self.assertRaises(ValueError):
            build_wifi_string("Network", "g" * 64, "WPA")

    def test_wpa_password_longer_than_64_raises_error(self):
        with self.assertRaises(ValueError):
            build_wifi_string("Network", "a" * 65, "WPA")


class TestGenerateQrImage(unittest.TestCase):

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_creates_a_file_at_output_path(self):
        output_path = self.temp_dir / "test.png"
        result = generate_qr_image("WIFI:T:WPA;S:Test;P:pass;;", output_path)
        self.assertTrue(result.exists())

    def test_generate_qr_image_returns_the_given_path(self):
        output_path = self.temp_dir / "out.png"
        result = generate_qr_image("hello", output_path)
        self.assertEqual(result, output_path)

    def test_creates_parent_directories_if_missing(self):
        nested_path = self.temp_dir / "nested" / "folder" / "test.png"
        result = generate_qr_image("some data", nested_path)
        self.assertTrue(result.exists())

    def test_custom_colors_produce_a_different_image(self):
        default_path = self.temp_dir / "default.png"
        custom_path = self.temp_dir / "custom.png"
        generate_qr_image("WIFI:T:WPA;S:Test;P:pass;;", default_path)
        generate_qr_image("WIFI:T:WPA;S:Test;P:pass;;", custom_path,
                          fill_color="darkblue", back_color="lightyellow")
        self.assertTrue(custom_path.exists())
        self.assertNotEqual(default_path.read_bytes(), custom_path.read_bytes())

    def test_print_qr_to_terminal_outputs_blocks(self):
        captured = io.StringIO()
        with contextlib.redirect_stdout(captured):
            print_qr_to_terminal("WIFI:T:WPA;S:Test;P:pass;;")
        output = captured.getvalue()
        self.assertTrue(output.strip())
        self.assertIn("██", output)


if __name__ == "__main__":
    unittest.main()
