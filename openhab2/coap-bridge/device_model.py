# Universal Device Model - Protocol mappings
# Abstract capability-based device representation

DEVICE_PROFILES = {
    "switch": {
        "capabilities": ["on_off", "state"],
        "channels": {
            "power": {"type": "Switch", "mqtt": "state", "http": "power", "coap": "0/0"},
            "state": {"type": "String", "mqtt": "state", "http": "status", "coap": "0/1"},
        },
        "version": "1.0",
    },
    "sensor": {
        "capabilities": ["measurement", "temperature", "humidity"],
        "channels": {
            "temperature": {"type": "Number", "mqtt": "temp", "http": "temperature", "coap": "3303/0"},
            "humidity": {"type": "Number", "mqtt": "humidity", "http": "humidity", "coap": "3304/0"},
        },
        "version": "1.0",
    },
    "light": {
        "capabilities": ["on_off", "dimmer", "color"],
        "channels": {
            "power": {"type": "Switch", "mqtt": "state", "http": "on", "coap": "0/0"},
            "brightness": {"type": "Dimmer", "mqtt": "brightness", "http": "brightness", "coap": "0/1"},
        },
        "version": "1.0",
    },
}

# Fallback: when protocol fails, try next
PROTOCOL_FALLBACK = ["mqtt", "http", "coap"]
