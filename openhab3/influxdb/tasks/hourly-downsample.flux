// Hourly aggregation (avg) - downsampling to openhab_hourly
option task = {name: "openhab-hourly-downsample", every: 1h, offset: 5m}

from(bucket: "openhab")
  |> range(start: -2h)
  |> filter(fn: (r) => r._field == "value")
  |> filter(fn: (r) => r._value is float or r._value is int)
  |> aggregateWindow(fn: mean, every: 1h, createEmpty: false)
  |> to(bucket: "openhab_hourly", org: "openhab")
