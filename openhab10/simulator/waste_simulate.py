#!/usr/bin/env python3
"""
Smart City Waste Management — симулятор віртуальних контейнерів (Варіант 1).
Симулює 10 контейнерів: ультразвуковий сенсор заповненості 0–100%, GPS.
Передача даних по MQTT (як LoRaWAN/MQTT у реальній системі).
"""
import os
import random
import time
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("waste-sim")

try:
    import paho.mqtt.client as mqtt
except ImportError:
    log.error("Install paho-mqtt: pip install paho-mqtt")
    raise

MQTT_BROKER = os.getenv("MQTT_BROKER", "mosquitto")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
SIM_INTERVAL = int(os.getenv("SIM_INTERVAL", "15"))

# 10 локацій у місті (широта, довгота) — симульовані GPS
LOCATIONS = [
    (50.4501, 30.5234),   # 01 Central Square
    (50.4404, 30.4895),   # 02 Railway Station
    (50.4547, 30.5038),   # 03 City Park
    (50.4477, 30.5024),   # 04 Market
    (50.4434, 30.5162),   # 05 University
    (50.4378, 30.5201),   # 06 Hospital
    (50.4345, 30.5102),   # 07 Stadium
    (50.4489, 30.5233),   # 08 Shopping Mall
    (50.4567, 30.4891),   # 09 Bus Depot
    (50.4389, 30.4987),   # 10 Residential Block
]

# Поточна заповненість кожного контейнера (0–100), початкове випадкове
state_fill = [random.randint(10, 80) for _ in range(10)]


def on_connect(client, userdata, flags, reason_code, properties=None):
    if reason_code == 0:
        log.info("Connected to MQTT broker %s:%s", MQTT_BROKER, MQTT_PORT)
    else:
        log.warning("Connect result: %s", reason_code)


def on_disconnect(client, userdata, reason_code, properties=None, reason_codes=None):
    log.warning("Disconnected: %s", reason_code)


def publish_cycle(client: mqtt.Client):
    global state_fill
    for i in range(10):
        cid = f"{i + 1:02d}"
        base = f"waste/container/{cid}"

        # Симуляція заповненості: повільне збільшення + випадковість (іноді "злив" = скидання)
        fill = state_fill[i]
        fill += random.gauss(1.5, 2.0)
        if random.random() < 0.02:
            fill = random.randint(0, 15)  # симуляція вивозу
        fill = max(0, min(100, round(fill, 1)))
        state_fill[i] = fill

        # Невеликий шум GPS (симуляція точності)
        lat, lon = LOCATIONS[i]
        lat += random.gauss(0, 0.0001)
        lon += random.gauss(0, 0.0001)

        client.publish(f"{base}/fill", str(int(fill)), qos=0, retain=False)
        client.publish(f"{base}/lat", f"{lat:.6f}", qos=0, retain=False)
        client.publish(f"{base}/lon", f"{lon:.6f}", qos=0, retain=False)

    avg = sum(state_fill) / 10
    critical = sum(1 for f in state_fill if f > 70)
    log.info(
        "Published 10 containers | avg=%.0f%% critical=%d",
        avg,
        critical,
    )


def main():
    log.info(
        "Waste simulator starting | broker=%s:%s interval=%ds",
        MQTT_BROKER,
        MQTT_PORT,
        SIM_INTERVAL,
    )
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="waste-sim")
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect

    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
    except Exception as e:
        log.error("MQTT connect failed: %s. Retrying in 5s...", e)
        time.sleep(5)
        return main()

    client.loop_start()
    time.sleep(2)

    while True:
        try:
            publish_cycle(client)
        except Exception as e:
            log.error("Publish failed: %s", e)
        time.sleep(SIM_INTERVAL)


if __name__ == "__main__":
    main()
