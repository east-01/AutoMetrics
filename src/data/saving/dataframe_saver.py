import os

from src.program_data.program_data import ProgramData
from src.data.data_repository import DataRepository
from src.data.filters import *
from src.data.saving.saver import Saver

class DataFrameSaver(Saver):
    def __init__(self, prog_data: ProgramData):
        self.prog_data = prog_data

    def save(self):

        data_repo: DataRepository = self.prog_data.data_repo

        outdir = self.prog_data.args.outdir
        out_path = os.path.join(outdir, "sources", "")
        if(not os.path.exists(out_path)):
            os.mkdir(out_path)
        
        for identifier in data_repo.filter_ids(filter_type(SourceIdentifier)):
            df = data_repo.get_data(identifier)
            metadata = data_repo.get_metadata(identifier)

            # Convert the readable_period into a string thats saveable by the file system
            df_path = os.path.join(out_path, f"{metadata['out_file_name']}.csv")
            print(f"  Saving DataFrame file \"{df_path}\"")

            df.to_csv(df_path, index=False)