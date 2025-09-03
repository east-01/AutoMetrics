from collections import defaultdict
import heapq
from typing import Dict, List

from src.program_data.program_data import ProgramData
from src.plugin_mgmt.plugins import Analysis
from src.plugin_mgmt.pluginloader import LoadedPlugins

def get_analysis_order(prog_data: ProgramData):
	"""
	Given the list of analyses to perform, re-order it such that analyses with dependencies are
	  performed last.
	"""

	loaded_plugins: LoadedPlugins = prog_data.loaded_plugins

	appended_metrics = []
	  
	# Populate additional analyses to perform from requirements
	for to_perform in prog_data.args.analysis_options:
		to_perform_analysis = prog_data.loaded_plugins.get_analysis_by_name(to_perform)
		prereq_analyses = to_perform_analysis.prereq_analyses

		if(prereq_analyses is None):
			continue

		for requirement in prereq_analyses:
			if(requirement not in prog_data.args.analysis_options):
				print(f"Added additional analysis \"{requirement}\" as it is a requirement of \"{to_perform}\"")
				appended_metrics.append(requirement)
				prog_data.args.analysis_options.append(requirement)

	if(len(appended_metrics) > 0):
		print(f"Added missing required analyses: {", ".join(appended_metrics)}")

	return _topo_sort([loaded_plugins.get_analysis_by_name(analysis) for analysis in prog_data.args.analysis_options])

def _topo_sort(analyses: List[Analysis]) -> List[Analysis]:
	# Map names to Analysis objects
	name_to_analysis: Dict[str, Analysis] = {a.name: a for a in analyses}

	# Build graph (dependencies: prereq -> dependent)
	graph = defaultdict(list)
	indegree = {a.name: 0 for a in analyses}

	for analysis in analyses:
		if(analysis.prereq_analyses is None):
			continue

		for prereq in analysis.prereq_analyses:
			if prereq not in name_to_analysis:
				raise ValueError(f"Prereq '{prereq}' for {analysis.name} not found in analyses")
			graph[prereq].append(analysis.name)
			indegree[analysis.name] += 1

	# Use min-heap for deterministic order
	heap = [name for name, deg in indegree.items() if deg == 0]
	heapq.heapify(heap)

	sorted_order = []

	while heap:
		name = heapq.heappop(heap)
		sorted_order.append(name_to_analysis[name])

		for dep in sorted(graph[name]):  # also sort dependents for consistency
			indegree[dep] -= 1
			if indegree[dep] == 0:
				heapq.heappush(heap, dep)

	if len(sorted_order) != len(analyses):
		raise ValueError("Cycle detected in prereq graph!")

	return sorted_order