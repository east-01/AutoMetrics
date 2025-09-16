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
    def __init__(self, start_ts, end_ts):
        self.start_ts = start_ts
        self.end_ts = end_ts

        self.main_periods = break_period_into_months(start_ts, end_ts)
        self.periods = []
        for period in self.main_periods:
            sub_periods = break_down_period(period[0], period[1])
            self.periods.extend(sub_periods)