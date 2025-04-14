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
def test_files_dir():
    """ The fixture that points to the directory of the testing files for ingest. """
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "test_files"))