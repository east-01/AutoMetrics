from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable, Type

from src.program_data.program_data import ProgramData
from src.data.data_repository import DataRepository
from src.data.identifier import Identifier
from src.program_data.config import ConfigurationException

@dataclass(frozen=True)
class Analysis(ABC):
    name: str
    prereq_analyses: list[str]
    vis_options: dict

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
        if(config_section is not None):
            raise ConfigurationException(f"The configuration for {type(self).__name__} is expected to be empty.")
        return True
    
class IngestPlugin(ConfigurablePlugin):    
    @abstractmethod
    def ingest(self, prog_data: ProgramData, config_section: dict) -> DataRepository:
        """
        Ingest data from a source.

        Returns:
            DataRepository: The ingested information.
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
        """
        Run this specific analysis.
        """
        pass