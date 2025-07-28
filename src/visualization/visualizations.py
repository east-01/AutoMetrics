import calendar
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import pandas as pd
import numpy as np
import datetime

from src.program_data.program_data import ProgramData
from src.data.data_repository import DataRepository
from src.utils.timeutils import get_range_as_month
from src.data.filters import *
from src.visualization.vis_impls import *
from src.visualization.vis_variables import VisualizationVariables
from plugins.grafana.settings import settings
from src.data.identifiers.identifier import *

def vizualize(prog_data: ProgramData):
    data_repo: DataRepository = prog_data.data_repo

    # Filter identifiers that are analyses and have vis options
    analysis_type_lambda = filter_type(AnalysisIdentifier)
    is_vis_analysis_filter = lambda identifier: analysis_type_lambda(identifier) and "vis_options" in settings["analysis_settings"][identifier.analysis].keys()
    identifiers = data_repo.filter_ids(is_vis_analysis_filter)

    # Loop through visualizable analysis identifiers
    for identifier in identifiers:

        analysis = identifier.analysis
        analysis_options = settings["analysis_settings"][analysis]
        analysis_result = data_repo.get_data(identifier)

        if(analysis_result is None or not isinstance(analysis_result, pd.DataFrame)):
            print(f"ERROR: Can't visualize analysis {analysis} it's result is not a pd.DataFrame ({type(analysis_result)})")
            continue
        if(len(analysis_result) == 0):
            print(f"WARN: Skipping visualization {analysis} for {identifier} because its DataFrame was empty.")
            continue
        # Skip visualization if the option doesn't exist.
        if("vis_options" not in analysis_options or analysis_options["vis_options"] == None):
            continue

        vis_options = analysis_options["vis_options"]

        vis_title = vis_options["title"]
        if("subtext" in vis_options.keys()):
            vis_subtext = vis_options["subtext"]

        if("variables" in vis_options.keys()):
            vis_variables = VisualizationVariables(prog_data, identifier, vis_options["variables"])
            vis_title = vis_variables.apply_variables(vis_title)
            vis_subtext = vis_variables.apply_variables(vis_subtext)

        vis_color = vis_options["color"]

        # Plot figure based off visualization type
        fig = None
        vis_type = vis_options["type"]
        if(vis_type == "horizontalbar"):
            fig = plot_simple_bargraph(data_repo, identifier, vis_title, vis_subtext, vis_color)
        elif(vis_type == "timeseries"):
            fig = plot_time_series(data_repo, identifier, vis_title, vis_color)
        else:
            raise Exception(f"Don't know how to handle visualization type \"{vis_type}\"")

        # Create vis identifier and add to repo
        vis_identifier = VisIdentifier(identifier, vis_type)
        data_repo.add(vis_identifier, fig)

        plt.close(fig)

    return data_repo