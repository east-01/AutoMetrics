from abc import ABC
from typing import Callable

from src.data.filters import *
from src.plugin_mgmt.plugins import Analysis

@dataclass(frozen=True)
class VisIdentifier(Identifier):
    """ An identifier for a visualization of an analysis. """
    of: Identifier
    graph_type: str

    def __hash__(self) -> int:
        return hash(("vis", self.of, self.graph_type))

    def __eq__(self, other) -> bool:
        return isinstance(other, VisIdentifier) and self.of == other.of and self.graph_type == other.graph_type

    def __str__(self) -> str:
        return f"vis of {self.of}"
    
@dataclass(frozen=True)
class VisSettings(ABC):
    """ Base settings for a visualization. Abstract, needs a concrete implementation to specify the
            type and details of a visualization.
    """
    title: str
    variables: dict

@dataclass(frozen=True)
class VisBarSettings(VisSettings):
    """ Visualization settings for a bar plot, adds subtext and color attributes for the graph. """
    subtext: str
    color: object

@dataclass(frozen=True)
class VisTimeSettings(VisSettings):
    """ Visualization settings for a time series plot, adds a color dict. """
    color: dict

@dataclass(frozen=True)
class VisualAnalysis(Analysis):
    """ The VisualAnalysis facilitates the generation of visualizations. """
    filter: Callable[[Identifier], bool]
    vis_settings: VisSettings