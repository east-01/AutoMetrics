from src.plugin_mgmt.plugins import AnalysisDriverPlugin
from src.data.data_repository import DataRepository
from plugins.builtin.builtin_analyses import SimpleAnalysis, MetaAnalysis

class SimpleAnalysisDriver(AnalysisDriverPlugin):
    SERVED_TYPE = SimpleAnalysis

    def run_analysis(self, analysis: SimpleAnalysis, prog_data) -> DataRepository:
        data_repo: DataRepository = prog_data.data_repo

        # Get filter and apply to data_repo, the filter finds the Identifiers that the analysis
        #   will use in its calculation.
        analysis_filter = analysis.filter
        identifiers = data_repo.filter_ids(analysis_filter)

        # If the length of the target identifiers is zero then we can't perform and fulfill 
        #   the analysis.
        if(len(identifiers) == 0):
            return

        # Get the analysis method implementation for this specific analysis.
        # For example, if the analysis is cpuhours the analysis_method will be 
        #   src/analysis/implementations/analyze_hours_byns.
        analysis_method = analysis_options_methods[analysis]

        print(f"  Performing {analysis} on {len(identifiers)} target(s).")

        for identifier in identifiers:
            analysis_result = analysis_method(identifier, data_repo)

            # Generate identifier and add to repository.
            analysis_identifier = AnalysisIdentifier(identifier, analysis)
            data_repo.add(analysis_identifier, analysis_result)

        fulfilled_analyses.add(analysis)