from src.program_data.program_data import ProgramData
from src.plugin_mgmt.plugins import IngestPlugin
from src.data.data_repository import DataRepository

# Ingests the timeline into a series of TimestampIdentifiers
class IngestTimeline(IngestPlugin):
    def ingest(self, prog_data: ProgramData) -> DataRepository:
        return DataRepository()