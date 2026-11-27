# WiFi QR Code Generator

A command line tool that generates a scannable QR code for a WiFi network. Scan it with a phone camera to connect automatically without typing the password by hand.

## Demo

```
$ python main.py --ssid "MyHomeNetwork" --password "supersecret123" --output wifi.png
QR code saved to: /home/user/wifi-qr-generator/wifi.png
Scan it with a phone camera to connect automatically.
```

## Features

- **WPA/WEP/open network support** generates the correct QR format for secured or open networks
- **Hidden network support** adds the `H:true` field for SSIDs that are not broadcast, with `--hidden`
- **Terminal preview** prints the QR code straight to the terminal with `--show`, no need to open the image file
- **Custom QR colors** pick the module and background colors with `--fill` and `--back`
- **Special character escaping** safely handles SSIDs or passwords containing backslashes, semicolons, commas, colons, or double quotes without breaking the QR format
- **Input validation** rejects invalid encryption types, empty or blank SSIDs, and missing passwords for secured networks before attempting anything. SSIDs are limited to 32 bytes (the 802.11 limit, counted in UTF-8 bytes), and WPA passwords must be 8 to 63 characters, or a 64 character hexadecimal pre-shared key
- **Automatic QR sizing** calculates the grid size automatically based on data length

## Tech Stack

- Python 3.9+
- [`qrcode`](https://github.com/lincolnloop/python-qrcode) — QR code generation
- `Pillow` — image saving (installed automatically as a dependency of `qrcode`)
- `argparse` — CLI argument parsing

## Getting Started

### Prerequisites
- Python 3.9 or higher

### Installation
```bash
git clone https://github.com/MugdhoAI/wifi-qr-generator
cd wifi-qr-generator
pip install -r requirements.txt
```

### Usage
```bash
# WPA-secured network
python main.py --ssid "MyNetwork" --password "mypassword" --output wifi.png

# Open network (no password)
python main.py --ssid "CafeWifi" --encryption nopass --output cafe.png

# WEP network
python main.py --ssid "OldRouter" --password "wepkey123" --encryption WEP

# Hidden network, with a terminal preview
python main.py --ssid "HiddenNet" --password "secret123" --hidden --show

# Custom QR colors
python main.py --ssid "MyNetwork" --password "mypassword" --fill darkblue --back lightyellow
```

## Project Structure
```
wifi-qr-generator/
├── main.py                # CLI entry point, argument parsing
├── src/
│   ├── wifi_string.py      # Builds the WIFI: connection string (pure logic, no I/O)
│   └── qr_builder.py        # Generates and saves the QR code image
├── tests/
│   └── test_main.py         # Unit tests for string building and image generation
├── requirements.txt
└── .gitignore
```

## Running Tests
```bash
python -m pytest
```
or with the standard library only:
```bash
python -m unittest discover tests
```

## What I Learned

This project introduced working with an external dependency instead of only the standard library — which meant learning `requirements.txt` so the exact same environment can be recreated on another machine with one command. I also learned why some values (like SSID/password) need character-escaping before being embedded into a structured text format, since unescaped special characters can silently break the format a scanner expects.

## Future Improvements
- [x] Optional terminal preview of the QR code (added with `--show`)
- [x] Custom QR code colors (added with `--fill` and `--back`)
- [ ] Batch mode: generate QR codes for multiple networks from a CSV file
- [ ] Logo embedding in the QR code

## Author
**Mugdho (All Asmaul Husnain)**
[GitHub](https://github.com/MugdhoAI) | [LinkedIn](https://linkedin.com/in/mugdhoai)
