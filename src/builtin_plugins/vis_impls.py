import datetime
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

from src.data.data_repository import DataRepository

def plot_simple_bargraph(data_repo: DataRepository, identifier, title, subtext, color):
    """
    Plots a bargraph comparing values between rows.
    Expects a dataframe with the first column being bar name, and the following column being bar
        value.
    """

    df, meta_data = data_repo.get(identifier)

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
            
def plot_time_series(data_repo: DataRepository, identifier, title, colors={}, default_color="blue"):
    """
    Plots a horizontal line showing the data points at each time.
    Expects a dataframe with the first column being period, each following column will be a new line
      on the graph.
    Assign colors to each line by adding in entry to dictionary:
      colors[<column name>] = "<color name>"
    """

    df, meta_data = data_repo.get(identifier)

    if(len(df.columns) < 2):
        raise ValueError("Can't plot horizontal series, DataFrame has less than 2 columns!")
    if("Period" not in df.columns):
        raise ValueError("Can't plot horizontal series, DataFrame doesn't have a Period column.")

    # Create figure and axis
    fig, ax = plt.subplots(figsize=(15, 8))

    # Set axis limits
    period_starts = [period[0] for period in meta_data["periods"]]
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
    df.loc[:, "Period"] = [datetime.datetime.fromtimestamp(period[0]) for period in meta_data["periods"]]

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
    ax.set_title(title)
    ax.legend()
    ax.grid(True)

    # Put the x-axis on top
    ax.xaxis.tick_top()
    
    return fig