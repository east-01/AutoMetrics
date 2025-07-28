# The ProgramData singleton holds program settings, data, and arguments. Any time a new ProgramData
#   class is created all of the same information can be accessed.
import pandas as pd

# from src.program_data.settings import settings
from src.program_data.arguments import load_arguments, verify_arguments, ArgumentException
# from src.program_data.config import load_config, verify_config
from src.data.data_repository import DataRepository

class ProgramData():
    def __init__(self, args):
        
        # # Settings are truths about the program that shouldn't be mutable by the user
        # self.settings = settings

        self.args = args
        try:
            verify_arguments(self)
        except ArgumentException as e:
            print(f"Invalid arguments: {e}")
            exit()

        # self.config = config
        # verify_config(self)

        self.data_repo = DataRepository()

        print("TODO: program_data.py:43 generate timeline")
