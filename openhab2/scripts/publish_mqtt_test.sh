#!/bin/sh
# Test script - publish sample data to MQTT for Universal Device Model
# Usage: ./publish_mqtt_test.sh [host] [port]
# Example: ./publish_mqtt_test.sh localhost 1884

HOST=${1:-localhost}
PORT=${2:-1884}

echo "Publishing test data to MQTT broker at $HOST:$PORT"

# Sensor data
mosquitto_pub -h "$HOST" -p "$PORT" -t "devices/mqtt_sensor/temp" -m "23.5"
mosquitto_pub -h "$HOST" -p "$PORT" -t "devices/mqtt_sensor/humidity" -m "52"

# Switch state
mosquitto_pub -h "$HOST" -p "$PORT" -t "devices/coap_switch_power" -m "ON"

# CoAP bridge discovery (simulates device discovery)
mosquitto_pub -h "$HOST" -p "$PORT" -t "devices/coap/discovery/sensor1" -m '{"id":"sensor1","profile":"sensor","capabilities":["temperature","humidity"]}'

echo "Done. Check OpenHAB UI at http://localhost:8080"
