#!/usr/bin/env python3
"""Validate OpenHAB .sitemap files: basic structure (sitemap name { ... }, Frame, Text/Switch/Slider/Group)."""
import re
import sys
from pathlib import Path

def validate_sitemap_file(path: Path) -> list[str]:
    errors = []
    text = path.read_text(encoding="utf-8", errors="replace")
    if "sitemap " not in text and "sitemap " not in text.lower():
        errors.append(f"{path}: missing 'sitemap name label=...' declaration")
    if "{" in text and "}" not in text:
        errors.append(f"{path}: unclosed brace")
    if "}" in text and text.count("{") != text.count("}"):
        errors.append(f"{path}: brace count mismatch")
    for i, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("//"):
            continue
        # Frame label="..." { ... } or standalone elements
        if re.match(r'^\s*(Frame|Text|Switch|Slider|Group|Selection|Setpoint|Colorpicker)\s', stripped) or "sitemap " in stripped or stripped in "{}":
            continue
        if stripped.startswith("}"):
            continue
        if not any(x in stripped for x in ["label=", "item=", "}", "{", "sitemap"]):
            errors.append(f"{path}:{i}: unknown sitemap element: {stripped[:50]}")
    return errors

def main():
    root = Path(__file__).resolve().parent.parent
    conf = root / "openhab" / "conf" / "sitemaps"
    if not conf.exists():
        print("No openhab/conf/sitemaps directory")
        sys.exit(0)
    all_errors = []
    for f in conf.glob("*.sitemap"):
        all_errors.extend(validate_sitemap_file(f))
    if all_errors:
        for e in all_errors:
            print(e)
        sys.exit(1)
    print("Sitemap validation OK")

if __name__ == "__main__":
    main()
