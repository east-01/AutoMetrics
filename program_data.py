# The ProgramData singleton holds program settings, data, and arguments. Any time a new ProgramData
#   class is created all of the same information can be accessed.
import os
import argparse
import time
import pandas as pd

# pip install pyyaml
import yaml

from timeutils import get_range_printable

class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class ProgramData(metaclass=SingletonMeta):
    def __init__(self):
        
        # Settings are truths about the program that shouldn't be mutable by the user
        self.settings = {
            "type_options": ["cpu", "gpu"],
            # A dictionary mapping a type option to the type that it appears as in the query
            "type_strings": {
                "cpu": "cpu",
                "gpu": "nvidia_com_gpu"
            },
            # The string in the query to be replaced with whatever type of data we're retrieving
            "type_string_identifier": "%TYPE_STRING%",
            # Analysis options, the types are the required types to perform the analysis.
            # Methods are filled out by analysis.py on the analysis() call
            # Requirements are fulfilled in the analysis() call
            "analysis_options": {
                "cpuhours": {
                    "types": ["cpu"],
                    "requires": [],
                    "method": None
                },
                "cpuhourstotal": {
                    "types": ["cpu"],
                    "requires": ["cpuhours"],
                    "method": None
                },
                "cpujobs": {
                    "types": ["cpu"],
                    "requires": ["gpujobs"],
                    "method": None
                },
                "gpuhours": {
                    "types": ["gpu"],
                    "requires": [],
                    "method": None
                },
                "gpuhourstotal": {
                    "types": ["gpu"],
                    "requires": ["gpuhours"],
                    "method": None
                },
                "gpujobs": {
                    "types": ["gpu"],
                    "requires": [],
                    "method": None,
                },
                "uniquens": {
                    "types": ["cpu", "gpu"],
                    "requires": [],
                    "method": None
                }
            }
        }

        self.load_arguments()
        self.verify_arguments()

        self.load_config()
        self.verify_config()
    
        self.data_repo = None # To be loaded with data_loader.py
        self.analysis_repo = None # To be loaded with analyzsis.py

    def load_arguments(self):
        """
        Using the argparse library, parse the command line arguments into usable data.
        """

        def is_integer(value):
            """
            Ensure a python value is either a true integer or an integer string.
            """
            if isinstance(value, int):
                return True
            if isinstance(value, str):
                return value.isdigit() or (value.startswith('-') and value[1:].isdigit())
            return False

        def parse_time_range(time_range_str):
            """
            Parse a time range with the format <start>-<end> with both the start and end times being
            UNIX Timestamps.
            """
            # Ensure delimiter exists
            if('-' not in time_range_str):
                print(f"Failed to parse time range string \"{time_range_str}\" it doesn't have the \"-\" required for splitting into start and end time.")
                raise ValueError()
            
            # Split the argument and ensure beginning and end are integers
            time_range_arr = time_range_str.split('-')
            if(not is_integer(time_range_arr[0]) or not is_integer(time_range_arr[1])):
                print(f"Failed to parse time range string \"{time_range_str}\" either the start or end time failed to parse as Integer.")
                raise ValueError()
            
            return (int(time_range_arr[0]), int(time_range_arr[1]))

        def parse_analysis_options(analysis_options_str):
            if(analysis_options_str == "all"):
                return list(self.settings['analysis_options'].keys())

            options = analysis_options_str.split(",")
            for option in options:
                if(option not in self.settings['analysis_options'].keys()):
                    print(f"Failed to parse analysis option list, \"{option}\" is not recognized as a valid option.")
                    raise ValueError()
            return options

        parser = argparse.ArgumentParser(prog='AutoTM', description='Auto Tide Metrics- Collect and visualize tide metrics')

        # These arguments will be populated if defaults arent provided
        # We could use default=__ here, but I want to be able to provide warnings in verify_arguments if necessary.
        parser.add_argument('analysis_options', type=parse_analysis_options, help="A list of analysis options separated by a comma (no spaces).")
        parser.add_argument('-p', '--period', dest='period', type=parse_time_range, help="A time range of the format <start>-<end> where your start and end times are UNIX timestamps.")

        parser.add_argument('-f', '--file', dest='file', type=str, help='A local file to be used instead of polling Prometheus.')
        parser.add_argument('-o', '--outdir', dest='outdir', type=str, help='The directory to send output files to.')
        # TODO: Input directory
        parser.add_argument('-v', dest='verbose', action='store_true', help="Enable verbose output.")

        self.args = parser.parse_args()

    def verify_arguments(self):
        args = self.args

        # Populate additional analyses to perform from requirements
        for to_perform in self.args.analysis_options:
            for requirement in self.settings['analysis_options'][to_perform]["requires"]:
                if(requirement not in self.args.analysis_options):
                    print(f"Added additional analysis \"{requirement}\" as it is a requirement of \"{to_perform}\"")
                    self.args.analysis_options.append(requirement)

        print(f"Will perform analyses: {", ".join(self.args.analysis_options)}")

        if(args.file is not None):
            # If the file exists, provide warnings about other arguments that won't be used
            if(args.period is not None):
                print("Warning: You provided at least one argument [type/period] that is overridden by the --file flag. You may see a different output than what you we're expecting.")
        else:
            if(args.period is None):
                # Gets current UNIX timestamp as an integer
                now = int(time.time())
                args.period = (now-60*60, now)
                print(f"Populating time period argument with default \"{args.period}\"")

    def load_config(self):
        config_file = "./config.yaml"

        if(not os.path.isfile(config_file)):
            print(f"Error: The config file \"{config}\" doesn't exist. Exiting...")
            exit(1)

        try:
            # Load the YAML file
            with open(config_file, 'r') as file:
                config = yaml.safe_load(file)

            # Ensure the YAML was parsed correctly
            if not isinstance(config, dict):
                raise ValueError("Invalid YAML format. Expected a dictionary structure.")

            self.config = config

        except yaml.YAMLError as e:
            # Catch and handle YAML syntax errors
            print(f"Error: YAML syntax issue in the config file. Details: {e}")
        except KeyError as e:
            # Handle missing keys in the YAML file
            print(f"Error: Missing expected key in the config file: {e}")
        except ValueError as e:
            # Handle any value errors
            print(f"Error: {e}")
    
    def verify_config(self):
        if(self.config is None):
            print("Failed to load configuration. Exiting.")
            exit(1)

        # A list of keys to ensure they: exist in config, have a value
        keys_to_check = ["base_url", "query", "step"]

        for key_to_check in keys_to_check:
            if(key_to_check not in self.config.keys() or len(self.config[key_to_check]) == 0):
                print(f"Failed to load configuration. Key \"{key_to_check}\" either doesn't exist in config or has no value. Exiting.")
                exit(1)

        if(self.settings['type_string_identifier'] not in self.config["query"]):
            print(f"The query (as specified in the configuration) doesn't have the type string identifier \"{self.settings['type_string_identifier']}\" in it. Exiting.")
            exit(1)

        return
    
    def save(self):
        # Only save if an out directory is specified
        if(self.args.outdir is None):
            return

        # Ensure out directory is created
        outdir = self.args.outdir
        if(not os.path.exists(outdir)):
            os.mkdir(outdir)

        print(f"Saving output to \"{outdir}\"")

        data_blocks = self.data_repo.data_blocks

        # Save DataFrames
        for identifier in data_blocks.keys():
            data_block = data_blocks[identifier]
            df = data_block['data']

            # Convert the readable_period into a string thats saveable by the file system
            df_path = os.path.join(outdir, f"{data_block['out_file_name']}.csv")
            print(f"  Saving DataFrame file \"{df_path}\"")

            df.to_csv(df_path, index=False)

        # Keep a list of files we've written to so we can clear the contents previously existing files
        has_written = []

        # Save analysis results
        for identifier in data_blocks.keys():
            data_block = data_blocks[identifier] 

            # Make sure we have results to save
            analysis_results = self.analysis_repo[identifier]
            if(len(analysis_results) == 0):
                print(f"Warning: No analysis results were created for data_block {data_block['out_file_name']}")
                continue

            # Make sure the directory holding these results is there
            analysis_dir_path = os.path.join(outdir, f"{data_block['out_file_name']} analysis")
            if(not os.path.exists(analysis_dir_path)):
                os.mkdir(analysis_dir_path)

            for analysis in analysis_results.keys():
                result = analysis_results[analysis]

                # Only save results that exist
                if(result is None):
                    continue

                # Save result to CSV if it's a dataframe, save to text file otherwise
                if(isinstance(result, pd.DataFrame)):
                    path = os.path.join(analysis_dir_path, f"{analysis}.csv")
                    print(f"  Saving analysis file \"{path}\"")
                    result.to_csv(path, index=False)
                else:
                    path = os.path.join(analysis_dir_path, f"text_results.txt")
                    print(f"  Saving analysis {analysis} to text results file.")

                    contents = ""
                    if(path in has_written):
                        with open(path, "r") as file:
                            contents = file.read()

                    with open(path, "w") as file:
                        if(len(contents) > 0):
                            contents += "\n"
                        contents += f"{analysis}: {str(result)}"
                        file.write(contents)

                    if(path not in has_written):
                        has_written.append(path)