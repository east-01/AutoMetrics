import os

from program_data.program_data import ProgramData
from program_data.saver import save
from data_mgmt.data_loader import load_data
from analysis.analysis import analyze
import pandas as pd

# Hides warnings for .fillna() calls
pd.set_option('future.no_silent_downcasting', True)

prog_data = ProgramData()

# Load DataFrames
load_data()

# Analyze dataframes
analyze()

# Save output data
save(prog_data)