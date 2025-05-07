# src/conf/config_loader.py
"""
Handles loading configuration settings for the application.

This module reads settings from the 'config.ini' file located within
this 'conf' directory. It provides functions to access specific
configuration values, such as data file paths.
"""

import configparser
import os

# --- Configuration File Path ---
# This script (config_loader.py) is in the 'src/conf/' directory,
# and 'config.ini' is in the same directory.
CONFIG_FILE_NAME = "config.ini"
# Get the directory where this script is located.
CURRENT_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Construct the full path to the config.ini file.
DEFAULT_CONFIG_PATH = os.path.join(CURRENT_SCRIPT_DIR, CONFIG_FILE_NAME)


def load_configuration(config_file_path: str = DEFAULT_CONFIG_PATH) -> configparser.ConfigParser:
    """
    Loads application settings from the specified .ini configuration file.

    Args:
        config_file_path (str): The full path to the configuration file.
                                Defaults to 'config.ini' in the same directory
                                as this script.

    Returns:
        configparser.ConfigParser: An object containing the parsed configuration.
                                   If the file is not found or an error occurs
                                   during parsing, an empty ConfigParser object is
                                   returned and a warning is printed.
    """
    config = configparser.ConfigParser()
    if not os.path.exists(config_file_path):
        print(f"Warning: Configuration file not found at '{config_file_path}'. "
              "The application might use default internal settings.")
        return config  # Return an empty config; calling code must handle defaults

    try:
        config.read(config_file_path, encoding='utf-8')
    except configparser.Error as e:
        print(f"Error: Could not parse configuration file '{config_file_path}': {e}")
        return configparser.ConfigParser() # Return empty on error to prevent crashes
    return config

def get_data_file_path(
    config: configparser.ConfigParser,
    file_key: str,
    default_path: str
) -> str:
    """
    Retrieves a specific data file path from the '[Paths]' section.

    Args:
        config (configparser.ConfigParser): The loaded configuration object.
        file_key (str): The key for the data file path in the config
                        (e.g., 'client_data_file').
        default_path (str): The default path to return if the key is not found
                            or the section is missing.

    Returns:
        str: The path to the specified data file.
    """
    try:
        # Paths in config.ini are assumed to be relative to the project root.
        # The calling code (e.g., main.py) will use these paths as is.
        return config.get('Paths', file_key, fallback=default_path)
    except (configparser.NoSectionError, configparser.NoOptionError):
        print(f"Warning: '[Paths]' section or '{file_key}' option not found in config. "
              f"Defaulting to '{default_path}'.")
        return default_path
    except Exception as e:
        # Catch any other unexpected error during config access
        print(f"Unexpected error getting '{file_key}' from config: {e}. "
              f"Defaulting to '{default_path}'.")
        return default_path

# --- Specific Path Getter Functions ---

def get_client_data_file(config: configparser.ConfigParser) -> str:
    """Gets the client data file path from config, with a fallback default."""
    return get_data_file_path(config, 'client_data_file', 'src/data/client_record.jsonl')

def get_airline_data_file(config: configparser.ConfigParser) -> str:
    """Gets the airline data file path from config, with a fallback default."""
    return get_data_file_path(config, 'airline_data_file', 'src/data/airline_record.jsonl')

def get_flight_data_file(config: configparser.ConfigParser) -> str:
    """Gets the flight data file path from config, with a fallback default."""
    return get_data_file_path(config, 'flight_data_file', 'src/data/flight_record.jsonl')


# This section allows for direct testing of the config_loader module.
if __name__ == "__main__":
    print("--- Config Loader Direct Test ---")
    print(f"Attempting to load configuration from: {DEFAULT_CONFIG_PATH}")

    # For this direct test, we'll check if a dummy config.ini exists or create one.
    # In the actual application, src/conf/config.ini should be present.
    TEMP_CONFIG_WAS_CREATED = False # Renamed to UPPER_CASE
    if not os.path.exists(DEFAULT_CONFIG_PATH):
        print(f"'{CONFIG_FILE_NAME}' not found in current directory ({CURRENT_SCRIPT_DIR}).\n"
              "Creating a temporary one for this test run.")
        try:
            with open(DEFAULT_CONFIG_PATH, 'w', encoding='utf-8') as temp_config_file:
                temp_config_file.write("[Paths]\n")
                temp_config_file.write("client_data_file = src/data/test_clients.jsonl\n")
                temp_config_file.write("airline_data_file = src/data/test_airlines.jsonl\n")
                # Missing flight_data_file intentionally to test fallback
            TEMP_CONFIG_WAS_CREATED = True # Renamed to UPPER_CASE
        except IOError as e:
            print(f"Error: Could not create temporary config file for testing: {e}")

    # Load the configuration
    app_configuration = load_configuration()

    if app_configuration.sections(): # Check if any sections were loaded
        print("\nConfiguration loaded successfully.")
        client_path = get_client_data_file(app_configuration)
        airline_path = get_airline_data_file(app_configuration)
        flight_path = get_flight_data_file(app_configuration) # This should use default

        print(f"  Client Data File: '{client_path}'")
        print(f"  Airline Data File: '{airline_path}'")
        print(f"  Flight Data File: '{flight_path}' (Note: may be default if not in test config)")
    else:
        print("\nWarning: Configuration could not be loaded or is empty.")
        print("Getter functions will return their default values:")
        print(f"  Default Client Data File: '{get_client_data_file(app_configuration)}'")
        print(f"  Default Airline Data File: '{get_airline_data_file(app_configuration)}'")
        print(f"  Default Flight Data File: '{get_flight_data_file(app_configuration)}'")


    # Clean up the temporary config file if it was created by this test
    if TEMP_CONFIG_WAS_CREATED: # Renamed to UPPER_CASE
        try:
            os.remove(DEFAULT_CONFIG_PATH)
            print(f"\nRemoved temporary '{CONFIG_FILE_NAME}' used for testing.")
        except OSError as e:
            print(f"Error: Could not remove temporary test config file: {e}")
