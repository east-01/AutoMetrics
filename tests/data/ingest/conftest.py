import pytest
import argparse
import os
import pandas as pd

from src.program_data.program_data import ProgramData
from program_data.parameters import parse_file_list

@pytest.fixture
def program_data_def_config(default_config):
    return ProgramData(argparse.Namespace(analysis_options=["cpuhours"], file=None, period=(0, 1)), default_config)

#region Dir/File paths
@pytest.fixture
def single_month_directory(test_files_dir):
    return os.path.join(test_files_dir, "jan24")

@pytest.fixture
def multi_month_directory(test_files_dir):
    return os.path.join(test_files_dir, "janfebmar24")

@pytest.fixture
def cpu_csv_path(single_month_directory):
    return os.path.join(single_month_directory, "cpu-January24.csv")

@pytest.fixture
def gpu_csv_path(single_month_directory):
    return os.path.join(single_month_directory, "gpu-January24.csv")

@pytest.fixture
def malformed_csv_path(test_files_dir):
    return os.path.join(test_files_dir, "malformed", "malformed_df.csv")
#endregion

#region Dataframes
@pytest.fixture
def cpu_df(cpu_csv_path):
    return pd.read_csv(cpu_csv_path)

@pytest.fixture
def gpu_df(gpu_csv_path):
    return pd.read_csv(gpu_csv_path)

# The malformed dataframe has multiple resource types (nvidia_com_gpu in 1st column then cpu in 
#   rest) and has a time period spanning from 1/1-2/26.
@pytest.fixture
def malformed_df(malformed_csv_path):
    return pd.read_csv(malformed_csv_path)
#endregion

#region File namespaces
@pytest.fixture
def file_args_malformed(program_data_def_config):
    program_data_def_config.args.file = "not a filepath"
    return program_data_def_config

@pytest.fixture
def file_args_single_file(program_data_def_config, cpu_csv_path):
    program_data_def_config.args.file = parse_file_list(cpu_csv_path)
    return program_data_def_config

@pytest.fixture
def file_args_single_month(program_data_def_config, single_month_directory):
    program_data_def_config.args.file = parse_file_list(single_month_directory)
    return program_data_def_config

@pytest.fixture
def file_args_multi_month(program_data_def_config, multi_month_directory):
    program_data_def_config.args.file = parse_file_list(multi_month_directory)
    return program_data_def_config
#endregion