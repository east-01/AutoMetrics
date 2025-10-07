# AutoMetrics

A Python script that facilitates the process of collecting, analyzing, and visualizing data. Uses a plugin based system where new code can be dropped into the plugins folder to be used by itself or with other plugins. Has three phases: Ingesting data -> Analysing data -> Saving results; with plugins for each phase of the process.

If you're interested in writing your own plugins for AutoMetrics see the [Technical Details](https://github.com/east-01/AutoMetrics/blob/master/TechnicalDetails.md) document.

This project was primarily developed along with [RCI Metrics](https://github.com/east-01/RCI-Metrics). See the repository for example configurations and plugin implementations.

## Installation

The installation instructions assume that you have:
- Python 3.12.6 or later

1. Clone the repository to your local directory with `git clone https://github.com/east-01/AutoMetrics.git`.
2. Install the requirements with `pip install -r <path_to_repo>\requirements.txt`.
3. After everything installs, AutoMetrics will be ready for use.

## Plugins

Plugins are automatically loaded from the `./plugins` directory. All python files will be searched, if any file contains a class (or multiple classes) that extends one of the plugins in `src/plugin_mgmt/plugins.py` that class will be loaded as it's plugin type.

Plugins are the first thing that are loaded in the program, it will show a list of all loaded plugins- if something isn't working check if all of your plugins are there.

Ensure your plugins are configured properly, see [configurable plugins](#configurable-plugins) for details.

## Usage

AutoMetrics is run from the command line, the base version can be run with:

```
python src/main.py <configuration>
```

Where \<configuration\> is the .yaml configuration file that specifies how AutoMetrics will run. See [Configurations](#configurations) for details.

The base version doesn't do much. Install [plugins](#plugins) to get advanced functionality.

### Configurations

The configuration is a .yaml file specifying how AutoMetrics will run. They're set up so you can create multiple .yaml files, one for each computation you'd like. For example, the [RCI Metrics](https://github.com/east-01/RCI-Metrics) project has a "monthly.yaml" configuration and a "tidesplit.yaml" configuration covering two groups of analyses.

The configuration has two main sections: 
1. The runtime config section that specifies what plugins and analyses will be used. 
2. The plugin-specific config section that passes configuration through to the plugins.

#### Runtime configuration

Here is an example of the runtime configuration:

```
period: MonthYR
ingest:
  run:
    - <Ingest>
analysis:
  run:
    - <Analysis>
saving:
  base-path: "./latest"
  run:
    - <Saver>
```

**period**: _Can be overridden in arguments._ Specifies the period for the configuration to run over. You can use one of the following formats:

Format | Example
-------|---------
Year | -p 2024
MonthYear | -p January25
MonthYear range | -p January25-March25
Unix timestamp range | -p 1738396800-1740815999

**ingest**: Has a single sub-section, run, which is a list of IngestPlugins to run. See [Plugins](#plugins) for details.

**analysis**: _Can be overridden in arguments._ Has a single sub-section, run, which is a list of Analyses to perform. See [Plugins](#plugins) for details.

**saving**: 
- **base-path**: Specifies the base path for all files to be saved to; Saver plugins also have an "addtl-base" section, meaning a filepath for a specific Saver plugin can look like `<base-path>/<addtl-base>/`.
- **exit-action**: _Can be overridden in arguments._ The action to take once AutoMetrics finishes running. Options are: `[none, openeach, opendir]`. `openeach` opens each file individually, `opendir` opens the directory.
- **run**: A list of Saver plugins to run. See [Plugins](#plugins) for details.

#### Configurable plugins

IngestPlugins, AnalysisDriverPlugins, and Saver plugins all are configurable, meaning config you specify in this section will be passed through to those plugins through the config_section dictionary variable when it is run.

To specify configuration for a specific plugin, you must specify the plugin name as the top level section, then any plugin-specific config can go under that section. Plugins should have readme documentation for their plugins' special configurations.

An example plugin specific config from [RCI Metrics](https://github.com/east-01/RCI-Metrics):
```
PromQLIngestController:
  main-periods: false
  query-cfgs:
    - monthly
```

### Command line arguments

Command line arguments are for quick overrides of configuration parameters. The base command:

```
python src/main.py <configuration>
```

Argument | Description | Example usage
---------|-------------|--------------
configuration | The path to the .yaml configuration file for the program. | "./configs/monthly.yaml"
-p/--period | Override the period parameter in the configuration. See [Runtime configuration](#runtime-configuration) for details. | -p January25
-a/--analyses | Override the analysis run list in the configuration, takes a list of analysis names separated by a comma with no spaces. | -a viscpuhours,summary 
-v | Verbose messaging in the console. | -v
--verify-config | Don't run the entire program, just load plugins and check if the configuration is valid. | --verify-config
--exit-action | The action to take once AutoMetrics finishes running. Options are: `[none, openeach, opendir]` | --exit-action openeach