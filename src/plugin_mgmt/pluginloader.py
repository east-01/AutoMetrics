import os
import importlib.util
import inspect
import sys
from dataclasses import dataclass

from src.plugin_mgmt.plugins import IngestPlugin, Analysis, AnalysisPlugin, AnalysisDriverPlugin, Saver

MODULE_DIR = "./plugins"

@dataclass
class LoadedPlugins:
    ingests: list[IngestPlugin]
    analysis_drivers: list[AnalysisDriverPlugin]
    analyses: list[Analysis]
    savers: list[Saver]

    def __init__(self):
        self.load_plugins()
        self.cache_plugins()

#region Loading
    def load_plugins(self):
        """
        Load all of the plugins in the plugins directory, automatically reads and populates
            extensions of the types in plugins.py. Instantiated objects are stored in the internal
            dataclass lists and can be read by the user.
        
        Returns: None
        """

        self.ingests = []
        self.analysis_drivers = []
        self.analyses = []
        self.savers = []

        self.load_plugins_from_directory(MODULE_DIR)
        self.load_plugins_from_directory("./src/plugin_mgmt/builtin/")

    def load_plugins_from_directory(self, directory):
        for root, dirs, files in os.walk(directory):
            if(root.endswith("__pycache__")):
                continue

            for filename in files:
                if(not filename.endswith(".py")):
                    continue

                path = os.path.join(root, filename)
                self.load_plugins_from_file(path)

    def load_plugins_from_file(self, path):
        """
        Load the plugins in a specific filepath. Instantiated objects stored in dataclass lists.

        Returns: None
        """

        # module_name = os.path.splitext(os.path.relpath(path, MODULE_DIR))[0].replace(os.sep, "_")

        # spec = importlib.util.spec_from_file_location(module_name, path)
        # module = importlib.util.module_from_spec(spec)
        # # module = importlib.import_module(module_name)
        # spec.loader.exec_module(module)

        module_name = os.path.splitext(os.path.relpath(path, MODULE_DIR))[0].replace(os.sep, "_")
        if module_name in sys.modules:
            module = sys.modules[module_name]
        else:
            spec = importlib.util.spec_from_file_location(module_name, path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

        # Scan the module for classes that subclass IngestPlugin
        for name, obj in inspect.getmembers(module, inspect.isclass):
            self.load_object(name, obj, path)

    def load_object(self, name, obj, path):
        """
        Load a specific object. Instantiated objects stored in dataclass lists.

        Returns: None
        """

        # Safely instantiate the object, catching the exception and throwing an error message
        def instantiate():
            try:
                return obj()                
            except Exception as e:
                print(f"Failed to load {name} as {type.__name__} in {path}: {e}")

        # General instantiation- these objects can be insantiated and directly added to their
        #   respective lists

        type_to_list = {
            IngestPlugin: self.ingests,
            AnalysisDriverPlugin: self.analysis_drivers,
            Saver: self.savers
        }

        for type in type_to_list.keys():
            if(not issubclass(obj, type) or obj is type):
                continue
            
            type_to_list[type].append(instantiate())
            
        # Special insantiation- these objects need extra processing to be added
        
        if(issubclass(obj, AnalysisPlugin) and obj is not AnalysisPlugin):
            instance = instantiate()
            for analysis in instance.get_analyses():
                if(analysis in self.analyses):
                    print(f"ERROR: Analysis named \"{analysis.name}\" has already been loaded, but another Analysis plugin {name} is trying to load a new one.")
                    continue

                self.analyses.append(analysis)

    def cache_plugins(self):
        """
        Caches various aspects about loaded plugins. Like storing analyses by name, 
        """
        pass
#endregion

#region Getters
    def get_plugin_by_name(self, plugin_type: str, name: str):
        lists = {
            "ingest": self.ingests,
            "analysisdriver": self.analysis_drivers,
            "saver": self.savers
        }

        if(plugin_type not in lists.keys()):
            raise Exception(f"Plugin type \"{plugin_type}\" not recognized. Supported values are: {", ".join(lists.keys())}")

        list_to_look = lists[plugin_type]

        for plugin in list_to_look:
            pl_name = type(plugin).__name__
            if(pl_name == name):
                return plugin
            
        raise Exception(f"Failed to get \"{plugin_type}\" plugin by name \"{name}\"")

    def get_analysis_driver(self, analysis_type: type):
        """
        Get the analysis driver plugin for this type of analysis.

        Raises:
            Exception: There are no drivers serving this specific type.

        Returns:
            AnalysisDriver: The analysis driver for this specific type.
        """

        for driver in self.analysis_drivers:
            if(driver.SERVED_TYPE == analysis_type):
                return driver
            
        raise Exception(f"No analysis driver for type {analysis_type.__name__} found.")
    
    def get_analysis_by_name(self, analysis_name: str):
        """
        Get an analysis by name.

        Raises:
            Exception: There are no analyses with a matching name to analysis_name.

        Returns:
            Analysis: The analysis with a matching name to analysis_name.
        """

        for analysis in self.analyses:
            if(analysis.name == analysis_name):
                return analysis
            
        raise Exception(f"No analysis present with name {analysis_name}.")
#endregion

    def print_details(self):
        """
        Prints details to the console
        """
        print(f"Loaded ingests: {", ".join([type(ingest).__name__ for ingest in self.ingests])}")
        print(f"Loaded analysis drivers: {", ".join([type(analysis_driver).__name__ for analysis_driver in self.analysis_drivers])}")
        print(f"Loaded analyses: {", ".join([analysis.name for analysis in self.analyses])}")
        print(f"Loaded savers: {", ".join([type(saver).__name__ for saver in self.savers])}")
