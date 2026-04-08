# Local Plugins

Put project-specific AutoMetrics plugins in this directory.

## What Belongs Here

- ingest plugins for your data sources
- analysis plugins that define concrete analyses
- custom analysis drivers when the built-in drivers are not enough
- custom savers for special output targets

## Loading Rules

- AutoMetrics scans this directory recursively.
- Only `.py` files are inspected.
- Classes are loaded when they subclass one of the base plugin types in [`src/plugin_mgmt/plugins.py`](../src/plugin_mgmt/plugins.py).

## First Steps

1. Add your plugin file under this folder.
2. Reference the plugin class name or analysis name from your YAML config.
3. Run `python src/main.py <config> --verify-config`.

For examples and base class details, see:

- [`../docs/plugins.md`](../docs/plugins.md)
- [`../TechnicalDetails.md`](../TechnicalDetails.md)
