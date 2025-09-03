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
class TimeStampIdentifier(Identifier):
    """
    Identifier for a time range.
    """
    start_ts: int
    end_ts: int

    def __hash__(self) -> int:
        return hash((self.start_ts, self.end_ts))

    def __eq__(self, other) -> bool:
        return isinstance(other, TimeStampIdentifier) and self.start_ts == other.start_ts and self.end_ts == other.end_ts

    def __str__(self) -> str:
        return f"timestamps {self.start_ts}-{self.end_ts}"

@dataclass(frozen=True)
class AnalysisIdentifier(Identifier):
    """
    Identifier for an anlysis of something else, can either be a SourceIdentifier or another
      AnalysisIdentifier. This means there can be multiple layers of AnalysisIdentifiers before you
      reach the root SourceIdentifier. Use find_base() to find the root.
    """
    on: Identifier
    analysis: str

    def __hash__(self) -> int:
        return hash((self.on, self.analysis))

    def __eq__(self, other) -> bool:
        return isinstance(other, AnalysisIdentifier) and self.on == other.on and self.analysis == other.analysis

    def __str__(self) -> str:
        return f"{self.analysis}({self.on})"
    
    def find_base(self) -> Identifier:
        """
        Find the base identifier for this analysis (follow the AnalysisIdentifier.on tree until 
          root is found). This is necessary as there can be multiple nested AnalysisIdentifiers.

        Returns:
            Identifier: The base identifier that this analysis is based off of.
        """
        on = self.on
        while(on is not None and isinstance(on, AnalysisIdentifier)):
            on = on.on

        return on

    def is_meta_analysis(self):
        """
        Is this analysis identifier a meta analysis?

        Returns:
          bool: if this analysis identifier has a root SourceIdentifier
        """
        return self.find_base() is None

@dataclass(frozen=True)
class VisIdentifier(Identifier):
    """
    An identifier for a visualization of an analysis.
    """
    of: Identifier
    graph_type: str

    def __hash__(self) -> int:
        return hash(("vis", self.of, self.graph_type))

    def __eq__(self, other) -> bool:
        return isinstance(other, VisIdentifier) and self.of == other.of and self.graph_type == other.graph_type

    def __str__(self) -> str:
        return f"vis of {self.of}"
    
@dataclass(frozen=True)
class SummaryIdentifier(Identifier):
    """
    An identifier for a summary of a period, the start_ts and end_ts will match the corresponding
      SourceIdentifiers' start_ts and end_ts.
    """
    start_ts: int
    end_ts: int

    def __hash__(self) -> int:
        return hash((self.start_ts, self.end_ts))

    def __eq__(self, other) -> bool:
        return isinstance(other, SummaryIdentifier) and self.start_ts == other.start_ts and self.end_ts == other.end_ts

    def __str__(self) -> str:
        return f"summary of {self.start_ts}-{self.end_ts}"