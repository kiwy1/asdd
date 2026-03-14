/**
 * Multi-variate Z-Score Anomaly Detection (для OpenHAB JS Scripting)
 * Використання: передати об'єкт з полями values (масив {temp, humidity, power, load}) та current.
 * Повертає: { score, severity, explanation }.
 */
(function(data) {
    const values = data.values || [];
    const current = data.current || {};
    const threshold = data.threshold || 2.5;

    function mean(arr) {
        if (arr.length === 0) return 0;
        return arr.reduce((a, b) => a + b, 0) / arr.length;
    }
    function std(arr, m) {
        if (arr.length < 2) return 0;
        const v = arr.reduce((s, x) => s + (x - m) * (x - m), 0) / (arr.length - 1);
        return Math.sqrt(v) || 1e-9;
    }

    let sumSqZ = 0;
    const dims = ['temp', 'humidity', 'power', 'load'];
    for (const dim of dims) {
        const arr = values.map(v => v[dim]).filter(v => v != null);
        const cur = current[dim];
        if (arr.length === 0 || cur == null) continue;
        const m = mean(arr);
        const s = std(arr, m);
        const z = (cur - m) / s;
        sumSqZ += z * z;
    }
    const score = Math.sqrt(sumSqZ);

    let severity = 'NORMAL';
    if (score >= threshold * 2) severity = 'CRITICAL';
    else if (score >= threshold * 1.5) severity = 'HIGH';
    else if (score >= threshold) severity = 'MEDIUM';
    else if (score >= threshold * 0.6) severity = 'LOW';

    return {
        score: Math.round(score * 1000) / 1000,
        severity: severity,
        explanation: 'Z_norm=' + score.toFixed(3)
    };
})(input);
