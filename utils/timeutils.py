import datetime
import calendar

def from_unix_ts(timestamp):
    """
    Given a UNIX timestamp, convert it to format %m/%d/%Y %H:%M.
    """
    # Format manually, using strftime adds leading 0s that we don't want to handle
    dt_object = datetime.datetime.fromtimestamp(timestamp)
    return f"{dt_object.month}/{dt_object.day}/{dt_object.year} {dt_object.hour}:{dt_object.minute:02d}"

def to_unix_ts(date_time_str):
    """
    Given a timestamp of the format %m/%d/%Y %H:%M convert to UNIX timestamp.
    """
    # Parse the date/time string into a datetime object
    dt = datetime.datetime.strptime(date_time_str, '%m/%d/%Y %H:%M')
    unix_timestamp = int(dt.timestamp())
    return unix_timestamp

def get_range_as_month(start_ts, end_ts):
    # Convert timestamps to datetime objects
    start_dt = datetime.datetime.fromtimestamp(start_ts)
    end_dt = datetime.datetime.fromtimestamp(end_ts)

    last_day = calendar.monthrange(start_dt.year, start_dt.month)[1]

    # Ensure the start unix timestamp is the first second of the month
    is_starting_second = start_dt.day == 1 and start_dt.hour == 0 and start_dt.minute == 0 and start_dt.second == 0
    if(not is_starting_second):
        return None

    # Ensure the end unix timestamp is the last second of the month
    is_ending_second = end_dt.day == last_day and end_dt.hour == 23 and end_dt.minute == 59 and end_dt.second == 59
    if(not is_ending_second):
        return None

    # Ensure the start and end times are talking about the same month
    same_month = start_dt.year == end_dt.year and start_dt.month == end_dt.month
    if(not same_month):
        return None

    return {
        'month': start_dt.month, 
        'year': start_dt.year
    }

def get_range_printable(start_ts, end_ts):
    """
    Get the unix timestamp range as a human-readable string.
    Two formats, higher priority first:
      - <MonthName><YY> The month name and the last two digits of the year
      - DD/MM/YYYY HH:MM-DD/MM/YYYY HH:MM
    """

    # First format, timestamp range needs to cover a month period
    monthyear = get_range_as_month(start_ts, end_ts)
    if(monthyear is not None):
        month_str = calendar.month_name[monthyear['month']]
        year_str = str(monthyear['year'])[2:]
        return f"{month_str}{year_str}"
    
    # Second format
    outstr = f"{from_unix_ts(start_ts)}-{from_unix_ts(end_ts)}"
    return outstr