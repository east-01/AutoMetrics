import os
import sys
import pandas as pd

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from src.program_data.program_data import load_std_prog_data
from src.data.ingest.ingest import ingest
from src.analysis.analysis import analyze
from src.visualization.visualizations import vizualize
from src.data.processors import *

# Hides warnings for .fillna() calls
pd.set_option('future.no_silent_downcasting', True)

prog_data = load_std_prog_data()
print("")

# Load DataFrames
prog_data.data_repo = ingest(prog_data)
prog_data.data_repo = process_periods(prog_data.data_repo)
prog_data.data_repo = generate_metadata(prog_data.data_repo, prog_data.config)
prog_data.data_repo.print_summary()
print("")

# Analyze dataframes
analyze(prog_data)
# prog_data.data_repo.print_summary()

# Visualize analysis results
vizualize(prog_data)
prog_data.data_repo.print_summary()

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