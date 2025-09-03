from dataclasses import dataclass
from typing import Callable

from src.data.identifier import Identifier
from src.plugin_mgmt.plugins import Analysis

@dataclass(frozen=True)
class SimpleAnalysis(Analysis):
    filter: Callable[[Identifier], bool]
    method: Callable

@dataclass(frozen=True)
class MetaAnalysis(Analysis):
    """
    A MetaAnalysis takes results for each of the analyses specified in the list from each time
        period, creating a table of results over time.
    """
    analysis_list: list[str]    