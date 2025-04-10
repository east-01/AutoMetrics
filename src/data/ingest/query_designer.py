import datetime
import json
import pandas as pd
import requests

from src.utils.timeutils import get_range_printable, break_period_into_months
from src.program_data.settings import settings

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

def build_query_url(config, start, end, type_string):
    """
    Build a URL for a single query.
    """
    base_url = config["base_url"]
    query_string = config["query"].replace(settings['type_string_identifier'], type_string)

    return build_url(base_url, {
        "start": start,
        "end": end,
        "step": config["step"],
        "query": query_string
    })

def build_query_list(config, args):
    """
    Build a list of queries by analysing the state of the current ProgramData.
    Generates a list of "query blocks" which are dictonaries containing the query URL itself and 
      useful information about said query.
    """

    analysis_options = settings['analysis_settings']

    required_types = set()
    for analysis in args.analysis_options:
        for type in analysis_options[analysis]['types']:
            required_types.add(type)

    periods = break_period_into_months(args.period[0], args.period[1])

    query_list = []
    for period in periods:
        for type in required_types:
            type_string = settings['type_strings'][type]
            query_url = build_query_url(config, period[0], period[1], type_string)
            query_list.append({
                'query': query_url,
                'type': type,
                'period': period
            })

    return query_list

def get_query_block_string(config, query_block):
    """
    Given a query block dictionary (see build_query_list)
    """
    return f"{query_block["type"].upper()} {get_range_printable(query_block["period"][0], query_block["period"][1]), config['step']}"