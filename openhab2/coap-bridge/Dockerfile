FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir aiocoap paho-mqtt

COPY coap_mqtt_bridge.py .
COPY device_model.py .

EXPOSE 5683/udp

CMD ["python", "coap_mqtt_bridge.py"]
