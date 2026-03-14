# OpenHAB 4.x — Edge AI Anomaly Detection System

**Варіант 1: ML-based Anomaly Detection** з навчанням нормальної поведінки та адаптивними порогами. Усі Items **віртуальні** з симуляцією даних.

## Запуск (Docker Compose)

```bash
cd openhab6
docker compose up -d
```

- **OpenHAB UI:** http://localhost:8086  
- Логін за замовчуванням: створюється при першому вході.

Після старту увімкніть **Симуляцію** в UI — віртуальні сенсори почнуть оновлюватись кожну хвилину. Для тесту аномалій встановіть **Інжектувати аномалію** (1 = спайк, 2 = дрифт).

---

## Anomaly Detection Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  Віртуальні сенсори (Items)                                      │
│  vSensor_Temperature, vSensor_Humidity, vSensor_Power, Load     │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  Симуляція (simulation.rules)                                    │
│  Cron кожну хв: сезонність (добовий цикл) + шум; опційно аномалія │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  Persistence (rrd4j, mapdb)                                      │
│  Historical data для baseline та ML                              │
└───────────────────────────┬─────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────────────┐
│ Baseline      │  │ Anomaly       │  │ Scripts (ML)           │
│ (Rules)       │  │ Detection     │  │ zscore_anomaly.py      │
│ mean/std з    │  │ (Rules)       │  │ multivariate_zscore.js│
│ останніх 24h  │  │ Z-score,     │  │ (опційно: CLI/REST)    │
│               │  │ severity      │  │                        │
└───────────────┘  └───────┬───────┘  └───────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  Alert Generation                                                 │
│  vAnomaly_Score, vAnomaly_Severity, vAnomaly_Explanation,         │
│  vAnomaly_Alert (з deduplication по таймеру)                      │
└─────────────────────────────────────────────────────────────────┘
```

- **Дані:** тільки віртуальні Items; жодних зовнішніх біндингів для сенсорів.
- **Правила:** симуляція даних, оновлення baseline, обчислення Z-score та severity, алерти.
- **Скрипти:** Python (Z-score з JSON stdin), JavaScript (multivariate Z-score) для інтеграції з ML pipeline.

---

## ML Algorithms Explanation

1. **Normal Behavior Learning**
   - **Historical data:** rrd4j зберігає кожну зміну та кожну хвилину для `gSensors*`.
   - **Pattern extraction / Baseline:** у правилах використовується `persistenceExtensions.averageSince()`, `maximumSince()`, `minimumSince()` за останні 24 год.
   - **Statistical profiling:** mean та оцінка std як (max−min)/4 для кожного каналу (температура, вологість).

2. **Outlier Detection**
   - **Z-score method:** \( z = (x - \mu) / \sigma \); поріг за замовчуванням 2.5.
   - **Multi-variate:** комбінований Z як евклідова норма Z по каналах: \( \sqrt{z_{temp}^2 + z_{hum}^2} \).
   - **Isolation Forest / LSTM:** заготовлені каталоги `conf/ml/models/`, `conf/ml/data/` та скрипти для подальшого підключення (опційно).

3. **Adaptive Thresholds**
   - **Dynamic threshold:** Item `vThreshold_ZScore` (1–5) — користувач або правило може змінювати.
   - **Seasonal pattern:** baseline перераховується з ковзним вікном 24 год, тому добова сезонність врахована в mean/std.
   - **Drift detection:** при зміні baseline (кожна зміна сенсорів) mean/std оновлюються — повільний дрифт відображається в новому baseline.

4. **Alert Generation**
   - **Anomaly scoring:** `vAnomaly_Score` — комбінований Z.
   - **Severity:** NORMAL | LOW | MEDIUM | HIGH | CRITICAL за порогами (0.6×, 1×, 1.5×, 2× від Z_threshold).
   - **Deduplication:** правило скидає `vAnomaly_Alert` через 5 хв після ON.
   - **Explanation:** `vAnomaly_Explanation` — текст з Z та коротким поясненням.

---

## Threshold Adaptation Strategy

- **Baseline:** ковзне вікно 24 год (rrd4j), оновлення mean/std при зміні сенсорів.
- **Поріг Z:** налаштовується через Item `vThreshold_ZScore`; в правилах використовується значення за замовчуванням 2.5, якщо Item не встановлено.
- **Сезонність:** 24-годинне вікно автоматично враховує добові цикли симуляції.
- **Оптимізація:** можлива подальша логіка (наприклад, правило або скрипт) для підбору порога за метриками (precision/recall) з історії алертів.

---

## Performance Metrics (Precision, Recall)

- **В симуляції:** при `vSimulation_AnomalyInject = 1` (спайк) або `2` (дрифт) очікується підвищення Z-score та алерт.
- **Метрики** можна оцінити так:
  - **True Positive:** алерт при інжектованій аномалії (inject=1 або 2).
  - **False Positive:** алерт при inject=0.
  - **Precision = TP / (TP + FP), Recall = TP / (TP + FN)** при заданому порозі.
- Для кількісних метрик варто збирати логи алертів та позначені періоди аномалій у `conf/ml/data/` і рахувати по ним (наприклад, скриптом у репозиторії).

---

## Що здати (Files)

| Компонент | Файли |
|-----------|--------|
| **Training data collection** | `openhab/conf/persistence/rrd4j.persist`, `mapdb.persist` — збір історії; `openhab/conf/ml/data/` — місце для експорту даних для навчання |
| **ML model code** | `openhab/conf/scripts/zscore_anomaly.py`, `openhab/conf/scripts/multivariate_zscore.js`; `openhab/conf/ml/models/` — навчені моделі |
| **Inference integration** | `openhab/conf/rules/anomaly_detection.rules` — використання persistence для baseline, Z-score та severity; виклик Python/JS при потребі через `executeCommandLine` / JS Scripting |
| **Alert rules** | `openhab/conf/rules/anomaly_detection.rules` — правила для baseline, Z-score, severity, `vAnomaly_Alert`, deduplication по таймеру |
| **Simulation** | `openhab/conf/rules/simulation.rules` — генерація віртуальних сенсорів та інжекція аномалій |
| **Config** | `openhab/conf/items/default.items`, `openhab/conf/sitemaps/default.sitemap`, `docker-compose.yml` |

---

## Структура репозиторію

```
openhab6/
├── docker-compose.yml
├── README.md
└── openhab/
    └── conf/
        ├── items/
        │   └── default.items
        ├── rules/
        │   ├── simulation.rules
        │   └── anomaly_detection.rules
        ├── scripts/
        │   ├── zscore_anomaly.py
        │   └── multivariate_zscore.js
        ├── ml/
        │   ├── models/
        │   └── data/
        ├── persistence/
        │   ├── rrd4j.persist
        │   └── mapdb.persist
        ├── services/
        │   ├── addons.cfg
        │   └── rrd4j.cfg
        └── sitemaps/
            └── default.sitemap
```

---

## Вимоги

- **OpenHAB 4.x** (образ `openhab/openhab:4.2.1`).
- **Python/JavaScript:** скрипти в `conf/scripts/`; для виклику Python з правил потрібен Python у контейнері або виклик через REST/зовнішній сервіс (опційно).
- **Persistence:** rrd4j, mapdb (додатки вказані в `addons.cfg`).
- **Automation:** Rule Engine + опційно JS (addon `js`).

Усі сенсори — **віртуальні**, дані генеруються правилами симуляції.
