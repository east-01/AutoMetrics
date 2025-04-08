# This code is repackaged from Tide2.ipynb in https://github.com/SDSU-Research-CI/rci-helpful-scripts
import pandas as pd

from src.data.data_repository import DataRepository
from src.data.identifiers.identifier import SourceIdentifier, AnalysisIdentifier
from src.analysis.grafana_df_cleaning import clear_duplicate_uids, clear_blacklisted_uids, has_time_column, clear_time_column
from src.data.ingest.grafana_df_analyzer import extract_column_data

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

def analyze_jobs(identifier, data_repo: DataRepository):
    df = data_repo.get_data(identifier)
    if(has_time_column(df)):
        df = clear_time_column(df)

    # Load data frame, dropping columns with duplicate uids
    df = clear_duplicate_uids(df)
    return _analyze_jobs_final(df)

def analyze_cpu_only_jobs(identifier: SourceIdentifier, data_repo: DataRepository):
    # We have to locate the corresponding GPU data block
    # The UIDs in the GPU will be used to clear blacklisted IDs
    gpu_identifier = SourceIdentifier(identifier.start_ts, identifier.end_ts, "gpu")
    if(not data_repo.contains(gpu_identifier)):
        raise Exception("Failed to analyze cpu only jobs, the corresponding gpu data_block could not be found.")
    
    gpu_df = data_repo.get_data(gpu_identifier)
    if(has_time_column(gpu_df)):
        gpu_df = clear_time_column(gpu_df)

    df = data_repo.get_data(identifier)
    if(has_time_column(df)):
        df = clear_time_column(df)

    gpu_greater_than_zero_cols = [col for col in gpu_df.columns if gpu_df[col].sum() > 0]
    gpu_df = gpu_df[gpu_greater_than_zero_cols].fillna(0)
    gpu_uuid = set(gpu_df.columns.str.extract(r'uid="([^"]+)"')[0].dropna())

    df = clear_duplicate_uids(df)
    df = clear_blacklisted_uids(df, gpu_uuid)

    return _analyze_jobs_final(df, True)

def analyze_jobs_total(identifier, data_repo: DataRepository):
    df = data_repo.get_data(identifier)
    return df['Count'].sum()

def analyze_all_jobs_total(cpu_identifier: AnalysisIdentifier, data_repo: DataRepository):
    src_id = cpu_identifier.find_source()

    cpu_jobs_tot = data_repo.get_data(cpu_identifier)
    gpu_jobs_tot = data_repo.get_data(AnalysisIdentifier(AnalysisIdentifier(SourceIdentifier(src_id.start_ts, src_id.end_ts, "gpu"), "gpujobs"), "gpujobstotal"))

    return cpu_jobs_tot + gpu_jobs_tot