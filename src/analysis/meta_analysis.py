import numpy as np
import pandas as pd

from program_data.program_data import ProgramData

def metaanalyze():
    prog_data = ProgramData()
    data_blocks = prog_data.data_repo.data_blocks
    prog_data.meta_analysis_repo = {}
    analysis_options = prog_data.settings['analysis_options']
    meta_analysis_options = prog_data.settings['meta_analysis_options']

    if(prog_data.args.meta_analysis_options is None):
        return

    user_meta_analysis_options = set(prog_data.args.meta_analysis_options)

    print(f"Will perform meta analyses for: {", ".join(user_meta_analysis_options)}")

    period_order = prog_data.data_repo.get_chronological_periods()

    for meta_analysis in user_meta_analysis_options:
        meta_analysis_impl = meta_analysis_options[meta_analysis]
        analyses = meta_analysis_impl["analyses"]

        df = pd.DataFrame(columns=(["Period"]+analyses))

        for period in period_order:
            row = [period]

            for analysis in analyses:
                analysis_impl = analysis_options[analysis]
                targ_type = analysis_impl["types"][0]
                identifier = (period, targ_type)            
                analysis_result = prog_data.analysis_repo[identifier][analysis]
                
                # Ensure result
                if(analysis_result is None):
                    row.append(0)
                    continue
                # Ensure result is a number
                is_number = isinstance(analysis_result, int) or isinstance(analysis_result, float) or isinstance(analysis_result, np.int_) or isinstance(analysis_result, np.float32) or isinstance(analysis_result, np.float64)
                if(not is_number):                    
                    raise ValueError(f"Error while performing meta analysis \"{meta_analysis}\" with analysis \"{analysis}\". The result data type is {type(analysis_result)} when it should be a number.")

                if(analysis_result is not None):
                    row.append(float(analysis_result))
                else:
                    row.append(0)

            df.loc[len(df)] = row

        prog_data.meta_analysis_repo[meta_analysis] = df