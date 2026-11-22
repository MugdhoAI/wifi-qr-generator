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


def print_qr_to_terminal(data: str) -> None:
    """
    Print the QR code for `data` to the terminal as text blocks,
    so the code can be scanned straight from the screen without
    opening the saved image file.
    """
    qr = qrcode.QRCode(
        version=None,          # None = auto-size based on data length
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        border=1,              # keep the printed code compact
    )
    qr.add_data(data)
    qr.make(fit=True)
    qr.print_ascii()


def generate_qr_image(data: str, output_path: Path,
                      fill_color: str = "black",
                      back_color: str = "white") -> Path:
    """
    Generate a QR code image encoding `data` and save it as a PNG.

    Args:
        data: The text to encode (e.g. a WIFI: connection string).
        output_path: Where to save the PNG file.
        fill_color: Color of the dark QR modules. Any Pillow color
            name or hex value, such as "darkblue" or "#1a365d".
        back_color: Color of the light background, same format.

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

    image = qr.make_image(fill_color=fill_color, back_color=back_color)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_path)

    return output_path
