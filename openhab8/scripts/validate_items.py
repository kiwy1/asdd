#!/usr/bin/env python3
"""Validate OpenHAB .items files: basic syntax check (lines, item type + name)."""
import re
import sys
from pathlib import Path

# Item types per OpenHAB docs
ITEM_TYPES = {
    "Group", "Switch", "Rollershutter", "Contact", "String", "Number", "Dimmer",
    "DateTime", "Color", "Image", "Player", "Location"
}
NUMBER_SUBTYPES = ("Temperature", "Dimensionless", "Power", "Pressure", "Length", "Speed", "Intensity", "Angle")

def validate_items_file(path: Path) -> list[str]:
    errors = []
    for i, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("//"):
            continue
        # Group ItemName "Label" ...
        # Number:Temperature ItemName "Label" ...
        if not re.match(r'^(Group|Switch|Rollershutter|Contact|String|Number(?::\w+)?|Dimmer|DateTime|Color|Image|Player|Location)\s+\w+', stripped):
            errors.append(f"{path}:{i}: invalid item declaration: {stripped[:60]}")
    return errors

def main():
    root = Path(__file__).resolve().parent.parent
    conf = root / "openhab" / "conf" / "items"
    if not conf.exists():
        print("No openhab/conf/items directory")
        sys.exit(0)
    all_errors = []
    for f in conf.glob("*.items"):
        all_errors.extend(validate_items_file(f))
    if all_errors:
        for e in all_errors:
            print(e)
        sys.exit(1)
    print("Items validation OK")

if __name__ == "__main__":
    main()
