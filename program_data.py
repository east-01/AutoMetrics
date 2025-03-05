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
        self.settings = argparse.Namespace(
            type_options=['cpu', 'gpu', 'uniquens'],
            # A dictionary mapping a type option to the type that it appears as in the query
            type_strings={
                'cpu': 'cpu',
                'gpu': 'nvidia_com_gpu'
            },
            # The string in the query to be replaced with whatever type of data we're retrieving
            type_string_identifier="%TYPE_STRING%"
        )

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

        parser = argparse.ArgumentParser(prog='AutoTM', description='Auto Tide Metrics- Collect and visualize tide metrics')

        # Required arguments, these will be populated if defaults arent provided
        # We could use default=__ here, but I want to be able to provide warnings below if necessary
        parser.add_argument('-t', '--type', dest='type', type=str, help='The type of poll to perform')
        parser.add_argument('-p', '--period', dest='period', type=parse_time_range, help="A time range of the format <start>-<end> where your start and end times are UNIX timestamps.")

        parser.add_argument('-f', '--file', dest='file', type=str, help='A local file to be used instead of polling Prometheus.')

        # Optional arguments
        parser.add_argument('-o', '--outdir', dest='outdir', type=str, help='The directory to send output files to.')
        # TODO: Input directory
        parser.add_argument('-v', dest='verbose', action='store_true', help="Enable verbose output.")

        self.args = parser.parse_args()

    def verify_arguments(self):
        args = self.args

        warnings = []
        errors = []

        if(args.file is not None):
            # If the file exists, provide warnings about other arguments that won't be used
            if(args.type is not None or args.period is not None):
                warnings.append("Warning: You provided at least one argument [type/period] that is overridden by the --file flag. You may see a different output than what you we're expecting.")
        else:
            # Populate default arguments
            if(args.type is None):
                args.type = "gpu"
                warnings.append(f"Populating type argument with default \"{args.type}\"")
            if(args.period is None):
                # Gets current UNIX timestamp as an integer
                now = int(time.time())
                args.period = (now-60*60, now)
                warnings.append(f"Populating time period argument with default \"{args.period}\"")

        if(args.type not in self.settings.type_options):
            errors.append(f"The data type \"{args.type}\" is not valid. Options: {self.settings.type_options}")

        # Print warnings/errors and exit if necessary
        for warning in warnings:
            print(warning)

        if(len(errors) > 0):
            print(f"{len(errors)} error(s) with arguments:")
            for error in errors:
                print(f" - {error}")
            print("Exiting...")
            exit(1)

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

        if(self.settings.type_string_identifier not in self.config["query"]):
            print(f"The query (as specified in the configuration) doesn't have the type string identifier \"{self.settings.type_string_identifier}\" in it. Exiting.")
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
                    with open(path, "w") as file:
                        file.write(f"{analysis}: {str(result)}\n")