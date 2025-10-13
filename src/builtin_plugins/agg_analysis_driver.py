from dataclasses import dataclass
from typing import Callable, Any
import pandas as pd

from src.data.data_repository import DataRepository
from src.data.filters import filter_type, filter_analyis_type
from src.data.identifier import Identifier, AggregateAnalysisIdentifier
from src.plugin_mgmt.plugins import Analysis, AnalysisDriverPlugin
from src.utils.timeutils import get_range_printable

import src.builtin_plugins.agg_analysis_driver as pkg

@dataclass(frozen=True)
class AggregateAnalysis(Analysis):
    """
    An aggregate analysis is like a 
    """
    filter: Callable[[Identifier], bool]
    """ A DataRepository filter. """
    key_method: Callable[[Identifier], str]
    """
    The key_method is a callable that takes the identifier and returns some key value from it, this
        key value is used to perform aggregate analyses on only the identifiers that have matching keys.
    """
    method: Callable[[list[Identifier], DataRepository], Any]

class AggregateAnalysisDriver(AnalysisDriverPlugin):
    SERVED_TYPE = pkg.AggregateAnalysis

    def run_analysis(self, analysis: pkg.AggregateAnalysis, prog_data, config_section: dict) -> DataRepository:
        """
        A meta analysis takes in a list of analysis names and creates a table with columns:
        Period, analysis1, analysis2, ...
        Each unique period in the DataRepository will correspond to a row in the meta analysis table.
        """

        data_repo: DataRepository = prog_data.data_repo

        key_method = analysis.key_method
        if(key_method is None):
            key_method = lambda x: None
        filter_method = analysis.filter
        analysis_method = analysis.method

        unique_keys = get_all_unique_keys(data_repo, analysis.filter, key_method)

        if(len(unique_keys) == 0):
            raise Exception(f"Failed to run aggregate analysis \"{analysis.name}\": key method \"{key_method.__name__}\" couldn't find keys.")

        for unique_key in unique_keys:
            
            keyed_filter = lambda id: filter_method(id) and key_method(id) == unique_key
            identifiers = data_repo.filter_ids(keyed_filter)

            result = analysis_method(identifiers, data_repo)

            out_identifier = AggregateAnalysisIdentifier(None, analysis.name, unique_key)
            data_repo.add(out_identifier, result)

def get_all_unique_keys(data_repo: DataRepository, filter_method, key_method):
    """ List form for analysis_names of get_unique_keys. """

    out_set = set()

    identifiers = data_repo.filter_ids(filter_method)
    if(len(identifiers) == 0):
        raise Exception("Failed to get unique keys. Filter yielded 0 identifiers.")

    for identifier in identifiers:
        out_set.add(key_method(identifier))
    
    return out_set