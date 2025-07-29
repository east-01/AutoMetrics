from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable, Type

from src.program_data.program_data import ProgramData
from src.data.data_repository import DataRepository
from src.data.identifier import Identifier

class IngestPlugin(ABC):    
    @abstractmethod
    def ingest(self, prog_data: ProgramData) -> DataRepository:
        """
        Ingest data from a source.

        Returns:
            DataRepository: The ingested information.
        """
        pass

@dataclass(frozen=True)
class Analysis(ABC):
    name: str
    prereq_analyses: list[str]

class AnalysisPlugin(ABC):
    @abstractmethod
    def get_analyses(self) -> list[Analysis]:
        """
        Get the list of Analysis objects from this plugin.

        Returns:
            list[Analysis]: The list of analyses.
        """
        pass

class AnalysisDriverPlugin(ABC):
    SERVED_TYPE: Type[Analysis] = None

    @abstractmethod
    def run_analysis(self, analysis, prog_data) -> DataRepository:
        """
        
        """
        pass