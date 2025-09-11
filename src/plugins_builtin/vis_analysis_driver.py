import matplotlib.pyplot as plt
import pandas as pd
from typing import Callable

from src.data.data_repository import DataRepository
from src.data.filters import *
from src.plugin_mgmt.plugins import Analysis, AnalysisDriverPlugin
from src.plugins_builtin.vis_impls import plot_simple_bargraph, plot_time_series
from src.plugins_builtin.vis_variables import VisualizationVariables

import src.plugins_builtin.vis_analysis_driver as pkg

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
class VisSettings():
    title: str
    variables: dict

@dataclass(frozen=True)
class VisBarSettings(VisSettings):
    subtext: str
    color: object

@dataclass(frozen=True)
class VisTimeSettings(VisSettings):
    color: dict

@dataclass(frozen=True)
class VisualAnalysis(Analysis):
    """
    The VisualAnalysis facilitates the generation of visualizations.
    """
    filter: Callable[[Identifier], bool]
    vis_settings: VisSettings

class VisualAnalysisDriver(AnalysisDriverPlugin):
    SERVED_TYPE=pkg.VisualAnalysis

    def run_analysis(self, analysis: pkg.VisualAnalysis, prog_data, config_section: dict):
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
            if(isinstance(vis_settings, pkg.VisBarSettings)):
                fig = plot_simple_bargraph(data_repo, identifier, vis_title, vis_subtext, vis_color)
            elif(isinstance(vis_settings, pkg.VisTimeSettings)):
                fig = plot_time_series(data_repo, identifier, vis_title, vis_color)
            else:
                raise Exception(f"Don't know how to handle visualization type \"{type(vis_settings)}\"")

            # Create vis identifier and add to repo
            vis_identifier = pkg.VisIdentifier(identifier, type(VisSettings).__name__)
            data_repo.add(vis_identifier, fig)

            plt.close(fig)