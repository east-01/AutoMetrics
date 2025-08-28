from src.utils.timeutils import break_period_into_months, break_down_period

class Timeline:
    def __init__(self, start_ts, end_ts):
        self.start_ts = start_ts
        self.end_ts = end_ts

        self.main_periods = break_period_into_months(start_ts, end_ts)
        self.periods = []
        for period in self.main_periods:
            sub_periods = break_down_period(period[0], period[1])
            self.periods.extend(sub_periods)