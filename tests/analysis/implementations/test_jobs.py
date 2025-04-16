import pytest
import pandas as pd

from src.analysis.implementations.jobs import _analyze_jobs_byns_ondf

def test_jobs_customgpu(customgpudf):
    result = _analyze_jobs_byns_ondf(customgpudf)
    targ_df = pd.DataFrame({
        'Namespace': ['ns1', 'ns2', 'ns3', 'ns4'],
        'Count': [1, 1, 1, 1]
    })

    # Sort results for equals comparison
    result_sorted = result.sort_values(by='Namespace').reset_index(drop=True)
    targ_sorted = targ_df.sort_values(by='Namespace').reset_index(drop=True)

    pd.testing.assert_frame_equal(result_sorted, targ_sorted)
    assert sum(result["Count"]) == 4

def test_jobs_customcpu(customcpudf):
    blacklist = ["uid1", "uid4", "uid6", "uid9"]
    result = _analyze_jobs_byns_ondf(customcpudf, blacklist)
    targ_df = pd.DataFrame({
        'Namespace': ['ns1', 'ns2', 'ns3', 'ns4'],
        'Count': [2, 1, 2, 4]
    })

    # Sort results for equals comparison
    result_sorted = result.sort_values(by='Namespace').reset_index(drop=True)
    targ_sorted = targ_df.sort_values(by='Namespace').reset_index(drop=True)

    pd.testing.assert_frame_equal(result_sorted, targ_sorted)
    assert sum(result["Count"]) == 9

def test_jobs_gpujan24(jan24gpudf):
    result = _analyze_jobs_byns_ondf(jan24gpudf)
    assert sum(result["Count"]) == 7

def test_jobs_gpufeb24(feb24gpudf):
    result = _analyze_jobs_byns_ondf(feb24gpudf)
    assert sum(result["Count"]) == 24