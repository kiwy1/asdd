#!/usr/bin/env python3
"""
Z-Score Anomaly Detection — для використання з OpenHAB (REST/CLI).
Normal behavior learning: mean/std з історичних даних.
Outlier detection: |z| > threshold.
"""
import sys
import json
import statistics


def zscore(values: list[float], current: float) -> tuple[float, float, float]:
    """Повертає (z_score, mean, std)."""
    if not values:
        return 0.0, 0.0, 0.0
    mean = statistics.mean(values)
    if len(values) < 2:
        return 0.0, mean, 0.0
    stdev = statistics.stdev(values)
    if stdev < 1e-9:
        stdev = 1e-9
    z = (current - mean) / stdev
    return z, mean, stdev


def main():
    # Вхід: JSON масив чисел (історія) та поточне значення
    # stdin: {"values": [1,2,3,...], "current": 5.0, "threshold": 2.5}
    try:
        raw = sys.stdin.read()
        data = json.loads(raw)
        values = data.get("values", [])
        current = float(data.get("current", 0))
        threshold = float(data.get("threshold", 2.5))
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        print(json.dumps({"error": str(e), "anomaly": False}))
        sys.exit(1)

    z, mean, std = zscore(values, current)
    anomaly = abs(z) > threshold
    severity = "NORMAL"
    if anomaly:
        if abs(z) >= threshold * 2:
            severity = "CRITICAL"
        elif abs(z) >= threshold * 1.5:
            severity = "HIGH"
        else:
            severity = "MEDIUM"

    out = {
        "z_score": round(z, 4),
        "mean": round(mean, 4),
        "std": round(std, 4),
        "anomaly": anomaly,
        "severity": severity,
        "explanation": f"Z={z:.3f} (mean={mean:.2f}, std={std:.2f})",
    }
    print(json.dumps(out))


if __name__ == "__main__":
    main()
