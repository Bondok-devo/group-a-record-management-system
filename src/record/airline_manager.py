# src/record/airline_manager.py
"""
Manages airline company records, including loading, saving, and CRUD operations.
This module provides the AirlineManager class to handle all aspects of
airline data persistence and manipulation.
"""

import json
import os
from typing import List, Dict, Optional, Any

# airline_record.py (with AirlineRecord class) is in the same package.
# An empty __init__.py in 'src/record/' makes 'record' a package.
from .airline_record import AirlineRecord


class AirlineManager:
    """
    Handles all operations related to airline company records.

    This class loads airline data from a JSONL file, allows for
    Create, Read, Update, and Delete (CRUD) operations, and saves
    changes back to the file.
    """

    def __init__(self, airlines_file_path: str):
        """
        Initializes the AirlineManager.

        Loads existing airline data from the specified file path.

        Args:
            airlines_file_path (str): The full path to the airline data file
                                     (e.g., 'src/data/airline_record.jsonl').
        """
        if not airlines_file_path:
            raise ValueError("AirlineManager requires a valid airlines_file_path.")

        self.airlines_file_path = airlines_file_path
        self._airlines: List[AirlineRecord] = []
        self._next_id: int = 1  # Used for generating unique airline IDs.
        self._load_airlines()

    def _load_airlines(self) -> None:
        """
        Loads airline records from the JSONL file into memory.

        Reads each line, expecting a JSON object representing an airline.
        Updates the internal list of airlines and determines the next
        available ID for new airlines.
        """
        self._airlines = []
        if not os.path.exists(self.airlines_file_path):
            return  # No file to load, will be created on first save.

        highest_id_found = 0
        try:
            with open(self.airlines_file_path, 'r', encoding='utf-8') as file:
                for line_number, line in enumerate(file, 1):
                    line_content = line.strip()
                    if not line_content:
                        continue

                    try:
                        data = json.loads(line_content)
                        # This manager should only deal with records of type "Airline".
                        if data.get("record_type") == "Airline":
                            airline = AirlineRecord.from_dict(data) # Expects "airline_id"
                            self._airlines.append(airline)
                            # Use .airline_id as per AirlineRecord class
                            if airline.airline_id is not None and airline.airline_id > highest_id_found:
                                highest_id_found = airline.airline_id
                    except json.JSONDecodeError:
                        print(f"Warning: Invalid JSON on line {line_number} in "
                              f"'{self.airlines_file_path}'. Skipping.")
                    except ValueError as e:
                        print(f"Warning: Invalid data for record on line {line_number} "
                              f"in '{self.airlines_file_path}': {e}. Skipping.")
                    except TypeError as e:
                        print(f"Warning: Type error for record on line {line_number} "
                              f"in '{self.airlines_file_path}': {e}. Skipping.")
        except IOError as e:
            print(f"Warning: Could not read '{self.airlines_file_path}': {e}. "
                  "Starting with no airlines.")
        except Exception as e:
            # This broad exception is a last resort to prevent crashing during load.
            print(f"An unexpected error occurred loading airlines: {e}")

        self._next_id = highest_id_found + 1

    def _save_airlines(self) -> bool:
        """
        Saves the current list of airlines to the JSONL file.

        Each airline is written as a JSON object on a new line, overwriting
        the existing file content. Ensures the directory for the file exists.

        Returns:
            True if saving was successful, False otherwise.
        """
        try:
            # Ensure the directory for the specific data file exists
            file_directory = os.path.dirname(self.airlines_file_path)
            if file_directory: # Check if there's a directory part (not just filename)
                os.makedirs(file_directory, exist_ok=True)

            with open(self.airlines_file_path, 'w', encoding='utf-8') as file:
                for airline_item in self._airlines:
                    airline_dict = airline_item.to_dict() # This will have "airline_id" key
                    # AirlineRecord.to_dict() should ensure record_type is "Airline"
                    json.dump(airline_dict, file)
                    file.write('\n')
            return True
        except IOError as e:
            print(f"Error: Could not write to '{self.airlines_file_path}': {e}. "
                  "Changes may not be saved.")
            return False
        except Exception as e:
            # This broad exception is a last resort for saving errors.
            print(f"An unexpected error occurred while saving airlines: {e}")
            return False

    def _generate_id(self) -> int:
        """Generates a new, unique ID for an airline."""
        new_id = self._next_id
        self._next_id += 1
        return new_id

    def add_airline(self, airline_data: Dict[str, Any]) -> Optional[AirlineRecord]:
        """
        Adds a new airline to the system.

        A unique ID is generated. The 'record_type' must be provided in airline_data
        and should typically be "Airline".
        The primary data expected in airline_data is 'company_name' and 'record_type'.

        Args:
            airline_data: Dictionary of airline information,
                          e.g., {"company_name": "PythonAir", "record_type": "Airline"}.

        Returns:
            The created AirlineRecord object if successful, else None.
        """
        new_airline_id_val = self._generate_id()
        data_for_record = airline_data.copy()
        # Key for AirlineRecord.from_dict and in its to_dict is "airline_id"
        data_for_record['airline_id'] = new_airline_id_val

        if 'record_type' not in data_for_record:
            print("Error: 'record_type' is required to add an airline.")
            self._next_id -=1 # Rollback ID
            return None
        if data_for_record['record_type'] != "Airline":
            print(f"Warning: Attempting to add an airline with record_type "
                  f"'{data_for_record['record_type']}'. Ensure this is intended.")

        if 'company_name' not in data_for_record or not data_for_record['company_name']:
            print("Error: Could not add airline. 'company_name' is required and cannot be empty.")
            self._next_id -=1 # Rollback ID
            return None

        try:
            new_airline = AirlineRecord.from_dict(data_for_record)
            self._airlines.append(new_airline)
            if self._save_airlines():
                return new_airline
            # Rollback if save failed
            self._airlines.pop()
            self._next_id -= 1
            print("Error: Failed to save after adding airline. Airline not added.")
            return None
        except ValueError as e: # Errors from AirlineRecord.from_dict
            print(f"Error: Could not add airline. Invalid data: {e}")
            self._next_id -= 1 # Rollback ID
            return None
        except Exception as e:
            # This broad exception is a last resort for add operation errors.
            print(f"An unexpected error occurred while adding airline: {e}")
            self._next_id -= 1
            return None

    def get_airline_by_id(self, airline_id_val: int) -> Optional[AirlineRecord]:
        """
        Retrieves an airline by its unique ID.

        Args:
            airline_id_val: The integer ID of the airline.

        Returns:
            The AirlineRecord object if found, otherwise None.
        """
        if not isinstance(airline_id_val, int):
            return None
        for airline_item in self._airlines:
            if airline_item.airline_id == airline_id_val: # Use .airline_id
                return airline_item
        return None

    def get_all_airlines(self) -> List[AirlineRecord]:
        """
        Returns a list of all airline records.

        Returns:
            A list of AirlineRecord objects (a copy of the internal list).
        """
        return self._airlines[:] # Return a shallow copy

    def update_airline(self, airline_id_val: int,
                       update_info: Dict[str, Any]) -> Optional[AirlineRecord]:
        """
        Updates an existing airline's information.

        'airline_id' in update_info will be ignored.
        Args:
            airline_id_val: The ID of the airline to update.
            update_info: Dictionary with fields to update.

        Returns:
            The updated AirlineRecord object if successful, else None.
        """
        airline_to_update = None
        airline_index = -1
        for i, al_item in enumerate(self._airlines):
            if al_item.airline_id == airline_id_val: # Use .airline_id
                airline_to_update = al_item
                airline_index = i
                break

        if not airline_to_update:
            print(f"Info: No airline found with ID {airline_id_val} to update.")
            return None

        current_data = airline_to_update.to_dict() # This will have "airline_id" key
        original_data_backup = current_data.copy()
        changed_fields = False

        for key, value in update_info.items():
            if key == "airline_id": # Prevent changing ID through this method
                continue
            if key in current_data:
                if current_data[key] != value:
                    current_data[key] = value
                    changed_fields = True
            # Allow adding new keys if AirlineRecord can handle them (flexible)
            # For AirlineRecord, we are mainly concerned with company_name and record_type
            elif key in ["company_name", "record_type"]:
                current_data[key] = value
                changed_fields = True

        if not changed_fields:
            return airline_to_update

        try:
            # from_dict expects "airline_id" key, which current_data (from to_dict) has.
            updated_airline_obj = AirlineRecord.from_dict(current_data)
            self._airlines[airline_index] = updated_airline_obj
            if self._save_airlines():
                return updated_airline_obj
            self._airlines[airline_index] = AirlineRecord.from_dict(original_data_backup)
            print(f"Error: Failed to save updates for airline ID {airline_id_val}. "
                  "Changes rolled back.")
            return None
        except ValueError as e:
            print(f"Error: Could not update airline ID {airline_id_val}. "
                  f"Invalid data after update: {e}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred while updating airline {airline_id_val}: {e}")
            return None

    def delete_airline(self, airline_id_val: int) -> bool:
        """
        Removes an airline from the system.

        Args:
            airline_id_val: The ID of the airline to delete.

        Returns:
            True if deletion was successful, False otherwise.
        """
        airline_to_delete = None
        airline_index = -1
        for i, al_item in enumerate(self._airlines):
            if al_item.airline_id == airline_id_val: # Use .airline_id
                airline_to_delete = al_item
                airline_index = i
                break

        if not airline_to_delete:
            return False

        self._airlines.pop(airline_index)
        if self._save_airlines():
            return True
        self._airlines.insert(airline_index, airline_to_delete)
        print(f"Error: Failed to save after deleting airline ID {airline_id_val}. "
              "Deletion rolled back.")
        return False

# This section is for direct testing of the AirlineManager.
if __name__ == "__main__":
    print("--- AirlineManager Direct Test ---")

    # Determine the project root directory (GROUP-A) to correctly place temp_test_output
    current_script_path = os.path.abspath(__file__)
    record_dir = os.path.dirname(current_script_path)
    src_dir = os.path.dirname(record_dir)
    project_root = os.path.dirname(src_dir)

    # Define the path for test data, ensuring it's outside src/
    TEST_DATA_SUBDIR_NAME = "airline_manager_test_data"
    TEMP_TEST_OUTPUT_ROOT_DIR_NAME = "temp_test_output" # This folder should be in .gitignore

    test_data_specific_folder = os.path.join(project_root,
                                             TEMP_TEST_OUTPUT_ROOT_DIR_NAME,
                                             TEST_DATA_SUBDIR_NAME)
    TEST_DATA_FILE_NAME = "airline_record.jsonl"
    test_file_full_path = os.path.join(test_data_specific_folder, TEST_DATA_FILE_NAME)


    if not os.path.exists(test_data_specific_folder):
        os.makedirs(test_data_specific_folder, exist_ok=True)
        print(f"Created test data directory: {test_data_specific_folder}")

    print("Test block assumes 'from .airline_record import AirlineRecord' at the top is working.")

    # Initialize manager with the specific test file path
    manager = AirlineManager(airlines_file_path=test_file_full_path)
    print(f"Test data file will be: {manager.airlines_file_path}")

    if os.path.exists(manager.airlines_file_path):
        os.remove(manager.airlines_file_path)
        print(f"Cleared old test file: {manager.airlines_file_path}")
    # Re-instantiate manager for a clean state.
    manager = AirlineManager(airlines_file_path=test_file_full_path)

    print(f"\nInitial airlines loaded: {len(manager.get_all_airlines())}")

    print("\n1. Adding new airlines...")
    airline1_data = {"record_type": "Airline", "company_name": "PythonAir"}
    airline2_data = {"record_type": "Airline", "company_name": "TkinterFly"}

    py_air = manager.add_airline(airline1_data)
    tk_fly = manager.add_airline(airline2_data)

    if py_air:
        print(f"Added: {py_air.company_name} with ID {py_air.airline_id}")
    if tk_fly:
        print(f"Added: {tk_fly.company_name} with ID {tk_fly.airline_id}")

    print(f"\nTotal airlines now: {len(manager.get_all_airlines())}")

    print("\n2. Getting an airline by ID...")
    if py_air:
        retrieved_py_air = manager.get_airline_by_id(py_air.airline_id)
        if retrieved_py_air:
            print(f"Found: {retrieved_py_air.company_name}")

    print("\n3. Updating an airline...")
    if tk_fly:
        updated_tk_fly = manager.update_airline(
            tk_fly.airline_id,
            {"company_name": "TkinterJet Express", "record_type": "Airline"}
        )
        if updated_tk_fly:
            print(f"Updated Airline: Name - {updated_tk_fly.company_name}")
        else:
            print(f"Failed to update TkinterFly (ID: {tk_fly.airline_id})")

    print("\n4. Listing all airlines again:")
    for al_obj in manager.get_all_airlines():
        print(f"  ID: {al_obj.airline_id}, Name: {al_obj.company_name}, "
              f"Type: {al_obj.record_type}")

    print("\n5. Deleting an airline...")
    DELETED_AIRLINE_FLAG = False
    if py_air:
        DELETED_AIRLINE_FLAG = manager.delete_airline(py_air.airline_id)
        print(f"PythonAir (ID: {py_air.airline_id}) deleted: {DELETED_AIRLINE_FLAG}")

    print("\nFinal list of airlines:")
    for al_obj_final in manager.get_all_airlines():
        print(f"  {al_obj_final}") # Uses AirlineRecord's __str__

    print(f"\nTotal airlines at end: {len(manager.get_all_airlines())}")
    print(f"Check the file: {manager.airlines_file_path}")
