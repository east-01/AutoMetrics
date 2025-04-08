from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass(frozen=True)
class Identifier(ABC):
    @abstractmethod
    def __hash__(self) -> int:
        pass

    @abstractmethod
    def __eq__(self, other) -> bool:
        pass

    @abstractmethod
    def __str__(self) -> str:
        pass

@dataclass(frozen=True)
class SourceIdentifier(Identifier):
    start_ts: int
    end_ts: int
    type: str

    def __hash__(self) -> int:
        return hash((self.start_ts, self.end_ts, self.type))

    def __eq__(self, other) -> bool:
        return isinstance(other, SourceIdentifier) and self.start_ts == other.start_ts and self.end_ts == other.end_ts and self.type == other.type

    def __str__(self) -> str:
        return f"sourcedata {self.type}:{self.start_ts}-{self.end_ts}"
    
@dataclass(frozen=True)
class AnalysisIdentifier(Identifier):
    on: Identifier
    analysis: str

    def __hash__(self) -> int:
        return hash((self.on, self.analysis))

    def __eq__(self, other) -> bool:
        return isinstance(other, AnalysisIdentifier) and self.on == other.on and self.analysis == other.analysis

    def __str__(self) -> str:
        return f"{self.analysis}({self.on})"
    
    def find_source(self) -> SourceIdentifier:
        """
        Find the source identifier for this analysis. This is necessary as there can be multiple
          nested AnalysisIdentifiers.

        Returns:
            SourceIdentifier: The base source identifier that this analysis is based off of.
        """
        on = self.on
        while(not isinstance(on, SourceIdentifier)):
            on = on.on
        return on
    
@dataclass(frozen=True)
class VisIdentifier(Identifier):
    of: Identifier
    graph_type: str

    def __hash__(self) -> int:
        return hash(("vis", self.of, self.graph_type))

    def __eq__(self, other) -> bool:
        return isinstance(other, VisIdentifier) and self.of == other.of and self.graph_type == other.graph_type

    def __str__(self) -> str:
        return f"vis of {self.of}"