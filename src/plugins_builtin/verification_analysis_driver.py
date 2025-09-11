from dataclasses import dataclass
from typing import Callable

from src.data.identifier import Identifier
from src.plugin_mgmt.plugins import Analysis
from src.data.data_repository import DataRepository
from src.plugin_mgmt.plugins import AnalysisDriverPlugin
from src.data.filters import filter_analyis_type

import src.plugins_builtin.verification_analysis_driver as pkg

@dataclass(frozen=True)
class VerificationAnalysis(Analysis):
    """
    The VerificationAnalysis exists to check other Analysis results, one application for this is
        checking if the amount of hours calculated > amount of hours in time frame.
    """
    targ_analysis: str
    method: Callable[[Identifier, DataRepository], bool]

class VerificationException(Exception):
    pass

class VerificationDriver(AnalysisDriverPlugin):
    """
    The VerificationDriver runs VerificationAnalyses where the analysis data is checked. Results
        from these runs do not get put into the DataRepository, only exceptions are thrown when
        data is invalid.
    """
    SERVED_TYPE = pkg.VerificationAnalysis

    def run_analysis(self, analysis: pkg.VerificationAnalysis, prog_data, config_section: dict):
        data_repo: DataRepository = prog_data.data_repo

        identifiers = data_repo.filter_ids(filter_analyis_type(analysis.targ_analysis))

        # If the length of the target identifiers is zero then we can't perform and fulfill 
        #   the analysis.
        if(len(identifiers) == 0):
            return

        for identifier in identifiers:
            if(not analysis.method(identifier, data_repo)):
                raise VerificationException(f"Failed to verify analysis \"{analysis.name}\" for identifier {identifier}")