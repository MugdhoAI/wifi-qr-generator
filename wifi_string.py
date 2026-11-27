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
    itself: backslash, semicolon, comma, colon, and double quote.
    The format reserves all five of these characters, so without this,
    a password like "pass;word" would break the format and could even
    get misread as a different field entirely, and a value containing
    a double quote could be misread by scanners that wrap values in
    quotes. Backslash is escaped first so the backslashes added for
    the other characters are not escaped again.
    """
    for char in ("\\", ";", ",", ":", '"'):
        value = value.replace(char, f"\\{char}")
    return value


def _validate_wpa_password(password: str) -> None:
    """
    Check a WPA password against the passphrase rules: 8 to 63
    characters, or exactly 64 hexadecimal characters when it is a
    raw pre-shared key instead of a passphrase. Anything else can
    never connect, so it is rejected here instead of producing a
    QR code that silently fails when scanned.
    """
    if len(password) == 64:
        if all(char in "0123456789abcdefABCDEF" for char in password):
            return
        raise ValueError(
            "A 64 character WPA password must be a hexadecimal pre-shared key."
        )
    if not 8 <= len(password) <= 63:
        raise ValueError("WPA password must be between 8 and 63 characters.")


def build_wifi_string(ssid: str, password: str, encryption: str = "WPA",
                      hidden: bool = False) -> str:
    """
    Build the WIFI: string that phone QR scanners recognize.

    Args:
        ssid: The WiFi network name.
        password: The WiFi password. Ignored if encryption is "nopass".
        encryption: One of "WPA", "WEP", or "nopass" (open network).
        hidden: True if the network SSID is hidden (not broadcast),
            which adds the H:true field scanners use to find it.

    Returns:
        A string like "WIFI:T:WPA;S:MyNetwork;P:mypassword;;"

    Raises:
        ValueError: If ssid is empty or longer than 32 bytes, or
            encryption isn't a recognized type.
    """
    if not ssid.strip():
        raise ValueError("SSID cannot be empty.")

    # The 802.11 standard limits SSIDs to 32 octets. The limit is in
    # bytes, not characters, so a name with multibyte characters
    # reaches it sooner than its character count suggests.
    if len(ssid.encode("utf-8")) > 32:
        raise ValueError("SSID cannot be longer than 32 bytes.")

    if encryption not in VALID_ENCRYPTION_TYPES:
        raise ValueError(
            f"Invalid encryption type '{encryption}'. "
            f"Must be one of: {', '.join(sorted(VALID_ENCRYPTION_TYPES))}"
        )

    if encryption != "nopass" and not password:
        raise ValueError("Password cannot be empty for WPA or WEP networks.")

    if encryption == "WPA":
        _validate_wpa_password(password)

    escaped_ssid = _escape(ssid)
    hidden_field = ";H:true" if hidden else ""

    if encryption == "nopass":
        # Open networks have no password field at all — including an
        # empty P: field would confuse some scanners into thinking
        # there IS a password (just blank), rather than no security.
        return f"WIFI:T:nopass;S:{escaped_ssid}{hidden_field};;"

    escaped_password = _escape(password)
    return f"WIFI:T:{encryption};S:{escaped_ssid};P:{escaped_password}{hidden_field};;"
