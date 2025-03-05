import os

from analysis import data_cleaning
from data_mgmt import data_frame_analysis, data_loader
from program_data import ProgramData
from analysis.analysis import analyze
import pandas as pd

# Hides warnings for .fillna() calls
pd.set_option('future.no_silent_downcasting', True)

prog_data = ProgramData()

# Load DataFrames
data_loader.load_data()

# Analyze dataframes
analyze()

# Save output data
prog_data.save()