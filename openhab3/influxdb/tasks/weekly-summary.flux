// Weekly summary - aggregate daily into weekly
option task = {name: "openhab-weekly-summary", every: 1w, offset: 6h}

from(bucket: "openhab_daily")
  |> range(start: -14d)
  |> filter(fn: (r) => r._field == "value")
  |> filter(fn: (r) => r._value is float or r._value is int)
  |> aggregateWindow(fn: mean, every: 1w, createEmpty: false)
  |> to(bucket: "openhab_weekly", org: "openhab")
