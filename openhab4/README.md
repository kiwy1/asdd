# Smart Grid Analytics - OpenHAB 4

Real-time Smart Grid monitoring з demand-response scenarios та grid stability detection.

## Функціональність

1. **Real-time Load Monitoring** – 6 віртуальних вузлів, power flow, frequency, voltage
2. **Demand-Response** – Peak detection, Load shedding, Priority-based control
3. **Grid Stability** – Frequency deviation, Voltage sag/swell, THD, Islanding
4. **Emergency Shutdown** – Cascade prevention, Critical load protection, Recovery

**Всі Items віртуальні** – оновлюються симулятором та rules.

## Запуск

```bash
cd openhab4
docker compose up -d
```

- **OpenHAB UI**: http://localhost:8084
- **Grafana**: http://localhost:3001 (admin/admin)

## Структура

```
openhab4/
├── docker-compose.yml
├── smart-grid-sim/          # Python симулятор (6 nodes, power flow, scenarios)
├── openhab_conf/
│   ├── items/               # Віртуальні Items
│   │   ├── smartgrid_nodes.items
│   │   ├── smartgrid_powerflow.items
│   │   ├── smartgrid_stability.items
│   │   ├── smartgrid_demand_response.items
│   │   ├── smartgrid_emergency.items
│   │   └── smartgrid_alerts.items
│   ├── rules/
│   │   ├── grid_stability.rules
│   │   ├── demand_response.rules
│   │   ├── emergency_shutdown.rules
│   │   └── performance_monitoring.rules
│   ├── persistence/
│   └── sitemaps/
└── grafana/
```

## State Machine

| State     | Умова                         |
|-----------|-------------------------------|
| NORMAL    | Power < 350 kW, стабільна мережа |
| PEAK      | Power ≥ 350 kW                |
| STRESSED  | Power ≥ 400 kW                |
| EMERGENCY | Overload / Islanding / Cascade |
| RECOVERY  | Після EMERGENCY, 20s sequence |

## InfluxDB (опціонально)

1. Settings → Add-ons → Persistence → InfluxDB 2 (встановити)
2. Токен у `influxdb.cfg` та `.env` мають збігатися з `DOCKER_INFLUXDB_INIT_ADMIN_TOKEN`
