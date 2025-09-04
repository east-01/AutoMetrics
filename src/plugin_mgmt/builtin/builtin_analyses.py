from dataclasses import dataclass
from typing import Callable

from src.data.identifier import Identifier
from src.plugin_mgmt.plugins import Analysis
from src.data.data_repository import DataRepository

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
    key_method: Callable[[Identifier], str]
    """
    The key_method is a callable that takes the identifier and returns some key value from it, this
        key value is used to perform meta analyses on only the identifiers that have matching keys.
    """

@dataclass(frozen=True)
class VerificationAnalysis(Analysis):
    """
    The VerificationAnalysis exists to check other Analysis results, one application for this is
        checking if the amount of hours calculated > amount of hours in time frame.
    """
    targ_analysis: str
    method: Callable[[Identifier, DataRepository], bool]