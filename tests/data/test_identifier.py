import os
import pytest
import sys
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.data.identifiers.identifier import Identifier, SourceIdentifier, AnalysisIdentifier, VisIdentifier

def test_equality():
    assert SourceIdentifier(1200, 1500, "cpu") == SourceIdentifier(1200, 1500, "cpu")

def test_inequality():
    assert SourceIdentifier(100, 200, "cpu") != SourceIdentifier(0, 10, "cpu")

def test_diff_type_equality():
    src_id = SourceIdentifier(21, 30, "gpu")
    assert AnalysisIdentifier(src_id, "gpuhours") != VisIdentifier(src_id, "gpuhours")

@pytest.fixture
def src_id_list():
    return [SourceIdentifier(0, 10, "cpu"), SourceIdentifier(11, 20, "cpu"), SourceIdentifier(21, 30, "gpu")]

def test_searching(src_id_list):
    assert SourceIdentifier(11, 20, "cpu") in src_id_list

def test_nested_source():
    srcid = SourceIdentifier(0, 1, "cpu")
    aid1 = AnalysisIdentifier(srcid, "analysis1")
    aid2 = AnalysisIdentifier(aid1, "analysis2")
    aid3 = AnalysisIdentifier(aid2, "analysis3")

    assert srcid == aid3.find_source()