import os

from program_data.program_data import ProgramData
from program_data.saving.summary_saver import SummarySaver
from program_data.saving.dataframe_saver import DataFrameSaver
from program_data.saving.analysis_saver import AnalysisSaver
from program_data.saving.vis_saver import VizualizationsSaver
from data_mgmt.data_loader import load_data
from analysis.analysis import analyze
from analysis.meta_analysis import metaanalyze
from visualization.visualizations import vizualize
import pandas as pd

# Hides warnings for .fillna() calls
pd.set_option('future.no_silent_downcasting', True)

prog_data = ProgramData()

# Load DataFrames
load_data()

# Analyze dataframes
analyze()
metaanalyze()

# Visualize analysis results
vizualize()

# Manually visualize meta analysis

# Save output data
savers = [SummarySaver(), DataFrameSaver(), AnalysisSaver(), VizualizationsSaver()]

# Only save if an out directory is specified
out_dir = ProgramData().args.outdir
if(out_dir is not None):
    if(not os.path.exists(out_dir)):
        os.mkdir(out_dir)

    for saver in savers:
        saver.save()

if(savers[0].can_summarize):
    savers[0].print_all_summaries()    