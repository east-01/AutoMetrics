# Built-In Plugins

This repository includes the runtime plus a small set of built-in ingest, analysis-driver, and saver plugins.

## Ingest

`IngestTimeline`

- Type: `IngestPlugin`
- Purpose: injects one `TimeStampIdentifier` per timeline main period into the repository
- Config: none
- Use when: later analyses need timeline periods present in the `DataRepository`

## Analysis Drivers

`SimpleAnalysisDriver`

- Serves: `SimpleAnalysis`
- Behavior: filters identifiers, runs a method for each match, stores results as `AnalysisIdentifier`
- Config: none

`MetaAnalysisDriver`

- Serves: `MetaAnalysis`
- Behavior: creates per-period tables from prerequisite analyses and stores them as `MetaAnalysisIdentifier`
- Config: none
- Important dependency: expects timestamp identifiers, which usually means `IngestTimeline` must run

`AggregateAnalysisDriver`

- Serves: `AggregateAnalysis`
- Behavior: groups identifiers by a key and stores one aggregate result per key
- Config: none

`VerificationDriver`

- Serves: `VerificationAnalysis`
- Behavior: validates prior analysis results and raises if a verification fails
- Config: none
- Output: verification results are not stored in the repository

`VisualAnalysisDriver`

- Serves: visual analysis dataclasses from [`src/builtin_plugins/vis_dataclasses.py`](../src/builtin_plugins/vis_dataclasses.py)
- Behavior: converts analysis DataFrames into matplotlib figures and stores them as visualization identifiers
- Config: none

## Savers

`AnalysisSaver`

- Saves analysis outputs to files under the effective base path
- DataFrame results become `.csv`
- other results are appended to `text_results.txt`
- Optional config:

```yaml
AnalysisSaver:
  whitelist:
    - summary
    - usedcapacity
```

`VizualizationsSaver`

- Saves generated matplotlib figures as `.png`
- Config: default saver config only, including optional `addtl-base`

`EmailSaver`

- Zips the output directory and emails it
- Current state: implementation is hard-coded and not production-ready
- Config verification is not implemented
- Treat as a project-specific starting point rather than a polished built-in

## Output Locations

The effective output directory starts with `saving.base-path`.

If a saver config includes:

```yaml
SaverName:
  addtl-base: reports
```

that saver writes under `<base-path>/reports`.

Typical output patterns:

- `AnalysisSaver`: CSV files plus `text_results.txt`
- `VizualizationsSaver`: PNG files
- `EmailSaver`: a zip file written next to the base output directory before sending

## Important Limitation

The built-in code does not define your domain-specific ingest controllers or concrete analyses. Those still need to come from local plugins or a companion repository.
