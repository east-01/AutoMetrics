from dataclasses import dataclass
from typing import Callable

from src.data.identifier import Identifier
from src.plugin_mgmt.plugins import Analysis

@dataclass(frozen=True)
class MetaAnalysis(Analysis):
    analysis_list: list[str]

@dataclass(frozen=True)
class SimpleAnalysis(Analysis):
    filter: Callable[[Identifier], bool]