# The ProgramData singleton holds program settings, data, and arguments. Any time a new ProgramData
#   class is created all of the same information can be accessed.
import pandas as pd

# from src.program_data.settings import settings
from src.program_data.arguments import load_arguments, verify_arguments, ArgumentException
from src.program_data.config import load_config, verify_config, ConfigurationException
from src.data.data_repository import DataRepository
from src.data.timeline import Timeline

class ProgramData():
    def __init__(self, loaded_plugins, args, config):
        
        # # Settings are truths about the program that shouldn't be mutable by the user
        # self.settings = settings

        self.loaded_plugins = loaded_plugins

        self.args = args
        try:
            verify_arguments(self)
        except ArgumentException as e:
            print(f"Invalid arguments: {e}")
            exit()

        self.config = config
        try:
            verify_config(self, self.config)
        except ConfigurationException as e:
            print(f"Invalid config: {e}")
            exit()

        self.timeline = Timeline(self.args.period[0], self.args.period[1])