# AutoMetrics

AutoMetrics is a Python CLI framework for metric pipelines built from plugins. It runs in three phases:

1. ingest data into a shared repository
2. run analyses and derived visualizations
3. save the results

## Quickstart

AutoMetrics needs Python 3.12+ and the packages in [`requirements.txt`](./requirements.txt).

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

If you are on Windows PowerShell, activate the environment with `.\venv\Scripts\Activate.ps1`.

Check the CLI:

```bash
python src/main.py --help
```

Validate a config without running the ingest, analysis, and save phases:

```bash
python src/main.py ./configs/monthly.yaml --verify-config
```

This repo ships the AutoMetrics runtime, plugin loader, base classes, and a handful of built-in helpers. The real ingest logic and the real domain-specific analyses are expected to come from plugins. In practice, base AutoMetrics is intentionally barebones: without plugins, there is very little useful analysis to run.

Most included configs expect project-specific plugins in [`plugins/`](./plugins) such as `PromQLIngestController`, so `--verify-config` is the safest first run until your plugin set is installed.

Run a config for real once the required plugins are present:

```bash
python src/main.py ./configs/monthly.yaml
```

## Typical Workflow

1. Put custom plugin files under [`plugins/`](./plugins).
2. Pick or create a YAML config under [`configs/`](./configs).
3. Run `--verify-config` to confirm plugin loading and config sections.
4. Run the config, optionally overriding `period`, `analyses`, or `exit-action` on the CLI.
5. Inspect outputs under the configured `saving.base-path`, usually somewhere under [`io/`](./io).

## Configuration Overview

Required top-level runtime sections:

```yaml
period: lastmonth
timeline:
  align: month
  sub_period_max_len: 302400
ingest:
  run:
    - IngestPluginName
analysis:
  run:
    - analysis_name
saving:
  base-path: "./io/latest"
  exit-action: none
  run:
    - SaverPluginName
```

Plugin-specific configuration lives in additional top-level sections keyed by class name:

```yaml
PromQLIngestController:
  query-cfgs:
    - monthly
```

See the full references in [`docs/configuration.md`](./docs/configuration.md) and [`docs/cli.md`](./docs/cli.md).

## Built-In Capabilities

AutoMetrics includes:

- plugin base classes and the runtime loader
- timeline ingestion
- analysis drivers for simple, meta, aggregate, verification, and visualization workflows
- savers for analysis files, visualization PNGs, and email delivery

The important constraint is that this base repository is mostly infrastructure for plugins. What it does not include by default is your project-specific ingest logic, your concrete analysis definitions, or your project’s output conventions. Those usually live in [`plugins/`](./plugins) or in a companion repo, and they are what make an AutoMetrics deployment actually useful.

See [`docs/builtins.md`](./docs/builtins.md).

## Writing Plugins

AutoMetrics discovers Python files under `./plugins` recursively. Any class that subclasses one of the supported plugin base classes will be loaded automatically.

Start with:

- [`docs/plugins.md`](./docs/plugins.md) for practical plugin examples
- [`TechnicalDetails.md`](./TechnicalDetails.md) for architecture details
- [`plugins/README.md`](./plugins/README.md) for local plugin folder conventions

## Documentation Map

- [`docs/configuration.md`](./docs/configuration.md): YAML structure and key reference
- [`docs/cli.md`](./docs/cli.md): CLI flags and examples
- [`docs/plugins.md`](./docs/plugins.md): plugin loading rules and minimal examples
- [`docs/builtins.md`](./docs/builtins.md): built-in plugins and outputs
- [`docs/troubleshooting.md`](./docs/troubleshooting.md): common failures and what to check
- [`TechnicalDetails.md`](./TechnicalDetails.md): deeper architecture notes
