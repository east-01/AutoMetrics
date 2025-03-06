import argparse
import time

from program_data.settings import settings

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
        return list(settings['analysis_options'].keys())

    options = analysis_options_str.split(",")
    for option in options:
        if(option not in settings['analysis_options'].keys()):
            print(f"Failed to parse analysis option list, \"{option}\" is not recognized as a valid option.")
            raise ValueError()
    return options

def load_arguments():
    """
    Using the argparse library, parse the command line arguments into usable data.
    """

    parser = argparse.ArgumentParser(prog='AutoTM', description='Auto Tide Metrics- Collect and visualize tide metrics')

    # These arguments will be populated if defaults arent provided
    # We could use default=__ here, but I want to be able to provide warnings in verify_arguments if necessary.
    parser.add_argument('analysis_options', type=parse_analysis_options, help="A list of analysis options separated by a comma (no spaces).")
    parser.add_argument('-p', '--period', dest='period', type=parse_time_range, help="A time range of the format <start>-<end> where your start and end times are UNIX timestamps.")

    parser.add_argument('-f', '--file', dest='file', type=str, help='A local file to be used instead of polling Prometheus.')
    parser.add_argument('-o', '--outdir', dest='outdir', type=str, help='The directory to send output files to.')
    # TODO: Input directory
    parser.add_argument('-v', dest='verbose', action='store_true', help="Enable verbose output.")

    return parser.parse_args()

def verify_arguments(prog_data):
    args = prog_data.args

    # Populate additional analyses to perform from requirements
    for to_perform in args.analysis_options:
        for requirement in prog_data.settings['analysis_options'][to_perform]["requires"]:
            if(requirement not in args.analysis_options):
                print(f"Added additional analysis \"{requirement}\" as it is a requirement of \"{to_perform}\"")
                args.analysis_options.append(requirement)

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