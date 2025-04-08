# This code is repackaged from Tide2.ipynb in https://github.com/SDSU-Research-CI/rci-helpful-scripts
import pandas as pd

from src.data.data_repository import DataRepository
from src.analysis.grafana_df_cleaning import has_time_column, clear_time_column
from src.data.ingest.grafana_df_analyzer import extract_column_data

def analyze_hours_byns(identifier, data_repo: DataRepository):
    df = data_repo.get_data(identifier)

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

def analyze_hours_total(identifier, data_repo: DataRepository):
    # Retrieve the corresponding analysis thats already been performed
    df = data_repo.get_data(identifier)
    return df['Hours'].sum()