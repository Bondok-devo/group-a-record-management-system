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
        self._next_id: int = 1
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
            return

        highest_id = 0
        try:
            with open(self.airlines_file_path, 'r', encoding='utf-8') as f:
                for idx, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        if data.get('record_type') == 'Airline':
                            airline = AirlineRecord.from_dict(data)
                            self._airlines.append(airline)
                            if airline.airline_id and airline.airline_id > highest_id:
                                highest_id = airline.airline_id
                    except (json.JSONDecodeError, ValueError, TypeError) as e:
                        print(f"Warning: Error on line {idx} in '{self.airlines_file_path}': {e}. Skipping.")
        except IOError as e:
            print(f"Warning: Cannot read '{self.airlines_file_path}': {e}. Starting empty.")
        except Exception as e:
            print(f"Unexpected error loading airlines: {e}")

        self._next_id = highest_id + 1

    def _save_airlines(self) -> bool:
        """
        Saves the current list of airlines to the JSONL file.

        Each airline is written as a JSON object on a new line, overwriting
        the existing file content. Ensures the directory for the file exists.

        Returns:
            True if saving was successful, False otherwise.
        """
        try:
            file_directory = os.path.dirname(self.airlines_file_path)
            if file_directory:
                os.makedirs(file_directory, exist_ok=True)
            with open(self.airlines_file_path, 'w', encoding='utf-8') as file:
                for airline_record in self._airlines:
                    json.dump(airline_record.to_dict(), file)
                    file.write("\n")
            return True
        except Exception as e:
            print(f"Error saving airlines: {e}")
            return False

    def _generate_id(self) -> int:
        """ Generates a new, unique ID for an airline."""
        new_id = self._next_id
        self._next_id += 1
        return new_id

    def add_airline(self, data: Dict[str, Any]) -> Optional[AirlineRecord]:
        """
        Adds a new airline to the system.
        
        A unique ID is genrated and 'record_type' is set to 'Airline'
         
        Args:
           airline_data: Dictiomnaru of airline information.
            
        Returns: 
           The created AirlineRecord object is successful, else None.
        """
        data_copy = data.copy()
        data_copy['airline_id'] = self._generate_id()
        if 'record_type' not in data_copy:
            print("Error: 'record_type' required.")
            self._next_id -= 1
            return None
        try:
            new_airline_record = AirlineRecord.from_dict(data_copy)
            self._airlines.append(new_airline_record)
            if self._save_airlines():
                return new_airline_record
            self._airlines.pop()
            self._next_id -= 1
            print("Error: save failed, rollback.")
        except Exception as e:
            print(f"Error adding airline: {e}")
            self._next_id -= 1
        return None

    def get_airline_by_id(self, airline_id: int) -> Optional[AirlineRecord]:
        """
        Retrieves an airline by their unique ID.

        Args:
            airline_id: The integer ID of the airline.

        Returns:
            The AirlineRecord object if found, otherwise None.
        """       
        if not isinstance(airline_id, int):
            return None
        for airline_record in self._airlines:
            if airline_record.airline_id == airline_id:
                return airline_record
        return None
        
    def get_all_airlines(self) -> List[AirlineRecord]:
        """
        Returns a list of all airline records.

        Returns:
            A list of AirlineRecord objects (a copy of the internal list).
        """
        return list(self._airlines)

    def update_airline(self, airline_id: int, updates: Dict[str, Any]) -> Optional[AirlineRecord]:
        record_index = next((i for i, airline_record in enumerate(self._airlines) if airline_record.airline_id == airline_id), None)
        if record_index is None:
            print(f"Info: No airline {airline_id} found.")
            return None
        original_data = self._airlines[record_index].to_dict()
        new_data = original_data.copy()
        changed = False
        for key, value in updates.items():
            if key == 'airline_id': continue
            if new_data[key] != value:
                new_data[key] = value
                changed = True

        if not changed:
            return self._airlines[record_index]
        try:
            updated_record = AirlineRecord.from_dict(new_data)
            self._airlines[record_index] = updated_record
            if self._save_airlines():
                return updated_record
            
            self._airlines[record_index] = AirlineRecord.from_dict(original_data)
            print("Error: save failed, rollback update.")
        except Exception as e:
            print(f"Error updating airline: {e}")
        return None

    def delete_airline(self, airline_id: int) -> bool:
        """
        Removes an airline from the system.
        
        Args:
          airline_id: the ID of the airline to delete.
          
        Returns:
          True if deletion was successful, False otherwise.
        """
        record_index = next((i for i, airline_record in enumerate(self._airlines) if airline_record.airline_id == airline_id), None)
        if record_index is None:
            return False
        
        removed_record = self._airlines.pop(record_index)
        if self._save_airlines():
            return True
        
        self._airlines.insert(record_index, removed_record)
        print("Error: delete failed, rollback.")
        return False

# This section is for direct testing of the AirlineManager.
def run_airline_manager_demo() -> None:
    """
    Demo and manual tests for AirlineManager. Creates a temporary test file,
    runs CRUD operations, and prints outcomes.
    """
    print("--- AirlineManager Direct Test ---")
   # Determine the project root directory (GROUP-A) to correctly place temp_test_output
    current_path = os.path.abspath(__file__)
    # Expected structure: .../GROUP-A/src/record/airline_manager.py
    # record_dir is .../GROUP-A/src/record/
    record_dir = os.path.dirname(current_path)
    # src_dir is .../GROUP-A/src/
    src_dir = os.path.dirname(record_dir)
    # project_root is .../GROUP-A/
    project_root = os.path.dirname(src_dir)


    TEST_SUBDIR = "airline_manager_test_data"
    TEMP_ROOT = "temp_test_output"

    test_folder = os.path.join(src_dir, TEMP_ROOT, TEST_SUBDIR)
    file_name = "airline_record.jsonl"
    test_file_path = os.path.join(test_folder, file_name)

    os.makedirs(test_folder, exist_ok=True)
    print(f"Test directory: {test_folder}")

    manager = AirlineManager(test_file_path)
    print(f"Using file: {manager.airlines_file_path}")

    if os.path.exists(test_file_path):
        os.remove(test_file_path)
        print("Cleared old test file.")
    manager = AirlineManager(test_file_path)

    print(f"Initial count: {len(manager.get_all_airlines())}")

    print("\nAdding Airlines...")
    for company_name in ["PythonAir", "TkinterFly"]:
        record = {"record_type": "Airline", "company_name": company_name}
        result = manager.add_airline(record)
        if result:
            print(f"Added: {result.company_name} (ID {result.airline_id})")

    print(f"\nCount after add: {len(manager.get_all_airlines())}")

    print("\nListing Airlines:")
    for airline_record in manager.get_all_airlines():
        print(f"  {airline_record}")

    print("\nUpdating first airline...")
    all_records = manager.get_all_airlines()
    if all_records:
        first_record = all_records[0]
        updated = manager.update_airline(first_record.airline_id, {"company_name": first_record.company_name + " Updated"})
        if updated:
            print(f"Updated: {updated}")

    print("\nFinal list:")
    for airline_record in manager.get_all_airlines():
        print(f"  {airline_record}")

    print(f"\nTotal at end: {len(manager.get_all_airlines())}")
    print(f"Check file at: {manager.airlines_file_path}")


if __name__ == "__main__":
    run_airline_manager_demo()
