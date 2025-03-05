import datetime
import json
import pandas as pd
import requests

from timeutils import from_unix_ts

def perform_query(queryURL):
    """
    Perform an HTTP GET request with the queryURL, handle the response and return the DataFrame
    """

    cache_mode = 'nocache'
    json_response = None

    if(cache_mode == 'nocache' or cache_mode == 'save'):
        response = requests.get(queryURL)

        if(response.status_code != 200):
            raise Exception(f"Failed to perform PromQL query for url:\n{queryURL}")

        # Check if 'data' is in the response JSON to avoid KeyError
        json_response = response.json()
        if 'data' not in json_response:
            raise Exception(f"Missing 'data' in the response:\n{json_response}")

    if(cache_mode == 'save'):
        with open('./cached_response.json', 'w') as f:
            json.dump(json_response, f)
            print("Saved json.")
    elif(cache_mode == 'use'):
        print("WARN: Used cached response instead of performing a new PromQL query.")
        with open('./cached_response.json', 'r') as f:
            json_response = json.load(f)

    query_response = json_response['data']['result']

    return transform_query_response(query_response)

def transform_query_response(query_response):
    """
    Given query_response json transform it into a "series joined by time" table. The query response
       json is the data.result portion of the web request, see query_facilitator#perform_query.
    This step is automatically performed by Grafana when we want to download the .csv file, so we
      have to perform the same actions to our raw data.
    """

    def transform_column_name(metric_dict):
        """
        Given a metric dictionary, convert it to string format such that {'key': 'pair'} to 
          {key="pair"}. This ensures parity with Grafana .csv downloads.
        """
        key_val_pairs = []
        for key in metric_dict.keys():
            key_val_pairs.append(f"{key}=\"{metric_dict[key]}\"")
        return "{" + ", ".join(key_val_pairs) + "}"

    # Convert json to usable DataFrame
    json_df = pd.DataFrame(query_response)    
    out_df = pd.DataFrame()

    for index, row in json_df.iterrows():
        # Get the metric column as a string
        metric = transform_column_name(row['metric'])
        timestamps = [int(pair[0]) for pair in row['values']]
        values = [pair[1] for pair in row['values']]

        # Generate temporary DataFrame with a time column and a values column with the metric as
        #   the title, this will allow for a clean outer join
        temp_df = pd.DataFrame({
            'Time': timestamps, 
            metric: values
        })

        # Use outer join with the output DataFrame to add the temporary DataFrame to the output
        if(out_df.empty):
            out_df = temp_df
        else:
            out_df = pd.merge(out_df, temp_df, on='Time', how='outer')

    # Transform timestamps from unix time to 
    out_df['Time'] = out_df['Time'].map(from_unix_ts)

    return out_df