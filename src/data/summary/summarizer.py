import pandas as pd

from src.program_data.program_data import ProgramData
from src.data.data_repository import DataRepository
from src.data.identifiers.identifier import *
from src.data.filters import *

def can_summarize(prog_data: ProgramData):
    """
    Ensure we can perform summaries, checks if the program data arguments contain all of the
      required analyses.
    """
    summary_analyses = ["cpuhours", "gpuhours", "jobstotal", "cpuhourstotal", "gpuhourstotal"]
    for summary_analyis in summary_analyses:
        if(summary_analyis not in prog_data.args.analysis_options):
            print(f"Can't summarize, analysis \"{summary_analyis}\" missing.")
            return False
    return True

def summarize(prog_data: ProgramData):

    data_repo: DataRepository = prog_data.data_repo
    
    for identifier in data_repo.filter_ids(filter_type(SourceIdentifier)):
        start_ts = identifier.start_ts
        end_ts = identifier.end_ts

        summary_id = SummaryIdentifier(start_ts, end_ts)

        if(data_repo.contains(summary_id)):
            continue

        cpu_src_id = SourceIdentifier(start_ts, end_ts, "cpu")
        gpu_src_id = SourceIdentifier(start_ts, end_ts, "gpu")

        if(not data_repo.contains(cpu_src_id) or not data_repo.contains(gpu_src_id)):
            raise ValueError(f"Can't summarize {start_ts}-{end_ts} the data_repo is missing either the cpu or gpu SourceIdentifier.")
        
        # Shorthand for the get_data method call for readability
        gd = data_repo.get_data

        # Collect analysis identifiers
        cpuhours = AnalysisIdentifier(cpu_src_id, "cpuhours")
        cpuhourstotal = AnalysisIdentifier(cpuhours, "cpuhourstotal")
        cpujobs = AnalysisIdentifier(cpu_src_id, "cpujobs")
        cpujobstotal = AnalysisIdentifier(cpujobs, "cpujobstotal")
        jobstotal = AnalysisIdentifier(cpujobstotal, "jobstotal")

        gpuhours = AnalysisIdentifier(gpu_src_id, "gpuhours")
        gpuhourstotal = AnalysisIdentifier(gpuhours, "gpuhourstotal")
        gpujobs = AnalysisIdentifier(gpu_src_id, "gpujobs")
        gpujobstotal = AnalysisIdentifier(gpujobs, "gpujobstotal")

        # Create the summary data frame
        summary_df = pd.DataFrame({
            "Analysis": ["CPU Only Jobs", "GPU Jobs", "Jobs Total", "CPU Hours", "GPU Hours"],
            "Value": [gd(cpujobstotal), gd(gpujobstotal), gd(jobstotal), gd(cpuhourstotal), gd(gpuhourstotal)]
        })

        # Generate top 5 hours dataframes
        top5_blacklist = prog_data.config['top5hours_blacklist']

        cpu_df = gd(cpuhours)
        cpu_df = cpu_df[cpu_df.apply(lambda row: row.iloc[0] not in top5_blacklist, axis=1)].iloc[0:5].reset_index(drop=True)

        gpu_df = gd(gpuhours)
        gpu_df = gpu_df[gpu_df.apply(lambda row: row.iloc[0] not in top5_blacklist, axis=1)].iloc[0:5].reset_index(drop=True)

        data_repo.add(summary_id, (summary_df, cpu_df, gpu_df))

def print_summary(identifier: SummaryIdentifier, data_repo: DataRepository):
    cpu_src_id = SourceIdentifier(identifier.start_ts, identifier.end_ts, "cpu")
    metadata = data_repo.get_metadata(cpu_src_id)

    summary_df, cpu_df, gpu_df = data_repo.get_data(identifier)

    print(f"Summary for {metadata['readable_period']}")
    print("\n  ".join(summary_df.to_string().split("\n")))
    if(len(cpu_df) > 0):
        print(f"  Top 5 CPU namespaces:")
        print("\n    ".join(cpu_df.to_string().split("\n")))
    if(len(gpu_df) > 0):
        print(f"  Top 5 GPU namespaces:")
        print("\n    ".join(gpu_df.to_string().split("\n")))

def print_all_summaries(data_repo: DataRepository):
    identifiers = data_repo.filter_ids(filter_type(SummaryIdentifier))
    identifiers.sort(key=lambda identifier: identifier.start_ts)
    for identifier in identifiers:
        print_summary(identifier, data_repo)