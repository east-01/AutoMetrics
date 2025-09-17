import os
import datetime

from src.utils.timeutils import get_unix_timestamp_range

class ArgumentException(Exception):
    pass
class ConfigurationException(Exception):
    pass

def is_integer(value):
    """ Ensure a python value is either a true integer or an integer string. """
    if isinstance(value, int):
        return True
    if isinstance(value, str):
        return value.isdigit() or (value.startswith('-') and value[1:].isdigit())
    return False   

def parse_month_year(time_str):
    """ Parse a string in the format <Month><YearLast2>, example being January25 for January 2025. """
    try:
        month_year = datetime.datetime.strptime(time_str, '%B%y')
        return get_unix_timestamp_range(month_year.month, month_year.year)
    except ValueError as e:
        return None

def parse_time_range(time_range_str):
    """ Parse a string as a time range. Can accept multiple formats:
            Single year: 2024
            Single month/year: January25
            Month/year range: January25-March25
            Timestamp range: 1735718400-1738396799 
        
    Arguments:
        time_range_str (str): The time range string.
            
    Raises:
        ArgumentException:
            - Failed to parse single year and single month/year and no '-' character found.
            - Split along the '-' character and got more than two elements.
        ValueError: The start/end timestamp fails to parse as an integer. 
    
    Returns:
        (int, int): A tuple of integers being the start and end timestamps, in unix timestamp form.
    """
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
        raise ArgumentException(f"Can't parse time range- found `-` character, but split found !=2 arguments: [{", ".join(time_str_arr)}]")

    start = parse_month_year(time_str_arr[0])
    end = parse_month_year(time_str_arr[1])
    if(start and end):
        return (start[0], end[1])        

    if(not is_integer(time_str_arr[0]) or not is_integer(time_str_arr[1])):
        print(f"Failed to parse time range string \"{time_range_str}\" either the start or end time failed to parse as Integer.")
        raise ValueError()
    
    return (int(time_str_arr[0]), int(time_str_arr[1]))

def parse_file_list(path):
    """ Parse a path as a list of files. Has two behaviours based off of the provided path
            argument:
            - Path is a file: Return a single element array with path in it.
            - Path is a directory: Return the files in that directory in an array. 
    
    Arguments:
        path (str): The filepath to parse as a file list.
    
    Raises:
        ArgumentException: The path is neither a file or a directory.
        
    Returns:
        list[str]: The list of file paths derived from the provided path.
    """
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