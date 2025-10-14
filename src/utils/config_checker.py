from src.parameter_utils import ConfigurationException

def verify_sections_exist(config_section: dict, section_name: str, required_sections: set[str], optional_sections: set[str]):
    """
    Verify that sections exist in config, so if we wanted to ensure the config_section had the
        structure:

    section:
      required1:
      required2:
      optional1:

    We would call verify_sections_exist(
                                    config["section"], 
                                    required_sections=["required1", "required2"], 
                                    optional_sections=["optional1", "optional2"]
                                )

    Params:
        config_section (dict): The dictionary holding the config keys/values you want to check.
        section_name (str): The string name of the section, this is for error reporting purposes so
            it can be anything.
        required_sections (set[str]): The list of required sections in the config.
        optional_sections (set[str]): The list of optional sections in the config.    

    Raises:
        ConfigurationException:
            1. The set of keys in config_section is not a superset of required_sections
            2. The set of keys in config_section has elements other than required_sections union 
                optional_sections
                
    Returns:
        None
    """

    if(required_sections is None):
        required_sections = set()
    if(optional_sections is None):
        optional_sections = set()

    config_keys = set(config_section.keys())

    # Ensure all required sections exist
    if(not required_sections.issubset(config_keys)):
        missing_keys = required_sections - config_keys
        raise ConfigurationException(f"Failed to verify config section \"{section_name}\" missing required keys: \"{", ".join(missing_keys)}\"")

    # Ensure config has only the keys listed in required_sections and optional_sections
    all_possible_keys = required_sections.union(optional_sections)
    if(not config_keys.issubset(all_possible_keys)):
        unexpected_keys = config_keys - all_possible_keys
        raise ConfigurationException(f"Failed to verify config section \"{section_name}\" got unexpected keys: \"{", ".join(unexpected_keys)}\"")