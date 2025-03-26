import calendar
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import pandas as pd
import numpy as np
import datetime

from program_data.program_data import ProgramData
from utils.timeutils import get_range_as_month

def vizualize():
    prog_data = ProgramData()

    prog_data.vis_repo = {}

    for identifier in prog_data.data_repo.data_blocks.keys():
        analyses = prog_data.analysis_repo[identifier]
        # Loop through each analysis that can be visualized
        for analysis in analyses.keys():
            analysis_options = prog_data.settings["analysis_settings"][analysis]
            # Ensure that this is an analysis we can visualize
            if("vis_options" not in analysis_options.keys()):
                continue

            analysis_result = analyses[analysis]
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
                parsed_variables[variable_name] = analyses[targ_analysis]

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

            prog_data.vis_repo[identifier][analysis] = plot_simple_bargraph(analysis_result, vis_title, vis_subtext, vis_color)
            plt.close(prog_data.vis_repo[identifier][analysis])

    for meta_analysis_key in prog_data.meta_analysis_repo.keys():
        meta_analysis_result = prog_data.meta_analysis_repo[meta_analysis_key]
        if(meta_analysis_result is None):
            continue

        vis_options = prog_data.settings["meta_analysis_options"][meta_analysis_key]["vis_options"]
        vis_title = apply_variables(vis_options["title"])
        vis_colors = vis_options["colors"]

        if("meta" not in prog_data.vis_repo.keys()):
            prog_data.vis_repo["meta"] = {}

        prog_data.vis_repo["meta"][meta_analysis_key] = plot_time_series(meta_analysis_result, vis_title, vis_colors)
        plt.close(prog_data.vis_repo["meta"][meta_analysis_key])

def plot_simple_bargraph(df, title, subtext, color):
    df = df.set_index(df.columns[0])
    df = df.iloc[::-1]

    # Create a new figure and axes
    fig, ax = plt.subplots(figsize=(12, 8))

    # Plot the horizontal bar chart
    df.plot(kind='barh', color=color, ax=ax)

    # Set title
    ax.set_title(title)

    # Annotate the bars with their counts
    for index, ndarr_value in enumerate(df.values):
        value = ndarr_value[0] # enumerate treats df.values as ndarray lists with a single element in them
        string_value = str(value)
        if(isinstance(value, float)):
            string_value = f'{value:.2f}'
        ax.text(value, index, string_value, ha='left', va='center')

    # Move x-axis to the top
    ax.xaxis.set_label_position('top')
    ax.xaxis.tick_top()

    # Add total count subtext
    ax.text(0.02, -0.1, subtext, transform=ax.transAxes, color='black', fontsize=12)

    # Enable grid
    ax.grid(True)

    # Adjust layout
    fig.tight_layout()

    return fig  # Return the figure object
            
def plot_time_series(df, title, colors={}, default_color="blue"):
    """
    Plots a horizontal line showing the data points at each time.
    Expects a dataframe with the first column being period, each following column will be a new line
      on the graph.
    Assign colors to each line by adding in entry to dictionary:
      colors[<column name>] = "<color name>"
    """

    if(len(df.columns) < 2):
        raise ValueError("Can't plot horizontal series, DataFrame has less than 2 columns!")
    if("Period" not in df.columns):
        raise ValueError("Can't plot horizontal series, DataFrame doesn't have a Period column.")

    # Create figure and axis
    fig, ax = plt.subplots(figsize=(15, 8))

    # Set axis limits
    period_starts = [period[0] for period in df["Period"]]
    ax.set_xlim(datetime.datetime.fromtimestamp(min(period_starts)) - datetime.timedelta(days=3),
                datetime.datetime.fromtimestamp(max(period_starts)) + datetime.timedelta(days=3))

    min_value = float("inf")
    max_value = float("-inf")
    for column in df.columns:
        if(column == "Period"):
            continue
        col_min = df[column].min()
        col_max = df[column].max()
        if(col_min < min_value):
            min_value = col_min
        if(col_max > max_value):
            max_value = col_max

    padding = (max_value-min_value)*0.1
    ax.set_ylim(min_value - padding, max_value + padding)
    
    # Change the period column from a timestamp tuple to a datetime object based off of the starting timestamp
    df.loc[:, "Period"] = df["Period"].apply(lambda period: datetime.datetime.fromtimestamp(period[0]))

    # Plot and annotate each line
    for column in df.columns:
        if(column == "Period"):
            continue

        color = default_color
        if(column in colors):
            color = colors[column]

        # Plot line
        ax.plot(df["Period"], df[column], color=color, label=column)

        # Add number annotation above each point
        for i, row in df.iterrows():
            ax.annotate(f'{row[column]:.0f}',
                (row['Period'], row[column]),
                xytext=(0, 5),
                textcoords='offset points',
                ha='center',
                va='bottom',
                color=color,
                fontsize=8)
    
    # Format x-axis to show months and year
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

    # Add labels, title, and legend
    # ax.set_xlabel('Month')
    # ax.set_ylabel('Hours')
    ax.set_title(title)
    ax.legend()
    ax.grid(True)

    # Put the x-axis on top
    ax.xaxis.tick_top()

    # Add total count to the plot
    # ax.text(0.02, -0.1, f'Total GPU hours: {total_all_namespaces}', transform=ax.transAxes, color='black', fontsize=12)
    
    return fig