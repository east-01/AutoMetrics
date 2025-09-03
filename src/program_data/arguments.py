import argparse
import time
import os
import datetime

from src.utils.timeutils import get_unix_timestamp_range

def load_arguments():
    """
    Using the argparse library, parse the command line arguments into usable data.
    """

    parser = argparse.ArgumentParser(prog='AutoTM', description='Auto Tide Metrics- Collect and visualize tide metrics')

    # These arguments will be populated if defaults arent provided
    # We could use default=__ here, but I want to be able to provide warnings in verify_arguments if necessary.
    parser.add_argument('analysis_options', type=parse_analysis_options, help="A list of analysis options separated by a comma (no spaces).")

    # Ingest options
    ingest_group = parser.add_argument_group("Ingest options", "Options for reading data")
    group = ingest_group.add_mutually_exclusive_group(required=True)
    group.add_argument('-p', '--period', dest='period', type=parse_time_range, help="A time range of the format <start>-<end> where your start and end times are UNIX timestamps.")
    group.add_argument('-f', '--file', dest='file', type=parse_file_list, help="A local file/directory to be used instead of polling Prometheus.")
    ingest_group.add_argument('-u', '--users', dest='users', action='store_true', help="Ingest users from JupyterHub sources specified in config.")

    # Output options
    output_group = parser.add_argument_group("Output options", "Options for data output")
    output_group.add_argument('-o', '--outdir', dest='outdir', type=str, help="The directory to send output files to.")

    parser.add_argument('-v', dest='verbose', action='store_true', help="Enable verbose output.")
    parser.add_argument('-c', '--config', dest="config", type=str, help="The location of the config file to use.", default="./config.yaml")

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

    if(args.file is not None and args.period is not None):
        # If the file exists, provide warnings about other arguments that won't be used
        raise ArgumentException("Both file and period arguments provided, these arguments are mutually exclusive and you must select one.")

    if(args.period is not None):
        now = int(time.time())
        if(args.period[0] > now or args.period[1] > now):
            raise ArgumentException("Either the start or end times of the period exceeds current time.")

def is_integer(value):
    """
    Ensure a python value is either a true integer or an integer string.
    """
    if isinstance(value, int):
        return True
    if isinstance(value, str):
        return value.isdigit() or (value.startswith('-') and value[1:].isdigit())
    return False   

def parse_month_year(time_str):
    try:
        month_year = datetime.datetime.strptime(time_str, '%B%y')
        return get_unix_timestamp_range(month_year.month, month_year.year)
    except ValueError as e:
        return None

def parse_time_range(time_range_str):
    # Parse the time range string as a single year (i.e. 2024, 2025)
    try:
        year_num = int(time_range_str)
        # Ensure the year is in modern era
        if(year_num >= 2000 and year_num < 4000):
            jan = get_unix_timestamp_range(1, year_num)
            dec = get_unix_timestamp_range(12, year_num)
            return (jan[0], dec[1])
    except:
        pass

    # Try to parse the time range string as a single month year combination (i.e. May25)
    single_month_year = parse_month_year(time_range_str)
    if(single_month_year):
        return single_month_year

    if("-" not in time_range_str):
        raise ArgumentException("Can't parse time range- failed to parse year & single month year formats. The following formats require a range but no '-' character present.")

    time_str_arr = time_range_str.split("-")
    if(len(time_str_arr) != 2):
        raise ArgumentException(f"Can't parse time range- found `-` character, but found !=2 arguments: {time_str_arr}")

    start = parse_month_year(time_str_arr[0])
    end = parse_month_year(time_str_arr[1])
    if(start and end):
        return (start[0], end[1])        

    if(not is_integer(time_str_arr[0]) or not is_integer(time_str_arr[1])):
        print(f"Failed to parse time range string \"{time_range_str}\" either the start or end time failed to parse as Integer.")
        raise ValueError()
    
    return (int(time_str_arr[0]), int(time_str_arr[1]))

def parse_analysis_options(analysis_options_str):
    options = analysis_options_str.split(",")
    return options

def parse_file_list(path):
    if(os.path.isfile(path)):
        return [path]
    elif(os.path.isdir(path)):
        file_paths = []
        for root, _, files in os.walk(path):
            for file in files:
                file_paths.append(os.path.join(root, file))
        return file_paths
    else:
        raise ArgumentException(f"Can't parse file list, path provided \"{path}\" is neither a file or directory.")

class ArgumentException(Exception):
    pass
