#!/usr/bin/env python3
"""
MQTT Virtual Device Simulator for Universal Device Model
Simulates IoT devices publishing to MQTT - works entirely with virtual/simulated data
"""
import os
import json
import random
import time
import logging
from threading import Thread

import paho.mqtt.client as mqtt

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("mqtt-virtual-sim")

MQTT_BROKER = os.getenv("MQTT_BROKER", "mosquitto")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
INTERVAL = float(os.getenv("SIM_INTERVAL", "5"))

# Simulated device state
state = {
    "temperature": 22.0,
    "humidity": 50.0,
    "switch": "ON",
    "light_brightness": 75,
}


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        log.info("Connected to MQTT broker %s:%s", MQTT_BROKER, MQTT_PORT)
        client.subscribe("devices/coap_switch_power/set", qos=1)
    else:
        log.error("Connection failed: %s", rc)


def on_message(client, userdata, msg):
    """Handle commands from OpenHAB (bidirectional)"""
    topic = msg.topic
    payload = msg.payload.decode()
    if topic == "devices/coap_switch_power/set":
        state["switch"] = payload.upper() if payload.upper() in ("ON", "OFF") else state["switch"]
        client.publish("devices/coap_switch_power", state["switch"], qos=1, retain=True)
        log.info("Switch command received: %s", state["switch"])


def simulate_sensor():
    """Simulate temperature/humidity with small random drift"""
    while True:
        state["temperature"] = max(18, min(28, state["temperature"] + random.uniform(-0.5, 0.5)))
        state["humidity"] = max(30, min(70, state["humidity"] + random.uniform(-2, 2)))
        yield state["temperature"], state["humidity"]
        time.sleep(INTERVAL)


def run_simulator(client):
    sensor_gen = simulate_sensor()
    discovery_sent = False

    while True:
        try:
            # Publish sensor data
            temp, hum = next(sensor_gen)
            client.publish("devices/mqtt_sensor/temp", f"{temp:.1f}", qos=1, retain=True)
            client.publish("devices/mqtt_sensor/humidity", f"{int(hum)}", qos=1, retain=True)
            log.debug("Published sensor: temp=%.1f, hum=%.0f", temp, hum)

            # Publish switch state (reflects commands or keeps current)
            client.publish("devices/coap_switch_power", state["switch"], qos=1, retain=True)

            # Discovery (once at start + periodically)
            if not discovery_sent or random.random() < 0.1:
                for dev_id, profile in [
                    ("sensor_living", "sensor"),
                    ("switch_kitchen", "switch"),
                    ("light_bedroom", "light"),
                ]:
                    payload = json.dumps({
                        "id": dev_id,
                        "profile": profile,
                        "capabilities": ["temperature", "humidity"] if profile == "sensor"
                        else ["on_off"] if profile == "switch" else ["on_off", "dimmer"],
                    })
                    client.publish(f"devices/coap/discovery/{dev_id}", payload, qos=1)
                discovery_sent = True
                log.info("Published discovery for virtual devices")

            time.sleep(INTERVAL)
        except Exception as e:
            log.error("Simulator error: %s", e)
            time.sleep(INTERVAL)


def main():
    client = mqtt.Client(client_id="udm-virtual-sim")
    client.on_connect = on_connect
    client.on_message = on_message

    for attempt in range(30):
        try:
            client.connect(MQTT_BROKER, MQTT_PORT, 60)
            break
        except Exception as e:
            log.warning("Connect attempt %d failed: %s", attempt + 1, e)
            time.sleep(2)
    else:
        log.error("Could not connect to MQTT broker")
        return 1

    client.loop_start()

    # Wait for connection
    time.sleep(2)
    run_simulator(client)


if __name__ == "__main__":
    main()
