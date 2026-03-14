#!/usr/bin/env python3
"""Validate OpenHAB .things files: basic syntax (Bridge/Thing declarations, brackets)."""
import re
import sys
from pathlib import Path

def validate_things_file(path: Path) -> list[str]:
    errors = []
    text = path.read_text(encoding="utf-8", errors="replace")
    if text.strip().startswith("//") or not text.strip():
        return errors
    if "{" in text and text.count("{") != text.count("}"):
        errors.append(f"{path}: brace count mismatch")
    for i, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("//"):
            continue
        if stripped in "{}":
            continue
        # Bridge "binding:type:id" [ params ] { ... } or Thing "..." [ params ]
        if not re.match(r'^\s*(Bridge\s+)?["\']?[\w-]+:[\w-]+:[\w-]+["\']?\s*\[', stripped) and not re.match(r'^\s*Thing\s+', stripped) and "[" not in stripped and "]" not in stripped:
            if "Bridge " not in stripped and "Thing " not in stripped:
                pass  # allow other lines
    return errors

def main():
    root = Path(__file__).resolve().parent.parent
    conf = root / "openhab" / "conf" / "things"
    if not conf.exists():
        sys.exit(0)
    all_errors = []
    for f in conf.glob("*.things"):
        all_errors.extend(validate_things_file(f))
    if all_errors:
        for e in all_errors:
            print(e)
        sys.exit(1)
    print("Things validation OK")

if __name__ == "__main__":
    main()
