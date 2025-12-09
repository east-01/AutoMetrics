import shutil

from src.parameter_utils import ConfigurationException
from src.utils.config_checker import verify_sections_exist
from src.utils.timeutils import break_period_into_months, break_down_period, get_range_printable

class Timeline:
    """ The Timeline acts as a standard agreed upon timeframe to fit data points into. This helps
            the search for TimeStampIdentifiers that have specific integer start and end points,
            we can look up those integers here.
        The Timeline is broke into two parts: the main periods and regular periods. The main
            periods act as the overall marking points to split data analysis, while the regular
            periods split the main periods into manageable chunks. The format looks like this:
            
        |--i--i--|--i--i--|--i--i--|--i--i--|--i--i--|
         
        Where the | symbol represents a main period timestamp and the i symbol represents a regular
            period timestamp.
    """
    def __init__(self, config_section, start_ts, end_ts):
        self.start_ts = start_ts
        self.end_ts = end_ts

        sub_period_max_len = 60*60*24*7
        if("sub_period_max_len" in config_section):
            sub_period_max_len = int(config_section["sub_period_max_len"])

        period_align = "month"
        if("align" in config_section):
            period_align = config_section["align"]

        if(period_align == "month"):
            self.main_periods = break_period_into_months(start_ts, end_ts)
        else:
            self.main_periods = [(start_ts, end_ts)]

        self.periods = []
        for period in self.main_periods:
            sub_periods = break_down_period(period[0], period[1], target_length=sub_period_max_len)
            self.periods.extend(sub_periods)

    def get_period_count(self):
        return len(self.main_periods)

    def get_period(self, index):
        """ Get the (start_ts, end_ts) tuple for the period at the provided index. """
        return self.main_periods[index]

    def get_sub_periods(self, main_period_index):
        """ Get the list of (start_ts, end_ts) tuples for the sub-periods within the main period
                at the provided index.
        """
        main_period = self.main_periods[main_period_index]
        sub_periods = []
        for period in self.periods:
            if(period[0] >= main_period[0] and period[1] <= main_period[1]):
                sub_periods.append(period)
        return sub_periods

    def __str__(self):
        
        def ts_as_float(timestamp):
            """ Get the timestamp as a float representing its progress through the whole timeline."""
            return (timestamp-self.start_ts)/(self.end_ts-self.start_ts)

        shell_width = shutil.get_terminal_size().columns-1

        firstline = "#"
        secondline = " "

        for i in range(self.get_period_count()):
            period = self.get_period(i)
            start_ts, end_ts = period
            sub_periods = self.get_sub_periods(i)  # unused, but left in case needed

            start_pos = int(ts_as_float(start_ts) * shell_width)
            end_pos = int(ts_as_float(end_ts) * shell_width)

            # Ensure ordered and clamped positions
            start_pos = max(min(start_pos, shell_width), 0)
            end_pos   = max(min(end_pos, shell_width), start_pos + 1)

            cell_width = max(end_pos - start_pos, 1)

            # First line: draw a block
            firstline += "-" * (cell_width - 1)
            firstline += "#"

            # Second line: label the block
            raw_label = get_range_printable(start_ts, end_ts)
            raw_label = raw_label[: cell_width - 1]  # trim to fit

            secondline += raw_label + " " * (cell_width - len(raw_label) - 1)

        return firstline + "\n" + secondline

TIMELINE_SECTION_NAME = "timeline"
def verify_timeline_config(config_section):
    """
    Verify the configuration section for the timeline.

    Args:
        config_section (dict): A dictionary holding config key/values. The section will be unded 
            TIMELINE_SECTION_NAME at the top level.

    Raises:
        ConfigurationException: The configuration is invalid.

    Returns:
        None
    """
    
    verify_sections_exist(
        config_section, TIMELINE_SECTION_NAME,
        required_sections={"align"},
        optional_sections={"sub_period_max_len"}
    )

    if("sub_period_max_len" in config_section):
        try:
            int(config_section["sub_period_max_len"])
        except:
            raise ConfigurationException(f"Timeline config invalid, sub period max len is not an integer")
    
