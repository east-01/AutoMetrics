import os
from matplotlib.figure import Figure

from src.program_data.program_data import ProgramData
from src.data.data_repository import DataRepository
from src.data.filters import *
from src.data.identifiers.identifier import *
from src.data.saving.saver import Saver

class VizualizationsSaver(Saver):
    def __init__(self, prog_data: ProgramData):
        self.prog_data = prog_data
        
    def save(self):

        data_repo: DataRepository = self.prog_data.data_repo
        identifiers = data_repo.filter_ids(filter_type(VisIdentifier))

        if(len(identifiers) == 0):
            return

        outdir = self.prog_data.args.outdir
        out_path = os.path.join(outdir, "visualizations", "")
        if(not os.path.exists(out_path)):
            os.mkdir(out_path)

        for identifier in identifiers:

            analysis_id: AnalysisIdentifier = identifier.of
            if(not analysis_id.is_meta_analysis()):
                src_id = analysis_id.find_source()

                metadata = data_repo.get_metadata(src_id)
                name_prefix = f"{src_id.type}-{metadata['out_file_name']}"
            else:
                name_prefix = "Entire period"

            fig: Figure = data_repo.get_data(identifier)
            fig.savefig(os.path.join(out_path, f"{name_prefix} {analysis_id.analysis}.png"), bbox_inches='tight')