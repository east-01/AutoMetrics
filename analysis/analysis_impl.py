# Each analysis implementation should take in a data_block dictionary and return either a 
#   dataframe, list, or float
# Most of this code is repackaged from Tide2.ipynb in https://github.com/SDSU-Research-CI/rci-helpful-scripts

import pandas as pd

from program_data import ProgramData
from analysis.data_cleaning import clear_duplicate_uids, clear_blacklisted_uids

def analyze_hours_byns(data_block):
    df = data_block['data']

    # Extract namespaces from column names, excluding the first since that's the Time column
    namespaces = df.columns[1:].str.extract(r'namespace="([^"]+)"')[0]

    # Calculate the sum for each namespace
    namespace_totals = {}
    for namespace in namespaces.unique():
        namespace_df = df.filter(regex=f'namespace="{namespace}"', axis=1)

        namespace_total = namespace_df.sum(axis=1).sum()
        namespace_totals[namespace] = namespace_total

    namespace_totals_df = pd.DataFrame(list(namespace_totals.items()), columns=["Namespace", "Hours"])

    # Drop NA and 0 values
    namespace_totals_df.dropna(inplace=True)
    namespace_totals_df = namespace_totals_df[namespace_totals_df["Hours"] >= 0.001]

    # Sort the final DataFrame by hours
    namespace_totals_df.sort_values(by="Hours", ascending=False, inplace=True)

    return namespace_totals_df

def _analyze_jobs_final(df):
    # Create a data frame where the columns 
    greater_than_zero_columns = [col for col in df.columns[1:] if df[col].sum() > 0]

    df = df[greater_than_zero_columns].fillna(0)

    #extract all the namespaces and use them as columns, group and summing the values 
    columns = df.columns[1:].str.extract(r'namespace="([^"]+)"')[0]

    namespace_counts_sorted = pd.DataFrame(columns.value_counts().sort_values(ascending=True)).reset_index()
    namespace_counts_sorted.columns = ["Namespace", "Count"]

    return namespace_counts_sorted

def analyze_jobs(data_block):
    # Load data frame, dropping columns with duplicate uids
    df = clear_duplicate_uids(data_block['data'])
    return _analyze_jobs_final(df)

def analyze_cpu_only_jobs(data_block):
    # We have to locate the corresponding GPU data block
    # The UIDs in the GPU will be used to clear blacklisted IDs
    gpu_identifier = (data_block['period'], "gpu")
    gpu_data_block = ProgramData().data_repo.data_blocks[gpu_identifier]

    if(gpu_data_block is None):
        raise Exception("Failed to analyze cpu only jobs, the corresponding gpu data_block could not be found.")

    gpu_uuid = set(gpu_data_block['data'].columns[1:].str.extract(r'uid="([^"]+)"')[0].dropna())

    df = clear_blacklisted_uids(data_block['data'], gpu_uuid)
    df = clear_duplicate_uids(df)
    return _analyze_jobs_final(df)

def analyze_unique_ns(data_block):
    return