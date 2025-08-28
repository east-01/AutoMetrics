import os
import yaml

def load_config(config_location = "./config.yaml"):
    if(not os.path.isfile(config_location)):
        print(f"Error: The config file \"{config}\" doesn't exist. Exiting...")
        exit(1)

    try:
        # Load the YAML file
        with open(config_location, 'r') as file:
            config = yaml.safe_load(file)

        # Ensure the YAML was parsed correctly
        if not isinstance(config, dict):
            raise ValueError("Invalid YAML format. Expected a dictionary structure.")

        return config

    except yaml.YAMLError as e:
        # Catch and handle YAML syntax errors
        print(f"Error: YAML syntax issue in the config file. Details: {e}")
    except KeyError as e:
        # Handle missing keys in the YAML file
        print(f"Error: Missing expected key in the config file: {e}")
    except ValueError as e:
        # Handle any value errors
        print(f"Error: {e}")

class ConfigurationException(Exception):
    pass

def verify_config(prog_data, config):
    if("ingest" not in config):
        raise ConfigurationException("Ingest controllers not configured. Make sure run config includes \"ingest\" as a top level section.")

    loaded_ingests_names = [type(x).__name__ for x in prog_data.loaded_plugins.ingests]
    missing_ingests=set(config["ingest"])-set(loaded_ingests_names)
    if(len(missing_ingests) > 0):
        raise ConfigurationException(f"Run config specifies ingest controller(s) \"{', '.join(missing_ingests)}\" but they were not loaded.")

# def verify_config(prog_data):
#     if(prog_data.config is None):
#         print("Failed to load configuration. Exiting.")
#         exit(1)

#     # A list of keys to ensure they: exist in config, have a value
#     keys_to_check = ["base_url", "queries", "step"]

#     for key_to_check in keys_to_check:
#         if(key_to_check not in prog_data.config.keys() or len(str(prog_data.config[key_to_check])) == 0):
#             print(f"Failed to load configuration. Key \"{key_to_check}\" either doesn't exist in config or has no value. Exiting.")
#             exit(1)

#     if(set(prog_data.config["queries"].keys()) != set(["status", "values"])):
#         print(f"Failed to load configuration. \"Queries\" section expects subsections \"status\" and \"values\"")
#         exit(1)

#     if(prog_data.settings['type_string_identifier'] not in prog_data.config["queries"]["values"]):
#         print(f"The values query (as specified in the configuration) doesn't have the type string identifier \"{prog_data.settings['type_string_identifier']}\" in it. Exiting.")
#         exit(1)

#     return