import os

from program_data.program_data import ProgramData
from program_data.saving.saver import Saver

class DataFrameSaver(Saver):
    def __init__(self):
        self.prog_data = ProgramData()

    def save(self):
        outdir = self.prog_data.args.outdir
        data_blocks = self.prog_data.data_repo.data_blocks

        for identifier in data_blocks.keys():
            data_block = data_blocks[identifier]
            df = data_block['data']

            # Convert the readable_period into a string thats saveable by the file system
            df_path = os.path.join(outdir, f"{data_block['out_file_name']}.csv")
            print(f"  Saving DataFrame file \"{df_path}\"")

            df.to_csv(df_path, index=False)