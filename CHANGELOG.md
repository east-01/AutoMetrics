# Changelog

All notable changes to **AutoMetrics** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),  
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [X.X.X] - Unreleased
### TODO
- Tests overhaul
- Add JupyterHub per-user hours

## [2.0.3] - 2025-10-28
### Added
- Advanced period parsing

### Removed
- Extra scripts, moved them to RCI-Metrics

### Fixed
- Saving problems for AnalysisSaver, added support for None identifiers.

## [2.0.2] - 2025-10-13
### Fixed
- Keying problems with meta analyses and aggregate analyses
- Timeline forcing sub-month long periods to a full month
- Mislabeles messages in main

## [2.0.1] - 2025-10-07
### Added
- Aggregate analysis for collecting multiple Analyses into one.
- Aggregate analysis driver to perform aggregate analyses.
- Exit actions: open the saved files or directory on program exit.

### Changed
- Updated TechnicalDetails.md document.

### Fixed
- The plugin loader will now follow symlinks.

## [2.0.0] - 2025-09-22
### Added
- Plugins: Each phase of AutoMetrics can support an arbitrary amount of custom plugins. The following plugins are:
    - IngestPlugin: Ingests data into AutoMetrics
    - AnalysisPlugin: Acts as a container for a list of analyses to load into AutoMetrics.
    - AnalysisDriver: Pairs with a specifc analysis type to perform more nuanced analyses.
    - Saver: Saves data from AutoMetrics to the file system.

### Changed
- Refactored codebase so there's only the main.py file interacting with plugins, increasing simplicity.
- Parameters: Program arguments and configuration are handled differently.
    - Configurations are set up to be created for each group of analyses you want to perform. See readme.
    - Program arguments supplement the configuration, arguments are able to override configuration.

### Removed
- Removed all RCI related code, converted them into plugins. Split into a new repository at [RCI Metrics](https://github.com/east-01/RCI-Metrics).
    - Changelog info for the same update to that code is 1.0.0 under RCI Metrics

## [1.1.4] - 2025-07-07
### Added
- New ingest system. Allows for multiple ingest sources of all kinds of data.

### Changed
- Upgrade argument parsing: subparsers and add_mutually_exclusive_group

### Fixed
- Bug with unix timestamp range
- Bug with vis gen

## [1.0.3] - 2025-06-25
### Added
- New analyses for available resource hours
- New meta-analysis 'utilization' to compare usage vs. availability

### Changed
- Visualizations to allow meta data usage

### Fixed
- README.md analyses example

## [1.0.2] - 2025-04-28
### Added
- Tests for hours analysis
- Tests for jobs analysis
- Message for empty top 5 CPU/GPU namespaces.
- Docstrings for analysis implementations

### Changed
- Refactored jobs analysis implementations for consistency.

### Fixed
- README.md output example
- Verification of file arguments is cleaner

## [1.0.1] - 2025-04-14
### Added
- Argument check for periods exceeding the current time.

### Changed
- Refactored analyze() to be clearer.

### Fixed
- README.md invalid command examples.

## [1.0.0] - 2025-04-10
### Added
- Initial release of AutoTM.
- Support for collecting data via PromQL or CSV file inputs.
- Analysis options for CPU/GPU hours, job counts, and total usage metrics.
- Visualization of metrics.
- Unit tests for core modules.
- README documentation covering usage, analysis types, CLI arguments, and configuration.