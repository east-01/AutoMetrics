# Changelog

All notable changes to **AutoTM (Tide Metrics Automation)** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),  
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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