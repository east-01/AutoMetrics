from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable, Type

from src.program_data import ProgramData
from src.data.data_repository import DataRepository
from src.data.identifier import Identifier
from src.parameter_utils import ConfigurationException

class ConfigurablePlugin(ABC):
    """
    The ConfigurablePlugin ensures that a plugin will be able to accept a configuration section
        before it runs.
    """

    def verify_config_section(self, config_section: dict):
        """
        Verify the configuration section that will be passed to this IngestPlugin. Default 
            behaviour assumes the config section should be empty.

        Raises:
            ConfigurationException: The configuration isn't expected or misconfigured.

        Returns:
            None
        """
        if(config_section is None):
            return True
        else:
            raise ConfigurationException(f"The configuration for {type(self).__name__} is expected to be empty.")

class IngestPlugin(ConfigurablePlugin):    
    @abstractmethod
    def ingest(self, prog_data: ProgramData, config_section: dict) -> DataRepository:
        """
        Ingest data from a source.

        Returns:
            DataRepository: The ingested information.
        """
        pass
    
@dataclass(frozen=True)
class Analysis(ABC):
    name: str
    prereq_analyses: list[str]

class AnalysisPlugin(ABC):
    """
    The AnalysisPlugin acts as a container for analyses that are going to be added. It's main
        purpose is to supply this list of analyses.
    """

    @abstractmethod
    def get_analyses(self) -> list[Analysis]:
        """
        Get the list of Analysis objects from this plugin.

        Returns:
            list[Analysis]: The list of analyses.
        """
        pass

class AnalysisDriverPlugin(ConfigurablePlugin):
    """
    The AnalysisDriverPlugin reads the analysis being performed and is handed the program data,
        this gives flexibility for custom analyses as the driver can supply whatever information it
        needs in run_analyses. See the built in analysis drivers for examples.
    """

    SERVED_TYPE: Type[Analysis] = None

    @abstractmethod
    def run_analysis(self, analysis, prog_data: ProgramData, config_section: dict):
        """ Run this specific analysis. """
        pass

class Saver(ConfigurablePlugin):
    """ The Saver plugin saves data from the DataRepository to the file system. The saver is a
            plugin to allow arbitrary saving of files.
    """

    def verify_config_section(self, config_section):
        """ A default implementation of verify_config_section for the Saver class, this version
                allows empty configs, or a config only with an addtl-base section. """
        if(config_section is None):
            return True
        
        if(len(config_section.keys()) != 1 or "addtl-base" not in config_section.keys()):
            raise ConfigurationException(f"Default verify_config_section for Saver expects either an empty config section or a section with only \"addtl-base\"")

    @abstractmethod
    def save(self, prog_data: ProgramData, config_section: dict, base_path: str) -> list[str]:
        """ Save the data from the DataRepository.
        
        Arguments:
            prog_data (ProgramData): The program data.
            config_section (dict): The configuration section for this plugin.
            base_path (str): The base path for files to be saved to. Specified in run configuration 
                as saving.base_path and in the config_section.addtl-base.

        Returns:
            list[str]: A list of file paths that the Saver plugin saved. 
        """
        pass