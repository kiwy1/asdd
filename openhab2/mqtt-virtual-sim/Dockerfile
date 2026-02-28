FROM python:3.11-slim

WORKDIR /app
RUN pip install --no-cache-dir paho-mqtt

COPY mqtt_virtual_sim.py .

CMD ["python", "mqtt_virtual_sim.py"]
