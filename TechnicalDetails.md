# Technical Details

This document covers the deeper architecture behind AutoMetrics. For task-oriented setup and usage, start with [`README.md`](./README.md), [`docs/configuration.md`](./docs/configuration.md), and [`docs/plugins.md`](./docs/plugins.md).

AutoMetrics was primarily developed alongside [RCI Metrics](https://github.com/east-01/RCI-Metrics), which contains examples of project-specific plugin implementations.

There are three phases in the AutoMetrics lifecycle: ingest, analysis, and saving.

- ingest collects data from external sources into a shared [`DataRepository`](#datarepository)
- analysis transforms and validates that data through loaded analyses and drivers
- saving writes chosen outputs to the filesystem or other targets

## Table Of Contents

- [Important structures](#important-structures)
- [Plugins](#plugins)

## Important Structures

### ProgramData

`ProgramData` is created early in startup and passed through the run. It holds:

- loaded plugins
- parsed arguments
- loaded config
- the active timeline
- the shared `DataRepository`

### Identifiers

Identifiers are frozen dataclasses that act as stable keys into the repository.

Built-in identifier types include:

- `TimeStampIdentifier`
- `AnalysisIdentifier`
- `MetaAnalysisIdentifier`
- `AggregateAnalysisIdentifier`

Custom projects can define additional identifier types when they need domain-specific keys.

### DataRepository

`DataRepository` stores data and metadata by `Identifier`. It is the central handoff point between ingest, analysis, and saving.

Typical operations are:

```python
data_repo.add(identifier, data, metadata)
data, metadata = data_repo.get(identifier)
matches = data_repo.filter_ids(lambda identifier: True)
```

## Plugins

The base plugin types live in [`src/plugin_mgmt/plugins.py`](./src/plugin_mgmt/plugins.py).

### Configurable Plugins

`IngestPlugin`, `AnalysisDriverPlugin`, and `Saver` inherit configurable behavior. If a config contains a top-level section matching the plugin class name, that section is passed into `verify_config_section()` and later into the runtime method.

### IngestPlugin

Ingest plugins pull external data into a new `DataRepository`, then AutoMetrics merges that repository into the shared one.

Shape:

```python
class IngestPlugin(ConfigurablePlugin):
    def verify_config_section(self, config_section: dict):
        pass

    def ingest(self, prog_data: ProgramData, config_section: dict) -> DataRepository:
        repo = DataRepository()
        return repo
```

### Analysis

`Analysis` is the base frozen dataclass for executable analysis definitions. Each analysis has:

- `name`
- `prereq_analyses`

These names are what the config and CLI reference.

### AnalysisPlugin

Analysis plugins return concrete analyses from `get_analyses()`.

Shape:

```python
class AnalysisPlugin(ABC):
    def get_analyses(self) -> list[Analysis]:
        return []
```

### AnalysisDriverPlugin

Drivers execute a specific analysis type, selected through `SERVED_TYPE`.

Shape:

```python
class AnalysisDriverPlugin(ConfigurablePlugin):
    SERVED_TYPE: Type[Analysis] = None

    def verify_config_section(self, config_section: dict):
        pass

    def run_analysis(self, analysis, prog_data: ProgramData, config_section: dict):
        pass
```

The built-in drivers show the main extension patterns:

- `SimpleAnalysisDriver` for per-identifier computations
- `MetaAnalysisDriver` for period-over-period tables
- `AggregateAnalysisDriver` for grouped results
- `VerificationDriver` for validation-only checks
- `VisualAnalysisDriver` for figure generation

### Saver

Savers read from the repository and write files or deliver outputs elsewhere.

Shape:

```python
class Saver(ConfigurablePlugin):
    def verify_config_section(self, config_section):
        super().verify_config_section(config_section)

    def save(self, prog_data: ProgramData, config_section: dict, base_path: str) -> list[str]:
        return []
```

The base saver implementation allows either no config section or one containing only `addtl-base`.

## Related Docs

- [`docs/plugins.md`](./docs/plugins.md)
- [`docs/builtins.md`](./docs/builtins.md)
- [`docs/troubleshooting.md`](./docs/troubleshooting.md)
