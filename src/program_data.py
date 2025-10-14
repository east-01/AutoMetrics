# The ProgramData singleton holds program settings, data, and arguments. Any time a new ProgramData
#   class is created all of the same information can be accessed.
import pandas as pd

# from src.settings import settings
from src.parameter_utils import ConfigurationException
from src.parameters import ArgumentException, verify_arguments, verify_config
from src.data.timeline import Timeline, TIMELINE_SECTION_NAME

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

        timeline_conf = dict()
        if(TIMELINE_SECTION_NAME in self.config.keys()):
            timeline_conf = self.config[TIMELINE_SECTION_NAME]
            
        self.timeline = Timeline(timeline_conf, self.args.period[0], self.args.period[1])