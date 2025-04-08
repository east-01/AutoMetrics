import os
import sys
import pandas as pd

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from src.program_data.program_data import ProgramData, load_std_prog_data
from src.data.ingest.ingest import ingest
from src.analysis.analysis import analyze
from src.analysis.meta_analysis import metaanalyze
from src.visualization.visualizations import vizualize

# Hides warnings for .fillna() calls
pd.set_option('future.no_silent_downcasting', True)

prog_data = load_std_prog_data()

# Load DataFrames
prog_data.data_repo = ingest(prog_data)
prog_data.data_repo.print_summary()

print("WARNING: Code will NOT work until the period filter is applied to the data repository. Notes about it in main.py")
# TODO: Apply period filter- adjust periods so they fill out time slots
# Instead of inferring the time period here, we should look at all time periods and fix their
#   start and end times to the closest checkpoints. Like this:
# month_st=0, df_st=12, df_et=30, month_et=45 -> month_st=df_st=0, month_et=df_et=45
# TODO: Add to SourceIdentifier's metadatas the following info:
# # Load readable period data at the end of all data loading; readable_period may be affected by 
# #   other DF names so we need to load it last.
# for data_block in data_repo.data_blocks.values():
#     start_ts, end_ts = data_block['period']
#     data_block['readable_period'] = get_range_printable(start_ts, end_ts, prog_data.config['step'])
#     fs_compat_name = data_block['readable_period'].replace("/", "_").replace(" ", "T").replace(":", "")
#     data_block['out_file_name'] = f"{data_block['type']}-{fs_compat_name}"

# Analyze dataframes
analyze(prog_data)
prog_data.data_repo.print_summary()

# Visualize analysis results
vizualize()

# Manually visualize meta analysis

# Save output data
# savers = [SummarySaver(), DataFrameSaver(), AnalysisSaver(), VizualizationsSaver()]

# Only save if an out directory is specified
# out_dir = ProgramData().args.outdir
# if(out_dir is not None):
#     if(not os.path.exists(out_dir)):
#         os.mkdir(out_dir)

#     for saver in savers:
#         saver.save()

# if(savers[0].can_summarize):
#     savers[0].print_all_summaries()    