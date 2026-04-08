# CLI Reference

AutoMetrics is launched from the repository root:

```bash
python src/main.py <configuration>
```

The argparse program name is `AutoMetrics`, so that is what you will see in `--help` output.

## Arguments

| Argument | Description |
|---|---|
| `config` | Path to the YAML config file. |
| `-p`, `--period` | Override the config period. |
| `-a`, `--analyses` | Override `analysis.run` with a comma-separated list of analysis names. |
| `-v` | Enable verbose console output. |
| `--verify-config` | Load plugins, parse config, verify plugin config sections, print the timeline and analysis order, then exit. |
| `--exit-action` | Override `saving.exit-action` with `none`, `openeach`, or `opendir`. |

## Examples

Validate a config:

```bash
python src/main.py ./configs/monthly.yaml --verify-config
```

Override the period:

```bash
python src/main.py ./configs/monthly.yaml --period January26
```

Run only selected analyses:

```bash
python src/main.py ./configs/monthly.yaml --analyses summary,viscpuhours
```

Show verbose repository output:

```bash
python src/main.py ./configs/monthly.yaml -v
```

Open the output directory after saving:

```bash
python src/main.py ./configs/monthly.yaml --exit-action opendir
```

## What `--verify-config` Actually Checks

`--verify-config` is the best first command when you are wiring up plugins. It does all of the following:

- loads plugins from `./plugins` and `./src/builtin_plugins`
- parses the CLI and YAML config
- verifies runtime sections
- verifies each configurable plugin section with `verify_config_section()`
- builds the timeline
- resolves and prints analysis execution order

It exits before ingest, analysis, saving, and exit-action behavior.

## Exit Codes And Behavior

- Invalid arguments or invalid config cause an early exit.
- Ingest and analysis failures terminate the run.
- Saver failures are logged and the program continues to the next saver.
