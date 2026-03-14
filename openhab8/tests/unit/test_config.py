"""Configuration tests: items list, sitemap structure, metadata."""
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent.parent
CONF = ROOT / "openhab" / "conf"


def test_items_dir_exists():
    assert (CONF / "items").is_dir()


def test_items_files_present():
    items_dir = CONF / "items"
    files = list(items_dir.glob("*.items"))
    assert len(files) >= 1, "At least one .items file required"


def test_sitemap_files_present():
    sitemaps = CONF / "sitemaps"
    if not sitemaps.exists():
        pytest.skip("No sitemaps dir")
    files = list(sitemaps.glob("*.sitemap"))
    assert len(files) >= 1


def test_metadata_json_valid():
    meta = CONF / "misc" / "metadata.json"
    if not meta.exists():
        pytest.skip("No metadata.json")
    data = json.loads(meta.read_text())
    assert "project" in data or "version" in data


def test_config_yml_structure():
    config = CONF / "misc" / "config.yml"
    if not config.exists():
        pytest.skip("No config.yml")
    text = config.read_text()
    assert "metadata" in text or "simulation" in text
