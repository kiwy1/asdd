#!/usr/bin/env python3
"""
OpenHAB REST API Pusher - pushes virtual device data directly to Items
Bypasses MQTT/HTTP bindings - ensures sitemap always shows values
"""
import os
import json
import random
import time
import logging
import base64
import urllib.request
import urllib.error

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("openhab-pusher")

OPENHAB_URL = os.getenv("OPENHAB_URL", "http://udm-openhab:8080")
OH_USER = os.getenv("OPENHAB_USER", "")
OH_PASS = os.getenv("OPENHAB_PASSWORD", "")


def _oh_headers():
    h = {}
    if OH_USER and OH_PASS:
        cred = base64.b64encode(f"{OH_USER}:{OH_PASS}".encode()).decode()
        h["Authorization"] = f"Basic {cred}"
    return h


HTTP_SIM_URL = os.getenv("HTTP_SIM_URL", "http://http-device-sim:9999")
INTERVAL = int(os.getenv("PUSH_INTERVAL", "5"))

# Simulated MQTT-style state
_state = {
    "temperature": 22.0,
    "humidity": 50.0,
    "switch": "ON",
    "discovery": '{"id":"sensor1","profile":"sensor"}',
    "coap_data": '{"temperature":22,"humidity":50}',
}


def _put_item(item_name: str, value: str) -> bool:
    try:
        url = f"{OPENHAB_URL}/rest/items/{item_name}/state"
        req = urllib.request.Request(url, data=value.encode(), method="PUT")
        req.add_header("Content-Type", "text/plain")
        for k, v in _oh_headers().items():
            req.add_header(k, v)
        with urllib.request.urlopen(req, timeout=5) as _:
            return True
    except Exception as e:
        log.debug("PUT %s failed: %s", item_name, e)
        return False


def _get_http(url: str) -> str:
    try:
        with urllib.request.urlopen(url, timeout=3) as r:
            return r.read().decode().strip()
    except Exception as e:
        log.debug("GET %s failed: %s", url, e)
        return ""


def _post_http(url: str, data: str) -> bool:
    try:
        req = urllib.request.Request(url, data=data.encode(), method="POST")
        req.add_header("Content-Type", "text/plain")
        with urllib.request.urlopen(req, timeout=3) as _:
            return True
    except Exception as e:
        log.debug("POST %s failed: %s", url, e)
        return False


def _get_oh_item(name: str) -> str:
    try:
        url = f"{OPENHAB_URL}/rest/items/{name}/state"
        req = urllib.request.Request(url)
        for k, v in _oh_headers().items():
            req.add_header(k, v)
        with urllib.request.urlopen(req, timeout=3) as r:
            return r.read().decode().strip()
    except Exception:
        return ""


def _push_cycle():
    # HTTP simulator data
    temp = _get_http(f"{HTTP_SIM_URL}/devices/sensor_living/temperature/raw")
    hum = _get_http(f"{HTTP_SIM_URL}/devices/sensor_living/humidity/raw")
    switch_sim = _get_http(f"{HTTP_SIM_URL}/devices/switch_kitchen/power/raw")
    if not temp:
        temp = str(_state["temperature"])
    if not hum:
        hum = str(_state["humidity"])
    if not switch_sim:
        switch_sim = _state["switch"]

    # If user toggled switch in UI, sync to HTTP simulator
    oh_switch = _get_oh_item("UDM_HTTP_Switch")
    if oh_switch and oh_switch.upper() in ("ON", "OFF") and oh_switch.upper() != switch_sim.upper():
        _post_http(f"{HTTP_SIM_URL}/devices/switch_kitchen/power", oh_switch.upper())
        switch_sim = oh_switch.upper()
    switch = switch_sim

    # Update MQTT-style state (drift)
    _state["temperature"] = max(18, min(28, float(temp) + random.uniform(-0.2, 0.2)))
    _state["humidity"] = max(30, min(70, float(hum) + random.uniform(-1, 1)))
    _state["switch"] = switch

    items = [
        ("UDM_HTTP_Temperature", temp),
        ("UDM_HTTP_Humidity", hum),
        ("UDM_HTTP_Switch", switch),
        ("UDM_Sensor_Temperature", f"{_state['temperature']:.1f}"),
        ("UDM_Sensor_Humidity", f"{int(_state['humidity'])}"),
        ("UDM_Switch_CoAP", _state["switch"]),
        ("UDM_Discovery_CoAP", _state["discovery"]),
        ("UDM_CoAP_Data", _state["coap_data"]),
    ]
    _state["coap_data"] = json.dumps({"temperature": _state["temperature"], "humidity": _state["humidity"]})

    ok = 0
    for name, val in items:
        if _put_item(name, val):
            ok += 1
    log.info("Pushed %d/%d items to OpenHAB", ok, len(items))


def main():
    log.info("OpenHAB Pusher starting, target=%s, interval=%ds", OPENHAB_URL, INTERVAL)
    time.sleep(15)  # Wait for OpenHAB to be ready

    while True:
        try:
            _push_cycle()
        except Exception as e:
            log.error("Push cycle failed: %s", e)
        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
