import os
import subprocess
import sys
import pandas as pd
import traceback

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from src.analysis import get_analysis_order
from src.data.data_repository import DataRepository
from src.parameter_utils import ConfigurationException
from src.parameters import load_parameters
from src.plugin_mgmt.pluginloader import LoadedPlugins
from src.program_data import ProgramData

# Hides warnings for .fillna() calls
pd.set_option('future.no_silent_downcasting', True)

#region Initialization
print("### Loading plugins...")

plugins = LoadedPlugins()
plugins.print_details()

args, config = load_parameters()
print()

# Verify ConfigurablePlugin config sections
print("Verifying config sections...")

prog_data = ProgramData(plugins, args, config)

successes = 0
config_checks = 0
# Join the set of allowed types with the types in config to safely loop
for plugin_name in prog_data.loaded_plugins.loaded_plugin_names:
    try:
        plugin = prog_data.loaded_plugins.get_plugin_by_name(plugin_name)
    except Exception as e:
        print(e)
        continue
    
    config_section = None
    if(plugin_name in prog_data.config.keys()):
        config_section = prog_data.config[plugin_name]
    
    config_checks += 1
    try:
        plugin.verify_config_section(config_section)
        successes += 1
    except ConfigurationException as e:
        print(f"Failed to verify config section for plugin \"{plugin_name}\": {e}")
        continue

config_section = None # Clear from above use

if(successes != config_checks):
    print(f"WARNING: {successes}/{config_checks} configs valid.")
else:
    print(f"All configs valid.")

if(prog_data.args.verifyconfig):
    exit()

print()
#endregion

#region Ingest
print("### Ingesting data...")
prog_data.data_repo = DataRepository()

for ingest_plugin_name in prog_data.config["ingest"]["run"]:
    try:
        ingest_plugin = prog_data.loaded_plugins.get_plugin_by_name(ingest_plugin_name)
    except Exception as e:
        print(f"Failed to run ingest plugin named \"{ingest_plugin_name}\". {e}")
        continue

    ingest_config_section = None
    if(ingest_plugin_name in prog_data.config.keys()):
        ingest_config_section = prog_data.config[ingest_plugin_name]

    try:
        ingested_repo = ingest_plugin.ingest(prog_data, ingest_config_section)
        prog_data.data_repo.join(ingested_repo)
    except Exception as e:
        print(f"Ingest plugin \"{ingest_plugin_name}\" failed:")
        traceback.print_exc()        
        exit(2)

print()

if(args.verbose):
    prog_data.data_repo.print_contents()
#endregion

#region Analysis
print("### Analyzing...")
analysis_order = get_analysis_order(prog_data)

analysis_order_printable = ", ".join([analysis.name for analysis in analysis_order])
print(f"Analysis order: {analysis_order_printable}")

for analysis in analysis_order:
    driver = plugins.get_analysis_driver(type(analysis))

    try:
        config_section = prog_data.config[type(driver).__name__]
    except KeyError as e:
        # Check if the driver can handle not having config, if so we can skip passing it
        if(driver.verify_config_section(None)):
            config_section = None
        else:
            raise Exception(f"Analysis driver failed, it was expecting config but didn't get any. The driver \"{type(driver).__name__}\" is required because of analysis \"{analysis.name}\"")

    try:
        driver.run_analysis(analysis, prog_data, config_section)
    except Exception as e:
        print(f"Analysis driver plugin \"{type(driver).__name__}\" failed on analysis \"{analysis.name}\":")
        traceback.print_exc()
        exit(2)

print()

if(args.verbose):
    prog_data.data_repo.print_contents()
#endregion

#region Saving
print("### Saving...")
base_path = "./latest_run"
if("saving" in prog_data.config.keys() and "base-path" in prog_data.config["saving"].keys()):
    base_path = prog_data.config["saving"]["base-path"]
else:
    print(f"WARNING: Using default base path \"{base_path}\" for saving.")

all_saved_files = []
for saver_name in prog_data.config["saving"]["run"]:
    try:
        saver_plugin = prog_data.loaded_plugins.get_plugin_by_name(saver_name)
    except Exception as e:
        print(f"Failed to run saver plugin named \"{saver_name}\". {e}")
        continue

    saver_config_section = None
    if(saver_name in prog_data.config.keys()):
        saver_config_section = prog_data.config[saver_name]
    
    specific_base_path = base_path
    if(saver_config_section is not None and "addtl-base" in saver_config_section):
        specific_base_path = os.path.join(base_path, saver_config_section["addtl-base"])

    try:
        saved_files = saver_plugin.save(prog_data, saver_config_section, specific_base_path)
        if(saved_files is not None):
            all_saved_files.extend(saved_files)
    except Exception as e:
        print(f"Saver plugin \"{saver_name}\" failed:")
        traceback.print_exc()        
        print("Continuing saving...")
        continue

print()
#endregion

def open_file(path: str):
    if sys.platform.startswith("darwin"):  # macOS
        subprocess.run(["open", path])
    elif os.name == "nt":  # Windows
        os.startfile(path)  # type: ignore[attr-defined]
    elif os.name == "posix":  # Linux / Unix
        subprocess.run(["xdg-open", path])
    else:
        raise OSError(f"Unsupported platform: {sys.platform}")
    
if(args.exitaction == "openeach"):
    print(f"Exit action: opening each saved file.")
    for saved_file in all_saved_files:
        open_file(saved_file)
elif(args.exitaction == "opendir"):
    print("Exit action: opening directory.")
    open_file(os.path.abspath(base_path))

try:
    import psutil
    psutil_available = True
except ImportError:
    psutil_available = False

if(psutil_available):
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    print(f"Memory usage: {memory_info.rss / (1024 * 1024):.2f} MB")