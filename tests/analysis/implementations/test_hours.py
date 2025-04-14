import pytest
import pandas as pd

from src.analysis.implementations.hours import _analyze_hours_byns_ondf

def test_hours_custom(customgpudf):
    result = _analyze_hours_byns_ondf(customgpudf)
    targ_df = pd.DataFrame({
        'Namespace': ['ns1', 'ns2', 'ns3', 'ns4'],
        'Hours': [7.0, 12.0, 18.0, 2.0]
    })

    # Sort results for equals comparison
    result_sorted = result.sort_values(by='Namespace').reset_index(drop=True)
    targ_sorted = targ_df.sort_values(by='Namespace').reset_index(drop=True)

    pd.testing.assert_frame_equal(result_sorted, targ_sorted)

    assert sum(result["Hours"]) == 39


def test_hours_cpujan24(jan24cpudf):
    result = _analyze_hours_byns_ondf(jan24cpudf)
    assert sum(result["Hours"]) == 4110

def test_hours_cpujan24(feb24cpudf):
    result = _analyze_hours_byns_ondf(feb24cpudf)
    assert sum(result["Hours"]) == 23088
