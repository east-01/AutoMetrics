from src.program_data.program_data import ProgramData
from src.plugin_mgmt.plugins import IngestPlugin
from src.data.data_repository import DataRepository

from src.program_data.config import ConfigurationException

# Ingests the timeline into a series of TimestampIdentifiers
class IngestTimeline(IngestPlugin):
    def verify_config_section(self, config_section):
        if(config_section is not None):
            raise ConfigurationException("The configuration for IngestTimeline is expected to be empty.")
        return True

    def ingest(self, prog_data: ProgramData, config_section: dict) -> DataRepository:
        return DataRepository()