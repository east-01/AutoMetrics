# Troubleshooting

## A Plugin Is Not Loading

Check:

- the file is under `./plugins`
- the file ends in `.py`
- the class subclasses one of the AutoMetrics base plugin classes
- the class can be instantiated without constructor arguments

Run:

```bash
python src/main.py ./configs/monthly.yaml --verify-config
```

The startup plugin summary is the first thing to inspect.

## A Config References A Plugin Name That Does Not Exist

`ingest.run` and `saving.run` must use plugin class names exactly. A common failure is copying a config from another repo without copying the matching plugin file.

## An Analysis Name Is Rejected

`analysis.run` entries must match `Analysis.name`, not the plugin class name.

Also check for:

- missing analysis plugin file
- typo in the analysis name
- analysis dependency cycles

## `--verify-config` Fails

Common causes:

- missing top-level `ingest`, `analysis`, or `saving` sections
- missing `run` list under one of those sections
- invalid `saving.exit-action`
- invalid plugin-specific config
- `timeline` present without `align`

## The Config Verifies But The Real Run Fails

That usually means verification passed, but runtime assumptions did not.

Examples:

- ingest plugin cannot reach its external data source
- an analysis expected identifiers that ingest never produced
- `MetaAnalysisDriver` needs timestamp identifiers and `IngestTimeline` was not run
- saver expected a certain result shape and got something else

## Output Is Empty Or Missing

Check:

- `saving.base-path`
- saver-specific `addtl-base`
- whether the selected analyses actually produced results
- whether `AnalysisSaver` is using a restrictive whitelist
- whether a saver logged an exception and continued

## Included Sample Config Does Not Run Standalone

That is expected for several configs in this repo. They demonstrate real AutoMetrics runs, but many rely on project-specific plugins that are not included here.

Use them to:

- inspect structure
- test `--verify-config` once your plugin set is installed
- copy patterns into your own configs
