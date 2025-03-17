import os

from program_data.program_data import ProgramData
from program_data.saving.saver import Saver

class VizualizationsSaver(Saver):
    def __init__(self):
        self.prog_data = ProgramData()

    def save(self):
        outdir = self.prog_data.args.outdir
        data_blocks = self.prog_data.data_repo.data_blocks

        for identifier in data_blocks.keys():
            data_block = data_blocks[identifier] 

            # Make sure we have visualizations to save
            vizualizations = self.prog_data.vis_repo[identifier]
            if(len(vizualizations) == 0):
                continue

            # Make sure the directory holding the vizualizations is there
            vis_dir_path = os.path.join(outdir, f"vizualizations")
            if(not os.path.exists(vis_dir_path)):
                os.mkdir(vis_dir_path)

            for analysis in vizualizations.keys():
                vis = vizualizations[analysis]
                vis.savefig(os.path.join(vis_dir_path, f"{data_block['type']}-{data_block['readable_period']} {analysis}.png"), bbox_inches='tight')