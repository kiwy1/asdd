#!/usr/bin/env python3
"""
HTTP Device Simulator for Universal Device Model
Simulates IoT devices with HTTP REST API - virtual/simulated data with drift
"""
import os
import json
import random
import threading
import time
from flask import Flask, request, jsonify

app = Flask(__name__)

# Simulated device state (updated by background thread)
devices = {
    "sensor_living": {"temperature": 22.5, "humidity": 45, "profile": "sensor"},
    "switch_kitchen": {"power": "ON", "profile": "switch"},
    "light_bedroom": {"on": True, "brightness": 80, "profile": "light"},
}
_lock = threading.Lock()


def _simulate_drift():
    """Background thread: simulate sensor value drift"""
    while True:
        time.sleep(10)
        with _lock:
            d = devices["sensor_living"]
            d["temperature"] = max(18, min(28, d["temperature"] + random.uniform(-0.3, 0.3)))
            d["humidity"] = max(30, min(70, d["humidity"] + random.uniform(-1.5, 1.5)))


@app.route("/devices", methods=["GET"])
def list_devices():
    """Device discovery - list available devices"""
    return jsonify({
        "devices": [
            {"id": k, "profile": v.get("profile", "generic")}
            for k, v in devices.items()
        ],
        "protocol": "http",
        "version": "1.0",
    })


@app.route("/devices/<device_id>", methods=["GET"])
def get_device(device_id):
    """Get device state"""
    if device_id not in devices:
        return jsonify({"error": "Device not found"}), 404
    return jsonify(devices[device_id])


@app.route("/devices/<device_id>/<channel>/raw", methods=["GET"])
def device_channel_raw(device_id, channel):
    """Plain text value - no JSON, for OpenHAB HTTP binding without transformation"""
    if device_id not in devices:
        return "0", 404
    with _lock:
        dev = devices[device_id]
        val = dev.get(channel) if channel in dev else dev.get("power")
        if val is True:
            return "ON"
        if val is False:
            return "OFF"
        return str(val)


@app.route("/devices/<device_id>/<channel>", methods=["GET", "POST", "PUT"])
def device_channel(device_id, channel):
    """Get or set device channel (capability)"""
    if device_id not in devices:
        return jsonify({"error": "Device not found"}), 404

    with _lock:
        dev = devices[device_id]
        if request.method in ("POST", "PUT"):
            data = request.get_json(silent=True) or {}
            value = data.get("value", data.get(channel))
            if value is None and request.args.get("value"):
                value = request.args.get("value")
            if value is None and request.get_data():
                value = request.get_data(as_text=True).strip()  # OpenHAB sends plain text body
            if value is not None:
                if channel == "power" and str(value).upper() in ("ON", "OFF"):
                    dev["power"] = str(value).upper()
                elif channel == "on":
                    dev["on"] = str(value).lower() in ("true", "1", "on")
                elif channel in ("brightness", "temperature", "humidity"):
                    try:
                        dev[channel] = float(value)
                    except (TypeError, ValueError):
                        pass
                else:
                    dev[channel] = value
            return jsonify({"status": "ok", "value": dev.get(channel) if channel in dev else dev.get("power")})

        val = dev.get(channel) if channel in dev else dev.get("power")
        if val is True or val is False:
            val = 1 if val else 0
        return jsonify({"value": val})


@app.route("/devices/<device_id>/discovery", methods=["POST"])
def device_discovery(device_id):
    """Device registration for plug-and-play"""
    data = request.get_json() or {}
    profile = data.get("profile", "generic")
    if device_id not in devices:
        devices[device_id] = {"profile": profile}
    return jsonify({"status": "registered", "id": device_id})


@app.route("/health")
def health():
    return jsonify({"status": "ok", "protocol": "http"})


if __name__ == "__main__":
    threading.Thread(target=_simulate_drift, daemon=True).start()
    port = int(os.getenv("PORT", 9999))
    app.run(host="0.0.0.0", port=port, debug=False)
