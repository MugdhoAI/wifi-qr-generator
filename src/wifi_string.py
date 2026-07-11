"""
wifi_string.py

Builds the special text format that phone cameras recognize as WiFi
connection data when scanned inside a QR code. No QR-code or image
logic lives here — this module only builds and validates the string,
exactly like classifier.py only decided categories without moving
files. Keeping format logic separate from image-generation logic
means we can test the string format without needing the qrcode
library installed at all.
"""

VALID_ENCRYPTION_TYPES = {"WPA", "WEP", "nopass"}


def _escape(value: str) -> str:
    """
    Escape characters that have special meaning in the WiFi QR format
    itself: backslash, semicolon, colon, and comma. Without this, a
    password like "pass;word" would break the format and could even
    get misread as a different field entirely.
    """
    for char in ("\\", ";", ",", ":"):
        value = value.replace(char, f"\\{char}")
    return value


def build_wifi_string(ssid: str, password: str, encryption: str = "WPA") -> str:
    """
    Build the WIFI: string that phone QR scanners recognize.

    Args:
        ssid: The WiFi network name.
        password: The WiFi password. Ignored if encryption is "nopass".
        encryption: One of "WPA", "WEP", or "nopass" (open network).

    Returns:
        A string like "WIFI:T:WPA;S:MyNetwork;P:mypassword;;"

    Raises:
        ValueError: If ssid is empty, or encryption isn't a recognized type.
    """
    if not ssid:
        raise ValueError("SSID cannot be empty.")

    if encryption not in VALID_ENCRYPTION_TYPES:
        raise ValueError(
            f"Invalid encryption type '{encryption}'. "
            f"Must be one of: {', '.join(sorted(VALID_ENCRYPTION_TYPES))}"
        )

    escaped_ssid = _escape(ssid)

    if encryption == "nopass":
        # Open networks have no password field at all — including an
        # empty P: field would confuse some scanners into thinking
        # there IS a password (just blank), rather than no security.
        return f"WIFI:T:nopass;S:{escaped_ssid};;"

    escaped_password = _escape(password)
    return f"WIFI:T:{encryption};S:{escaped_ssid};P:{escaped_password};;"
