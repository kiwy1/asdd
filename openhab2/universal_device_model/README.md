# Universal Device Model (UDM)

## Variant 6: Abstract Device Model with Multi-Protocol Support

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Abstract Device Model                          │
│  (Protocol-agnostic, Capability-based, Extensible, Versioned)    │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
   ┌─────────┐          ┌─────────┐          ┌─────────┐
   │  MQTT   │          │  HTTP   │          │  CoAP   │
   │ Binding │          │ Binding │          │ Bridge  │
   └────┬────┘          └────┬────┘          └────┬────┘
        │                    │                    │
        └────────────────────┼────────────────────┘
                             │
                             ▼
                    ┌────────────────┐
                    │  OpenHAB Core  │
                    │  Items/Things  │
                    └────────────────┘
```

### Device Profiles (Capability-based)

| Profile   | Capabilities          | Channels                        | Version |
|----------|------------------------|----------------------------------|---------|
| switch   | on_off, state          | power, state                     | 1.0     |
| sensor   | measurement, temp, hum | temperature, humidity            | 1.0     |
| light    | on_off, dimmer, color  | power, brightness                | 1.0     |

### Protocol Mappings

- **MQTT**: `devices/{profile}_{id}/{channel}` 
- **HTTP**: `GET/POST /devices/{id}/{channel}`
- **CoAP**: `PUT coap://host/devices` → MQTT bridge

### Fallback Order

1. MQTT (primary)
2. HTTP (fallback)
3. CoAP (via bridge)
