# The data loader observer will take in the command line arguments and retrieve the corresponding
#   data. The observer currently checks arguments:
# type (cpu/gpu/uniquens): For the type of data to retrieve
# file [optional]: The file to pull the data from

import pandas as pd

from src.program_data.program_data import ProgramData
from .grafana_df_analyzer import get_resource_type, get_period
from .query_executor import perform_query
from .query_designer import build_query_list, get_query_block_string
from src.data.identifiers.identifier import SourceIdentifier
from src.data.data_repository import DataRepository

def ingest(prog_data: ProgramData):
    """
    Observes the state of args and builds the corresponding DataRepository object.
    """

    data_repo = DataRepository()
    data_frames = _load_dfs(prog_data)

    for df in data_frames:
        out_df, identifier = _ingest_grafana_df(df)
        data_repo.add(identifier, out_df)

    # Ensure the DataRepository loaded properly
    if(data_repo.count() == 0):
        raise Exception(f"Failed to load DataRepository. The repo is empty.")

    print(f"Loaded {data_repo.count()} data frame(s).")

    return data_repo

def _load_dfs(prog_data: ProgramData):
    """
    Load the data_frames as specified by the arguments.
    Two cases:
    1. A CSV file/directory was passed in:
      Load said file/directory, verify it's valid, and ingest the DataFrame.
    2. A query needs to be generated:
      Generate a list of query URLs with build_query_list.
      Perform queries, ingesting each returned DataFrame.
    """

    data_frames = []
     
    if(prog_data.args.file is not None):

        input_directory = prog_data.args.file
        print(f"Loading data from {len(input_directory)} file(s):")
        
        for file_path in input_directory:
            print(f"  {file_path}")

            file_df = pd.read_csv(file_path)
            data_frames.append(file_df)

    else:

        query_blocks = build_query_list(prog_data.config)
        print(f"Loading data from {len(query_blocks)} query/queries:")

        for query_block in query_blocks:
            print(f"  {get_query_block_string(prog_data.config, query_block)}")

            query_url = query_block['query']
            query_response = perform_query(query_url)
            data_frames.append(query_response)

    return data_frames

def _ingest_grafana_df(df):
    """
    Take in a DataFrame object, assuming the format of a Grafana csv file, and extract info from it.
    We OPTIONALLY take in additional attributes about the DataFrame, this is because DataFrames
        can either be retrieved from files or PromQL queries. With DataFrames that are generated
        by PromQL we already know the type and period, but for DataFrames generated from files
        we'll have to analyze the actual data for these attributes.
    Target attributes: 
    - The period/step of the data, taken from the time column
    - The type of the data, taken from column names' "resource=<type>" section

    Currently, DataFrames are saved with the start of it's period as the identifier, this
        allows us to read the DataFrames in chronological order later.
    """

    # We still want to perform these analyses for the DataFrame even if the values we're
    #   looking for were passed in as arguments. This ensures the data is clean.
    period = get_period(df)
    resource_type = get_resource_type(df)

    identifier = SourceIdentifier(period[0], period[1], resource_type)

    # Convert the data frame to numeric values so we can properly analyze it later.
    df.iloc[:, 1:] = df.iloc[:, 1:].map(pd.to_numeric, errors="coerce")

    return (df, identifier)
