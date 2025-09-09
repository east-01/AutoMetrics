import pandas as pd
import numpy as np

from src.data.identifier import AnalysisIdentifier, MetaAnalysisIdentifier
from src.data.data_repository import DataRepository
from src.plugin_mgmt.plugins import AnalysisDriverPlugin
from src.plugin_mgmt.builtin.builtin_analyses import SimpleAnalysis, MetaAnalysis, VerificationAnalysis
from src.data.filters import filter_analyis_type
from src.utils.timeutils import get_range_printable
from src.data.filters import filter_type
from src.data.identifier import TimeStampIdentifier

class SimpleAnalysisDriver(AnalysisDriverPlugin):
    SERVED_TYPE = SimpleAnalysis

    def run_analysis(self, analysis: SimpleAnalysis, prog_data, config_section: dict):
        data_repo: DataRepository = prog_data.data_repo

        # Get filter and apply to data_repo, the filter finds the Identifiers that the analysis
        #   will use in its calculation.
        analysis_filter = analysis.filter
        identifiers = data_repo.filter_ids(analysis_filter)

        # If the length of the target identifiers is zero then we can't perform and fulfill 
        #   the analysis.
        if(len(identifiers) == 0):
            return

        for identifier in identifiers:
            analysis_result = analysis.method(identifier, data_repo)

            # Generate identifier and add to repository.
            analysis_identifier = AnalysisIdentifier(identifier, analysis.name)
            data_repo.add(analysis_identifier, analysis_result)

class MetaAnalysisDriver(AnalysisDriverPlugin):
    SERVED_TYPE = MetaAnalysis

    def run_analysis(self, analysis: MetaAnalysis, prog_data, config_section: dict) -> DataRepository:
        """
        A meta analysis takes in a list of analysis names and creates a table with columns:
        Period, analysis1, analysis2, ...
        Each unique period in the DataRepository will correspond to a row in the meta analysis table.
        """

        data_repo: DataRepository = prog_data.data_repo
        # The list of analyses that this meta-analysis is compiling
        sub_analyses = analysis.prereq_analyses 
        key_method = analysis.key_method
        if(key_method is None):
            key_method = lambda x: None

        unique_keys = get_all_unique_keys(data_repo, sub_analyses, key_method)

        if(len(unique_keys) == 0):
            raise Exception(f"Failed to run meta analysis, key method \"{key_method}\" couldn't find keys.")

        timestamps = data_repo.filter_ids(filter_type(TimeStampIdentifier, strict=True))
        timestamps.sort(key=lambda id: id.start_ts)

        print(f"Timestamps:", timestamps)

        if(len(timestamps) == 0):
            raise Exception(f"Failed to run meta analysis, there were no Timestamps loaded. Is !!IngestTimeline!! configured?")

        for unique_key in unique_keys:

            out_df = pd.DataFrame(columns=(["Period"]+sub_analyses))

            def resolve_analysis(start_ts, end_ts, analysis_name):
                """ Resolve an analysis identifier with a specific analysis and matching start and 
                        end timestamps. Matches with the key method as well. """
                
                for identifier in data_repo.filter_ids(filter_analyis_type(analysis_name)):
                    key_val = key_method(identifier)
                    if(key_val != unique_key):
                        continue

                    src_id = identifier.find_base()

                    if(src_id.start_ts == start_ts and src_id.end_ts == end_ts):
                        return identifier
                    
                return None

            for identifier in timestamps:
                start_ts = identifier.start_ts
                end_ts = identifier.end_ts

                readable_period = get_range_printable(start_ts, end_ts, 3600)
                row = [readable_period]

                for sub_analysis in sub_analyses:
                    analysis_id = resolve_analysis(start_ts, end_ts, sub_analysis)
                    if(analysis_id is None):
                        row.append(0)
                        continue

                    analysis_result = data_repo.get_data(analysis_id)
                    
                    if(not verify_result_for_meta(analysis_result)):
                        row.append(0)
                        continue

                    row.append(float(analysis_result))

                out_df.loc[len(out_df)] = row
            
            out_identifier = MetaAnalysisIdentifier(None, analysis.name, unique_key)
            metadata = {
                "periods": [(id.start_ts, id.end_ts) for id in timestamps]
            }

            data_repo.add(out_identifier, out_df, metadata)

def verify_result_for_meta(result):
    """ Verify if the object is valid to be used in a meta analysis- ensures it exists and is a single value. """
    # Ensure result
    if(result is None):
        return False

    # Ensure result is a number
    is_number = isinstance(result, int) or isinstance(result, float) or isinstance(result, np.int_) or isinstance(result, np.float32) or isinstance(result, np.float64)
    if(not is_number):                    
        raise ValueError(f"Error while performing meta analysis, the result data type is {type(result)} when it should be a number.")
    
    return True

def get_all_unique_keys(data_repo: DataRepository, analysis_names: list[str], key_method):
    """ List form for analysis_names of get_unique_keys. """

    out_set = set()

    for analysis_name in analysis_names:
        keys = get_unique_keys(data_repo, analysis_name, key_method)
        out_set.update(keys)
    
    return out_set

def get_unique_keys(data_repo: DataRepository, analysis_name: str, key_method):
    """ Get the unique set of keys that are retrieved by the key_method from this specific
            analysis. Serves as the grouping key for the meta-analysis. """

    identifiers = data_repo.filter_ids(filter_analyis_type(analysis_name))
    return set([key_method(id) for id in identifiers])

class VerificationException(Exception):
    pass

class VerificationDriver(AnalysisDriverPlugin):
    """
    The VerificationDriver runs VerificationAnalyses where the analysis data is checked. Results
        from these runs do not get put into the DataRepository, only exceptions are thrown when
        data is invalid.
    """
    SERVED_TYPE = VerificationAnalysis

    def run_analysis(self, analysis: VerificationAnalysis, prog_data, config_section: dict):
        data_repo: DataRepository = prog_data.data_repo

        identifiers = data_repo.filter_ids(filter_analyis_type(analysis.targ_analysis))

        # If the length of the target identifiers is zero then we can't perform and fulfill 
        #   the analysis.
        if(len(identifiers) == 0):
            return

        for identifier in identifiers:
            if(not analysis.method(identifier, data_repo)):
                raise VerificationException(f"Failed to verify analysis \"{analysis.name}\" for identifier {identifier}")