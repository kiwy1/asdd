#!/usr/bin/env python3
"""
Virtual Health Monitor Simulator — PIA Варіант 1.
Симулює носимий пристрій: серцевий ритм, активність, сон, геолокація.
Оновлює віртуальні Items через OpenHAB REST API.
"""
import os
import random
import time
import logging
import urllib.request
import urllib.error

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger("health-sim")

OPENHAB_URL = os.getenv("OPENHAB_URL", "http://openhab:8080").rstrip("/")
INTERVAL = int(os.getenv("PUSH_INTERVAL", "10"))

# Київ (базова точка для "блукання" геолокації)
BASE_LAT, BASE_LON = 50.4501, 30.5234

_state = {
    "heart_rate": 72,
    "activity_level": "moderate",  # sedentary, light, moderate, high
    "activity_score": 55.0,
    "sleep_duration": 7.2,
    "sleep_phase": "light",  # awake, light, deep, REM
    "sleep_quality": 78.0,
    "lat": BASE_LAT,
    "lon": BASE_LON,
    "alt": 120.0,
}

ACTIVITY_LEVELS = ["sedentary", "light", "moderate", "high"]
SLEEP_PHASES = ["awake", "light", "deep", "REM"]


def _put_item(item_name: str, value: str) -> bool:
    try:
        url = f"{OPENHAB_URL}/rest/items/{item_name}/state"
        req = urllib.request.Request(url, data=value.encode(), method="PUT")
        req.add_header("Content-Type", "text/plain")
        with urllib.request.urlopen(req, timeout=5) as _:
            return True
    except Exception as e:
        log.warning("PUT %s failed: %s", item_name, e)
        return False


def _push_cycle():
    # Серцевий ритм: 55–95 bpm, повільна зміна
    _state["heart_rate"] = int(
        max(55, min(95, _state["heart_rate"] + random.gauss(0, 2)))
    )
    # Активність: іноді зміна рівня та score
    if random.random() < 0.15:
        _state["activity_level"] = random.choice(ACTIVITY_LEVELS)
    _state["activity_score"] = max(
        0, min(100, _state["activity_score"] + random.gauss(0, 3))
    )
    # Сон: тривалість 5–9 год, фаза, якість
    _state["sleep_duration"] = max(
        5.0, min(9.0, _state["sleep_duration"] + random.gauss(0, 0.1))
    )
    if random.random() < 0.2:
        _state["sleep_phase"] = random.choice(SLEEP_PHASES)
    _state["sleep_quality"] = max(
        40, min(98, _state["sleep_quality"] + random.gauss(0, 2))
    )
    # Геолокація: невелике зміщення навколо бази (симуляція руху)
    step = 0.0002
    _state["lat"] = BASE_LAT + (random.random() - 0.5) * step * 10
    _state["lon"] = BASE_LON + (random.random() - 0.5) * step * 10
    _state["alt"] = max(80, min(200, _state["alt"] + random.gauss(0, 2)))

    # OpenHAB Location: "latitude,longitude,altitude"
    location_str = f"{_state['lat']:.4f},{_state['lon']:.4f},{_state['alt']:.0f}"

    items = [
        ("V_HeartRate", str(_state["heart_rate"])),
        ("V_ActivityLevel", _state["activity_level"]),
        ("V_ActivityScore", f"{_state['activity_score']:.0f}"),
        ("V_SleepDuration", f"{_state['sleep_duration']:.1f}"),
        ("V_SleepPhase", _state["sleep_phase"]),
        ("V_SleepQuality", f"{_state['sleep_quality']:.0f}"),
        ("V_Geolocation", location_str),
        ("V_LocationLat", f"{_state['lat']:.4f}"),
        ("V_LocationLon", f"{_state['lon']:.4f}"),
        ("V_LocationAlt", f"{_state['alt']:.0f}"),
    ]
    ok = sum(1 for n, v in items if _put_item(n, v))
    log.info(
        "Pushed %d/%d health items | HR=%d %s sleep=%.1fh %s",
        ok,
        len(items),
        _state["heart_rate"],
        _state["activity_level"],
        _state["sleep_duration"],
        _state["sleep_phase"],
    )


def main():
    log.info(
        "Health Monitor Sim starting, target=%s, interval=%ds",
        OPENHAB_URL,
        INTERVAL,
    )
    time.sleep(25)
    while True:
        try:
            _push_cycle()
        except Exception as e:
            log.error("Push failed: %s", e)
        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
