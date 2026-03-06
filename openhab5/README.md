# Smart Home Edge Gateway (Variant 1)

Автономний Smart Home Gateway з повним **local processing**, **offline** операціями та **edge dashboard** без залежності від хмари.

## Функціональні вимоги (виконано)

| Вимога | Реалізація |
|--------|------------|
| **Local Processing** | Всі правила в `openhab/conf/rules/` виконуються локально, без зовнішніх API |
| **No Cloud Dependency** | Тільки OpenHAB + локальний MQTT брокер (Mosquitto), локальне зберігання |
| **Offline Operations** | Працює без інтернету; індикатори в сістемній секції Dashboard; локальний backup по кнопці |
| **Edge Dashboard** | Локальний sitemap, UI без зовнішніх CDN, адаптивний Basic/Paper UI |

## Технічний стек

- **OpenHAB 5.1.3** — standalone, без cloud bindings
- **Eclipse Mosquitto** — локальний MQTT брокер (порт 1883)
- **Local persistence**: RRD4J, MapDB
- **Всі items віртуальні** — у `openhab/conf/items/default.items`
- **Правила автоматизації** — у `openhab/conf/rules/` (automation, offline, edge_optimization)

## Запуск

```bash
cd openhab5
docker compose up -d
```

- **OpenHAB UI**: http://localhost:8080 (логін створюється при першому вході)
- **MQTT**: localhost:1883 (для правил/біндінгів — внутрішня мережа контейнерів: `mosquitto:1883`)

## Структура проєкту

```
openhab5/
├── docker-compose.yml      # OpenHAB + Mosquitto, мережа edge-net
├── .env
├── mosquitto/
│   └── config/
│       └── mosquitto.conf # Локальний брокер, без зовнішніх підключень
└── openhab/
    └── conf/
        ├── items/
        │   └── default.items   # Віртуальні items (світло, клімат, безпека, система)
        ├── things/
        │   └── mqtt.things     # Локальний MQTT broker (mosquitto)
        ├── persistence/
        │   ├── rrd4j.persist
        │   └── mapdb.persist
        ├── rules/
        │   ├── automation.rules
        │   ├── offline.rules
        │   └── edge_optimization.rules
        ├── sitemaps/
        │   └── default.sitemap # Edge Dashboard (без CDN)
        └── services/
            └── addons.cfg     # mqtt, rrd4j, mapdb, basic, paper
```

## Оптимізація для edge

- Обмеження пам’яті JVM у `docker-compose`: `-Xmx256m -Xms64m`
- Persistence тільки локальна (rrd4j + mapdb)
- Немає викликів зовнішніх API в правилах
- Локальна автентифікація та дані — у каталогах OpenHAB (userdata/conf)

## Відновлення після offline

- Дані зберігаються в `./openhab/userdata` (MapDB/RRD4J).
- Після появи мережі достатньо перезапустити контейнери при потребі; синхронізація з хмарою не використовується.
