import pytest
import argparse
import os
import pandas as pd

from src.program_data.program_data import ProgramData
from src.program_data.arguments import parse_file_list

@pytest.fixture
def default_config():
    return {
        "base_url": "https://thanos.nrp-nautilus.io/api/v1/query_range",
        "step": 3600,
        "query": r"""
            kube_pod_container_resource_requests{
                namespace=~"csusb.*|csu.*|cal-poly-humboldt.*|sdsu-.*|csun-.*|nsf-maica", 
                namespace!~"sdsu-jupyterhub.*", 
                resource = "%TYPE_STRING%", 
                node=~"rci-tide.*|rci-nrp-gpu-08.*|rci-nrp-gpu-07.*|rci-nrp-gpu-06.*|rci-nrp-gpu-05.*", 
                node!~"rci-tide-dtn.*"
            } * on(uid, ) group_left(phase) 
            kube_pod_status_phase{
                phase="Running", 
                namespace=~"csusb.*|csu.*|cal-poly-humboldt.*|sdsu-.*|csun-.*|nsf-maica", 
                namespace!~"sdsu-jupyterhub.*"
            }""",
        "top5hours_blacklist": ["sdsu-rci-jh", "csu-tide-jupyterhub"]
    }

@pytest.fixture
def program_data_def_config(default_config):
    return ProgramData(argparse.Namespace(analysis_options=["cpuhours"], file=None, period=(0, 1)), default_config)

#region Dir/File paths
@pytest.fixture
def ingest_directory():
    """ The fixture that points to the directory of the testing files for ingest. """
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "test_ingest_files"))

@pytest.fixture
def single_month_directory(ingest_directory):
    return os.path.join(ingest_directory, "jan24")

@pytest.fixture
def multi_month_directory(ingest_directory):
    return os.path.join(ingest_directory, "janfebmar24")

@pytest.fixture
def cpu_csv_path(single_month_directory):
    return os.path.join(single_month_directory, "cpu-January24.csv")

@pytest.fixture
def gpu_csv_path(single_month_directory):
    return os.path.join(single_month_directory, "gpu-January24.csv")

@pytest.fixture
def malformed_csv_path(ingest_directory):
    return os.path.join(ingest_directory, "malformed", "malformed_df.csv")
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