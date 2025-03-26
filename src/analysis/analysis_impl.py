# Each analysis implementation should take in a data_block dictionary and return either a 
#   dataframe, list, or float
# Most of this code is repackaged from Tide2.ipynb in https://github.com/SDSU-Research-CI/rci-helpful-scripts

import pandas as pd

from program_data.program_data import ProgramData
from .grafana_df_cleaning import clear_duplicate_uids, clear_blacklisted_uids, has_time_column, clear_time_column
from data.ingest.grafana_df_analyzer import extract_column_data
from data.identifiers.identifier import SourceIdentifier, AnalysisIdentifier

#region Hours
def analyze_hours_byns(identifier):
    print(f"Analyzing hours by ns for {identifier}")
    df = ProgramData().data_repo.get(identifier)
    print(type(df))
    if(has_time_column(df)):
        df = clear_time_column(df)

    # Extract namespaces from column names, excluding the first since that's the Time column
    namespaces = df.columns.str.extract(r'namespace="([^"]+)"')[0]

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

def analyze_hours_total(identifier):
    # Retrieve the corresponding analysis thats already been performed
    df = ProgramData().data_repo.get(identifier)
    return df['Hours'].sum()
#endregion

#region Jobs
def _analyze_jobs_final(df, strip_cols_0=True):
    df = df.fillna(0)

    # Create a data frame where the columns 
    if(strip_cols_0):
        greater_than_zero_columns = [col for col in df.columns if df[col].sum() > 0]

        df = df[greater_than_zero_columns].fillna(0)

    #extract all the namespaces and use them as columns, group and summing the values 
    columns = df.columns.str.extract(r'namespace="([^"]+)"')[0]

    namespace_counts_sorted = pd.DataFrame(columns.value_counts().sort_values(ascending=False)).reset_index()
    namespace_counts_sorted.columns = ["Namespace", "Count"]

    return namespace_counts_sorted

def analyze_jobs(identifier):
    df = ProgramData().data_repo.get(identifier)
    if(has_time_column(df)):
        df = clear_time_column(df)

    # Load data frame, dropping columns with duplicate uids
    df = clear_duplicate_uids(df)
    return _analyze_jobs_final(df)

def analyze_cpu_only_jobs(identifier: SourceIdentifier):
    data_repo = ProgramData().data_repo

    # We have to locate the corresponding GPU data block
    # The UIDs in the GPU will be used to clear blacklisted IDs
    gpu_identifier = SourceIdentifier(identifier.start_ts, identifier.end_ts, "gpu")
    if(not data_repo.contains(gpu_identifier)):
        raise Exception("Failed to analyze cpu only jobs, the corresponding gpu data_block could not be found.")
    
    gpu_df = data_repo.get(gpu_identifier)
    if(has_time_column(gpu_df)):
        gpu_df = clear_time_column(gpu_df)

    df = data_repo.get(identifier)
    if(has_time_column(df)):
        df = clear_time_column(df)

    gpu_greater_than_zero_cols = [col for col in gpu_df.columns if gpu_df[col].sum() > 0]
    gpu_df = gpu_df[gpu_greater_than_zero_cols].fillna(0)
    gpu_uuid = set(gpu_df.columns.str.extract(r'uid="([^"]+)"')[0].dropna())

    df = clear_duplicate_uids(df)
    df = clear_blacklisted_uids(df, gpu_uuid)

    return _analyze_jobs_final(df, True)

def analyze_jobs_total(identifier):
    df = ProgramData().data_repo.get(identifier)
    return df['Count'].sum()

def analyze_all_jobs_total(cpu_identifier):
    src_id = cpu_identifier.on

    cpu_jobs_tot = ProgramData().data_repo.get(cpu_identifier)
    gpu_jobs_tot = ProgramData().data_repo.get(AnalysisIdentifier(SourceIdentifier(src_id.start_ts, src_id.end_ts, "gpu"), "gpujobstotal"))

    return cpu_jobs_tot + gpu_jobs_tot
#endregion