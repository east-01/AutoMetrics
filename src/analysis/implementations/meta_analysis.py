import numpy as np
import pandas as pd

from src.program_data.program_data import ProgramData
from src.data.data_repository import DataRepository
from src.data.identifiers.identifier import *
from src.data.filters import *
from src.utils.timeutils import get_range_printable

def meta_analyze(analyses: list, data_repo: DataRepository):
    """
    A meta analysis takes in a list of analysis names and creates a table with columns:
      Period, analysis1, analysis2, ...
    Each unique period in the DataRepository will correspond to a row in the meta analysis table.
    """

    df = pd.DataFrame(columns=(["Period"]+analyses))

    # TODO: This seen() solution is temporary until I can bring in the dev versions period
    #   identifier. With this we can filter by TimeStampIdentifier then make that a set.
    seen = set()

    # identifiers = data_repo.filter_ids(filter_type(TimeStampIdentifier))
    src_identifiers = data_repo.filter_ids(filter_type(SourceIdentifier))
    src_identifiers.sort(key=lambda identifier: identifier.start_ts)

    periods = [] # Periods to be stored in meta data

    for identifier in src_identifiers:
        start_ts = identifier.start_ts
        end_ts = identifier.end_ts
        period = (start_ts, end_ts)
        if(period in seen):
            continue

        seen.add(period)
        periods.append(period)

        readable_period = get_range_printable(start_ts, end_ts, 3600)
        row = [readable_period]

        for analysis in analyses:
            analysis_id = resolve_analysis(data_repo, start_ts, end_ts, analysis)
            analysis_result = data_repo.get_data(analysis_id)
            
            # Ensure result
            if(analysis_result is None):
                row.append(0)
                continue

            # Ensure result is a number
            is_number = isinstance(analysis_result, int) or isinstance(analysis_result, float) or isinstance(analysis_result, np.int_) or isinstance(analysis_result, np.float32) or isinstance(analysis_result, np.float64)
            if(not is_number):                    
                raise ValueError(f"Error while performing meta analysis with analysis \"{analysis}\". The result data type is {type(analysis_result)} when it should be a number.")

            row.append(float(analysis_result))

        df.loc[len(df)] = row
    
    metadata = {
        "periods": periods
    }

    return df, metadata

def resolve_analysis(data_repo: DataRepository, start_ts, end_ts, analysis):
    """
    Resolve an analysis identifier with a specific analysis and matching start and end timestamps.
    """
    for identifier in data_repo.filter_ids(filter_analyis_type(analysis)):
        src_id: SourceIdentifier = identifier.find_source()

        if(src_id.start_ts == start_ts and src_id.end_ts == end_ts):
            return identifier
    return None