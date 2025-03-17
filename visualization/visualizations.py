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
            analysis_options = prog_data.settings["analysis_options"][analysis]
            # Ensure that this is an analysis we can visualize
            if("vis_options" not in analysis_options.keys()):
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

            prog_data.vis_repo[identifier][analysis] = plot_simple_bargraph(analyses[analysis], vis_title, vis_subtext, vis_color)

    return

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
        print(string_value)
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

def add_labels(ax, data, column, color, condition=lambda row: True):
    for i, row in data.iterrows():
        if condition(row):
            ax.annotate(f'{row[column]:.0f}',
                (row['Date'], row[column]),
                xytext=(0, 5),
                textcoords='offset points',
                ha='center',
                va='bottom',
                color=color,
                fontsize=8)
                
def plot_cpu_gpu_hours_namespace(cpu_namespace_totals_series,gpu_namespace_totals_series,months,data_directory):
    total_all_namespaces = cpu_namespace_totals_series['hours'].sum()
    # Plotting the horizontal bar chart for each namespace
    month_data =  ','.join(months)
    cpu_namespace_totals_series.loc[:, 'Date'] = cpu_namespace_totals_series['month'].apply(lambda x:datetime.datetime.strptime(f"{x} 2024", "%B %Y"))
    cpu_namespace_totals_series = cpu_namespace_totals_series.sort_values('Date')
    gpu_namespace_totals_series.loc[:, 'Date'] = gpu_namespace_totals_series['month'].apply(lambda x:datetime.datetime.strptime(f"{x} 2024", "%B %Y"))
    gpu_namespace_totals_series = gpu_namespace_totals_series.sort_values('Date')
    fig, ax = plt.subplots(figsize=(15,8))

# Create Line2D objects and add to plot
    line1 = Line2D(cpu_namespace_totals_series['Date'], cpu_namespace_totals_series['hours'], color='red', label='CPU Hours')
    line2 = Line2D(gpu_namespace_totals_series['Date'], gpu_namespace_totals_series['hours'], color='blue', label='GPU Hours')
    ax.add_line(line1)
    ax.add_line(line2)

    # Set the axis limits
    ax.set_xlim(cpu_namespace_totals_series['Date'].min()-datetime.timedelta(days=3), cpu_namespace_totals_series['Date'].max()+datetime.timedelta(days=3))
    ax.set_ylim(min(cpu_namespace_totals_series['hours'].min(),gpu_namespace_totals_series['hours'].min())-10000,max(cpu_namespace_totals_series['hours'].max(),gpu_namespace_totals_series['hours'].max())+10000)

    # Format x-axis to show months and year
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

    # Add labels, title, and legend
    ax.set_xlabel('Month')
    ax.set_ylabel('Hpurs ')
    ax.set_title('CPU and GPU Hours by Month')
    ax.legend()
    plt.tight_layout()
    plt.grid(True)

    # Annotate the bars with their counts
    add_labels(ax, cpu_namespace_totals_series, 'hours', 'red')
    add_labels(ax, gpu_namespace_totals_series, 'hours', 'blue')
    
    # Put the x-axis on top
    ax.xaxis.tick_top()

    # Add total count to the plot
    plt.text(0.02, -0.1, f'Total GPU hours: {total_all_namespaces}', transform=ax.transAxes, color='black', fontsize=12)
    # Calculate and add total of all
    plt.savefig(data_directory+'/total_cpu_gpu_hours.png', bbox_inches='tight')
    plt.show()

def plot_cpu_gpu_jobs_namespace(gpu_namespace_counts_sorted, cpu_namespace_counts_sorted, months,data_directory):
    total_counts = gpu_namespace_counts_sorted['count'].sum()

    # Plotting the horiz1ntal bar chart for Total GPU Jobs by Namespace
    
    month_data =  ','.join(months)
    gpu_namespace_counts_sorted.loc[:, 'Date'] = gpu_namespace_counts_sorted['month'].apply(lambda x:datetime.datetime.strptime(f"{x} 2024", "%B %Y"))
    gpu_namespace_counts_sorted = gpu_namespace_counts_sorted.sort_values('Date')
    cpu_namespace_counts_sorted.loc[:, 'Date'] = cpu_namespace_counts_sorted['month'].apply(lambda x:datetime.datetime.strptime(f"{x} 2024", "%B %Y"))
    cpu_namespace_counts_sorted = cpu_namespace_counts_sorted.sort_values('Date')
    fig, ax = plt.subplots(figsize=(20,8))

# Create Line2D objects and add to plot
    line1 = Line2D(gpu_namespace_counts_sorted['Date'], gpu_namespace_counts_sorted['count'], color='red', label='CPU Jobs')
    line2 = Line2D(cpu_namespace_counts_sorted['Date'], cpu_namespace_counts_sorted['count'], color='blue', label='GPU Jobs')
    ax.add_line(line1)
    ax.add_line(line2)

    # Set the axis limits
    ax.set_xlim(cpu_namespace_counts_sorted['Date'].min()-datetime.timedelta(days=3), gpu_namespace_counts_sorted['Date'].max()+datetime.timedelta(days=3))
    ax.set_ylim(min(cpu_namespace_counts_sorted['count'].min(),
                    cpu_namespace_counts_sorted['count'].min())-100,
                    max(gpu_namespace_counts_sorted['count'].max(),
                    cpu_namespace_counts_sorted['count'].max())+100)

    # Format x-axis to show months and year
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

    # Add labels, title, and legend
    ax.set_xlabel('Month')
    ax.set_ylabel('Jobs count')
    ax.set_title('CPU and GPU Jobs by Month')
    ax.legend()
    plt.tight_layout()
    plt.grid(True)

    # Annotate the bars with their counts
    add_labels(ax, cpu_namespace_counts_sorted, 'count', 'blue')
    add_labels(ax, gpu_namespace_counts_sorted, 'count', 'red')
    
    # Put the x-axis on top
    ax.xaxis.tick_top()

    # Add total count to the plot
    plt.text(0.02, -0.1, f'Total GPU Jobs: {total_counts}', transform=ax.transAxes, color='black', fontsize=12)

    plt.savefig(data_directory+'/total_cpu_gpu_jobs.png', bbox_inches='tight')
    plt.show()
    