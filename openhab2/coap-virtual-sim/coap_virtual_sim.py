#!/usr/bin/env python3
"""
CoAP Virtual Device Simulator - sends simulated data via CoAP to the bridge
CoAP -> Bridge -> MQTT -> OpenHAB
"""
import asyncio
import json
import os
import random
import logging
from aiocoap import Context, Message, PUT, POST

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("coap-virtual-sim")

COAP_HOST = os.getenv("COAP_HOST", "coap-bridge")
COAP_PORT = int(os.getenv("COAP_PORT", "5683"))
INTERVAL = float(os.getenv("SIM_INTERVAL", "15"))


async def send_discovery(context, device_id: str, profile: str):
    uri = f"coap://{COAP_HOST}:{COAP_PORT}/devices"
    payload = json.dumps({"id": device_id, "profile": profile}).encode()
    try:
        request = Message(code=POST, payload=payload, uri=uri)
        response = await context.request(request).response
        log.info("CoAP discovery sent: %s -> %s", device_id, response.code)
    except Exception as e:
        log.warning("CoAP discovery failed: %s", e)


async def send_sensor_data(context, temp: float, hum: float):
    uri = f"coap://{COAP_HOST}:{COAP_PORT}/devices"
    payload = json.dumps({"temperature": temp, "humidity": hum}).encode()
    try:
        request = Message(code=PUT, payload=payload, uri=uri)
        await context.request(request).response
        log.debug("CoAP sensor data: temp=%.1f hum=%.0f", temp, hum)
    except Exception as e:
        log.warning("CoAP PUT failed: %s", e)


async def main():
    await asyncio.sleep(10)  # Wait for coap-bridge to be ready
    temp, hum = 22.0, 50.0
    context = await Context.create_client_context()

    while True:
        try:
            await send_discovery(context, "sensor_coap", "sensor")
            await send_discovery(context, "switch_coap", "switch")
            await send_sensor_data(context, temp, hum)
            temp = max(18, min(28, temp + random.uniform(-0.5, 0.5)))
            hum = max(30, min(70, hum + random.uniform(-2, 2)))
        except Exception as e:
            log.error("CoAP sim error: %s", e)
        await asyncio.sleep(INTERVAL)


if __name__ == "__main__":
    asyncio.run(main())
