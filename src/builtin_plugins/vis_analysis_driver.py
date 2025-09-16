import matplotlib.pyplot as plt
import pandas as pd

from src.builtin_plugins.vis_dataclasses import VisIdentifier, VisualAnalysis, VisSettings, VisBarSettings, VisTimeSettings
from src.builtin_plugins.vis_impls import plot_simple_bargraph, plot_time_series
from src.builtin_plugins.vis_variables import VisualizationVariables
from src.data.data_repository import DataRepository
from src.data.filters import *
from src.plugin_mgmt.plugins import AnalysisDriverPlugin

class VisualAnalysisDriver(AnalysisDriverPlugin):
    """ The VisualAnalysisDriver will perform VisualAnalyses, taking in the VisSettings and
            applying them to the provided analysis. Visualized plots are stored with VisIdentifiers
            in the DataRepository.
    """
    SERVED_TYPE=VisualAnalysis

    def run_analysis(self, analysis: VisualAnalysis, prog_data, config_section: dict):
        """ Loop through the identifiers returned by the VisualAnalysis' filter, performing the
                corresponding visualization specified by the VisualAnalysis. Store each plot with a
                VisIdentifier.
        """
        vis_settings = analysis.vis_settings

        data_repo: DataRepository = prog_data.data_repo
        identifiers = data_repo.filter_ids(analysis.filter)

        for identifier in identifiers:

            analysis_result = data_repo.get_data(identifier)

            if(analysis_result is None or not isinstance(analysis_result, pd.DataFrame)):
                raise Exception(f"ERROR: Can't visualize analysis {analysis} it's result is not a pd.DataFrame ({type(analysis_result)})")

            vis_title = vis_settings.title
            vis_subtext = ""
            if(isinstance(vis_settings, VisBarSettings) and vis_subtext is not None):
                vis_subtext = vis_settings.subtext

            if(vis_settings.variables is not None):
                vis_variables = VisualizationVariables(prog_data, identifier, vis_settings.variables)
                vis_title = vis_variables.apply_variables(vis_title)
                vis_subtext = vis_variables.apply_variables(vis_subtext)

            vis_color = vis_settings.color

            # Plot figure based off visualization type
            fig = None
            if(isinstance(vis_settings, VisBarSettings)):
                fig = plot_simple_bargraph(data_repo, identifier, vis_title, vis_subtext, vis_color)
            elif(isinstance(vis_settings, VisTimeSettings)):
                fig = plot_time_series(data_repo, identifier, vis_title, vis_color)
            else:
                raise Exception(f"Don't know how to handle visualization type \"{type(vis_settings)}\"")

            # Create vis identifier and add to repo
            vis_identifier = VisIdentifier(identifier, type(VisSettings).__name__)
            data_repo.add(vis_identifier, fig)

            plt.close(fig)