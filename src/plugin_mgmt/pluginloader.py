import os
import importlib.util
import inspect
from dataclasses import dataclass

from src.plugin_mgmt.plugins import IngestPlugin, Analysis, AnalysisPlugin

MODULE_DIR = "./plugins"

@dataclass
class LoadedPlugins:
    ingests: list[IngestPlugin]
    analyses: dict[str, Analysis]

def load_plugins():
    loaded_ingests = []
    loaded_analyses = {}

    for root, dirs, files in os.walk(MODULE_DIR):
        if(root.endswith("__pycache__")):
            continue

        for filename in files:
            if(not filename.endswith(".py")):
                continue

            path = os.path.join(root, filename)
            module_name = os.path.splitext(os.path.relpath(path, MODULE_DIR))[0].replace(os.sep, "_")

            spec = importlib.util.spec_from_file_location(module_name, path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Scan the module for classes that subclass IngestPlugin
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, IngestPlugin) and obj is not IngestPlugin:
                    instance = obj()
                    loaded_ingests.append(instance)
                elif(issubclass(obj, AnalysisPlugin) and obj is not AnalysisPlugin):
                    instance = obj()
                    for analysis in instance.get_analyses():
                        if(analysis.name in loaded_analyses.keys()):
                            print(f"ERROR: Analysis named \"{analysis.name}\" has already been loaded, but another Analysis plugin {name} is trying to load a new one.")
                            continue

                        loaded_analyses[analysis.name] = analysis

    return LoadedPlugins(ingests=loaded_ingests, analyses=loaded_analyses)
