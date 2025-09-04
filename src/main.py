import os
import sys
import pandas as pd
import traceback

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from src.plugin_mgmt.pluginloader import LoadedPlugins
from src.program_data.arguments import load_arguments, ArgumentException
from src.program_data.config import load_config
from src.program_data.program_data import ProgramData
from src.data.data_repository import DataRepository
from src.program_data.config import ConfigurationException
from src.analysis.analysis import get_analysis_order

# Hides warnings for .fillna() calls
pd.set_option('future.no_silent_downcasting', True)

#region Initialization
print("### Loading plugins...")
plugins = LoadedPlugins()
plugins.print_details()

try:
    args = load_arguments()
except ArgumentException as e:
    print(f"Invalid arguments: {e}")
    exit()

try:
    config = load_config(args.config)
except Exception as e:
    print(f"Failed to load config: {e}")
    exit()

print()

prog_data = ProgramData(plugins, args, config)

# Verify ConfigurablePlugin config sections
print("Verifying config sections...")
successes = 0
config_checks = 0
for plugin_type in ["ingest", "analysisdriver"]:
    for plugin_name in prog_data.config[plugin_type].keys():
        try:
            plugin = prog_data.loaded_plugins.get_plugin_by_name(plugin_type, plugin_name)
        except Exception as e:
            print(e)
            continue

        config_section = prog_data.config[plugin_type][plugin_name]
        
        config_checks += 1
        try:
            plugin.verify_config_section(config_section)
            successes += 1
        except ConfigurationException as e:
            print(f"Failed to verify config section for \"{plugin_type}\" plugin \"{plugin_name}\": {e}")
            continue

config_section = None # Clear from above use

if(successes != config_checks):
    print(f"WARNING: {successes}/{config_checks} configs valid.")
else:
    print(f"All configs valid.")

print()
#endregion

#region Ingest
print("### Ingesting data...")
prog_data.data_repo = DataRepository()

for ingest_plugin_name in prog_data.config["ingest"].keys():
    # We can safely do this, this is checked above when verifying ConfigurablePlugins
    ingest_plugin = prog_data.loaded_plugins.get_plugin_by_name("ingest", ingest_plugin_name)

    ingest_config_section = prog_data.config["ingest"][ingest_plugin_name]

    try:
        ingested_repo = ingest_plugin.ingest(prog_data, ingest_config_section)
        prog_data.data_repo.join(ingested_repo)
    except Exception as e:
        print(f"Ingest plugin \"{ingest_plugin_name}\" failed:")
        traceback.print_exc()        
        exit(2)

# prog_data.data_repo.print_contents()
print()
#endregion

#region Analysis
print("### Analyzing...")
analysis_order = get_analysis_order(prog_data)
analysis_order_printable = ", ".join([analysis.name for analysis in analysis_order])

print(f"Will perform analyses: {analysis_order_printable}")
for analysis in analysis_order:
    driver = plugins.get_analysis_driver(type(analysis))

    try:
        config_section = prog_data.config["analysisdriver"][type(driver).__name__]
    except KeyError as e:
        # Check if the driver can handle not having config, if so we can skip passing it
        if(driver.verify_config_section(None)):
            config_section = None
        else:
            raise Exception(f"Analysis driver failed, it was expecting config but didn't get any. The driver \"{type(driver).__name__}\" is required because of analysis \"{analysis.name}\"")

    try:
        driver.run_analysis(analysis, prog_data, config_section)
    except Exception as e:
        print(f"Analysis driver plugin \"{ingest_plugin_name}\" failed on analysis \"{analysis.name}\":")
        traceback.print_exc()        
        exit(2)

print()
#endregion

print("TODO: Saving")
prog_data.data_repo.print_contents(print_dfs=True)

try:
    import psutil
    psutil_available = True
except ImportError:
    psutil_available = False

if(psutil_available):
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    print(f"\nMemory usage: {memory_info.rss / (1024 * 1024):.2f} MB")