from matplotlib.figure import Figure
import os

from src.builtin_plugins.vis_analysis_driver import VisIdentifier
from src.data.data_repository import DataRepository
from src.data.filters import *
from src.plugin_mgmt.plugins import Saver
from src.program_data import ProgramData

class VizualizationsSaver(Saver):
    """ The VisualizationsSaver will save generated visualizations as pngs. Only looking for
            VisIdentifiers and saving them.
    """ 
    def save(self, prog_data: ProgramData, config_section: dict, base_path: str):

        data_repo: DataRepository = prog_data.data_repo
        identifiers = data_repo.filter_ids(filter_type(VisIdentifier))

        if(len(identifiers) == 0):
            return

        out_path = base_path
        if(not os.path.exists(out_path)):
            os.mkdir(out_path)

        saved_files = []

        for identifier in identifiers:

            analysis_id: AnalysisIdentifier = identifier.of
            if(not isinstance(analysis_id, MetaAnalysisIdentifier)):
                src_id = analysis_id.find_base()
                name_prefix = src_id.fs_str()
            else:
                name_prefix = "Entire period"

            fig: Figure = data_repo.get_data(identifier)
            path = os.path.join(out_path, f"{name_prefix} {analysis_id.analysis}.png")
            print(f"  Saving visualization file \"{path}\"")

            fig.savefig(path, bbox_inches='tight')

            saved_files.append(path)
        
        return saved_files