// Daily rollup - aggregate hourly bucket into daily
option task = {name: "openhab-daily-rollup", every: 1d, offset: 1h}

from(bucket: "openhab_hourly")
  |> range(start: -2d)
  |> filter(fn: (r) => r._field == "value")
  |> filter(fn: (r) => r._value is float or r._value is int)
  |> aggregateWindow(fn: mean, every: 1d, createEmpty: false)
  |> to(bucket: "openhab_daily", org: "openhab")
