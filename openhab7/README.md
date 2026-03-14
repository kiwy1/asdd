# OpenHAB7 – Docker Compose Stack (IaC / Configuration Management)

Automated deployment solution for OpenHAB with **Infrastructure as Code** and **Configuration Management**: Docker Compose stack with InfluxDB, Grafana, Mosquitto MQTT, Nginx, and **virtual items with simulation**.

---

## Architecture Diagram

```
                    ┌─────────────────────────────────────────────────────────────┐
                    │                    openhab7-net (bridge)                     │
                    │                                                               │
  ┌───────────────┐ │  ┌─────────────┐   ┌─────────────┐   ┌─────────────────┐   │
  │   Client      │ │  │   Nginx     │   │   OpenHAB   │   │   virtual-sim   │   │
  │   Browser     │──┼──│  :80 / :443│───│   :8080     │◄──│   (REST push)    │   │
  └───────────────┘ │  └──────┬──────┘   └──────┬──────┘   └─────────────────┘   │
                    │         │                 │                                 │
                    │         │                 │  persistence                    │
                    │  ┌──────▼──────┐   ┌──────▼──────┐   ┌─────────────────┐   │
                    │  │   Grafana   │   │  InfluxDB   │   │   Mosquitto     │   │
                    │  │   :3000     │───│   :8086     │   │   MQTT :1883    │   │
                    │  └─────────────┘   └─────────────┘   └─────────────────┘   │
                    │                                                               │
                    └─────────────────────────────────────────────────────────────┘
                                         DNS: openhab, influxdb, grafana, mosquitto
```

**Components:**

| Service      | Role                    | Ports (host)     | Persistence              |
|-------------|-------------------------|------------------|---------------------------|
| OpenHAB     | Automation / UI         | 8080, 8443       | `openhab/conf`, userdata  |
| InfluxDB    | Time-series persistence | 8086             | volume `influxdb_data`    |
| Grafana     | Dashboards              | 3000             | volume `grafana_data`     |
| Mosquitto   | MQTT broker             | 1883, 9001       | volume `mosquitto_data`   |
| Nginx       | Reverse proxy (optional)| 80, 443          | config only               |
| virtual-sim | Simulates virtual items | —                | —                         |

**Virtual items:** All items are virtual; state is updated by the `virtual-sim` container via OpenHAB REST API (temperature, humidity, lights, power, CO2).

---

## Project Structure

```
openhab7/
├── docker/
│   └── docker-compose.yml      # Multi-container stack
├── openhab/
│   └── conf/                   # OpenHAB config (items, persistence, things, sitemaps)
├── mosquitto/
│   └── config/
│       └── mosquitto.conf
├── nginx/
│   ├── conf.d/
│   │   └── default.conf
│   └── certs/
├── grafana/
│   └── provisioning/           # Datasources, dashboards
├── virtual-sim/                # Virtual item simulator (Python)
│   ├── Dockerfile
│   └── virtual_sim.py
├── scripts/
│   ├── backup.sh
│   └── restore.sh
├── ansible/
│   ├── playbooks/
│   │   └── deploy.yml
│   └── inventory/
│       └── hosts.yml
├── terraform/
│   └── main.tf
├── .env.example
└── README.md
```

---

## Deployment Process

Як показати процес розгортання (deployment process):

### Варіант 1: Ручний deployment (Docker Compose)

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│ 1. Clone & .env  │ ──► │ 2. Compose up     │ ──► │ 3. Verify        │
│ git clone; .env  │     │ docker compose up │     │ UI, logs, health │
└──────────────────┘     └──────────────────┘     └──────────────────┘
```

**Кроки:**

| Крок | Дія | Команда / дія |
|------|-----|----------------|
| 1 | Клонувати репозиторій | `git clone <repo> && cd openhab7` |
| 2 | Створити конфіг з секретами | `cp .env.example .env` та відредагувати паролі |
| 3 | Запустити стек | `docker compose -f docker/docker-compose.yml --env-file .env -p openhab7 up -d --build` |
| 4 | Перевірити контейнери | `docker compose -f docker/docker-compose.yml -p openhab7 ps` |
| 5 | Перевірити логи (за потреби) | `docker compose -f docker/docker-compose.yml -p openhab7 logs -f` |
| 6 | Відкрити OpenHAB / Grafana | http://localhost:8080, http://localhost:3000 |

### Варіант 2: Автоматизований deployment (Ansible)

Для демонстрації automated deployment можна використати Ansible playbook:

```bash
cd openhab7
ansible-playbook -i ansible/inventory/hosts.yml ansible/playbooks/deploy.yml
```

Playbook перевіряє наявність Docker на хосту, створює `.env` з example за потреби та запускає `docker compose up -d`.

**Windows:** Ansible як control node на Windows не підтримується (помилка `os.get_blocking` — це Unix-only API). Варіанти:
- Запускати playbook у **WSL**: `wsl` → далі ті самі команди в bash.
- Або розгортати тільки через **Docker Compose** (варіант 1 вище).

### Що показати в звіті / презентації

1. **Architecture diagram** — схема з цього README (стек, мережа, сервіси).
2. **Deployment flow** — таблиця кроків вище або скріншоти терміналу: `cp .env.example .env` → `docker compose ... up -d` → `docker ps`.
3. **Configuration versioning** — конфіг у Git (`openhab/conf/`, `docker-compose.yml`, `.env.example`), без коміту `.env`.
4. **Backup/restore** — виконання `./scripts/backup.sh` та `./scripts/restore.sh backups/<timestamp>`.
5. **Health checks** — `docker ps` (статус healthy) або логи після `docker compose logs`.

---

## Quick Start

### Prerequisites

- Docker and Docker Compose (v2+)
- Git

### 1. Clone and configure

```bash
git clone <repo_url>
cd openhab7
cp .env.example .env
```

Edit `.env`: set at least:

- `INFLUXDB_ADMIN_PASSWORD`
- `INFLUXDB_TOKEN`
- `GRAFANA_ADMIN_PASSWORD`

Use the **same** `INFLUXDB_TOKEN` in OpenHAB InfluxDB addon and in Grafana datasource (see `openhab/conf/services/influxdb.cfg` and `grafana/provisioning/datasources/datasource.yml`), or leave placeholders for first run and fix after.

### 2. Start the stack

From the project root (use `--env-file .env` so Compose reads variables; if port 8086 is in use, set `INFLUXDB_PORT=8087` in `.env`):

```bash
docker compose -f docker/docker-compose.yml --env-file .env -p openhab7 up -d --build
```

Or from `docker/`:

```bash
cd docker
docker compose --env-file ../.env -p openhab7 up -d --build
```

### 3. Open UIs

- **OpenHAB:** http://localhost:8080 (or http://localhost/openhab if using Nginx on 80)
- **Grafana:** http://localhost:3000 (admin / password from `.env`)
- **InfluxDB:** http://localhost:8086 (admin / token from `.env`)

Wait 1–2 minutes for OpenHAB to install addons and for `virtual-sim` to start pushing; then virtual items will show data in the OpenHAB UI and in persistence.

---

## Backup and Restore

### Backup

Backs up OpenHAB `conf`, and Docker volumes (userdata, InfluxDB, Grafana, Mosquitto).

```bash
./scripts/backup.sh
# Or custom directory:
./scripts/backup.sh /path/to/backups
```

Backups are stored under `backups/<timestamp>/`.  
Retention: last **7 days** (override with `BACKUP_RETENTION_DAYS=14`).

**Scheduled backups (cron):**

```bash
# Example: daily at 02:00
0 2 * * * /path/to/openhab7/scripts/backup.sh
```

### Restore

1. Stop the stack:

   ```bash
   docker compose -f docker/docker-compose.yml -p openhab7 down
   ```

2. Restore from a backup directory:

   ```bash
   ./scripts/restore.sh backups/20250114_120000
   ```

3. Start the stack again:

   ```bash
   docker compose -f docker/docker-compose.yml -p openhab7 up -d
   ```

---

## Troubleshooting

| Problem | What to check |
|--------|-----------------|
| OpenHAB not starting / 502 | Wait 2–3 min for first boot and addon install. Check logs: `docker logs openhab7-openhab`. |
| Virtual items empty | Ensure `virtual-sim` is running and OpenHAB REST is up: `docker logs openhab7-virtual-sim`. Sim waits ~25 s then pushes every 10 s. |
| InfluxDB connection failed in OpenHAB | InfluxDB addon: URL `http://influxdb:8086`, same org/bucket/token as in `.env` and Grafana. |
| Grafana “no datasource” | Token in `grafana/provisioning/datasources/datasource.yml` must match `INFLUXDB_TOKEN`. Restart Grafana after editing. |
| Mosquitto connection refused | Check `mosquitto/config/mosquitto.conf` is mounted and container is healthy: `docker ps` and `docker logs openhab7-mosquitto`. |
| Port already in use | Change ports in `.env` (e.g. `OPENHAB_HTTP_PORT=8081`, `GRAFANA_PORT=3001`, `INFLUXDB_PORT=8087`). Always run with `--env-file .env`. |
| Backup script: “volume not found” | Run at least once `docker compose -f docker/docker-compose.yml -p openhab7 up -d` so volumes exist; use same project name `openhab7`. |

**Useful commands:**

```bash
# Logs
docker compose -f docker/docker-compose.yml -p openhab7 logs -f

# Restart one service
docker restart openhab7-openhab

# Rebuild virtual-sim after code change
docker compose -f docker/docker-compose.yml -p openhab7 up -d --build virtual-sim
```

---

## Technical Requirements (Checklist)

- **Multi-container stack:** OpenHAB, InfluxDB, Grafana, Mosquitto, Nginx, virtual-sim
- **Persistent volumes:** OpenHAB conf + userdata, InfluxDB, Grafana, Mosquitto data
- **Networking:** Custom network `openhab7-net`, DNS resolution between containers
- **Health checks:** Mosquitto, InfluxDB, OpenHAB, Grafana, Nginx
- **Restart policy:** `unless-stopped` for all services
- **Backup:** `scripts/backup.sh` (config + volumes, rotation)
- **Restore:** `scripts/restore.sh`
- **Configuration:** `.env` + `.env.example`; OpenHAB config under `openhab/conf/` (versioned)

All **items are virtual** and driven by the **virtual-sim** service (REST API).
