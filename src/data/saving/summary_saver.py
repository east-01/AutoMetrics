import os
import pandas as pd

from src.program_data.program_data import ProgramData
from src.data.saving.saver import Saver

class SummarySaver(Saver):
    def __init__(self):
        self.prog_data = ProgramData()

        # Ensure we have all of the required analyses for the summary
        self.can_summarize = True
        summary_analyses = ["cpuhours", "gpuhours", "jobstotal", "cpuhourstotal", "gpuhourstotal"]
        for summary_analyis in summary_analyses:
            if(summary_analyis not in self.prog_data.args.analysis_options):
                print(f"Can't summarize, analysis \"{summary_analyis}\" missing.")
                self.can_summarize = False
                break
            
        # Stores summary tuples (see return of get_summary) with data_block identifier keys
        self.summaries = {}

    def get_summary(self, identifier) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        if(identifier in self.summaries.keys()):
            return self.summaries[identifier]
        
        # Summaries should be determined based off of the CPU dataframe (it holds most analysis results)
        if(identifier[1] == 'gpu'):
            return self.get_summary((identifier[0], 'cpu'))
        
        # Load top 5 namespaces data frames from each _hours analysis result
        top5_blacklist = self.prog_data.config['top5hours_blacklist']
        cpu_ar = self.prog_data.analysis_repo[identifier]
        cpu_df = cpu_ar["cpuhours"]
        cpu_df = cpu_df[cpu_df.apply(lambda row: row.iloc[0] not in top5_blacklist, axis=1)].iloc[0:5].reset_index(drop=True)
        
        gpu_ar = self.prog_data.analysis_repo[(identifier[0], 'gpu')]
        gpu_df = gpu_ar["gpuhours"]
        gpu_df = gpu_df[gpu_df.apply(lambda row: row.iloc[0] not in top5_blacklist, axis=1)].iloc[0:5].reset_index(drop=True)

        # Create the summary data frame
        summary_df = pd.DataFrame({
            "Analysis": ["CPU Only Jobs", "GPU Jobs", "Jobs Total", "CPU Hours", "GPU Hours"],
            "Value": [cpu_ar["cpujobstotal"], gpu_ar["gpujobstotal"], cpu_ar["jobstotal"], cpu_ar["cpuhourstotal"], gpu_ar["gpuhourstotal"]]
        })

        self.summaries[identifier] = (summary_df, cpu_df, gpu_df)
        return self.summaries[identifier]

    def print_summary(self, identifier):
        summary_df, cpu_df, gpu_df = self.get_summary(identifier)
        data_block = self.prog_data.data_repo.data_blocks[identifier]

        print(f"Summary for {data_block['readable_period']}")
        print("\n  ".join(summary_df.to_string().split("\n")))
        print(f"  Top 5 CPU namespaces:")
        print("\n    ".join(cpu_df.to_string().split("\n")))
        print(f"  Top 5 GPU namespaces:")
        print("\n    ".join(gpu_df.to_string().split("\n")))

    def print_all_summaries(self):
        for identifier in self.prog_data.data_repo.data_blocks.keys():
            if(identifier[1]=='gpu'):
                continue

            self.print_summary(identifier)

    def save(self):
        outdir = self.prog_data.args.outdir
        try:
            for identifier in self.prog_data.data_repo.data_blocks.keys():
                if(identifier[1]=='gpu'):
                    continue

                summary_df, cpu_df, gpu_df = self.get_summary(identifier)
                data_block = self.prog_data.data_repo.data_blocks[identifier]

                summary_filepath = os.path.join(outdir, f"{data_block['readable_period']} summary.xlsx")
                with pd.ExcelWriter(summary_filepath, engine="xlsxwriter") as writer:
                    summary_df.to_excel(writer, sheet_name="Summary", index=False)
                    cpu_df.to_excel(writer, sheet_name="Top5 CPU NS", index=False)
                    gpu_df.to_excel(writer, sheet_name="Top5 GPU NS", index=False)

                    worksheet = writer.sheets["Summary"]
                    worksheet.set_column(0, 0, 20)
        except PermissionError:
            print("ERROR: Recieved PermissionError when trying to save summary excel spreadsheet. This can happen if the sheet is open in another window (close excel).")