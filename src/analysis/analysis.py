from program_data.program_data import ProgramData
from analysis.analysis_impl import analyze_hours_byns, analyze_hours_total, analyze_jobs, analyze_jobs_total, analyze_cpu_only_jobs, analyze_all_jobs_total
from data.data_repository import DataRepository
from data.filters import filter_type
from data.identifiers.identifier import Identifier, AnalysisIdentifier, SourceIdentifier

analysis_options_methods = {
    "cpuhours": analyze_hours_byns,
    "cpuhourstotal": analyze_hours_total,
    "cpujobs": analyze_cpu_only_jobs,
    "cpujobstotal": analyze_jobs_total,
    "gpuhours": analyze_hours_byns,
    "gpuhourstotal": analyze_hours_total,
    "gpujobs": analyze_jobs,
    "gpujobstotal": analyze_jobs_total,
    "jobstotal": analyze_all_jobs_total
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
    data_repo: DataRepository = prog_data.data_repo

    analyses_to_perform = get_analysis_order()

    print(f"Analysis perform order: {", ".join(analyses_to_perform)}")

    fulfilled_analyses = set()
    # Perform each analysis, performing analyses in the outer loop ensures the dependency order
    #   is maintained.
    for analysis in analyses_to_perform:
        analysis_settings = prog_data.settings["analysis_settings"][analysis]
        analysis_filter = analysis_settings["filter"]
        analysis_method = analysis_options_methods[analysis]

        if(analysis_filter is None):
            analysis_method(None)            
        else:
            identifiers = data_repo.filter_ids(analysis_filter)

            for identifier in identifiers:
                analysis_identifier = AnalysisIdentifier(identifier, analysis)
                analysis_result = analysis_method(identifier)

                data_repo.add(analysis_identifier, analysis_result)
                
    analyses_to_perform_set = set(analyses_to_perform)
    if(analyses_to_perform_set != fulfilled_analyses):
        raise Exception(f"Failed to fulfill all analyses: {list(analyses_to_perform_set-fulfilled_analyses)} (was all data loaded properly? using custom file/directory?)")

def get_analysis_order():
    """
    Given the list of analyses to perform, re-order it such that analyses with dependencies are
      performed last.
    """
    order = []

    prog_data = ProgramData()
    user_analysis_options = set(prog_data.args.analysis_options)
    analysis_options = prog_data.settings["analysis_settings"]

    # Only iterate n**2 times, any further iterations would mean there is an impossible/circular dependency
    for _ in range(0, len(analysis_options.keys())**2):
        for analysis_key in list(user_analysis_options):
            requirements = analysis_options[analysis_key]["requires"]
            if(all(x in order for x in requirements)):
                order.append(analysis_key)
                user_analysis_options.remove(analysis_key)

    if(len(user_analysis_options) > 0):
        raise Exception(f"Failed to generate analysis order, could there be a circular/impossible dependency? Remaining analyses: {user_analysis_options}")

    return order


