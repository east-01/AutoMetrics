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
from src.program_data.settings import settings
from src.data.identifiers.identifier import *

def vizualize(prog_data: ProgramData):
    data_repo: DataRepository = prog_data.data_repo

    is_vis_analysis_filter = lambda identifier: filter_type(AnalysisIdentifier) and "vis_options" in settings["analysis_settings"][identifier.analysis].keys()

    for identifier in data_repo.filter_ids(is_vis_analysis_filter):
        # analyses = prog_data.analysis_repo[identifier]
        # # Loop through each analysis that can be visualized
        # for analysis in analyses.keys():
        #     analysis_options = prog_data.settings["analysis_settings"][analysis]
        #     # Ensure that this is an analysis we can visualize
        #     if("vis_options" not in analysis_options.keys()):
        #         continue

        analysis = identifier.analysis
        analysis_options = settings["analysis_settings"][analysis]
        analysis_result = data_repo.get(identifier)
        if(analysis_result is None or not isinstance(analysis_result, pd.DataFrame)):
            print(f"ERROR: Can't visualize analysis {analysis} it's result is not a pd.DataFrame ({type(analysis_result)})")
            continue
        if(len(analysis_result) == 0):
            print(f"WARN: Skipping visualization {analysis} for {identifier} because its DataFrame was empty.")
            continue

        # Ensure that there is a dictionary for this identifier in the vis repo
        if(identifier not in prog_data.vis_repo.keys()):
            prog_data.vis_repo[identifier] = {}

        vis_options = analysis_options["vis_options"]
        vis_type = vis_options["type"]
        variables = vis_options["variables"]

        # Holds the variable name and parsed variable value
        parsed_variables = {}
        for variable_name in variables:
            # The analysis name that the variable wants to load
            targ_analysis = variables[variable_name]
            
            # Resolve the corresponding analysis variable with matching SourceIdentifier
            variable_value = None
            for comp_id in data_repo.filter_ids(filter_analyis_type(targ_analysis)):
                if(comp_id.find_source() == identifier.find_source()):
                    variable_value = data_repo.get_data(comp_id)

            if(variable_value is None):
                raise Exception(f"Failed to resolve corresponding analysis variable for {targ_analysis}, current SourceID: {identifier.find_source()}")

            parsed_variables[variable_name] = variable_value

        start_ts, end_ts = identifier[0]
        range_data = get_range_as_month(start_ts, end_ts, prog_data.config['step'])
        parsed_variables["MONTH"] = calendar.month_name[range_data["month"]]
        parsed_variables["YEAR"] = range_data["year"]

        def apply_variables(text):
            for variable_name in parsed_variables:
                text = text.replace(f"%{variable_name}%", str(parsed_variables[variable_name]))
            return text

        vis_title = apply_variables(vis_options["title"])
        vis_subtext = apply_variables(vis_options["subtext"])
        vis_color = vis_options["color"]

        vis_identifier = VisIdentifier(identifier, vis_type)
        fig = plot_simple_bargraph(analysis_result, vis_title, vis_subtext, vis_color)

        data_repo.add(vis_identifier, fig)

        plt.close(fig)

    # for meta_analysis_key in prog_data.meta_analysis_repo.keys():
    #     meta_analysis_result = prog_data.meta_analysis_repo[meta_analysis_key]
    #     if(meta_analysis_result is None):
    #         continue

    #     vis_options = prog_data.settings["meta_analysis_options"][meta_analysis_key]["vis_options"]
    #     vis_title = apply_variables(vis_options["title"])
    #     vis_colors = vis_options["colors"]

    #     if("meta" not in prog_data.vis_repo.keys()):
    #         prog_data.vis_repo["meta"] = {}

    #     prog_data.vis_repo["meta"][meta_analysis_key] = plot_time_series(meta_analysis_result, vis_title, vis_colors)
    #     plt.close(prog_data.vis_repo["meta"][meta_analysis_key])

    return data_repo