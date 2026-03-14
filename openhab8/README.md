# OpenHAB 8 — CI/CD Pipeline (Віртуальні Items + симуляція)

Спроектовано та реалізовано **CI/CD pipeline** для конфігурації OpenHAB з automated testing, validation та deployment. Усі Items — **віртуальні**, з симуляцією через контейнер `virtual-sim`.

---

## Pipeline architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         CI/CD Pipeline                                   │
├─────────────┬─────────────┬─────────────┬─────────────┬─────────────────┤
│  Validate   │    Test     │   Build     │   Deploy    │ Branch protect  │
│  (config)   │ (unit+int)  │ (Docker)    │ (artifacts) │ (optional)      │
├─────────────┼─────────────┼─────────────┼─────────────┼─────────────────┤
│ • Items     │ • pytest    │ • Multi-    │ • Upload    │ • Require       │
│ • Things    │ • config   │   stage     │   openhab/  │   status checks │
│ • Sitemaps  │ • rules    │ • Trivy     │   conf      │ • Require PR     │
│ • Rules DSL │ • REST API │ • Tagging   │ • Summary   │   review         │
│ • YAML/JSON │             │ • GHCR push │             │                 │
└─────────────┴─────────────┴─────────────┴─────────────┴─────────────────┘
```

- **Validate** — синтаксис та структура конфігурації (Items, Things, Sitemaps, Rules, YAML/JSON).
- **Test** — unit-тести (config, rules logic), integration-тести (REST API після підняття OpenHAB у Docker).
- **Build** — multi-stage збірка образу симулятора, Trivy security scan, публікація в GHCR.
- **Deploy** — збереження артефактів конфігурації та підсумок (опційно — розгортання на сервер).

---

## Workflow descriptions

| Workflow    | File              | Trigger                    | Jobs |
|------------|-------------------|----------------------------|------|
| **Validate** | `validate.yml`    | push/PR на `main`, `develop` | OpenHAB config validation, YAML/JSON validation |
| **Test**     | `test.yml`        | push/PR на `main`, `develop` | Unit tests, Integration tests, Config tests |
| **Build**    | `build.yml`       | push/PR на `main`          | Build virtual-sim image, Trivy scan, push to GHCR (on main) |
| **Deploy**   | `deploy.yml`      | after Validate/Test/Build success, or manual | Upload config artifact, summary |

### Validate

- **Items syntax** — `scripts/validate_items.py` (тип + ім’я Item).
- **Things** — `scripts/validate_thing.py` (дужки, базова структура).
- **Sitemaps** — `scripts/validate_sitemap.py` (sitemap {}, Frame, Text/Switch/Slider/Group).
- **Rules DSL** — `scripts/validate_rules.py` (rule/when/then/end).
- **YAML** — `yamllint` для `openhab/conf/misc/config.yml` та інших `.yml`.
- **JSON** — `python -c "json.load(...)"` для всіх `.json` у `openhab/conf`.

### Test

- **Unit**: структура конфігурації (`test_config.py`), логіка правил (`test_rules_logic.py`).
- **Integration**: REST API Items після `docker compose up openhab` (`test_rest_api.py`).
- **Config tests**: окремі тести конфігурації в `tests/unit/test_config.py`.

### Build

- **Multi-stage Dockerfile**: builder (pip install) → runtime (alpine + copy app, non-root user).
- **Trivy** — сканування образу на CRITICAL/HIGH, SARIF upload для CodeQL.
- **Tagging**: `latest` на `main`, branch name, SHA.

### Deploy

- Збереження артефакту `openhab-conf-<sha>` (вміст `openhab/conf/`).
- Підсумок у GitHub Step Summary (артефакт + посилання на образ).

---

## Testing strategy

| Level        | Tool    | Scope |
|-------------|---------|--------|
| **Unit**    | pytest  | Config (items/sitemaps/metadata), rules structure (when/then/end). |
| **Integration** | pytest + requests | REST `/rest/items` після запуску OpenHAB у Docker. |
| **Regression** | Same unit + integration | Повторний прогон при кожному push/PR. |
| **Config**  | Custom scripts + yamllint | Items, Things, Sitemaps, YAML/JSON. |

---

## Status badges

Додайте у README репозиторію (замініть `OWNER` та `REPO` на ваші):

```markdown
[![Validate](https://github.com/OWNER/REPO/actions/workflows/validate.yml/badge.svg)](https://github.com/OWNER/REPO/actions/workflows/validate.yml)
[![Test](https://github.com/OWNER/REPO/actions/workflows/test.yml/badge.svg)](https://github.com/OWNER/REPO/actions/workflows/test.yml)
[![Build](https://github.com/OWNER/REPO/actions/workflows/build.yml/badge.svg)](https://github.com/OWNER/REPO/actions/workflows/build.yml)
[![Deploy](https://github.com/OWNER/REPO/actions/workflows/deploy.yml/badge.svg)](https://github.com/OWNER/REPO/actions/workflows/deploy.yml)
```

---

## Структура проекту

```
openhab8/
├── .github/workflows/
│   ├── validate.yml
│   ├── test.yml
│   ├── build.yml
│   └── deploy.yml
├── .gitlab-ci.yml
├── tests/
│   ├── unit/
│   │   ├── test_config.py
│   │   └── test_rules_logic.py
│   ├── integration/
│   │   └── test_rest_api.py
│   └── conftest.py
├── openhab/conf/
│   ├── items/virtual.items
│   ├── things/virtual.things
│   ├── sitemaps/default.sitemap
│   ├── rules/virtual.rules
│   └── misc/config.yml, metadata.json
├── simulator/
│   └── simulate.py
├── scripts/
│   ├── validate_items.py
│   ├── validate_thing.py
│   ├── validate_sitemap.py
│   └── validate_rules.py
├── Dockerfile          # Multi-stage для virtual-sim
├── Dockerfile.sim      # Простий варіант для docker-compose
├── docker-compose.yml
├── pytest.ini
└── README.md
```

---

## Локальний запуск (Docker Compose)

Усі Items — віртуальні; стан оновлюється симулятором через REST API.

```bash
cd openhab8
docker compose up -d
```

- **OpenHAB UI**: http://localhost:9080 (за замовчуванням; 8080 змінено на 9080, щоб уникнути конфліктів)
- **Симулятор** кожні 15 с оновлює: температуру, вологість, світло, вимикач, потужність, CO2.

Перемінні середовища (опційно): `OPENHAB_HTTP_PORT` (за замовчуванням 9080), `OPENHAB_HTTPS_PORT` (9443), `TZ`, `SIM_INTERVAL`, `STARTUP_DELAY` (секунди очікування перед першим циклом симулятора, за замовчуванням 45).

**Якщо порт зайнятий або virtual-sim не стартує:** запустіть тільки OpenHAB: `docker compose up -d openhab`. Симулятор можна запустити локально: `pip install requests && OPENHAB_URL=http://localhost:9080 python simulator/simulate.py`.

---

## Вимоги

- Git repository (GitHub або GitLab).
- CI: **GitHub Actions** (основний) або **GitLab CI** (`.gitlab-ci.yml`).
- Python 3.12 для скриптів валідації та тестів.
- Docker та Docker Compose для збірки образу та інтеграційних тестів.
