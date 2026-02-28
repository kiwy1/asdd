#!/usr/bin/env python3
"""
CoAP-MQTT Bridge for Universal Device Model
Bidirectional mapping: CoAP <-> MQTT
"""
import asyncio
import json
import os
import logging
import aiocoap
from aiocoap import resource
from aiocoap.numbers.contentformat import ContentFormat
import paho.mqtt.client as mqtt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("coap-mqtt-bridge")

MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPIC_PREFIX = "devices/coap"

# Global MQTT client (runs in background thread)
mqtt_client = None

def init_mqtt():
    global mqtt_client
    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = lambda c, u, f, r: c.subscribe(f"{MQTT_TOPIC_PREFIX}/#")
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    mqtt_client.loop_start()
    logger.info("MQTT client connected")

class DeviceResource(resource.Resource):
    """CoAP resource for device data - maps to MQTT"""

    async def render_put(self, request):
        """Handle CoAP PUT - publish to MQTT"""
        try:
            payload = request.payload.decode() if request.payload else "{}"
            path = "/".join(request.opt.uri_path) if request.opt.uri_path else "data"
            topic = path.replace("/", "_") or "unknown"
            mqtt_topic = f"{MQTT_TOPIC_PREFIX}/{topic}"
            mqtt_client.publish(mqtt_topic, payload, qos=1)
            logger.info(f"CoAP->MQTT: {mqtt_topic} = {payload}")
            return aiocoap.Message(code=aiocoap.CHANGED, payload=b"OK")
        except Exception as e:
            logger.error(f"CoAP PUT error: {e}")
            return aiocoap.Message(code=aiocoap.BAD_REQUEST, payload=str(e).encode())

    async def render_post(self, request):
        """Handle CoAP POST - device registration/discovery"""
        try:
            payload = request.payload.decode() if request.payload else "{}"
            data = json.loads(payload) if payload else {}
            device_id = data.get("id", "unknown")
            mqtt_topic = f"{MQTT_TOPIC_PREFIX}/discovery/{device_id}"
            mqtt_client.publish(mqtt_topic, json.dumps(data), qos=1)
            logger.info(f"Device discovery: {device_id}")
            return aiocoap.Message(code=aiocoap.CREATED, payload=b"Registered")
        except Exception as e:
            logger.error(f"CoAP POST error: {e}")
            return aiocoap.Message(code=aiocoap.BAD_REQUEST, payload=str(e).encode())

    async def render_get(self, request):
        """Handle CoAP GET - capability negotiation"""
        capabilities = {
            "protocol": "coap",
            "version": "1.0",
            "profiles": ["switch", "sensor", "light"],
            "mqtt_bridge": True,
        }
        return aiocoap.Message(
            code=aiocoap.CONTENT,
            payload=json.dumps(capabilities).encode(),
            content_format=ContentFormat.JSON,
        )


async def main():
    init_mqtt()
    root = resource.Site()
    root.add_resource(["devices"], DeviceResource())
    root.add_resource([".well-known", "core"], resource.WKCResource(root.get_resources_as_linkheader))

    await aiocoap.Context.create_server_context(root, bind=("0.0.0.0", 5683))
    logger.info("CoAP-MQTT Bridge running on UDP 5683")

    await asyncio.get_running_loop().create_future()


if __name__ == "__main__":
    asyncio.run(main())
