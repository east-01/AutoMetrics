from src.parameter_utils import ConfigurationException
from src.utils.config_checker import verify_sections_exist
from src.utils.timeutils import break_period_into_months, break_down_period

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
    def __init__(self, config, start_ts, end_ts):
        self.start_ts = start_ts
        self.end_ts = end_ts

        sub_period_max_len = 60*60*24*7
        if("sub_period_max_len" in config):
            sub_period_max_len = int(config["sub_period_max_len"])
        print(f"maxlen: {sub_period_max_len}")

        self.main_periods = break_period_into_months(start_ts, end_ts)
        self.periods = []
        for period in self.main_periods:
            sub_periods = break_down_period(period[0], period[1], target_length=sub_period_max_len)
            self.periods.extend(sub_periods)

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
        required_sections={"sub_period_max_len"},
        optional_sections={"align"}
    )

    try:
        int(config_section["sub_period_max_len"])
    except:
        raise ConfigurationException(f"Timeline config invalid, sub period max len is not an integer")