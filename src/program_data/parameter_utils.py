import os
import datetime

from src.utils.timeutils import get_unix_timestamp_range

class ArgumentException(Exception):
    pass
class ConfigurationException(Exception):
    pass

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