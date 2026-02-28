#!/usr/bin/env python3
import os
import random
import time
from datetime import datetime, timezone
import logging
import urllib.request

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("smart-grid-sim")

OPENHAB_URL = os.getenv("OPENHAB_URL", "http://oh4-smartgrid:8080")
INTERVAL = float(os.getenv("PUSH_INTERVAL", "2"))
INFLUXDB_URL = os.getenv("INFLUXDB_URL", "http://influxdb:8086")
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN", "smartgrid-token-change-me")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG", "openhab")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET", "smartgrid")

_influx = None


def _get_influx():
    global _influx
    if _influx is None and INFLUXDB_URL:
        try:
            from influxdb_client import InfluxDBClient, Point
            _influx = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
        except Exception as e:
            log.warning("InfluxDB client init failed: %s", e)
    return _influx

NOMINAL_FREQ = 50.0
NOMINAL_VOLTAGE = 230.0
NODES = 6

_state = {
    "node_power": [80 + i * 15 + random.uniform(-5, 5) for i in range(NODES)],
    "node_voltage": [NOMINAL_VOLTAGE] * NODES,
    "node_frequency": [NOMINAL_FREQ] * NODES,
    "flow_ab": 25.0, "flow_bc": 18.0, "flow_cd": 12.0, "flow_de": 8.0,
    "thd": 2.5,
    "scenario": "normal",
    "scenario_timer": 0,
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


def _evolve_state():
    s = _state

    if s["scenario_timer"] > 0:
        s["scenario_timer"] -= 1
        if s["scenario_timer"] <= 0:
            s["scenario"] = "normal"
    else:
        if random.random() < 0.02:
            scenarios = ["sag", "swell", "freq_dev", "islanding", "overload"]
            s["scenario"] = random.choice(scenarios)
            s["scenario_timer"] = random.randint(5, 20)

    if s["scenario"] == "sag":
        for i in range(NODES):
            s["node_voltage"][i] = NOMINAL_VOLTAGE * (0.82 + random.uniform(-0.02, 0.02))
        s["thd"] = min(8, s["thd"] + 0.2)
    elif s["scenario"] == "swell":
        for i in range(NODES):
            s["node_voltage"][i] = NOMINAL_VOLTAGE * (1.12 + random.uniform(-0.02, 0.02))
        s["thd"] = min(8, s["thd"] + 0.15)
    elif s["scenario"] == "freq_dev":
        dev = random.choice([-0.5, 0.5]) + random.uniform(-0.1, 0.1)
        for i in range(NODES):
            s["node_frequency"][i] = NOMINAL_FREQ + dev
    elif s["scenario"] == "islanding":
        for i in range(NODES):
            s["node_frequency"][i] = NOMINAL_FREQ + random.uniform(-0.8, 0.8)
            s["node_voltage"][i] = NOMINAL_VOLTAGE * (0.9 + random.uniform(-0.1, 0.1))
        s["thd"] = min(12, s["thd"] + 0.5)
    elif s["scenario"] == "overload":
        for i in range(NODES):
            s["node_power"][i] = min(500, s["node_power"][i] * (1.2 + random.uniform(0, 0.15)))
    else:
        for i in range(NODES):
            s["node_power"][i] = max(10, min(400, s["node_power"][i] + random.uniform(-3, 3)))
            s["node_voltage"][i] = NOMINAL_VOLTAGE + random.uniform(-5, 5)
            s["node_frequency"][i] = NOMINAL_FREQ + random.uniform(-0.05, 0.05)
        s["thd"] = max(1.5, min(5, s["thd"] + random.uniform(-0.1, 0.1)))

    s["flow_ab"] = max(0, s["flow_ab"] + random.uniform(-2, 2))
    s["flow_bc"] = max(0, s["flow_bc"] + random.uniform(-1.5, 1.5))
    s["flow_cd"] = max(0, s["flow_cd"] + random.uniform(-1, 1))
    s["flow_de"] = max(0, s["flow_de"] + random.uniform(-0.5, 0.5))


def _push_cycle():
    _evolve_state()
    s = _state

    items = []
    for i in range(NODES):
        n = i + 1
        items.append((f"V_Node{n}_Power", f"{s['node_power'][i]:.1f}"))
        items.append((f"V_Node{n}_Voltage", f"{s['node_voltage'][i]:.1f}"))
        items.append((f"V_Node{n}_Frequency", f"{s['node_frequency'][i]:.2f}"))

    total_power = sum(s["node_power"])
    avg_voltage = sum(s["node_voltage"]) / NODES
    avg_freq = sum(s["node_frequency"]) / NODES

    items.extend([
        ("V_Grid_TotalPower", f"{total_power:.1f}"),
        ("V_Grid_AvgVoltage", f"{avg_voltage:.1f}"),
        ("V_Grid_AvgFrequency", f"{avg_freq:.2f}"),
        ("V_Flow_A_to_B", f"{s['flow_ab']:.1f}"),
        ("V_Flow_B_to_C", f"{s['flow_bc']:.1f}"),
        ("V_Flow_C_to_D", f"{s['flow_cd']:.1f}"),
        ("V_Flow_D_to_E", f"{s['flow_de']:.1f}"),
        ("V_Flow_ZoneBalance", f"{(s['flow_ab'] - s['flow_de']):.1f}"),
        ("V_THD", f"{s['thd']:.2f}"),
    ])

    ok = sum(1 for n, v in items if _put_item(n, v))
    log.info("Pushed %d/%d items (scenario=%s)", ok, len(items), s["scenario"])

    client = _get_influx()
    if client:
        try:
            from influxdb_client import Point
            write_api = client.write_api()
            ts = datetime.now(timezone.utc)
            for name, val in items:
                try:
                    v = float(val)
                    p = Point(name).field("value", v).time(ts)
                    write_api.write(bucket=INFLUXDB_BUCKET, record=p)
                except ValueError:
                    pass
        except Exception as e:
            log.debug("InfluxDB write failed: %s", e)


def main():
    log.info("Smart Grid Sim starting, target=%s, interval=%.1fs", OPENHAB_URL, INTERVAL)
    time.sleep(30)
    while True:
        try:
            _push_cycle()
        except Exception as e:
            log.error("Push failed: %s", e)
        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
