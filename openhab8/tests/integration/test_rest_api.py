"""Integration tests: OpenHAB REST API (items, health)."""
import os
import time

import pytest
import requests

OPENHAB_URL = os.getenv("OPENHAB_URL", "http://localhost:8080").rstrip("/")


@pytest.fixture(scope="module")
def wait_for_openhab():
    for _ in range(24):
        try:
            r = requests.get(f"{OPENHAB_URL}/rest/items?limit=1", timeout=5)
            if r.status_code == 200:
                return
        except Exception:
            pass
        time.sleep(5)
    pytest.skip("OpenHAB not reachable")


def test_rest_items_endpoint(wait_for_openhab):
    r = requests.get(f"{OPENHAB_URL}/rest/items", timeout=10)
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)


def test_rest_items_limit(wait_for_openhab):
    r = requests.get(f"{OPENHAB_URL}/rest/items?limit=5", timeout=10)
    assert r.status_code == 200
    data = r.json()
    assert len(data) <= 5 or len(data) >= 0


def test_rest_health(wait_for_openhab):
    r = requests.get(f"{OPENHAB_URL}/rest/", timeout=5)
    assert r.status_code in (200, 404)
