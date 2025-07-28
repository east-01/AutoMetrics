from dataclasses import dataclass
import math

from src.utils.timeutils import get_range_printable, break_period_into_months
from plugins.grafana.settings import settings

@dataclass(frozen=True)
class QueryData():
    """
    Information for a query, including the query url, the target type, and the period.
    """
    query_url: str
    query_name: str
    type: str
    start_ts: int
    end_ts: int

    def __str__(self) -> str:
        return f"{self.query_name} {self.type.upper()} {get_range_printable(self.start_ts, self.end_ts)}"

def build_query_list(config, args) -> list[QueryData]:
    """
    Build a list of queries by analysing the state of the current ProgramData.
    
    Args:
        config (dict): The loaded configuration.
        args (argparse.Namespace): The program arguments.

    Returns:
        list[QueryData]: The list of QueryData which contains the query URL itself and 
            useful information about said query.
    """

    analysis_options = settings['analysis_settings']

    required_types = set()
    for analysis in args.analysis_options:
        for type in analysis_options[analysis]['types']:
            required_types.add(type)

    orig_periods = break_period_into_months(args.period[0], args.period[1])
    periods = []
    for period in orig_periods:
        sub_periods = break_down_period(period[0], period[1])
        periods.extend(sub_periods)

    query_list = []
    for query_name in config["queries"]:

        query_string_orig: str = config["queries"][query_name]

        for period in periods:
            for type in required_types:
                
                type_string = settings['type_strings'][type]
                query_string = query_string_orig.replace(settings['type_string_identifier'], type_string)

                query_url = build_url(
                    config["base_url"], 
                    {
                        "start": period[0],
                        "end": period[1],
                        "step": config["step"],
                        "query": query_string
                    }
                )

                query_data = QueryData(
                    query_url,
                    query_name,
                    type,
                    period[0],
                    period[1]
                )

                query_list.append(query_data)

                # If the type string identifier is not in the query string, we don't have to worry
                #   about all other types in required_types since they will yield the same 
                #   query_data -> break out of type loop.
                if(settings['type_string_identifier'] not in query_string_orig):
                    break

    return query_list

def build_url(base, url_options = {}):
    """
    Build a URL using a base url and additional options.
    Example: The URL https://google.com and the associated options { testopt: "testval" } will
      yield: https://google.com?testopt=testval
    """
    url = base

    if(len(url_options.keys()) > 0):
        url += '?'
        option_pairs = []
        for option_key in url_options:
            option_pairs.append(option_key + "=" + str(url_options[option_key]))
        url += "&".join(option_pairs)

    return url        

def break_down_period(start_ts, end_ts, target_length = 60*60*24*7):
    """
    Given a starting and ending timestamp, return a list of starting and ending timestamps that
      do not exceed the target length.
    """

    period_length = end_ts-start_ts
    divisions = math.ceil(period_length/target_length)
    sub_period_length = period_length/divisions
    
    periods = []
    for i in range(divisions):
        sub_start_ts = start_ts + sub_period_length*i
        sub_end_ts = start_ts + sub_period_length*(i+1) - 1
        periods.append((sub_start_ts, sub_end_ts))

    return periods