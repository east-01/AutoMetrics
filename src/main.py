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

# Hides warnings for .fillna() calls
pd.set_option('future.no_silent_downcasting', True)

####################################
#region Initialization
####################################

print("Loading plugins...")
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

prog_data = ProgramData(plugins, args, config)

####################################
#endregion
####################################

prog_data.data_repo = DataRepository()

for ingest_plugin_name in prog_data.config["ingest"]:
    try:
        ingest_plugin = prog_data.loaded_plugins.get_ingest_plugin_by_name(ingest_plugin_name)
    except Exception as e:
        print(e)
        continue

    config_section = prog_data.config["ingest"][ingest_plugin_name]
    
    try:
        ingest_plugin.verify_config_section(config_section)
    except ConfigurationException as e:
        print(f"Failed to verify config section for ingest plugin \"{ingest_plugin_name}\": {e}")
        continue

    try:
        ingested_repo = ingest_plugin.ingest(prog_data, config_section)
        prog_data.data_repo.join(ingested_repo)
    except Exception as e:
        print(f"Ingest plugin \"{ingest_plugin_name}\" failed:")
        traceback.print_exc()        
        continue

prog_data.data_repo.print_contents()

print(f"Will perform analyses: {", ".join(prog_data.args.analysis_options)}")
print("")

# # Load DataFrames
# print("Starting ingest...")
# prog_data.data_repo = ingest(prog_data)
# # prog_data.data_repo = process_periods(prog_data.data_repo)
# prog_data.data_repo = generate_metadata(prog_data.data_repo, prog_data.config)

# if(has_overlaps(prog_data.data_repo)):
#     print("Error: The ingested DataRepository has overlapping timestamps for some of its SourceData. This is not allowed- if using FileSystem ingest try PromQL instead.")

# if(prog_data.args.verbose):
#     prog_data.data_repo.print_contents()
# print("")

# # Analyze dataframes
# print("Starting analysis...")
# analyze(prog_data)

# # Summarize analysis results
# if(can_summarize(prog_data)):
#     summarize(prog_data)
# print("")

# # Visualize analysis results
# print("Generating visualizations...")
# vizualize(prog_data)
# if(prog_data.args.verbose):
#     prog_data.data_repo.print_contents()
# print("")

# # Save output data, only if an out directory is specified
# out_dir = prog_data.args.outdir
# if(out_dir is not None):
#     print("Saving data...")    
#     if(not os.path.exists(out_dir)):
#         os.mkdir(out_dir)

#     for saver in [DataFrameSaver(prog_data), AnalysisSaver(prog_data), SummarySaver(prog_data), VizualizationsSaver(prog_data)]:
#         try:
#             saver.save()
#         except Exception as e:
#             print(f"Saving failed for saver \"{type(saver)}\": {e}")
#     print("")

# # Print summaries
# print_all_summaries(prog_data.data_repo)

# try:
#     import psutil
#     psutil_available = True
# except ImportError:
#     psutil_available = False

# if(psutil_available):
#     process = psutil.Process(os.getpid())
#     memory_info = process.memory_info()
#     print(f"\nMemory usage: {memory_info.rss / (1024 * 1024):.2f} MB")