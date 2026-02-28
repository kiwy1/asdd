#!/usr/bin/env python3
import os
import random
import time
import logging
import urllib.request
import urllib.error

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("virtual-sim")

OPENHAB_URL = os.getenv("OPENHAB_URL", "http://oh3-openhab:8080")
INTERVAL = int(os.getenv("PUSH_INTERVAL", "10"))

_state = {
    "temp_living": 22.0,
    "temp_bedroom": 21.0,
    "temp_kitchen": 23.0,
    "hum_living": 45.0,
    "hum_bedroom": 50.0,
    "light_bedroom": 80,
    "switch_kitchen": "ON",
    "power": 150.0,
    "co2": 450,
}


def _put_item(item_name: str, value: str) -> bool:
    try:
        url = f"{OPENHAB_URL}/rest/items/{item_name}/state"
        req = urllib.request.Request(url, data=value.encode(), method="PUT")
        req.add_header("Content-Type", "text/plain")
        with urllib.request.urlopen(req, timeout=5) as _:
            return True
    except Exception as e:
        log.debug("PUT %s failed: %s", item_name, e)
        return False


def _push_cycle():
    _state["temp_living"] = max(18, min(28, _state["temp_living"] + random.uniform(-0.3, 0.3)))
    _state["temp_bedroom"] = max(18, min(26, _state["temp_bedroom"] + random.uniform(-0.2, 0.2)))
    _state["temp_kitchen"] = max(19, min(30, _state["temp_kitchen"] + random.uniform(-0.4, 0.4)))
    _state["hum_living"] = max(30, min(70, _state["hum_living"] + random.uniform(-1, 1)))
    _state["hum_bedroom"] = max(35, min(65, _state["hum_bedroom"] + random.uniform(-1.5, 1.5)))
    if random.random() < 0.1:
        _state["light_bedroom"] = max(0, min(100, _state["light_bedroom"] + random.randint(-20, 20)))
    if random.random() < 0.05:
        _state["switch_kitchen"] = "OFF" if _state["switch_kitchen"] == "ON" else "ON"
    _state["power"] = max(50, min(500, _state["power"] + random.uniform(-10, 10)))
    _state["co2"] = max(350, min(1200, int(_state["co2"] + random.uniform(-30, 30))))

    items = [
        ("V_Temp_Living", f"{_state['temp_living']:.1f}"),
        ("V_Temp_Bedroom", f"{_state['temp_bedroom']:.1f}"),
        ("V_Temp_Kitchen", f"{_state['temp_kitchen']:.1f}"),
        ("V_Hum_Living", f"{int(_state['hum_living'])}"),
        ("V_Hum_Bedroom", f"{int(_state['hum_bedroom'])}"),
        ("V_Light_Bedroom", str(_state["light_bedroom"])),
        ("V_Switch_Kitchen", _state["switch_kitchen"]),
        ("V_Power_Consumption", f"{_state['power']:.1f}"),
        ("V_CO2_Level", str(_state["co2"])),
    ]
    ok = sum(1 for n, v in items if _put_item(n, v))
    log.info("Pushed %d/%d virtual items", ok, len(items))


def main():
    log.info("Virtual Sim starting, target=%s, interval=%ds", OPENHAB_URL, INTERVAL)
    time.sleep(25)
    while True:
        try:
            _push_cycle()
        except Exception as e:
            log.error("Push failed: %s", e)
        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
