# OpenHAB 10 — Smart City Waste Management System (Варіант 1)

IoT-система для симуляції оптимізації збору сміття: **усі Items віртуальні з симуляцією** через MQTT. Розумні контейнери (заповненість 0–100%, GPS) передають дані на OpenHAB.

## Вимоги завдання (базовий рівень)

| Вимога | Реалізація |
|--------|------------|
| **IoT з симульованими пристроями** | 10 віртуальних контейнерів, симулятор публікує fill/lat/lon по MQTT |
| **MQTT** | Eclipse Mosquitto; OpenHAB MQTT binding підписаний на `waste/container/XX/*` |
| **Мінімум 10 контейнерів у різних локаціях** | 10 контейнерів з різними GPS (Київ), окремі MQTT things/items |
| **Заповненість 0–100%** | Number items, симуляція поступового заповнення + вивозу |
| **Docker / docker-compose** | `docker-compose.yml`: OpenHAB, Mosquitto, waste-sim |
| **Віртуальні Items з симуляцією** | Items отримують дані тільки з MQTT від симулятора (немає фізичних сенсорів) |

## Запуск

```bash
cd openhab10
docker compose up -d
```

- **OpenHAB UI**: http://localhost:8080 (при першому вході створиться обліковий запис)
- **MQTT**: порт 1883 (внутрішня мережа: `mosquitto:1883` для OpenHAB і симулятора)

Після старту почекайте 1–2 хвилини, поки OpenHAB завантажить біндинги та Things. Симулятор починає публікувати дані одразу після здорового MQTT.

## Змінні середовища (.env)

| Змінна | Опис | За замовчуванням |
|--------|------|-------------------|
| `TZ` | Часовий пояс | Europe/Kyiv |
| `OPENHAB_HTTP_PORT` | Порт HTTP UI | 8080 |
| `OPENHAB_HTTPS_PORT` | Порт HTTPS | 8443 |
| `MQTT_PORT` | Порт MQTT | 1883 |
| `SIM_INTERVAL` | Інтервал оновлення симулятора (сек) | 15 |

## Структура проєкту

```
openhab10/
├── docker-compose.yml       # OpenHAB, Mosquitto, waste-sim
├── .env
├── Dockerfile.sim           # Образ симулятора (Python + paho-mqtt)
├── mosquitto/
│   └── config/
│       └── mosquitto.conf
├── simulator/
│   └── waste_simulate.py    # Публікація fill/lat/lon для 10 контейнерів по MQTT
└── openhab/
    └── conf/
        ├── services/
        │   └── addons.cfg   # mqtt, rrd4j, mapdb, basic, paper
        ├── things/
        │   └── mqtt.things  # Broker + 10 MQTT Things (контейнери)
        ├── items/
        │   └── waste_containers.items
        ├── rules/
        │   └── waste.rules  # Середня заповненість, лічильник критичних, лог >70%
        ├── persistence/
        │   ├── mapdb.persist
        │   └── rrd4j.persist
        └── sitemaps/
            └── default.sitemap  # Dashboard + контейнери
```

## MQTT-топи (симулятор → OpenHAB)

- `waste/container/01/fill` … `waste/container/10/fill` — заповненість 0–100
- `waste/container/01/lat`, `waste/container/01/lon` … аналогічно для 10 контейнерів

Усі Items в OpenHAB віртуальні: вони прив’язані до MQTT channels і оновлюються лише даними з цих топів (симуляція).

## Далі для повного проєкту (Backend, Frontend, безпека, ML)

Цей репозиторій забезпечує **IoT-шар з OpenHAB і симуляцією**. Для здачі повного проєкту варто додати:

- **Backend**: REST API (наприклад Node.js/Python), який читає дані з OpenHAB REST або з БД; алгоритм оптимізації маршруту (TSP); WebSocket для real-time.
- **Frontend**: карта з контейнерами, кольорова індикація (<30% / 30–70% / >70%), візуалізація маршруту, dashboard.
- **Безпека**: TLS, JWT, RBAC, rate limiting.
- **Аналітика/ML**: прогноз заповненості, детекція аномалій.
- **Документація**: ARCHITECTURE.md, ETHICS.md (PIA, GDPR, open data).

OpenHAB тут виступає як **edge/gateway**: приймає MQTT від симульованих контейнерів, зберігає стан у Items, надає REST API для зовнішнього backend.
