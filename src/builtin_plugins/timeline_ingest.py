from src.data.data_repository import DataRepository
from src.data.identifier import TimeStampIdentifier
from src.data.timeline import Timeline
from src.plugin_mgmt.plugins import IngestPlugin
from src.program_data import ProgramData

# Ingests the timeline into a series of TimestampIdentifiers
class IngestTimeline(IngestPlugin):
    """ The IngestTimeline plugin takes the ProgramData's timeline and ingests plain 
            TimeStampIdentifiers for each main period, this data can be used by other analyses.
    """
    def ingest(self, prog_data: ProgramData, config_section: dict) -> DataRepository:
        """ Get the main periods from the ProgramData's Timeline, then ingest them as 
                TimeStampIdentifiers.
        """

        timeline: Timeline = prog_data.timeline
        data_repo: DataRepository = DataRepository()

        print(f"IngestTimeline: {len(timeline.main_periods)} main period(s).")

        for period in timeline.main_periods:
            identifier = TimeStampIdentifier(period[0], period[1])
            data_repo.add(identifier, None)

        return data_repo