# Plugin Guide

AutoMetrics loads plugins from two places:

- `./plugins`
- `./src/builtin_plugins`

The local `plugins/` folder is where project-specific code normally lives.

## Discovery Rules

- Files are scanned recursively.
- Only `.py` files are inspected.
- Classes are discovered by subclassing the base types in [`src/plugin_mgmt/plugins.py`](../src/plugin_mgmt/plugins.py).
- Ingest plugins, analysis drivers, and savers are instantiated directly.
- Analysis plugins are instantiated so AutoMetrics can collect the analyses returned by `get_analyses()`.

## Supported Plugin Types

- `IngestPlugin`
- `AnalysisPlugin`
- `AnalysisDriverPlugin`
- `Saver`

Configurable plugin types can optionally implement `verify_config_section(config_section)`.

## Minimal Ingest Plugin

```python
from dataclasses import dataclass

from src.data.data_repository import DataRepository
from src.data.identifier import Identifier
from src.plugin_mgmt.plugins import IngestPlugin

@dataclass(frozen=True)
class ExampleIdentifier(Identifier):
    name: str

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return isinstance(other, ExampleIdentifier) and self.name == other.name

    def __str__(self):
        return self.name

class ExampleIngest(IngestPlugin):
    def ingest(self, prog_data, config_section):
        repo = DataRepository()
        repo.add(ExampleIdentifier("demo"), 123, {"source": "example"})
        return repo
```

## Minimal Analysis Type, Analysis Plugin, And Driver

An `AnalysisPlugin` is only a container. Its job is to return instantiated `Analysis` objects from `get_analyses()`. The actual runtime behavior lives in the analysis dataclass and its matching `AnalysisDriverPlugin`.

If you can use an existing built-in driver, do that instead of writing a new one. `SimpleAnalysisDriver` is still the easiest starting point for many projects.

### Using a built-in driver instead of writing your own

```python
from src.builtin_plugins.simple_analysis_driver import SimpleAnalysis
from src.plugin_mgmt.plugins import AnalysisPlugin

class ExampleSimpleAnalysisPlugin(AnalysisPlugin):
    def get_analyses(self):
        return [
            SimpleAnalysis(
                name="double_value",
                prereq_analyses=[],
                filter=lambda identifier: identifier.type == "cpu",
                method=lambda identifier, repo: repo.get_data(identifier) * 2,
            )
        ]
```

That version works because the built-in `SimpleAnalysisDriver` already serves the `SimpleAnalysis` type.

### 1. Define a custom analysis type

```python
from dataclasses import dataclass

from src.plugin_mgmt.plugins import Analysis

@dataclass(frozen=True)
class MultiplyAnalysis(Analysis):
    factor: int
```

### 2. Expose concrete analyses through an analysis plugin

```python
from src.plugin_mgmt.plugins import AnalysisPlugin

class ExampleAnalysisPlugin(AnalysisPlugin):
    def get_analyses(self):
        return [
            MultiplyAnalysis(
                name="double_value",
                prereq_analyses=[],
                factor=2,
            ),
            MultiplyAnalysis(
                name="triple_value",
                prereq_analyses=[],
                factor=3,
            ),
        ]
```

### 3. Implement the driver for that analysis type

```python
from src.data.data_repository import DataRepository
from src.data.identifier import AnalysisIdentifier
from src.plugin_mgmt.plugins import AnalysisDriverPlugin

class MultiplyAnalysisDriver(AnalysisDriverPlugin):
    SERVED_TYPE = MultiplyAnalysis

    def run_analysis(self, analysis, prog_data, config_section):
        data_repo: DataRepository = prog_data.data_repo

        for identifier in data_repo.get_ids():
            value = data_repo.get_data(identifier)
            if not isinstance(value, (int, float)):
                continue

            result_identifier = AnalysisIdentifier(identifier, analysis.name)
            data_repo.add(result_identifier, value * analysis.factor)
```

With those three pieces in place:

- the driver tells AutoMetrics how to execute `MultiplyAnalysis`
- the analysis plugin returns the concrete named analyses
- the config refers to `double_value` or `triple_value`, not to the plugin class name

## Minimal Saver

```python
import os

from src.plugin_mgmt.plugins import Saver

class ExampleSaver(Saver):
    def save(self, prog_data, config_section, base_path):
        os.makedirs(base_path, exist_ok=True)
        out_path = os.path.join(base_path, "example.txt")
        with open(out_path, "w", encoding="utf-8") as handle:
            handle.write(f"Stored {prog_data.data_repo.count()} items\n")
        return [out_path]
```

## Wiring A Plugin Into A Config

```yaml
period: lastmonth
ingest:
  run:
    - ExampleIngest
analysis:
  run:
    - double_value
saving:
  base-path: "./io/example"
  run:
    - ExampleSaver
```

Plugin-specific config is added as another top-level section:

```yaml
ExampleSaver:
  addtl-base: custom_subdir
```

## Loading And Naming Expectations

- `ingest.run` and `saving.run` entries must match plugin class names.
- `analysis.run` entries must match `Analysis.name`.
- Analysis dependencies are declared in `prereq_analyses`.
- Circular analysis dependencies are rejected during analysis ordering.

## Practical Advice

- Start by running `--verify-config`.
- Keep each plugin file focused on one concern.
- Prefer built-in drivers before inventing a new analysis type.
- When you need custom identifiers, make them frozen dataclasses with stable `__hash__`, `__eq__`, and `__str__`.
