# Завдання Варіант 6: Universal Device Model

## Звіт про виконання

### 1. Abstract Device Model ✅

- **Protocol-agnostic device representation**: `universal_device_model/device_profiles.json` — JSON-модель пристроїв без прив'язки до протоколу
- **Capability-based model**: профілі switch, sensor, light з каналами (power, temperature, humidity, brightness)
- **Extensible architecture**: додавання нових профілів через JSON
- **Version management**: поле `version` у кожному профілі

### 2. Multiple Protocol Mappings ✅

**Мінімум 3 protocol bindings:**


| Протокол | Реалізація                            | Файли                                  |
| -------- | ------------------------------------- | -------------------------------------- |
| MQTT     | OpenHAB MQTT binding, Mosquitto       | `mqtt.things`, `udm_items.items`       |
| HTTP     | OpenHAB HTTP binding, Flask simulator | `udm_items.items`, `http_simulator.py` |
| CoAP     | Python aiocoap bridge → MQTT          | `coap_mqtt_bridge.py`                  |


**Bidirectional mapping**: MQTT command/state topics, HTTP GET/POST, CoAP PUT/POST → MQTT  
**Protocol-specific optimizations**: `mapping_config.yaml`  
**Fallback mechanisms**: `udm_fallback.rules` — MQTT → HTTP → CoAP

### 3. Dynamic Device Discovery ✅

- **Auto-discovery**: CoAP POST → MQTT `devices/coap/discovery/+`, Rules обробляють
- **Capability negotiation**: GET coap://host/devices повертає profiles
- **Device profiling**: `discovery.js` — detectProfile()
- **Plug-and-play**: автоматична реєстрація через discovery topics

### 4. OpenHAB Templates ✅

- **Reusable device templates**: `template_engine.js` — switch, sensor, light
- **Template instantiation**: instantiateDeviceTemplate(id, profile, protocol)
- **Parameter customization**: substituteParams() для {id} в topics
- **Template library structure**: `templates/README.md`, `template_engine.js`

### Технічні вимоги ✅

- OpenHAB multiple bindings: mqtt, http, exec (addons.cfg)
- Abstract model: device_profiles.json
- Template engine: Rules DSL + template_engine.js
- Discovery automation: udm_discovery.rules
- Mapping configurations: mapping_config.yaml
- Template library: templates/, template_engine.js

