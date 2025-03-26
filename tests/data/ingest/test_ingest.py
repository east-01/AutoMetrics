import pytest

from src.data.ingest.ingest import ingest
from src.data.identifiers.identifier import *

def test_malformed_file_args(malformed_file_args, default_config):
    with pytest.raises(FileNotFoundError):
        ingest(malformed_file_args, default_config)
    
def test_single_file(file_args_single_file, default_config):
    data_repo = ingest(file_args_single_file, default_config)
    assert data_repo.count() == 1

def test_single_month(file_args_single_month, default_config):
    data_repo = ingest(file_args_single_month, default_config)
    assert data_repo.count() == 2

def test_multi_month(file_args_multi_month, default_config):
    data_repo = ingest(file_args_multi_month, default_config)
    assert data_repo.count() == 6