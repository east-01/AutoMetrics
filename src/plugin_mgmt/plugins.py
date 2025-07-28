from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable

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
    required_analyses: list[str]
    required_ingests: list[str]
    filter: Callable[[Identifier], bool]

class AnalysisPlugin(ABC):
    @abstractmethod
    def get_analyses(self) -> list[Analysis]:
        pass