# Technical details

There three main phases to AutoTM's lifecycle: collection, analysis, and visualization. 

## Important structures

There are a couple data structures to keep in mind to understand how this program works:

### ProgramData

The ProgramData class is a singleton object that holds *all* of the data that is used throughout the lifecycle of the program. The list of things inside ProgramData:
- Command line arguments (argparse.Namespace)
- config.yaml values (Dictionary)
- Settings (Dictionary- hard-coded values that shouldn't be mutable by the user)
- __DataRepository__ (DataRepository class)

### DataRepository

The DataRepository holds all data for AutoTM, labeled with specific Identifiers.

Identifier | Value type | Description
-----------|------------|------------
SourceIdentifier | DataFrame | Holds the Grafana DataFrames containing metrics data.
AnalysisIdentifier | object | Holds the result of an analysis, can be nested. For example the cpujobstotal AnalysisIdentifier holds the cpujobs AnalysisIdentifier.
VisIdentifier | matplotlib.Figure | Holds the figure representing an analysis.
SummaryIdentifier | tuple[DataFrame, DataFrame, DataFrame] | Holds summary DataFrames for a specific period.

## Program lifecycle

- Initialize ProgramData
  - Initializes arguments, config, and settings
- Start collection with `ingest`
  - Creates a DataRepository object
  - Gathers DataFrames from source (either PromQL or .csv)
- Start analysis with `analysis`
  - Perform each analysis on corresponding SourceIdentifier data.
- Summarize data if possible with `summarize`.
- Generate visualizations with `visualize`.
- Save output files if output directory is provided.
