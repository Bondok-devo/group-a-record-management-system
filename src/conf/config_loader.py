# src/conf/config_loader.py
"""
Handles loading configuration settings for the application.

This module reads settings, prioritizing environment variables for data file paths,
and falling back to hardcoded defaults if environment variables are not set.
The use of config.ini has been removed.
"""

import os

# --- Environment Variable Names ---
ENV_CLIENT_DATA_FILE = 'TRMS_CLIENT_DATA_FILE'
ENV_AIRLINE_DATA_FILE = 'TRMS_AIRLINE_DATA_FILE'
ENV_FLIGHT_DATA_FILE = 'TRMS_FLIGHT_DATA_FILE'

# --- Default Paths (relative to project root if not overridden by env vars) ---
# These are used if environment variables do not specify the path.
DEFAULT_CLIENT_PATH_REL = 'src/data/client_record.jsonl'
DEFAULT_AIRLINE_PATH_REL = 'src/data/airline_record.jsonl'
DEFAULT_FLIGHT_PATH_REL = 'src/data/flight_record.jsonl'


def get_data_file_path(
    env_var_name: str,
    default_relative_path: str
) -> str:
    """
    Retrieves a specific data file path with priority: Environment Variable > Default.
    Default paths are assumed relative to the project root.
    Environment variable paths are used as-is (expected to be absolute or correctly relative).

    Args:
        env_var_name (str): The name of the environment variable.
        default_relative_path (str): Default path relative to project root.

    Returns:
        str: The determined path to the data file.
    """
    # 1. Check Environment Variable
    path_from_env = os.getenv(env_var_name)
    if path_from_env:
        print(f"Using path from environment variable {env_var_name}: '{path_from_env}'")
        # Assuming env var path is either absolute or correctly relative to CWD
        return os.path.normpath(path_from_env)

    # 2. Use Default Path
    print(f"Warning: Environment variable '{env_var_name}' not set. "
          f"Using default path: '{default_relative_path}'.")
    # Default paths like "src/data/file.jsonl" are relative to project root.
    # When the app runs from project root, these paths work directly.
    # If main.py is in src/ and project root is added to sys.path,
    # these relative paths from project root are fine.
    return os.path.normpath(default_relative_path)

# --- Specific Path Getter Functions ---
# These functions no longer require the 'config' object.

def get_client_data_file() -> str:
    """Gets the client data file path."""
    return get_data_file_path(
        ENV_CLIENT_DATA_FILE, DEFAULT_CLIENT_PATH_REL
    )

def get_airline_data_file() -> str:
    """Gets the airline data file path."""
    return get_data_file_path(
        ENV_AIRLINE_DATA_FILE, DEFAULT_AIRLINE_PATH_REL
    )

def get_flight_data_file() -> str:
    """Gets the flight data file path."""
    return get_data_file_path(
        ENV_FLIGHT_DATA_FILE, DEFAULT_FLIGHT_PATH_REL
    )


# This section allows for direct testing of the config_loader module.
if __name__ == "__main__":
    print("--- Config Loader Direct Test (No config.ini) ---")

    # To test, you would typically set environment variables before running this script,
    # or rely on the defaults. For example, in your terminal:
    # export TRMS_CLIENT_DATA_FILE="/tmp/env_client_test.jsonl"
    # python src/conf/config_loader.py
    # unset TRMS_CLIENT_DATA_FILE

    # Or, for a programmatic test, you can temporarily set them (not recommended for app code):
    # original_env_value = os.getenv(ENV_CLIENT_DATA_FILE)
    # os.environ[ENV_CLIENT_DATA_FILE] = "/tmp/prog_env_client_test.jsonl"
    # print(f"Temporarily set {ENV_CLIENT_DATA_FILE} for testing via os.environ.")

    print("\n--- Path Resolution Test ---")
    client_path = get_client_data_file()
    airline_path = get_airline_data_file()
    flight_path = get_flight_data_file()

    print(f"  Resolved Client Data File: '{client_path}'")
    print(f"  Resolved Airline Data File: '{airline_path}'")
    print(f"  Resolved Flight Data File: '{flight_path}'")

    # Clean up programmatic test env var if set
    # if original_env_value is None and ENV_CLIENT_DATA_FILE in os.environ:
    #     del os.environ[ENV_CLIENT_DATA_FILE]
    #     print(f"Cleaned up temporary env var {ENV_CLIENT_DATA_FILE} (was not set before).")
    # elif original_env_value is not None:
    #     os.environ[ENV_CLIENT_DATA_FILE] = original_env_value # Restore original
    #     print(f"Restored original env var {ENV_CLIENT_DATA_FILE}.")

    print("\nTest finished. If you set environment variables manually, "
          "they might still be in your session.")
