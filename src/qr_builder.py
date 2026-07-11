"""
qr_builder.py

Turns a text string into a QR code image and saves it to disk.
This is the only module that touches the external `qrcode` library
and does image/file work — same isolation principle as mover.py in
the file organizer project: keep the "risky"/external-dependency
code in one place, separate from pure logic.
"""

from pathlib import Path

import qrcode


def generate_qr_image(data: str, output_path: Path) -> Path:
    """
    Generate a QR code image encoding `data` and save it as a PNG.

    Args:
        data: The text to encode (e.g. a WIFI: connection string).
        output_path: Where to save the PNG file.

    Returns:
        The path the image was saved to (same as output_path, returned
        for convenience so calling code can immediately reference it).
    """
    qr = qrcode.QRCode(
        version=None,          # None = auto-size based on data length
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,           # pixel size of each QR "module" (square)
        border=4,              # thickness of the white border, in modules
    )
    qr.add_data(data)
    qr.make(fit=True)

    image = qr.make_image(fill_color="black", back_color="white")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_path)

    return output_path
