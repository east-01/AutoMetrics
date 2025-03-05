AutoTM - Tide Metrics Automation
---

Python script to automate the collection, analysis, and visualization of metrics for the TIDE cluster. It uses the requests library to poll a prometheus endpoint with a PromQL query, or load data directly from CSV files.

## Installation

The installation instructions assume that you have:
- Python 3.12.6 or later

1. Clone the repository to your local directory with `git clone https://github.com/east-01/AutoTM.git`.
2. Install the requirements with `pip install -r <path_to_install>\requirements.txt`.
3. After everything installs, AutoTM will be ready for use.

## Usage

AutoTM is run from the command line, the base version of it can be run with:
```
python tidemetrics.py <analyses>
```
Where \<analyses\> is a list of analysis options you want to perform, separated by a comma. See the [command line arguments](#command-line-arguments) section to fully use AutoTM.

### Analysis options

Analysis options must be spelled correctly and listed without spaces. Here is an example of a valid command collecting the amount of GPU hours and unique namespaces.
```
python tidemetrics.py gpuhours,uniquens
```
You can use `all` to denote all analysis options, so if you wanted to collect analyses for all of the following options you would do:
```
python tidemetrics.py all
```

Option | Description
-------|------------
cpuhours | The amount of CPU hours consumed by each namespace.
gpuhours | The amount of GPU hours consumed by each namespace.
gpujobs | The amount of unique jobs for each namespace.
cpujobs | The amount of unique *cpu only* jobs for each namespace.
uniquens | The amount of unique namespaces.

### Command line arguments

Command line arguments can be used to greatly fine tune the source of the data. However, there are two groups of command line arguments that must be considered: the arguments for using PromQL vs. the arguments for using local .CSV files.

#### PromQL related arguments

These arguments should not be used when inputting a custom file/directory.

Argument | Description | Example usage
---------|-------------|--------------
-p or --period | The period to analyze in the format \<start_ts\>-\<end_ts\>. Where each timestamp is a UNIX timestamp. | -p 1738396800-1740815999

#### Input file related arguments

These arguments should not be used when using a PromQL query.

Argument | Description | Example usage
---------|-------------|--------------
-f or --file | The input file to use. | -f "./input/input_file.csv"
-i or --in-dir | The input directory to use. | -f "./input"

#### Other arguments

These arguments can be used with either a PromQL query or custom file/directory input.

Argument | Description | Example usage
---------|-------------|--------------
-o or --out-dir | The directory that the result files will be placed in. | -o 
"./output"
-v | Verbose messaging in the console. | -v

## Technical details

There three main phases to AutoTM's lifecycle: collection, analysis, and visualization. 

### Important structures

There are a couple data structures to keep in mind to understand how this program works:

#### ProgramData

The ProgramData class is a singleton object that holds *all* of the data that is used throughout the lifecycle of the program. The list of things inside ProgramData:
- Command line arguments (argparse.Namespace)
- config.yaml values (Dictionary)
- Settings (Dictionary- hard-coded values that shouldn't be mutable by the user)
- __DataRepository__ (DataRepository class)
- __Analysis repository__ (Dictionary)

#### DataRepository

The DataRepository holds a group of "data blocks" which represents a pandas DataFrame and additional info surrounding it; I'd prefer to store these as a struct type but we don't have that in Python. Each data block is stored with a tuple key in the format (period, type) allowing for unique data blocks. In each data block:

Key | Value type | Description
----|------------|------------
data | pandas.DataFrame | The data frame.
type | String | The type that this DataFrame holds (currently either "cpu" or "gpu")
period | (int, int) | The period that this DataFrame covers where each int is a UNIX Timestamp.
readable_period | String | The period converted to human-readable form.
out_file_name | String | The filename that this data block should be saved as.

#### Analysis repository

The analysis repository is a supplemental dictionary that holds the analysis output for each data block, the keys for this dictionary are the same as the corresponding data block key. Example retrieval of data:

```
cpu_hours = analysis_repo[<identifier>]["cpuhours"]
```

### Program lifecycle

- Initialize ProgramData
  - Initializes arguments, config, and settings
- Start collection with `data_loader#load_data`
  - Creates a DataRepository object
  - Gathers DataFrames from source (either PromQL or .csv)
  - DataFrames are ingested and turned into data blocks
- Start analysis with `analysis` call
  - Creates analysis repository dictionary
  - Perform each analysis on each data block
  - Analysis results are stored for each data block
- TODO: Visualize/Generate summary .csv
- Save output files
  - Saves each data block
  - Saves the results for each analysis