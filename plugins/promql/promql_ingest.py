import os
import yaml

import json

from src.data.data_repository import DataRepository
from src.plugin_mgmt.plugins import IngestPlugin
from src.program_data.program_data import ProgramData
from src.program_data.config import ConfigurationException

from plugins.promql.query_ingest import run

class PromQLIngestController(IngestPlugin):
    def verify_config_section(self, config_section) -> bool:
        if(not isinstance(config_section, list)):
            raise ConfigurationException("The config section is not in the form of a list. PromQLIngestController config section expects a list of names for query configs stored in the plugin_dir/ingest_configs/ directory.")

        dir_path = os.path.dirname(os.path.abspath(__file__))
        for cfg_name in config_section:
            file_path = os.path.join(dir_path, "ingest_configs", f"{cfg_name}.yaml")
            if(not os.path.exists(file_path)):
                raise ConfigurationException(f"Failed to find ingest config named \"{cfg_name}\" was expecting to find the file at: {file_path}")

    def ingest(self, prog_data: ProgramData, config_section: dict) -> DataRepository:
        
        data_repo = DataRepository()

        dir_path = os.path.dirname(os.path.abspath(__file__))
        for cfg_name in config_section:
            file_path = os.path.join(dir_path, "ingest_configs", f"{cfg_name}.yaml")
            if(not os.path.exists(file_path)):
                raise Exception(f"Failed to find ingest config named \"{cfg_name}\" was expecting to find the file at: {file_path}")
            
            with open(file_path, "r") as file:
                data = yaml.safe_load(file)
            
            data["cfg_name"] = cfg_name

            returned_data_repo = run(data, prog_data.timeline)

            # Save a data_repo.join() step if the existing repo is already empty
            if(data_repo.count() > 0):
                data_repo.join(returned_data_repo)
            else:
                data_repo = returned_data_repo

        return data_repo

