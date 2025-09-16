from dataclasses import dataclass
from typing import Callable, Any

from src.data.data_repository import DataRepository
from src.data.identifier import Identifier, AnalysisIdentifier
from src.plugin_mgmt.plugins import Analysis, AnalysisDriverPlugin

import src.builtin_plugins.simple_analysis_driver as pkg

@dataclass(frozen=True)
class SimpleAnalysis(Analysis):
    """ The SimpleAnalysis is intented to be the "first layer" of analyses on top of ingested data.
        Since the SimpleAnalysis has a constrained pipeline, it means only simple operations can be
            performed. See details about the pipeline under SimpleAnalysisDriver. 
    """
    filter: Callable[[Identifier], bool]
    """ A DataRepository filter. """
    method: Callable[[Identifier, DataRepository], Any]

class SimpleAnalysisDriver(AnalysisDriverPlugin):
    """ The SimpleAnalysis process has two phases:
            Filter -> Method 
        The filter and method have specific signatures, see definitions in SimpleAnalysis class.
    """
    SERVED_TYPE = pkg.SimpleAnalysis

    def run_analysis(self, analysis: pkg.SimpleAnalysis, prog_data, config_section: dict):
        """ The SimpleAnalysisDriver will poll the DataRepository with the passed filter, then run 
                the passed method on it. Storing the data with the default AnalysisIdentifier. 
        """
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