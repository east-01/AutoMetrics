# Configuration Reference

AutoMetrics reads one YAML file per run. The configuration has:

- runtime sections that control the run
- optional plugin-specific sections keyed by plugin class name

## Required Runtime Sections

`period`

- Required unless overridden with `--period`.
- Parsed into a `(start_ts, end_ts)` tuple.

`ingest.run`

- Required.
- List of ingest plugin class names to execute in order.

`analysis.run`

- Required unless overridden with `--analyses`.
- List of analysis names, not class names.

`saving.run`

- Required.
- List of saver plugin class names to execute in order.

## Optional Runtime Sections

`timeline`

- Optional.
- If omitted, AutoMetrics still creates a timeline using defaults.
- Supported keys:
  - `align`: required when `timeline` is present; currently `month` creates month-aligned main periods, any other value falls back to one main period for the full run
  - `sub_period_max_len`: optional integer number of seconds for sub-period splitting

`saving.base-path`

- Optional.
- Defaults to `./latest_run` when omitted.

`saving.exit-action`

- Optional.
- Must be one of `none`, `openeach`, or `opendir`.
- Can be overridden by `--exit-action`.

## Period Formats

Supported single-value periods:

| Format | Example | Result |
|---|---|---|
| Year | `2024` | whole calendar year |
| MonthYear | `January25` | whole month |
| Unix timestamp | `1738396800` | exact instant |
| Keyword | `now`, `yesterday`, `lastweek`, `lastmonth`, `ytd` | relative range |

Supported range syntax:

```yaml
period: January25-March25
```

The start token contributes the range start, and the end token contributes the range end.

## Minimal Runtime Example

```yaml
period: lastmonth
timeline:
  align: month
  sub_period_max_len: 302400
ingest:
  run:
    - IngestTimeline
analysis:
  run:
    - summary
saving:
  base-path: "./io/monthly_latest"
  exit-action: none
  run:
    - AnalysisSaver
```

This example still requires a plugin that actually defines the `summary` analysis.

## Plugin-Specific Sections

Any configurable plugin can read a top-level section named after its class:

```yaml
AnalysisSaver:
  whitelist:
    - summary
    - usedcapacity
```

```yaml
PromQLIngestController:
  main-periods: true
  query-cfgs:
    - monthly
```

AutoMetrics calls `verify_config_section()` on loaded configurable plugins before the run starts.

## Validation Rules That Matter

- `ingest.run`, `analysis.run`, and `saving.run` must exist.
- `analysis.run` entries must match loaded analysis names.
- `saving.exit-action` must be one of the supported choices.
- If `timeline` is present, it must include `align`.
- `period` cannot end before it starts or extend into the future.

## Notes On Included Sample Configs

Configs under [`configs/`](../configs) demonstrate real runs, but several of them rely on external plugins not included in this repository. Common examples are project-specific ingest controllers and analysis definitions.
