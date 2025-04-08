import datetime
import calendar

from src.data.data_repository import DataRepository
from src.data.filters import *
from src.program_data.settings import settings
from src.utils.timeutils import get_range_printable, to_unix_ts, get_unix_timestamp_range

def process_periods(data_repo: DataRepository) -> DataRepository:
    """
    Take the current DataRepository and expand the periods to the nearest reference point. This
      should only be performed on a DataRepository that contains only SourceData, as any analyses
      will be invalidated.
    Currently only expands the reference frame to the start and end of each month.
        
    Args:
        data_repo (DataRepository): The identifier for the data and metadata.
    Returns:
        DataRepository: The processed DataRepository.
    Raises:
        ValueError: The DataRepository contains anything other than SourceIdentifiers, time stamps
          overlap.
    """
    if(len(data_repo.filter_ids(filter_type(SourceIdentifier))) != data_repo.count()):
        raise ValueError("The DataRepository contains non source identifiers.")

    new_data_repo = DataRepository()

    for type in settings["type_options"]:
        identifiers = data_repo.filter_ids(filter_source_type(type))
        identifiers.sort(key=lambda x: x.start_ts)

        for i, identifier in enumerate(identifiers):
            if(i < len(identifiers)-1 and identifier.end_ts > identifiers[i+1].start_ts):
                raise ValueError(f"Found overlapping identifiers: {identifier} and {identifiers[i+1]}")

            start_ts = identifier.start_ts
            start_dt = datetime.datetime.fromtimestamp(start_ts)
            start_range = get_unix_timestamp_range(start_dt.month, start_dt.year)
            if(start_ts != start_range[0]):
                print(f"WARN: Inferring time range start to the first second of the month {start_ts} -> {start_range[0]}")
                start_ts = start_range[0]

            end_ts = identifier.end_ts
            end_dt = datetime.datetime.fromtimestamp(end_ts)
            end_range = get_unix_timestamp_range(end_dt.month, end_dt.year)
            if(end_ts != end_range[1]):
                print(f"WARN: Inferring time range end to the last second of the month {end_ts} -> {end_range[1]}")
                end_ts = end_range[1]

            new_identifier = SourceIdentifier(int(start_ts), int(end_ts), identifier.type)
            data, metadata = data_repo.get(identifier)

            new_data_repo.add(new_identifier, data, metadata)

    return new_data_repo

def generate_metadata(data_repo: DataRepository, config):
     
    # Load readable period data at the end of all data loading; readable_period may be affected by 
    #   other DF names so we need to load it last.
    for identifier in data_repo.filter_ids(filter_type(SourceIdentifier)):
        start_ts = identifier.start_ts
        end_ts = identifier.end_ts
        
        metadata = data_repo.get_metadata(identifier)

        metadata["readable_period"] = get_range_printable(start_ts, end_ts, config['step'])

        fs_compat_name = metadata["readable_period"].replace("/", "_").replace(" ", "T").replace(":", "")
        metadata["out_file_name"] = f"{identifier.type}-{fs_compat_name}"

        data_repo.update_metadata(identifier, metadata)

    return data_repo