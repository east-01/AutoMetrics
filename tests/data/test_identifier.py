import os
import pytest
import sys
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.data.identifier import Identifier, AnalysisIdentifier, VisIdentifier, TimeStampIdentifier
from plugins.rci.rci_identifiers import GrafanaIdentifier, SummaryIdentifier

def test_equality():
    assert GrafanaIdentifier(1200, 1500, "cpu", "def") == GrafanaIdentifier(1200, 1500, "cpu", "def")

def test_inequality():
    assert GrafanaIdentifier(100, 200, "cpu", "def") != GrafanaIdentifier(0, 10, "cpu", "def")

def test_diff_type_equality():
    src_id = GrafanaIdentifier(21, 30, "gpu", "def")
    assert AnalysisIdentifier(src_id, "gpuhours") != VisIdentifier(src_id, "gpuhours")

def test_diff_type_equality_two():
    assert SummaryIdentifier(1, 2) != TimeStampIdentifier(1, 2)

@pytest.fixture
def src_id_list():
    return [GrafanaIdentifier(0, 10, "cpu", "def"), GrafanaIdentifier(11, 20, "cpu", "def"), GrafanaIdentifier(21, 30, "gpu", "def")]

def test_searching(src_id_list):
    assert GrafanaIdentifier(11, 20, "cpu", "def") in src_id_list

def test_nested_source():
    srcid = GrafanaIdentifier(0, 1, "cpu", "def")
    aid1 = AnalysisIdentifier(srcid, "analysis1")
    aid2 = AnalysisIdentifier(aid1, "analysis2")
    aid3 = AnalysisIdentifier(aid2, "analysis3")

    assert srcid == aid3.find_base()

# def test_meta_analysis():
#     aid1 = AnalysisIdentifier(None, "analysis1")

#     assert aid1.is_meta_analysis()