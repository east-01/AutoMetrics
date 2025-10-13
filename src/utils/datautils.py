from src.data.data_repository import DataRepository
from src.data.filters import filter_analyis_type

def resolve_analysis(data_repo: DataRepository, start_ts, end_ts, analysis_name, key_method=None, unique_key=None):
    """ Resolve an analysis identifier with a specific analysis and matching start and 
            end timestamps. Matches with the key method as well. """

    if((key_method is not None) ^ (unique_key is not None)):
        raise Exception("Can't resolve analysis, a key_method or unique_key provided without the other value being provided! If key_method is there, ensure unique_key is there too- other way around as well.")

    for identifier in data_repo.get_ids():
        if(not filter_analyis_type(analysis_name)(identifier)):
            continue

        if(key_method is not None and unique_key is not None):
            key_val = key_method(identifier)
            if(key_val != unique_key):
                continue

        src_id = identifier.find_base()

        if(src_id.start_ts == start_ts and src_id.end_ts == end_ts):
            return identifier
        
    return None