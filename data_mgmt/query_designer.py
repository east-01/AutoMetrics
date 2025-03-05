import datetime
import json
import pandas as pd
import requests

from program_data import ProgramData
from timeutils import get_range_printable

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

def build_query_url(start, end, type_string):
    """
    Build a URL for a single query.
    """
    prog_data = ProgramData()
    base_url = prog_data.config["base_url"]
    query_string = prog_data.config["query"].replace(prog_data.settings.type_string_identifier, type_string)

    return build_url(base_url, {
        "start": start,
        "end": end,
        "step": prog_data.config["step"],
        "query": query_string
    })

def build_query_list():
    """
    Build a list of queries by analysing the state of the current ProgramData.
    Generates a list of "query blocks" which are dictonaries containing the query URL itself and 
      useful information about said query.
    """

    prog_data = ProgramData()
    args = prog_data.args

    type_string = prog_data.settings.type_strings[args.type]
    query_url = build_query_url(args.period[0], args.period[1], type_string)
    query_block = {
        'query': query_url,
        'type': args.type,
        'period': args.period
    }
    
    return [query_block]

def get_query_block_string(query_block):
    """
    Given a query block dictionary (see build_query_list)
    """
    return f"{query_block["type"].upper()} {get_range_printable(query_block["period"][0], query_block["period"][1])}"