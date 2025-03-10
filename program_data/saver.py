import os
import pandas as pd

from utils.fileutils import append_line_to_file

def save(prog_data):
    # Only save if an out directory is specified
    if(prog_data.args.outdir is None):
        return

    # Ensure out directory is created
    outdir = prog_data.args.outdir
    if(not os.path.exists(outdir)):
        os.mkdir(outdir)

    print(f"Saving output to \"{outdir}\"")

    data_blocks = prog_data.data_repo.data_blocks
    # Keep a list of files we've written to so we can clear the contents previously existing files
    has_written = set()

    # Save DataFrames
    for identifier in data_blocks.keys():
        data_block = data_blocks[identifier]
        df = data_block['data']

        # Convert the readable_period into a string thats saveable by the file system
        df_path = os.path.join(outdir, f"{data_block['out_file_name']}.csv")
        print(f"  Saving DataFrame file \"{df_path}\"")

        df.to_csv(df_path, index=False)

    # Save analysis results
    for identifier in data_blocks.keys():
        data_block = data_blocks[identifier] 

        # Make sure we have results to save
        analysis_results = prog_data.analysis_repo[identifier]
        if(len(analysis_results) == 0):
            print(f"Warning: No analysis results were created for data_block {data_block['out_file_name']}")
            continue

        # Make sure the directory holding these results is there
        analysis_dir_path = os.path.join(outdir, f"{data_block['out_file_name']} analysis")
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
            path = os.path.join(outdir, f"text_results.txt")
            to_append = f"For {data_block['type']}-{data_block['readable_period']}:\n  {"\n  ".join(text_results)}"

            append_line_to_file(path, to_append, path not in has_written)
            has_written.add(path)

    # Generate summary csv
    top5_blacklist = prog_data.config['top5hours_blacklist']

    for identifier in data_blocks.keys():
        if(identifier[1] == 'gpu'):
            continue
        
        cpu_ar = prog_data.analysis_repo[identifier]
        gpu_ar = prog_data.analysis_repo[(identifier[0], 'gpu')]

        cpu_df = cpu_ar["cpuhours"]
        cpu_df = cpu_df[cpu_df.apply(lambda row: row.iloc[0] not in top5_blacklist, axis=1)]
        cpu_df = cpu_df.iloc[0:5]
        
        gpu_df = gpu_ar["gpuhours"]
        gpu_df = gpu_df[gpu_df.apply(lambda row: row.iloc[0] not in top5_blacklist, axis=1)]
        gpu_df = gpu_df.iloc[0:5]

        summary_df = pd.DataFrame({
            "Analysis": ["CPU Only Jobs", "GPU Jobs", "Jobs Total", "CPU Hours", "GPU Hours"],
            "Value": [cpu_ar["cpujobstotal"], gpu_ar["gpujobstotal"], cpu_ar["jobstotal"], cpu_ar["cpuhourstotal"], gpu_ar["gpuhourstotal"]]
        })

        try:
            summary_filepath = os.path.join(outdir, f"{data_block['readable_period']} summary.xlsx")
            with pd.ExcelWriter(summary_filepath, engine="xlsxwriter") as writer:
                summary_df.to_excel(writer, sheet_name="Summary", index=False)
                cpu_df.to_excel(writer, sheet_name="Top5 CPU NS", index=False)
                gpu_df.to_excel(writer, sheet_name="Top5 GPU NS", index=False)

                worksheet = writer.sheets["Summary"]
                worksheet.set_column(0, 0, 20)
        except PermissionError:
            print("ERROR: Recieved PermissionError when trying to save summary excel spreadsheet. This can happen if the sheet is open in another window (close excel).")

        print(f"Summary for {data_block['readable_period']}")
        print("\n  ".join(summary_df.to_string().split("\n")))
        print(f"  Top 5 CPU namespaces:")
        print("\n    ".join(cpu_df.to_string().split("\n")))
        print(f"  Top 5 GPU namespaces:")
        print("\n    ".join(gpu_df.to_string().split("\n")))
