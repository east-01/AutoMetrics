import pytest

from src.data.data_repository import DataRepository
from src.data.processors import process_periods
from src.data.identifiers.identifier import *

@pytest.fixture
def timestamps():
    return [
        1704182400, # 1/2/24 T0:0:0
        1706428800, # 1/28/24 T0:0:0
        1706774400, # 2/1/24 T0:0:0 Shouldn't be adjusted
        1709020800  # 2/27/24 T0:0:0
    ]

@pytest.fixture
def adjusted_timestamps():
    return [
        1704096000, # 1/1/24 T0:0:0
        1706774399, # 1/31/24 T23:59:59
        1706774400, # 2/1/24 T0:0:0
        1709279999  # 2/29/24 T23:59:59
    ]

def test_process_periods(timestamps, adjusted_timestamps):
    srcid1 = SourceIdentifier(timestamps[0], timestamps[1], "cpu")
    srcid2 = SourceIdentifier(timestamps[2], timestamps[3], "cpu")

    metadata = {"meta_test": "yeah"}

    data_repo = DataRepository()
    data_repo.add(srcid1, "test", metadata)
    data_repo.add(srcid2, "test2")

    new_data_repo = process_periods(data_repo)

    adjsrcid1 = SourceIdentifier(adjusted_timestamps[0], adjusted_timestamps[1], "cpu")
    adjsrcid2 = SourceIdentifier(adjusted_timestamps[2], adjusted_timestamps[3], "cpu")

    assert new_data_repo.contains(adjsrcid1)
    assert new_data_repo.contains(adjsrcid2)

    assert new_data_repo.get_data(adjsrcid1) == "test"
    assert new_data_repo.get_metadata(adjsrcid1) == metadata

def test_process_periods_overlap(timestamps):
    extra_ts = 1706342400 # 1/27/24 T:0:0:0

    srcid1 = SourceIdentifier(timestamps[0], timestamps[1], "cpu")
    srcid2 = SourceIdentifier(extra_ts, timestamps[3], "cpu")

    data_repo = DataRepository()
    data_repo.add(srcid1, "test")
    data_repo.add(srcid2, "test2")

    with pytest.raises(ValueError):
        process_periods(data_repo)