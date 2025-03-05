from program_data import ProgramData
from analysis.analysis_impl import analyze_hours_byns, analyze_jobs, analyze_cpu_only_jobs, analyze_unique_ns

analysis_options = {
    "cpuhours": {
        "types": ["cpu"],
        "method": analyze_hours_byns
    },
    "cpujobs": {
        "types": ["cpu", "gpu"],
        "method": analyze_cpu_only_jobs
    },
    "gpuhours": {
        "types": ["gpu"],
        "method": analyze_hours_byns
    },
    "gpujobs": {
        "types": ["gpu"],
        "method": analyze_jobs
    },
    "uniquens": {
        "types": ["cpu", "gpu"],
        "method": analyze_unique_ns
    }
}

def analyze():
    """
    Analyze the current ProgramData for the target analysis options selected. Analysis options are
      performed for each data block, meaning there will be a separate set of analysis results for
      each.
    Results are stored in a dictionary with the analysis name as the key and the result output as 
      the value.
    Results are placed in ProgramData#data_repo as they are generated so that other methods can
      use them.
    """
    prog_data = ProgramData()
    prog_data.analysis_repo = {}
    # TODO: This is selecting the ALL keys from the analysis dict, this should be a command line argument. 
    analyses_to_perform = set(analysis_options.keys())
    fulfilled_analyses = set()

    data_blocks = prog_data.data_repo.data_blocks
    for data_block_identifier in data_blocks.keys():
        data_block = data_blocks[data_block_identifier]
        # The analysis results for this data_block only
        results = {}

        for analysis in analyses_to_perform:
            analysis_impl = analysis_options[analysis]
            if(not data_block['type'] == analysis_impl['types'][0]):
                continue

            results[analysis] = analysis_impl['method'](data_block)
            fulfilled_analyses.add(analysis)

        prog_data.analysis_repo[data_block_identifier] = results

    if(analyses_to_perform != fulfilled_analyses):
        raise Exception(f"Failed to fulfill all analyses: {list(analyses_to_perform-fulfilled_analyses)} (was all data loaded properly? using custom file/directory?)")



