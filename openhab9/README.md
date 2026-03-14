# OpenHAB 9 — Практична робота 16.1 (PIA, Варіант 1)

Віртуальна система моніторингу здоров'я для завдання «Privacy Impact Assessment для розумної системи моніторингу здоров'я». Всі Items — **віртуальні** з симуляцією (серцевий ритм, активність, сон, геолокація).

## Запуск

```bash
cd openhab9
docker compose up -d
```

- OpenHAB UI: http://localhost:8080  
- Симулятор оновлює Items кожні 10 с (змінна `SIM_INTERVAL`).

## Що здати

| Файл | Опис |
|------|------|
| `variant1-pia-health-monitor.md` | Повний PIA |
| `data-flow-diagram.png` | Візуалізація потоку даних |

Якщо діаграма згенерована в іншій папці (наприклад `assets/data-flow-diagram.png`), скопіюйте її в `openhab9` як `data-flow-diagram.png` перед здачею.

Згенерувати PNG з Mermaid можна на [mermaid.live](https://mermaid.live) — вставте вміст файлу `data-flow-diagram.mmd` і експортуйте як PNG.
