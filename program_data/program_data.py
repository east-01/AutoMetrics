# The ProgramData singleton holds program settings, data, and arguments. Any time a new ProgramData
#   class is created all of the same information can be accessed.
import pandas as pd

from program_data.settings import settings
from program_data.arguments import load_arguments, verify_arguments
from program_data.config import load_config, verify_config

class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class ProgramData(metaclass=SingletonMeta):
    def __init__(self):
        
        # Settings are truths about the program that shouldn't be mutable by the user
        self.settings = settings

        self.args = load_arguments()
        verify_arguments(self)

        print(f"Will perform analyses: {", ".join(self.args.analysis_options)}")

        self.config = load_config()
        verify_config(self)
    
        self.data_repo = None # To be loaded with data_loader.py
        self.analysis_repo = None # To be loaded with analysis.py
        self.meta_analysis_repo = None # To be loaded with meta_analysis.py
        self.vis_repo = None # To be loaded with visualizations.py, same format as analysis_repo