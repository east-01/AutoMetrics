import os
import pandas as pd

from src.program_data.program_data import ProgramData
from src.data.data_repository import DataRepository
from src.data.filters import *
from src.plugin_mgmt.plugins import Saver
from src.utils.fileutils import append_line_to_file
from src.utils.timeutils import get_range_printable
from src.program_data.config import ConfigurationException

class AnalysisSaver(Saver):
    def verify_config_section(self, config_section):
        if(config_section is None):
            return True
        
        if("whitelist" not in config_section):
            raise ConfigurationException("A config section was provided, but no whitelist section exists.")

        if(not isinstance(config_section["whitelist"], list)):
            raise ConfigurationException("The config section for \"whitelist\" should be in the form of a list.")
        
        return True

    def save(self, prog_data: ProgramData, config_section: dict, base_path: str):

        self.prog_data = prog_data
        data_repo: DataRepository = prog_data.data_repo

        self.base_path = base_path
        if(not os.path.exists(self.base_path)):
            os.makedirs(self.base_path, exist_ok=True)

        # Keep a list of files we've written to so we can clear the contents previously existing files
        self.has_written = set()
        # Keep a dict of SourceIdentifiers and their corresponding text results
        self.text_results = {}

        identifiers = []
        if(config_section is not None and "whitelist" in config_section):
            for whitelisted_analysis in config_section["whitelist"]:
                addtl_identifiers = data_repo.filter_ids(filter_analyis_type(whitelisted_analysis))
                identifiers.extend(addtl_identifiers)
        else:
            identifiers = data_repo.filter_ids(filter_type(AnalysisIdentifier))

        for identifier in identifiers:
            identifier: AnalysisIdentifier = identifier

            result = data_repo.get_data(identifier)

            # Only save results that exist
            if(result is None):
                return

            if(isinstance(identifier, MetaAnalysisIdentifier)):
                self.save_meta_analysis(identifier)
            else:
                self.save_analysis(identifier)

        # Save text results, order keys by start time
        ordered_keys = sorted(self.text_results.keys(), key=lambda x: x.start_ts)
        for identifier in ordered_keys:

            if(len(self.text_results[identifier]) > 0):
                path = os.path.join(self.base_path, f"text_results.txt")
                out_file_name = get_range_printable(identifier.start_ts, identifier.end_ts, 3600)
                to_append = f"For {out_file_name}:\n  {"\n  ".join(self.text_results[identifier])}"

                append_line_to_file(path, to_append, path not in self.has_written)
                self.has_written.add(path)

    def save_analysis(self, identifier: AnalysisIdentifier):

        data_repo: DataRepository = self.prog_data.data_repo

        result = data_repo.get_data(identifier)
        
        src_id = identifier.find_base()

        # Make sure the directory holding these results is there
        readable_period = get_range_printable(src_id.start_ts, src_id.end_ts, 3600)
        analysis_dir_path = os.path.join(self.base_path, f"{readable_period} analysis")
        if(not os.path.exists(analysis_dir_path)):
            os.mkdir(analysis_dir_path)

        if(src_id not in self.text_results.keys()):
            self.text_results[src_id] = []

        # Save result to CSV if it's a dataframe, save to text file otherwise
        if(isinstance(result, pd.DataFrame)):
            path = os.path.join(analysis_dir_path, f"{identifier.analysis}.csv")
            print(f"  Saving analysis file \"{path}\"")
            result.to_csv(path, index=False)
        else:
            self.text_results[src_id].append(f"{identifier.analysis}: {str(result)}")

    def save_meta_analysis(self, identifier):
        data_repo: DataRepository = self.prog_data.data_repo

        result = data_repo.get_data(identifier)
        
        readable_period = "Entire range"

        # Make sure the directory holding these results is there
        analysis_dir_path = os.path.join(self.base_path, f"{readable_period} analysis")
        if(not os.path.exists(analysis_dir_path)):
            os.mkdir(analysis_dir_path)

        # Save as a DataFrame, meta analyses are always DataFrames
        path = os.path.join(analysis_dir_path, f"{identifier.analysis}.csv")
        print(f"  Saving analysis file \"{path}\"")
        result.to_csv(path, index=False)
                
            
            