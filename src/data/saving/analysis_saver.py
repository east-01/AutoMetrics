import os
import pandas as pd

from src.program_data.program_data import ProgramData
from src.data.saving.saver import Saver
from src.utils.fileutils import append_line_to_file

class AnalysisSaver(Saver):
    def __init__(self):
        self.prog_data = ProgramData()

    def save(self):
        outdir = self.prog_data.args.outdir
        out_path = os.path.join(outdir, "analysis", "")
        if(not os.path.exists(out_path)):
            os.mkdir(out_path)
        data_blocks = self.prog_data.data_repo.data_blocks

        # Keep a list of files we've written to so we can clear the contents previously existing files
        has_written = set()

        for identifier in data_blocks.keys():
            data_block = data_blocks[identifier] 

            # Make sure we have results to save
            analysis_results = self.prog_data.analysis_repo[identifier]
            if(len(analysis_results) == 0):
                print(f"Warning: No analysis results were created for data_block {data_block['out_file_name']}")
                continue

            # Make sure the directory holding these results is there
            analysis_dir_path = os.path.join(out_path, f"{data_block['readable_period']} analysis")
            if(not os.path.exists(analysis_dir_path)):
                os.mkdir(analysis_dir_path)

            text_results = []

            for analysis in analysis_results.keys():
                result = analysis_results[analysis]

                # Only save results that exist
                if(result is None):
                    continue

                # Save result to CSV if it's a dataframe, save to text file otherwise
                if(isinstance(result, pd.DataFrame)):
                    path = os.path.join(analysis_dir_path, f"{analysis}.csv")
                    print(f"  Saving analysis file \"{path}\"")
                    result.to_csv(path, index=False)
                else:
                    text_results.append(f"{analysis}: {str(result)}")
            
            if(len(text_results) > 0):
                path = os.path.join(out_path, f"text_results.txt")
                to_append = f"For {data_block['type']}-{data_block['readable_period']}:\n  {"\n  ".join(text_results)}"

                append_line_to_file(path, to_append, path not in has_written)
                has_written.add(path)