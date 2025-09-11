import pandas as pd
import numpy as np
from dataclasses import dataclass
import typing
from typing import Callable

from src.data.identifier import AnalysisIdentifier
from src.data.data_repository import DataRepository
from src.plugin_mgmt.plugins import AnalysisDriverPlugin
from src.data.identifier import Identifier
from src.plugin_mgmt.plugins import Analysis

import src.plugins_builtin.simple_analysis_driver as pkg

@dataclass(frozen=True)
class SimpleAnalysis(Analysis):
    filter: Callable[[Identifier], bool]
    method: Callable

class SimpleAnalysisDriver(AnalysisDriverPlugin):
    SERVED_TYPE = pkg.SimpleAnalysis

    def run_analysis(self, analysis: pkg.SimpleAnalysis, prog_data, config_section: dict):
        data_repo: DataRepository = prog_data.data_repo

        # Get filter and apply to data_repo, the filter finds the Identifiers that the analysis
        #   will use in its calculation.
        analysis_filter = analysis.filter
        identifiers = data_repo.filter_ids(analysis_filter)

        # If the length of the target identifiers is zero then we can't perform and fulfill 
        #   the analysis.
        if(len(identifiers) == 0):
            return

        for identifier in identifiers:
            analysis_result = analysis.method(identifier, data_repo)

            # Generate identifier and add to repository.
            analysis_identifier = AnalysisIdentifier(identifier, analysis.name)
            data_repo.add(analysis_identifier, analysis_result)