import os
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

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
        month_year = datetime.strptime(time_str, '%B%y')
        return get_unix_timestamp_range(month_year.month, month_year.year)
    except ValueError as e:
        return None

def parse_year_num(period_arg):
    """ Parse a string in the format <Year>, example being 2024. """
    # Parse the time range string as a single year (i.e. 2024, 2025)
    try:
        year_num = int(period_arg)
        # Ensure the year is in modern era
        if(year_num >= 2000 and year_num < 4000):
            jan = get_unix_timestamp_range(1, year_num)
            dec = get_unix_timestamp_range(12, year_num)
            return (jan[0], dec[1])
    except:
        return None
    
def parse_timestamp(period_arg):
    """ Parse a string in the format <Timestamp>, example being 1735718400. """
    # Parse the time range string as a single year (i.e. 2024, 2025)
    try:
        timestamp = int(period_arg)
        # Ensure the year is in modern era
        if(timestamp >= 1.6e9):
            return (timestamp, timestamp)
    except:
        return None
    
def parse_keywords(period_arg):
    now = datetime.now(ZoneInfo("America/Los_Angeles"))

    match(period_arg):
        case "yesterday":
            start_of_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
            start_of_yesterday = start_of_today - timedelta(days=1)
            end_of_yesterday = start_of_today - timedelta(seconds=1)
            
            return int(start_of_yesterday.timestamp()), int(end_of_yesterday.timestamp())
        case "lastweek":
            this_sunday = now - timedelta(days=now.weekday() + 1)
            this_sunday = this_sunday.replace(hour=0, minute=0, second=0, microsecond=0)
            last_sunday = this_sunday - timedelta(days=7)
            last_saturday_end = this_sunday - timedelta(seconds=1)
            
            return int(last_sunday.timestamp()), int(last_saturday_end.timestamp())
        case "lastmonth":
            first_of_this_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end_of_last_month = first_of_this_month - timedelta(seconds=1)
            start_of_last_month = end_of_last_month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            return int(start_of_last_month.timestamp()), int(end_of_last_month.timestamp())
        case "ytd":
            start_of_year = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end_of_year_to_date = now
            
            return int(start_of_year.timestamp()), int(end_of_year_to_date.timestamp())

    return None

def parse_range_period_arg(period_arg):
    """ Parse as a ranged value of single values in the format <Value1>-<Value2>. 
        Both Value1 and Value2 must be acceptable arguments to parse_single_period_arg. 
        Examples:
            Year range: 2024-2025        
            Month/year range: January25-March25
            Timestamp range: 1735718400-1738396799 
    """

    if("-" not in period_arg):
        raise ArgumentException("Can't parse time range- failed to parse year & single month year formats. The following formats require a range but no '-' character present.")

    time_str_arr = period_arg.split("-")
    if(len(time_str_arr) != 2):
        raise ArgumentException(f"Can't parse time range- found `-` character, but split found !=2 arguments: [{", ".join(time_str_arr)}]")

    start_arg = time_str_arr[0]
    end_arg = time_str_arr[1]

    start = parse_single_period_arg(start_arg, allow_timestamp=True)
    end = parse_single_period_arg(end_arg, allow_timestamp=True)
    if(not start):
        raise ArgumentException(f"Failed to parse the first part of period range \"{start_arg}\". This value must be acceptable to parse_single_period_arg or a single unix timestamp, and not be a keyword.")
    if(not end):
        raise ArgumentException(f"Failed to parse the second part of period range \"{end_arg}\". This value must be acceptable to parse_single_period_arg or a single unix timestamp, and not be a keyword.")

    return (start[0], end[1])

def parse_single_period_arg(period_arg, allow_timestamp=False):
    """ Parse a string argument as a time range. Can accept multiple formats:
            Single year: 2024
            Single month/year: January25
            Keyword: lastweek, lastmonth, yeartodate
            Timestamp (if allow_timestamp=True): 1735718400
                - This is for use with ranged arguments, allow_timestamp should normally be false.
    """

    # Parse as a single year (i.e. 2024)
    year_num = parse_year_num(period_arg)
    if(year_num):
        return year_num

    # Try to parse the time range string as a single month year combination (i.e. May25)
    single_month_year = parse_month_year(period_arg)
    if(single_month_year):
        return single_month_year

    keyword = parse_keywords(period_arg)
    if(keyword):
        return keyword

    timestamp = parse_timestamp(period_arg)
    if(allow_timestamp and timestamp):
        return timestamp

def parse_period_argument(period_arg):
    """ Parse a string as a time range. Can accept multiple formats:
            Single year: 2024
            Single month/year: January25
            Month/year range: January25-March25
            Timestamp range: 1735718400-1738396799 
        
    Arguments:
        period_arg (str): The period argument.
            
    Raises:
        ArgumentException:
            - Failed to parse single year and single month/year and no '-' character found.
            - Split along the '-' character and got more than two elements.
        ValueError: The start/end timestamp fails to parse as an integer. 
    
    Returns:
        (int, int): A tuple of integers being the start and end timestamps, in unix timestamp form.
    """
    
    value = None
    if("-" in period_arg):
        value = parse_range_period_arg(period_arg)
    else:
        value = parse_single_period_arg(period_arg)
    
    if(not value):
        raise ArgumentException(f"Failed to parse period argument \"{period_arg}\"")

    return value

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