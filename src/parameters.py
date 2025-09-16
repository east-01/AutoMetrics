import argparse
import time
import os
import yaml
import traceback

from src.parameter_utils import parse_time_range, parse_analysis_options, ConfigurationException, ArgumentException

def load_parameters():
    try:
        args = load_arguments()
    except ArgumentException as e:
        print(f"Invalid arguments: {e}")
        exit()

    try:
        config = load_config(args.config)
    except Exception as e:
        print(f"Failed to load config: {e}")
        if(args.verbose):
            traceback.print_exc()
        exit()

    install_config(config, args)

    return args, config

def load_arguments():
    """
    Using the argparse library, parse the command line arguments into usable data.
    """

    parser = argparse.ArgumentParser(prog='AutoTM', description='Auto Tide Metrics- Collect and visualize tide metrics')
    parser.add_argument("config", default="./config.yaml", type=str, help="The location of the config file to use.")
    parser.add_argument('-p', '--period', dest='period', type=parse_time_range, help="A time range of the format <start>-<end> where your start and end times are UNIX timestamps.")
    parser.add_argument('-a', '--analyses', dest='analysis_options', type=parse_analysis_options, help="A list of analysis options separated by a comma (no spaces).")
    parser.add_argument('-v', dest='verbose', action='store_true', help="Enable verbose output.")
    parser.add_argument('--verify-config', dest="verifyconfig", action='store_true', help='Load plugins and check their configurations, early exit.')

    return parser.parse_args()

def verify_arguments(prog_data):
    args = prog_data.args

    # Verify analysis arguments exist
    if(not isinstance(args.analysis_options, list)):
        raise ArgumentException("Analysis options is not a list.")

    analyses = prog_data.loaded_plugins.analyses

    if(len(args.analysis_options) == 1 and args.analysis_options[0] == "all"):
        args.analysis_options = [analysis.name for analysis in analyses]

    for analysis_option in args.analysis_options:
        try:
            prog_data.loaded_plugins.get_analysis_by_name(analysis_option)
        except Exception as e:
            raise ArgumentException(f"Failed to parse analysis option list, \"{analysis_option}\" is not recognized as loaded analysis option.")

    if(args.period is not None):
        now = int(time.time())
        if(args.period[0] > now or args.period[1] > now):
            raise ArgumentException("Either the start or end times of the period exceeds current time.")

def load_config(config_location = "./config.yaml"):
    if(not os.path.isfile(config_location)):
        print(f"Error: The config file \"{config_location}\" doesn't exist. Exiting...")
        exit(1)

    try:
        # Load the YAML file
        with open(config_location, 'r') as file:
            config = yaml.safe_load(file)

        # Ensure the YAML was parsed correctly
        if not isinstance(config, dict):
            raise ValueError("Invalid YAML format. Expected a dictionary structure.")

        return config

    except yaml.YAMLError as e:
        # Catch and handle YAML syntax errors
        print(f"Error: YAML syntax issue in the config file. Details: {e}")
    except KeyError as e:
        # Handle missing keys in the YAML file
        print(f"Error: Missing expected key in the config file: {e}")
    except ValueError as e:
        # Handle any value errors
        print(f"Error: {e}")

def verify_config(prog_data, config):
    def check_phase_section(name, desc):
        if(name not in config):
            raise ConfigurationException(f"{desc} not configured. Make sure run config includes \"{name}\" as a top level section.")
        if("run" not in config[name]):
            raise ConfigurationException(f"{desc} \"run\" section not configured. Make sure run config includes \"{name}.run\" as a section, with a list of plugins.")

    check_phase_section("ingest", "Ingest controllers")
    check_phase_section("analysis", "Analyses")
    check_phase_section("saving", "Saving")
    
def install_config(config, args):
    """ Install the config onto the arguments object, replacing missing values with ones from the 
            config, like period."""
    
    if(args.period is None):
        if("period" not in config.keys()):
            raise ConfigurationException(f"There was no period provided in arguments, and it isn't present in the config. Specify the period in either config or arguments.")
        else:
            args.period = parse_time_range(config["period"])

    if(args.analysis_options is None):
        if("analysis" not in config.keys()):
            raise ConfigurationException(f"There was no provided analyses in arguments, and they aren't present in the config. Specify the analysis options in either config under analyses.run or arguments.")
        elif("run" not in config["analysis"].keys()):
            raise ConfigurationException(f"There was no provided analyses in arguments, and they aren't present in the config. Specify the analysis options in either config under analyses.run or arguments.")
        else:
            args.analysis_options = config["analysis"]["run"]