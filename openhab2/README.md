# Universal Device Model - OpenHAB IoT Platform

**Варіант 6**: Abstract Device Model з mappings до різних протоколів та dynamic device discovery.

## Швидкий старт

```bash
# Якщо є конфлікт імен з існуючими контейнерами:
docker compose down 2>/dev/null; docker rm -f udm-openhab udm-mosquitto coap-mqtt-bridge http-device-sim 2>/dev/null

# Запуск всіх сервісів
docker compose up -d --build

# Очікуйте ~2 хвилини для ініціалізації OpenHAB
# Відкрийте http://localhost:8081
# Всі пристрої віртуальні — дані публікуються автоматично
```

## Архітектура

| Компонент | Порт | Призначення |
|-----------|------|-------------|
| OpenHAB | 8081, 8444 | Головна платформа, UI (localhost:8081) |
| Mosquitto (MQTT) | 1884 (host→1883) | MQTT брокер |
| CoAP Bridge | 5683/udp | CoAP ↔ MQTT мост |
| HTTP Device Sim | 9999 | Симулятор HTTP пристроїв |
| **mqtt-virtual-sim** | - | Публікує sensor/switch/discovery у MQTT |
| **coap-virtual-sim** | - | Відправляє discovery/data через CoAP |

## Функціональні вимоги

### 1. Abstract Device Model
- **Протокол-агностичне** представлення: `universal_device_model/device_profiles.json`
- **Capability-based**: switch, sensor, light з каналами
- **Версіонування**: кожен профіль має version
- **Розширювана архітектура**: додавання нових профілів у JSON

### 2. Multiple Protocol Mappings (3+ протоколи)
- **MQTT**: native binding, topics `devices/{profile}_{id}/{channel}`
- **HTTP**: binding для REST API, `GET/POST /devices/{id}/{channel}`
- **CoAP**: bridge публікує в MQTT, `PUT coap://host/devices`

**Конфігурація маппінгів**: `universal_device_model/mapping_config.yaml`

### 3. Dynamic Device Discovery
- CoAP discovery → MQTT topic `devices/coap/discovery/+`
- Rules: `udm_discovery.rules` - обробка discovery events
- Scripts: `discovery.js`, `template_engine.js` - профілювання, plug-and-play

### 4. OpenHAB Templates
- Бібліотека: `openhab_conf/scripts/template_engine.js`
- Профілі: switch, sensor, light
- Parameter customization: `{id}` substitution для device-specific topics

## Структура проекту

```
├── docker-compose.yml
├── openhab_conf/
│   ├── things/        # MQTT bridge, things
│   ├── items/         # UDM items, template items
│   ├── rules/         # discovery, template, fallback
│   ├── scripts/       # discovery.js, template_engine.js
│   └── sitemaps/      # udm.sitemap
├── universal_device_model/
│   ├── device_profiles.json
│   ├── mapping_config.yaml
│   └── README.md
├── coap-bridge/       # CoAP-MQTT bridge
├── http-device-sim/   # HTTP device simulator
├── mosquitto/         # MQTT config
├── templates/         # Template library docs
└── scripts/           # Test scripts
```

## Віртуальні пристрої (симуляція)

При запуску `docker compose up` автоматично стартують симулятори:
- **mqtt-virtual-sim** — температури/вологість/вимикач у MQTT кожні 5 с
- **coap-virtual-sim** — discovery та дані через CoAP кожні 20 с
- **http-device-sim** — значення змінюються з drift кожні 10 с

Жодних реальних пристроїв не потрібно — все працює у симуляції.

## Тестування

### MQTT (опційно, якщо симулятор не запущений)
```bash
# Встановіть mosquitto_pub (brew install mosquitto)
./scripts/publish_mqtt_test.sh localhost 1884
```

### CoAP
```bash
# Встановіть coap-client (brew install libcoap)
coap-client -m put coap://localhost:5683/devices -e '{"id":"test","profile":"sensor"}'
```

### HTTP
```bash
curl http://localhost:9999/devices
curl http://localhost:9999/devices/sensor_living/temperature
```

## Fallback механізм

При недоступності MQTT сенсора - використовується HTTP fallback (правило `udm_fallback.rules`).
Порядок: MQTT → HTTP → CoAP

## Якщо Items показують "-"

1. **Перезапустіть контейнери** після змін:
   ```bash
   docker compose down && docker compose up -d --build
   ```

2. **HTTP items** (Temp, Humidity, Switch) — використовують `/raw` endpoints. Якщо "-":
   - Перевірте, що http-device-sim працює: `curl http://localhost:9999/devices/sensor_living/temperature/raw`
   - Має повертати число, напр. `22.5`

3. **openhab-pusher** — пушить дані прямо в Items через REST API (не залежить від біндінгів).
   Якщо sitemap все ще "-", перевірте: `docker logs openhab-pusher`
   Якщо OpenHAB має пароль: `OPENHAB_USER` та `OPENHAB_PASSWORD` в docker-compose для openhab-pusher
