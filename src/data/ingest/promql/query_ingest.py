import re
import math
import time
import datetime
import numpy as np

from src.program_data.program_data import ProgramData
from src.data.data_repository import DataRepository
from src.data.identifiers.identifier import SourceQueryIdentifier
from data.ingest.ingest_controller import *
from src.data.ingest.grafana_df_analyzer import *
from src.data.processors import process_periods
from src.data.ingest.promql.query_executor import perform_query, transform_query_response
from src.data.ingest.promql.query_designer import build_query_list
from src.utils.timeutils import to_unix_ts, from_unix_ts, get_range_printable
from src.data.filters import *
from src.data.ingest.promql.query_preprocess import _preprocess_df

class PromQLIngestController(IngestController):
    def ingest(self) -> DataRepository:
        
        prog_data: ProgramData = self.prog_data
        # The data repository that holds SourceQueryIdentifiers, this is different from the
        #   standard DataRepository because there are multiple queries per period and type, to be
        #   used in the processing step where we only get pending/running pods.
        data_repo: DataRepository = DataRepository()

        query_blocks = build_query_list(prog_data.config, prog_data.args)

        print(f"Loading data from {len(query_blocks)} query/queries:")

        for query_block in query_blocks:
            print(f"  {query_block}")

            # Perform the query and transform the json response into a Grafana DataFrame
            json_response = perform_query(query_block.query_url)
            grafana_df = transform_query_response(json_response)

            if(len(grafana_df) == 0):
                print("WARN: Empty data frame")

            # Convert values to numeric
            grafana_df = convert_to_numeric(grafana_df)

            # Read identifying data about DataFrame
            period = (query_block.start_ts, query_block.end_ts)
            resource_type = None
            if(query_block.query_name == "truth"):
                resource_type = get_resource_type(grafana_df)

            identifier = SourceQueryIdentifier(period[0], period[1], resource_type, query_block.query_name)
            
            data_repo.add(identifier, grafana_df)

        # Normalize periods for filtering step, then perform filtering
        # data_repo = process_periods(data_repo)

        print("Applying running/pending filter...")

        start_time = time.time()
        data_repo = _filter_to_running_pending(self.prog_data, data_repo)

        print(f"Filtering took {(time.time()-start_time):.2f} seconds.")

        print("Stitching...")

        start_time = time.time()
        data_repo = stitch(data_repo)

        print(f"Stitching took {(time.time()-start_time):.2f} seconds.")

        return data_repo

def _filter_to_running_pending(prog_data: ProgramData, data_repo: DataRepository) -> DataRepository:
    """
    Filter a DataRepository containing multiple SourceQueryIdentifiers to SourceIdentifiers
        based off of their running/pending status.

    Args:
        data_repo (DataRepository): The input repository, contains SourceQueryIdentifiers to
            be transformed.
    
    Returns:
        DataRepository: The output DataRepository, contains SourceIdentifiers.
    """

    out_repository = DataRepository()

    step = prog_data.config["step"]

    # Get filter lambdas for both source query types
    source_query_type_lambda = filter_type(SourceQueryIdentifier)
    status_lambda = lambda id: source_query_type_lambda(id) and id.query_name == "status"
    truth_lambda = lambda id: source_query_type_lambda(id) and id.query_name == "truth"

    for status_identifier in data_repo.filter_ids(status_lambda):
        status_df_raw = data_repo.get_data(status_identifier)

        if(len(status_df_raw) == 0):
            readable_period = get_range_printable(status_identifier.start_ts, status_identifier.end_ts, 3600)
            print(f"Skipping applying status filter to {readable_period} the status DataFrame is empty")
            continue

        status_df = _preprocess_df(status_df_raw, False, step)

        # Tracks the set of created types, used to protect from creating multiple SourceIdentifiers
        #   with the same start_ts, end_ts, and type        
        created_types = set() 

        # Filter identifiers with type SourceQueryIdentifier, query_name=truth, and matching 
        #   timestamps 
        timestamps_filter = filter_timestamps(status_identifier.start_ts, status_identifier.end_ts)
        identifiers_filter = lambda identifier: truth_lambda(identifier) and timestamps_filter(identifier)
        identifiers = data_repo.filter_ids(identifiers_filter)

        for values_identifier in identifiers:
            if(values_identifier.type in created_types):
                print(f"ERROR: Identifier of type \"{values_identifier.type}\" is already in created_types for this timestamp range. This shouldn't happen.")
                continue
        
            values_df_raw = data_repo.get_data(values_identifier)

            values_df = _preprocess_df(values_df_raw, True, step)
            values_df = _apply_status_df(status_df, values_df)

            identifier = SourceIdentifier(values_identifier.start_ts, values_identifier.end_ts, values_identifier.type)
            out_repository.add(identifier, values_df)         

            created_types.add(identifier.type)   

    return out_repository

def _apply_status_df(status_df, values_df):
    """
    Apply the status DataFrame to the values DataFrame, only accepting values from the values_df
        when the status_df has a 1 in that cell position.
    Cells are identified by column=uid and row=timestamp, so the status_df and the values_df must
        have matching time columns.

    Args:
        status_df (pd.DataFrame): The DataFrame holding running/pending statuses.
        values_df (pd.DataFrame): The DataFrame holding the usage values.

    Returns:
        pd.DataFrame: The values DataFrame with the running/pending statuses applied.
    """

    def select_uid(string):
        if(string == "Time"):
            return string

        match = re.search(r'uid="([^"]+)"', string)
        if match:
            uid = match.group(1)
            return uid
        else:
            raise Exception(f"Failed to read uid in column name \"{string}\"")

    start_ts = to_unix_ts(values_df["Time"][0])
    end_ts = to_unix_ts(list(values_df["Time"])[-1])

    times_list = [to_unix_ts(time) for time in status_df["Time"]]

    try:
        start_index = times_list.index(start_ts)
    except ValueError:
        start_index = 0

    try:
        end_index = times_list.index(end_ts)
    except ValueError:
        end_index = len(times_list)-1

    drop_columns = []

    for column in values_df.columns:
        if(column == "Time"):
            continue

        uid = select_uid(column)

        if(uid not in status_df.columns):
            drop_columns.append(column)
            continue

        status_column = status_df[uid].iloc[range(start_index, end_index+1)]
        status_column.index = values_df.index

        values_df[column] = values_df[column].where(status_column == 1)

    values_df.drop(columns=drop_columns, inplace=True)

    return values_df

def stitch(data_repo: DataRepository):
    """
    Filter a DataRepository containing multiple SourceQueryIdentifiers to SourceIdentifiers
        based off of their running/pending status.

    Args:
        data_repo (DataRepository): The input repository, contains SourceQueryIdentifiers to
            be transformed.
    
    Returns:
        DataRepository: The output DataRepository, contains SourceIdentifiers.
    """

    out_data_repo = DataRepository()

    for type in settings["type_strings"]:
        identifiers = data_repo.filter_ids(filter_source_type(type))
        identifiers.sort(key=lambda id: id.start_ts)

        if(len(identifiers) == 0):
            continue

        # The data frame that we're building for the current period; right now the data frames
        #   are built by month. But we should use Timeline later
        df = pd.DataFrame()
        df_ids = [] # Stores a list of identifiers for this specific dataframe
        last_dt = datetime.datetime.fromtimestamp(identifiers[0].start_ts)

        # Store the current data frame
        def store_df():
            nonlocal df, df_ids

            new_identifier = SourceIdentifier(df_ids[0].start_ts, df_ids[-1].end_ts, df_ids[0].type)
            out_data_repo.add(new_identifier, df)

        def reset_df():
            nonlocal df, df_ids

            df = pd.DataFrame()
            df_ids = []

        for identifier in identifiers:

            # If the current month and year do not match the existing dataframe's month and year,
            #   switch to a new df
            curr_dt = datetime.datetime.fromtimestamp(identifier.start_ts)
            if((curr_dt.month, curr_dt.year) != (last_dt.month, last_dt.year)):
                store_df()
                reset_df()

            last_dt = curr_dt

            df_toadd = data_repo.get_data(identifier)
            df = pd.concat([df, df_toadd], ignore_index=True, sort=False)
            df_ids.append(identifier)

        store_df()

    return out_data_repo