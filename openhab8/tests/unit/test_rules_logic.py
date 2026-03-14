"""Unit tests for rule logic (simulated behavior)."""
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent.parent
RULES_DIR = ROOT / "openhab" / "conf" / "rules"


def _all_rules_content():
    if not RULES_DIR.exists():
        return []
    parts = []
    for f in RULES_DIR.glob("*.rules"):
        parts.append(f.read_text(encoding="utf-8", errors="replace"))
    return parts


def test_rules_contain_when_then():
    content = "".join(_all_rules_content())
    if "rule " not in content:
        pytest.skip("No rules files")
    assert "when" in content, "Rules should have 'when' clause"
    assert "then" in content, "Rules should have 'then' clause"


def test_rules_balanced_end():
    content = "".join(_all_rules_content())
    if "rule " not in content:
        pytest.skip("No rules files")
    rule_count = len(re.findall(r'\brule\s+["\']', content))
    end_count = len(re.findall(r'\bend\s*', content))
    assert rule_count <= end_count, "Each rule should have matching 'end'"


def test_no_empty_rule_blocks():
    content = "".join(_all_rules_content())
    if "rule " not in content:
        pytest.skip("No rules files")
    blocks = re.findall(r"then\s*(.*?)end", content, re.DOTALL)
    for block in blocks:
        stripped = block.strip()
        assert len(stripped) > 0, "Rule 'then' block should not be empty"
