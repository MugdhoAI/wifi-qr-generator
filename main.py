#!/usr/bin/env python3
"""
WiFi QR Code Generator
-----------------------
Generates a scannable QR code that lets a phone camera connect to a
WiFi network automatically, without typing the password by hand.

Usage:
    python main.py --ssid "MyNetwork" --password "mypassword" --output wifi.png
    python main.py --ssid "OpenCafeWifi" --encryption nopass --output cafe.png
"""

import argparse
import sys
from pathlib import Path

from src.wifi_string import build_wifi_string
from src.qr_builder import generate_qr_image


def run(ssid: str, password: str, encryption: str, output: str) -> Path:
    """
    Build the WiFi QR string and save it as an image.

    Args:
        ssid: WiFi network name.
        password: WiFi password (ignored if encryption is "nopass").
        encryption: "WPA", "WEP", or "nopass".
        output: File path to save the PNG to.

    Returns:
        The path the QR image was saved to.
    """
    wifi_data = build_wifi_string(ssid, password, encryption)
    output_path = Path(output).expanduser().resolve()
    return generate_qr_image(wifi_data, output_path)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a scannable WiFi QR code that connects a phone automatically."
    )
    parser.add_argument("--ssid", required=True, help="WiFi network name (SSID).")
    parser.add_argument(
        "--password", default="",
        help="WiFi password. Not required if --encryption is nopass."
    )
    parser.add_argument(
        "--encryption", default="WPA", choices=["WPA", "WEP", "nopass"],
        help="Network encryption type. Default: WPA."
    )
    parser.add_argument(
        "--output", default="wifi_qr.png",
        help="Output PNG file path. Default: wifi_qr.png"
    )
    args = parser.parse_args()

    if args.encryption != "nopass" and not args.password:
        print("Error: --password is required unless --encryption is nopass.")
        sys.exit(1)

    try:
        saved_path = run(args.ssid, args.password, args.encryption, args.output)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    print(f"QR code saved to: {saved_path}")
    print("Scan it with a phone camera to connect automatically.")


if __name__ == "__main__":
    main()
