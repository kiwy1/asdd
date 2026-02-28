# OpenHAB 3 - InfluxDB Integration Stack

**Варіант 1: OpenHAB → InfluxDB → Grafana**

Docker Compose з OpenHAB, InfluxDB 2.x та Grafana. Всі Items віртуальні (оновлюються `virtual-sim`).

## Запуск

```bash
cd openhab3
cp .env.example .env   # опціонально змініть паролі
docker compose up -d
```

## Доступ

| Сервіс   | URL                         |
|----------|-----------------------------|
| OpenHAB  | http://localhost:8082       |
| InfluxDB | http://localhost:8086       |
| Grafana  | http://localhost:3000       |

**Grafana:** admin / admin (з .env)

## Компоненти

### 1. OpenHAB → InfluxDB Persistence
- **Items:** 10+ віртуальних (температура, вологість, світло, switch, power, CO2)
- **Measurement/tags:** через metadata `influxdb="temperature" [room="living", floor="ground"]`
- **Batch writes:** стратегія everyChange + everyMinute
- **Retention:** 52 тижні (основний bucket)

### 2. Grafana Dashboard
- **Charts:** Line (timeseries), Gauge, Stat
- **Time-range selector:** вбудовано
- **Variables:** `room` (All / living / bedroom / kitchen)
- **Panel linking:** посилання на InfluxDB UI
- **Refresh:** 30s

### 3. Continuous Queries (InfluxDB Tasks)
- **Hourly:** avg агрегація → `openhab_hourly` (90d retention)
- **Daily:** rollup з hourly → `openhab_daily` (365d)
- **Weekly:** summary з daily → `openhab_weekly` (без обмежень)

### 4. Alerting
- Contact points: webhook, email (симуляція)
- Політики в `grafana/provisioning/alerting/`
- Alert rules можна додати в UI (Threshold / Anomaly)

### 5. Derived Metrics (OpenHAB Rules)
- `V_Temp_Avg` – середня температура
- `V_Hum_Avg` – середня вологість  
- `V_Comfort_Index` – індекс комфорту (0–1)

## Перший запуск

1. **userdata** використовує named volume (не bind mount), щоб OpenHAB міг коректно ініціалізувати etc/, cache та інші каталоги.
2. **InfluxDB Persistence addon:** OpenHAB UI (http://localhost:8082) → Settings → Add-ons → Persistence → InfluxDB → Install.
2. **Token:** Переконайтесь, що `INFLUXDB_TOKEN` в .env збігається з `services/influxdb.cfg` (token=).
3. **Дані:** Через ~1–2 хв після старту virtual-sim почне писати дані. Grafana покаже графіки після накопичення точок.

## Структура

```
openhab3/
├── docker-compose.yml
├── openhab_conf/
│   ├── items/          # virtual_items.items, derived_items.items
│   ├── persistence/    # influxdb.persist
│   ├── rules/          # derived_metrics.rules
│   └── services/       # influxdb.cfg
├── influxdb/
│   └── tasks/          # hourly, daily, weekly Flux tasks
├── grafana/
│   ├── provisioning/   # datasources, dashboards, alerting
│   └── dashboards/     # openhab_iot.json
└── virtual-sim/        # Python симулятор
```

> **Примітка:** `openhab_userdata/` у репозиторії більше не монтується — userdata зберігається в named volume `openhab-userdata`.

## Dashboard Export

Dashboard зберігається в `grafana/dashboards/openhab_iot.json`. Експорт через Grafana UI: Dashboard settings → JSON Model.
