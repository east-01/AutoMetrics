from src.program_data.program_data import ProgramData
from src.analysis.implementations.hours import *
from src.analysis.implementations.jobs import *
from src.analysis.implementations.meta_analysis import meta_analyze
from src.data.data_repository import DataRepository
from src.data.identifiers.identifier import Identifier, AnalysisIdentifier, SourceIdentifier
from src.data.filters import filter_type
from src.analysis.grafana_df_cleaning import extract_column_data

analysis_options_methods = {
	"cpuhours": analyze_hours_byns,
	"cpuhourstotal": analyze_hours_total,
	"cpujobs": analyze_cpu_only_jobs_byns,
	"cpujobstotal": analyze_jobs_total,
	"gpuhours": analyze_hours_byns,
	"gpuhourstotal": analyze_hours_total,
	"gpujobs": analyze_jobs_byns,
	"gpujobstotal": analyze_jobs_total,
	"jobstotal": analyze_all_jobs_total
}



def analyze(prog_data: ProgramData):
	"""
	Analyze the current ProgramData for the target analysis options selected. Analysis options are
	  performed for each data block, meaning there will be a separate set of analysis results for
	  each.
	Results are stored in a dictionary with the analysis name as the key and the result output as 
	  the value.
	Results are placed in ProgramData#data_repo as they are generated so that other methods can
	  use them.
	"""
	data_repo: DataRepository = prog_data.data_repo
	
	analyses_to_perform = get_analysis_order(prog_data)

	


	print(f"Analysis perform order: {", ".join(analyses_to_perform)}")

	# Fulfilled analyses is used to ensure all analysis that were requested were performed. All
	#   analyses may not be fulfilled if the user provides an input directory without all the
	#   required csv files. For example, the user requests gpuhours but only provides cpu dfs.
	fulfilled_analyses = set()

	for analysis in analyses_to_perform:
		analysis_settings = prog_data.settings["analysis_settings"][analysis]

		# When the analysis settings do not have a filter it's considered a meta analysis, see
		#   meta_analyze description for more details.
		is_standard_analysis = "filter" in analysis_settings.keys()

		if(is_standard_analysis):
			# Perform a standard analysis.

			# Get filter and apply to data_repo, the filter finds the Identifiers that the analysis
			#   will use in its calculation.
			analysis_filter = analysis_settings["filter"]
			identifiers = data_repo.filter_ids(analysis_filter)

			# If the length of the target identifiers is zero then we can't perform and fulfill 
			#   the analysis.
			if(len(identifiers) == 0):
				continue

			# Get the analysis method implementation for this specific analysis.
			# For example, if the analysis is cpuhours the analysis_method will be 
			#   src/analysis/implementations/analyze_hours_byns.
			analysis_method = analysis_options_methods[analysis]

			print(f"  Performing {analysis} on {len(identifiers)} target(s).")

			for identifier in identifiers:
				analysis_result = analysis_method(identifier, data_repo)
				if analysis == "cpuhourstotal":
					max_hours = check_if_over_monthly_hours(identifier, data_repo, prog_data)
					import sys
					sys.exit()
				# Generate identifier and add to repository.
				analysis_identifier = AnalysisIdentifier(identifier, analysis)
				data_repo.add(analysis_identifier, analysis_result)

			fulfilled_analyses.add(analysis)

		else:
			# Perform a meta analysis.

			print(f"  Performing {analysis}.")

			analysis_result = meta_analyze(analysis_settings["requires"], data_repo)

			# Generate identifier and add to repository.
			analysis_identifier = AnalysisIdentifier(None, analysis)
			data_repo.add(analysis_identifier, analysis_result)

			fulfilled_analyses.add(analysis)     			
			# print("test")
			# max_hours = check_if_over_monthly_hours(identifier, data_repo, prog_data)
			# print(analysis)
			# import sys
			# sys.exit()
	# Check with fulfilled_analyses to ensure all we're properly fulfilled.
	analyses_to_perform_set = set(analyses_to_perform)
	if(analyses_to_perform_set != fulfilled_analyses):
		raise Exception(f"Failed to fulfill all analyses: {list(analyses_to_perform_set-fulfilled_analyses)} (was all data loaded properly? using custom file/directory?)")

	prog_data.data_repo = data_repo

def check_if_over_monthly_hours(identifier, data_repo,prog_data):
	
	# start_ts = identifier.on.start_ts
	# end_ts = identifier.on.end_ts
	# print(start_ts)
	# print(end_ts)
	# total_hours_month = (end_ts-start_ts+1)/3600
	# print("total hours in month ", total_hours_month)
	# print(filter_ids(SourceIdentifier))
	source_id = data_repo.filter_ids(filter_type(SourceIdentifier))
	print(len(source_id))
	for id in source_id:
		print(id)
		col_names = data_repo.get_data(id).columns
		for col_name in col_names[1:]:
			col_data = extract_column_data(col_name)
			print(col_data)

	print(data_repo.print_contents())

	cpu_core_per_node_tide = prog_data.settings["cpu_core_per_node_tide"]
	num_cpu_cores = cpu_core_per_node_tide['cpu']
	
	# total_hours_month * cpu * nodes 
	return 

def get_analysis_order(prog_data: ProgramData):
	"""
	Given the list of analyses to perform, re-order it such that analyses with dependencies are
	  performed last.
	"""
	order = []

	user_analysis_options = set(prog_data.args.analysis_options)
	analysis_options = prog_data.settings["analysis_settings"]
	
	# Only iterate n**2 times, any further iterations would mean there is an impossible/circular dependency
	for _ in range(0, len(analysis_options.keys())**2):
		for analysis_key in list(user_analysis_options):
			requirements = analysis_options[analysis_key]["requires"]
			if(all(x in order for x in requirements)):
				order.append(analysis_key)
				user_analysis_options.remove(analysis_key)

	if(len(user_analysis_options) > 0):
		raise Exception(f"Failed to generate analysis order, could there be a circular/impossible dependency? Remaining analyses: {user_analysis_options}")

	return order


