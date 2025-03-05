# The data loader observer will take in the command line arguments and retrieve the corresponding
#   data. The observer currently checks arguments:
# type (cpu/gpu/uniquens): For the type of data to retrieve
# file [optional]: The file to pull the data from

# The data loader will observe the current ProgramData and load everything thats necessary.

import pandas as pd
import datetime

from program_data import ProgramData
from data_mgmt.data_frame_analysis import extract_column_data, analyze_df_type, analyze_df_period
from data_mgmt.query_executor import perform_query
from data_mgmt.query_designer import build_query_list, get_query_block_string
from timeutils import get_range_printable

def load_data():
    """
    Observes the state of ProgramData's args and builds the corresponding DataRepository object.
    Two cases:
    1. A CSV file/directory was passed in:
      Load said file/directory, verify it's valid, and ingest the DataFrame.
    2. A query needs to be generated:
      Generate a list of query URLs with build_query_list.
      Perform queries, ingesting each returned DataFrame.
    """

    prog_data = ProgramData()
    args = prog_data.args

    data_repo = DataRepository()
    
    if(args.file is not None):

        input_directory = [args.file] # TODO: Add input directory argument
        print(f"Loading data from {len(input_directory)} file(s):")
        
        for file_path in input_directory:
            print(f"  {file_path}")

            file_df = pd.read_csv(args.file)
            data_repo.add_data_frame(file_df, args.file)

    else:

        if(args.type == 'uniquens'):
            print("ERROR: Haven't handled uniquens case in load_data yet")
            exit(1)

        query_blocks = build_query_list()
        print(f"Loading data from {len(query_blocks)} query/queries:")

        for query_block in query_blocks:
            print(f"  {get_query_block_string(query_block)}")

            query_url = query_block['query']
            query_response = perform_query(query_url)
            data_repo.add_data_frame(query_response, "PromQL", query_block)

    # Ensure the DataRepository loaded properly
    if(data_repo is None):
        raise Exception(f"Failed to load DataRepository. The repo is null.")
    if(data_repo.count() == 0):
        raise Exception(f"Failed to load DataRepository. The repo is empty.")

    # TODO: Aggregate all of the data blocks if that's what the user wants

    # Load readable period data at the end of all data loading; readable_period may be affected by 
    #   other DF names so we need to load it last.
    for data_block in data_repo.data_blocks.values():
        start_ts, end_ts = data_block['period']
        data_block['readable_period'] = get_range_printable(start_ts, end_ts)
        fs_compat_name = data_block['readable_period'].replace("/", "_").replace(" ", "T").replace(":", "")
        data_block['out_file_name'] = f"{data_block['type']}-{fs_compat_name}"

    prog_data.data_repo = data_repo

    print(f"Loaded {data_repo.count()} data frame(s).")
    
class DataRepository():
    def __init__(self):
        self.data_blocks = {}
    
    def add_data_frame(self, df, source, addtl_attributes=None):
        """
        Take in a DataFrame object and add it to the repository.
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

        try:
            col_datas = [extract_column_data(col_name) for col_name in df.columns[1:]]

            # We still want to perform these analyses for the DataFrame even if the values we're
            #   looking for were passed in as arguments. This ensures the data is clean.
            period = analyze_df_period(df)
            type = analyze_df_type(col_datas)

            # Overwrite the inferred attributes with the true attributes passed as an argument.
            if(addtl_attributes is not None):
                if('period' in addtl_attributes.keys()):
                    period = addtl_attributes['period']
                if('type' in addtl_attributes.keys()):
                    type = addtl_attributes['type']

            identifier = (period, type)

            # Convert the data frame to numeric values so we can properly analyze it later.
            df.iloc[:, 1:] = df.iloc[:, 1:].map(pd.to_numeric, errors="coerce")

            self.data_blocks[identifier] = {
                "data": df,
                "type": type,
                "period": period
            }
        except Exception as e:
            print(f"Failed to add DataFrame from source {source}. Details:\n{e}")
            

    def count(self):
        return len(self.data_blocks.keys())
