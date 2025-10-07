# Technical details

This document specifies the technical details for AutoMetrics, start here to understand how to write your own code for the program. This project was primarily developed along with [RCI Metrics](https://github.com/east-01/RCI-Metrics). See the repository for example configurations and plugin implementations.

There are three main phases to AutoMetric's lifecycle: collection (ingest), analysis, and visualization. 

The ingest phase will take data from other sources like a file system or API and collect it to a central [DataRepository](#datarepository). Once this step is complete, AutoMetrics should have all of the data it will need to perform it's analyses.

The analysis phase takes all of the raw data ingested from the various sources and performs calculations, verifications, and visualizations on it. This is the whole reason for the program: the flexible analysis of raw data. Implementations of Analyses can vary widely due to the flexibility of the [AnalysisDriverPlugin](#analysisdriverplugin) system.

Finally, the saving phase looks at what data you want to save and saves it to the file system. Savers are plugin based so you can save things to special places if you wanted to- like an S3 bucket.

## Table of Contents
* [Important structures](#important-structures)

  * [ProgramData](#programdata)
  * [Identifiers](#identifiers)
  * [DataRepository](#datarepository)
* [Plugins](#plugins)

  * [Configurable plugins](#configurable-plugins)
  * [IngestPlugin](#ingestplugin)
  * [Analysis](#analysis)
  * [AnalysisPlugin](#analysisplugin)
  * [AnalysisDriverPlugin](#analysisdriverplugin)
  * [Saver](#saver)


### Important structures

There are a couple data structures to keep in mind to understand how this program works.

#### ProgramData

The ProgramData gets loaded immediately after the plugins at the start of the program. It holds loaded plugins, arguments, configuration, and the central DataRepository. ProgramData exists to be passed around as a central reference to important objects.

#### Identifiers

An Identifier is a frozen dataclass (acting as a struct) that allows us to have a unique label for a piece of data in the DataRepository. It's a **key for data**, not the actual data itself.

The Identifier class can be extended to create new identifying information for a piece of data. For example, [RCI Metric's GrafanaIdentifier](https://github.com/east-01/RCI-Metrics/blob/master/rci_plugins/rci_identifiers.py) adds a type and query_cfg data points for additional information about the Grafana DataFrame.

#### DataRepository

The DataRepository holds all data for AutoMetrics, labeled with Identifiers. It can also store meta data with a data point in case you want to store anything that isn't the primary focus for this data point. An example use case for this is holding the readable version of the file name in meta data.

```
identifier = # Identifier for data point
data_repo: DataRepository = program_data.data_repo

data, metadata = data_repo.get(identifier)
print(f"Data point {identifier} has data: {data} and metadata: {metadata}")
```

You can also access data and metadata individually:

```
identifier = # Identifier for data point
data_repo: DataRepository = program_data.data_repo

data = data_repo.get_data(identifier)
metadata = data_repo.get_metadata(identifier)
print(f"Data point {identifier} has data: {data} and metadata: {metadata}")
```

## Plugins

How to use plugins is specified in the original README, but this version will explain how to write custom plugins.

### Configurable plugins

IngestPlugin, AnalysisDriverPlugin, and Savers are all configurable plugins. This means that they can have a special configuration section (specified in AutoMetric's configuration) which will be passed to each plugin as a dict named `config_section`. See the main README's "configurable plugins" section for more details and an example.

### IngestPlugin

The goal of IngestPlugins is to get data from external sources into AutoMetrics; for example, loading data files from the file system or polling them from a database. The IngestPlugin will create a DataRepository and populate it with data that it has ingested, once this DR is passed back AutoMetrics will combine this new DataRepository with the program's shared one. An IngestPlugin should have the following signature:

```
class IngestPlugin(ConfigurablePlugin):    
    # Optional config section verification
    def verify_config_section(self, config_section: dict):
        pass

    @abstractmethod
    def ingest(self, prog_data: ProgramData, config_section: dict) -> DataRepository:
        data_repo = DataRepository()
        
        # Ingest data

        return data_repo
```

### Analysis

The Analysis is the core of AutoMetrics, anything that extends from the Analysis class will work with the Analysis system; see [AnalysisPlugin](#analysisplugin) for how the instantiated Analysis objects get loaded in. Extending the Analysis class allows you to have more nuanced functionalities, see the builtin plugins' [SimpleAnalysis](https://github.com/east-01/AutoMetrics/blob/master/src/builtin_plugins/simple_analysis_driver.py) and [MetaAnalysis](https://github.com/east-01/AutoMetrics/blob/master/src/builtin_plugins/meta_analysis_driver.py) classes for examples.

These custom classes might need to be called in special ways at runtime, see [AnalysisDriverPlugin](#analysisdriverplugin) for how this is done. 

Each Analysis is defined by a unique name and a list of prerequisite analyses, the list of prerequisites will be completed before this analysis is called. These names are how they will be referred to in the program's arguments and configuration. This also means dependencies can arise- AutoMetrics will check for circular references on startup. **Note**: sometimes you can get a circular dependency if you have the list of prerequisites as `[a, b]` and then analysis `a` is a prerequisite of `b`. The Analysis class is a frozen dataclass which acts as a struct, this means that Analyses will be instantiated like this:

```
Analysis(
    name="ex_analaysis"
    prereq_analyses=["analysis1", "analysis2"]
)
```

### AnalysisPlugin

The AnalysisPlugin acts as a container for Analyses. Since Analyses are frozen dataclasses and can't be instantiated (and recognized) as objects in the global scope, we have to instantiate them in a list and return that instead. The AnalysisPlugin will have the following signature:

```
class AnalysisPlugin(ABC):
    @abstractmethod
    def get_analyses(self) -> list[Analysis]:
        # Create and return the list in "one line"
        return [
            Analysis(
                name="analysis1",
                prereq_analyses=None
            ),
            Analysis(
                name="analysis2",
                prereq_analyses=["analysis1"]
            )
        ]
```

### AnalysisDriverPlugin

The AnalysisDriverPlugin will serve a specific type of Analysis (like SimpleAnalysis or MetaAnalysis) with `SERVED_TYPE`. AnalysisDriverPlugins exist because each analysis method may require a different method signature or configuration; the AnalysisDriverPlugin specifies these. The AnalysisDriverPlugin will have the following signature:

```
class AnalysisDriverPlugin(ConfigurablePlugin):
    SERVED_TYPE: Type[Analysis] = None

    # Optional config section verification
    def verify_config_section(self, config_section: dict):
        pass

    @abstractmethod
    def run_analysis(self, analysis, prog_data: ProgramData, config_section: dict):
        data_repo: DataRepository = prog_data.data_repo

        # Run analysis, create Identifier and get data

        data_repo.add(identifier, data)
```

An example of a generalized AnalysisDriverPlugin is the builtin SimpleAnalysisDriver. Notice the SimpleAnalysis dataclass has a filter and a method: the filter acts as a DataRepository filter and will collect identifiers for this analysis to be performed on, the method will accept the identifiers and the DataRepository as parameters like so:

```
def analysis_method(identifier: Identifier, data_repo: DataRepository):
    pass
```

So, for SimpleAnalysis methods, they must follow the above signature and the SimpleAnalysisDriver will call analysis_method entering the returned data from the method into the program DataRepository. The SimpleAnalysis example works as a general case where we can filter out items from the DataRepository and apply a general method to them. See [RCI Metrics' SummaryDriver](https://github.com/east-01/RCI-Metrics/blob/master/rci_plugins/analyses/summary_driver.py) for an example of an AnalysisDriverPlugin that doesn't try to generalize but performs a specific purpose: generating a summary for the monthly.yaml configuration file.

### Saver

The Saver has full access to AutoMetric's DataRepository and can save whatever it want. The goal of a saver will be to save a specific type of thing: like analysis results to .csv files or visualizations to .png files. The Saver will have the following signature:

**Note**: Saver's have a special verify_config_section method that checks for an addtl-base definition. Make sure you call super().verify_config_section and verify addtl-base is there.

```
class Saver(ConfigurablePlugin):
    # Optional verify config section
    def verify_config_section(self, config_section):
        super().verify_config_section(self, config_section)
        pass

    @abstractmethod
    def save(self, prog_data: ProgramData, config_section: dict, base_path: str) -> list[str]:
        # Save data
        pass
```