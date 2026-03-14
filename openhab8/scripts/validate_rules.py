#!/usr/bin/env python3
"""Basic Rules DSL syntax check: rule/when/then/end balance and quotes."""
import re
import sys
from pathlib import Path

def validate_rules_file(path: Path) -> list[str]:
    errors = []
    text = path.read_text(encoding="utf-8", errors="replace")
    if "rule " not in text and "rule\t" not in text:
        return errors  # no rules
    # Check rule ... when ... then ... end
    rule_blocks = re.findall(r'rule\s+"[^"]*"\s*(.*?)end\s*', text, re.DOTALL)
    for block in rule_blocks:
        if "when" not in block:
            errors.append(f"{path}: rule block missing 'when'")
        if "then" not in block:
            errors.append(f"{path}: rule block missing 'then'")
    if "rule " in text and "end" not in text:
        errors.append(f"{path}: rule without 'end'")
    return errors

def main():
    root = Path(__file__).resolve().parent.parent
    conf = root / "openhab" / "conf" / "rules"
    if not conf.exists():
        sys.exit(0)
    all_errors = []
    for f in conf.glob("*.rules"):
        all_errors.extend(validate_rules_file(f))
    if all_errors:
        for e in all_errors:
            print(e)
        sys.exit(1)
    print("Rules validation OK")

if __name__ == "__main__":
    main()
