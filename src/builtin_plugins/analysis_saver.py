from collections.abc import Iterable
import os
import pandas as pd

from src.data.data_repository import DataRepository
from src.data.filters import *
from src.parameter_utils import ConfigurationException
from src.plugin_mgmt.plugins import Saver
from src.program_data import ProgramData
from src.utils.fileutils import append_line_to_file
from src.utils.timeutils import get_range_printable

class AnalysisSaver(Saver):
    """ The AnalysisSaver will attempt to cover all AnalysisIdentifiers and their extensions. It
            can save standard AnalysisIdentifiers and MetaAnalysisIdentifiers. There are two types
            of result: text result and dataframe; text results will be put into a single .txt file
            while dataframes will be saved as .csvs """

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
        # Handle if there is a whitelist in the config section
        if(config_section is not None and "whitelist" in config_section):
            # If there is a whitelist, filter by the analysis type of the whitelisted analysis and
            #   extend identifiers untill all whitelisted analyses are consumed.
            for whitelisted_analysis in config_section["whitelist"]:
                addtl_identifiers = data_repo.filter_ids(filter_analyis_type(whitelisted_analysis))
                identifiers.extend(addtl_identifiers)
        else:
            # If no whitelist, we'll just get all of the AnalysisIdentifiers
            identifiers = data_repo.filter_ids(filter_type(AnalysisIdentifier))

        # Loop through each result given by identifiers saving it by its type
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
        
        self.save_text_results()

        return list(self.has_written)

    def save_analysis(self, identifier: AnalysisIdentifier):

        data_repo: DataRepository = self.prog_data.data_repo
        src_id = identifier.find_base()
        result = data_repo.get_data(identifier)        

        readable_period = "Unknown period"
        if(src_id is not None):
            readable_period = get_range_printable(src_id.start_ts, src_id.end_ts, 3600)

        # Make sure the directory holding these results is there
        analysis_dir_path = os.path.join(self.base_path, f"{readable_period} analysis")
        if(not os.path.exists(analysis_dir_path)):
            os.mkdir(analysis_dir_path)

        # Ensure there is a list to append to
        if(src_id not in self.text_results.keys()):
            self.text_results[src_id] = []

        # Save result to CSV if it's a dataframe, save to text file otherwise
        if(isinstance(result, pd.DataFrame)):
            path = os.path.join(analysis_dir_path, f"{identifier.analysis}.csv")
            print(f"  Saving analysis file \"{path}\"")
            result.to_csv(path, index=False)

            self.has_written.add(path)
        else:
            if(isinstance(result, Iterable) and not isinstance(result, str)):
                result = ", ".join(result)
            else:
                result = str(result)

            self.text_results[src_id].append(f"{identifier.analysis}: {result}")

    def save_text_results(self):
        path = os.path.join(self.base_path, f"text_results.txt")

        # Save text results, order keys by start time
        ordered_keys = sorted(self.text_results.keys(), key=lambda x: x.start_ts if hasattr(x, "start_ts") and not None else -float('inf'))
        for identifier in ordered_keys:

            if(len(self.text_results[identifier]) == 0):
                continue
            
            out_name = str(identifier) if identifier else "Unknown period"
            to_append = f"For {out_name}:\n  {"\n  ".join(self.text_results[identifier])}"

            overwrite = path not in self.has_written
            append_line_to_file(path, to_append, overwrite)

            self.has_written.add(path)

        if(path in self.has_written):
            print(f"  Saved analysis text results file \"{path}\"")

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

        self.has_written.add(path)