import os
import pytest
import pandas as pd

@pytest.fixture
def customcpudf(test_files_dir):
    path = os.path.join(test_files_dir, "custom", "cpucustom.csv")
    return pd.read_csv(path)

@pytest.fixture
def customgpudf(test_files_dir):
    path = os.path.join(test_files_dir, "custom", "gpucustom.csv")
    return pd.read_csv(path)

@pytest.fixture
def jan24cpudf(test_files_dir):
    path = os.path.join(test_files_dir, "janfebmar24", "cpu-January24.csv")
    return pd.read_csv(path)

@pytest.fixture
def jan24gpudf(test_files_dir):
    path = os.path.join(test_files_dir, "janfebmar24", "gpu-January24.csv")
    return pd.read_csv(path)

@pytest.fixture
def feb24cpudf(test_files_dir):
    path = os.path.join(test_files_dir, "janfebmar24", "cpu-February24.csv")
    return pd.read_csv(path)

@pytest.fixture
def feb24gpudf(test_files_dir):
    path = os.path.join(test_files_dir, "janfebmar24", "gpu-February24.csv")
    return pd.read_csv(path)

@pytest.fixture
def mar25cpudf(test_files_dir):
    path = os.path.join(test_files_dir, "mar25", "cpu-March25.csv")
    return pd.read_csv(path)

@pytest.fixture
def mar25gpudf(test_files_dir):
    path = os.path.join(test_files_dir, "mar25", "gpu-March25.csv")
    return pd.read_csv(path)