import os

from src.program_data.program_data import ProgramData
from src.data.saving.saver import Saver

class DataFrameSaver(Saver):
    def __init__(self):
        self.prog_data = ProgramData()

    def save(self):
        outdir = self.prog_data.args.outdir
        out_path = os.path.join(outdir, "sources", "")
        if(not os.path.exists(out_path)):
            os.mkdir(out_path)
        data_blocks = self.prog_data.data_repo.data_blocks

        for identifier in data_blocks.keys():
            data_block = data_blocks[identifier]
            df = data_block['data']

            # Convert the readable_period into a string thats saveable by the file system
            df_path = os.path.join(out_path, f"{data_block['out_file_name']}.csv")
            print(f"  Saving DataFrame file \"{df_path}\"")

            df.to_csv(df_path, index=False)