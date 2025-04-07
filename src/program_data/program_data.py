# The ProgramData singleton holds program settings, data, and arguments. Any time a new ProgramData
#   class is created all of the same information can be accessed.
import pandas as pd

from program_data.settings import settings
from program_data.arguments import load_arguments, verify_arguments
from program_data.config import load_config, verify_config
from data.data_repository import DataRepository

def load_std_prog_data():
    """
    Loads the ProgramData in the context of a standard running program.
    """
    return ProgramData(load_arguments(), load_config())

class ProgramData():
    def __init__(self, args, config):
        
        # Settings are truths about the program that shouldn't be mutable by the user
        self.settings = settings

        self.args = args
        verify_arguments(self)

        print(f"Will perform analyses: {", ".join(self.args.analysis_options)}")

        self.config = config
        verify_config(self)
    
        self.data_repo = DataRepository()
