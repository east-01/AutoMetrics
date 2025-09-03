from src.program_data.program_data import ProgramData
from src.plugin_mgmt.plugins import IngestPlugin
from src.data.data_repository import DataRepository

from src.data.timeline import Timeline
from src.data.identifier import TimeStampIdentifier

# Ingests the timeline into a series of TimestampIdentifiers
class IngestTimeline(IngestPlugin):
    def ingest(self, prog_data: ProgramData, config_section: dict) -> DataRepository:

        timeline: Timeline = prog_data.timeline
        data_repo: DataRepository = DataRepository()

        print(f"IngestTimeline: {len(timeline.main_periods)} main period(s).")

        for period in timeline.main_periods:
            identifier = TimeStampIdentifier(period[0], period[1])
            data_repo.add(identifier, None)

        return data_repo