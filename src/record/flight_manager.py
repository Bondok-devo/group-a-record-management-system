# src/record/flight_manager.py
"""
Manages flight records, including loading, saving, and CRUD operations.
This module provides the FlightManager class to handle all aspects of
flight data persistence and manipulation, including validation of
foreign keys (Client_ID, Airline_ID).
"""

import json
import os
import sys # Added for sys.exit in test block
from datetime import datetime
from typing import List, Dict, Optional, Any

# flight_record.py (with FlightRecord class) is in the same package.
# An empty __init__.py in 'src/record/' makes 'record' a package.
from .flight_record import FlightRecord
from .client_manager import ClientManager
from .airline_manager import AirlineManager


class FlightManager:
    """
    Handles all operations related to flight records.

    This class loads flight data from a JSONL file, allows for
    Create, Read, Update, and Delete (CRUD) operations, and saves
    changes back to the file. It also validates the existence of
    Client and Airline IDs when adding or updating flights.
    """

    def __init__(self,
                 flights_file_path: str,
                 client_manager: ClientManager,
                 airline_manager: AirlineManager):
        """
        Initializes the FlightManager.

        Loads existing flight data from the specified file path and
        stores references to Client and Airline managers for validation.

        Args:
            flights_file_path (str): The full path to the flight data file.
            client_manager (ClientManager): An instance of ClientManager.
            airline_manager (AirlineManager): An instance of AirlineManager.
        """
        if not flights_file_path:
            raise ValueError("FlightManager requires a valid flights_file_path.")
        if not isinstance(client_manager, ClientManager):
            raise TypeError("FlightManager requires a valid ClientManager instance.")
        if not isinstance(airline_manager, AirlineManager):
            raise TypeError("FlightManager requires a valid AirlineManager instance.")

        self.flights_file_path = flights_file_path
        self.client_manager = client_manager
        self.airline_manager = airline_manager
        self._flights: List[FlightRecord] = []
        self._load_flights()


    def _load_flights(self) -> None:
        """
        Loads flight records from the JSONL file into memory.

        Reads each line, expecting a JSON object representing a flight.
        Updates the internal list of flights.
        """
        self._flights = []
        if not os.path.exists(self.flights_file_path):
            return

        try:
            with open(self.flights_file_path, 'r', encoding='utf-8') as file:
                for line_number, line in enumerate(file, 1):
                    line_content = line.strip()
                    if not line_content:
                        continue

                    try:
                        data = json.loads(line_content)
                        if data.get("record_type") == "Flight":
                            flight = FlightRecord.from_dict(data)
                            self._flights.append(flight)
                    except json.JSONDecodeError:
                        print(f"Warning: Invalid JSON on line {line_number} in "
                              f"'{self.flights_file_path}'. Skipping.")
                    except ValueError as e:
                        print(f"Warning: Invalid data for flight record on line {line_number} "
                              f"in '{self.flights_file_path}': {e}. Skipping.")
                    except TypeError as e:
                        print(f"Warning: Type error for flight record on line {line_number} "
                              f"in '{self.flights_file_path}': {e}. Skipping.")
        except IOError as e:
            print(f"Warning: Could not read '{self.flights_file_path}': {e}. "
                  "Starting with no flights.")
        except Exception as e:
            # This broad exception is a last resort to prevent crashing during load.
            print(f"An unexpected error occurred loading flights: {e}")

    def _save_flights(self) -> bool:
        """
        Saves the current list of flights to the JSONL file.

        Returns:
            True if saving was successful, False otherwise.
        """
        try:
            file_directory = os.path.dirname(self.flights_file_path)
            if file_directory:
                os.makedirs(file_directory, exist_ok=True)

            with open(self.flights_file_path, 'w', encoding='utf-8') as file:
                for flight_item in self._flights:
                    flight_dict = flight_item.to_dict()
                    json.dump(flight_dict, file)
                    file.write('\n')
            return True
        except IOError as e:
            print(f"Error: Could not write to '{self.flights_file_path}': {e}. "
                  "Changes may not be saved.")
            return False
        except Exception as e:
            # This broad exception is a last resort for saving errors.
            print(f"An unexpected error occurred while saving flights: {e}")
            return False

    def add_flight(self, flight_data: Dict[str, Any]) -> Optional[FlightRecord]:
        """
        Adds a new flight to the system after validating Client and Airline IDs.

        Args:
            flight_data: Dictionary of flight information. Must include "Client_ID"
                         and "Airline_ID" which will be validated.

        Returns:
            The created FlightRecord object if successful, else None.
        """
        required_keys = ["record_type", "Client_ID", "Airline_ID", "Date",
                           "Start City", "End City"]
        for key in required_keys:
            if key not in flight_data:
                print(f"Error: Could not add flight. Missing data key: '{key}'.")
                return None

        if flight_data.get("record_type") != "Flight":
            print(f"Warning: Adding record with type '{flight_data.get('record_type')}' "
                  "via FlightManager. Expected 'Flight'.")

        # Validate foreign keys
        client_id = flight_data.get("Client_ID")
        airline_id = flight_data.get("Airline_ID")

        # Check if client_id is valid (integer and exists)
        if not isinstance(client_id, int) or \
           not self.client_manager.get_client_by_id(client_id):
            print(f"Error: Invalid or non-existent Client_ID: {client_id}. "
                  "Flight not added.")
            return None

        # Check if airline_id is valid (integer and exists)
        if not isinstance(airline_id, int) or \
           not self.airline_manager.get_airline_by_id(airline_id):
            print(f"Error: Invalid or non-existent Airline_ID: {airline_id}. "
                  "Flight not added.")
            return None

        try:
            new_flight = FlightRecord.from_dict(flight_data)
            self._flights.append(new_flight)
            if self._save_flights():
                return new_flight
            self._flights.pop()
            print("Error: Failed to save after adding flight. Flight not added.")
            return None
        except ValueError as e:
            print(f"Error: Could not add flight. Invalid data: {e}")
            return None
        except Exception as e:
            # This broad exception is a last resort for add operation errors.
            print(f"An unexpected error occurred while adding flight: {e}")
            return None

    def get_all_flights(self) -> List[FlightRecord]:
        """Returns a list of all flight records."""
        return self._flights[:]

    def find_flights(self, criteria: Dict[str, Any]) -> List[FlightRecord]:
        """
        Finds flights matching the given criteria.
        Args:
            criteria: A dictionary of attributes and values to match.
        Returns:
            A list of matching FlightRecord objects.
        """
        results: List[FlightRecord] = []
        if not criteria:
            return self.get_all_flights()

        for flight in self._flights:
            match = True
            flight_dict_for_search = flight.to_dict()
            for key, value_to_match in criteria.items():
                flight_val = None
                if hasattr(flight, key): # Check internal attribute name first
                    flight_val = getattr(flight, key)
                elif key in flight_dict_for_search: # Check external dict key
                    flight_val = flight_dict_for_search[key]
                else:
                    match = False
                    break # Key not found in flight record

                # Handle date comparison carefully
                is_date_key = key.lower() == "date"
                is_dt_val = isinstance(flight_val, datetime)
                is_str_criteria = isinstance(value_to_match, str)

                if is_date_key and is_dt_val and is_str_criteria:
                    try:
                        # Check if criteria is likely full ISO string or just date part
                        if len(value_to_match) > 10:
                            criteria_dt = datetime.fromisoformat(value_to_match)
                            if flight_val != criteria_dt:
                                match = False
                                break
                        else:
                            criteria_date_only = datetime.fromisoformat(value_to_match).date()
                            if flight_val.date() != criteria_date_only:
                                match = False
                                break
                    except ValueError: # Invalid date format in criteria
                        match = False
                        break
                elif flight_val != value_to_match: # General comparison for other types
                    match = False
                    break
            if match:
                results.append(flight)
        return results

    def _find_flight_index(self, identifying_details: Dict[str, Any]) -> Optional[int]:
        """
        Internal helper to find the index of a flight based on its details.
        Date in identifying_details should be an ISO string.
        """
        for i, flight in enumerate(self._flights):
            flight_dict = flight.to_dict()
            match = True
            id_keys = ["Client_ID", "Airline_ID", "Date", "Start City", "End City"]
            for key in id_keys:
                # Check if key is present and values match
                if key not in identifying_details or \
                   identifying_details[key] != flight_dict.get(key):
                    match = False
                    break
            if match:
                return i
        return None


    def update_flight(self, identifying_details: Dict[str, Any],
                      update_data: Dict[str, Any]) -> Optional[FlightRecord]:
        """
        Updates an existing flight record. Validates new Client/Airline IDs if changed.
        Args:
            identifying_details: Dictionary with current key details to find the flight.
            update_data: Dictionary with fields to update.
        Returns:
            The updated FlightRecord object if successful, else None.
        """
        flight_index = self._find_flight_index(identifying_details)
        if flight_index is None:
            print(f"Info: No flight found matching details: {identifying_details}")
            return None

        flight_to_update = self._flights[flight_index]
        current_flight_dict = flight_to_update.to_dict()
        original_flight_dict_backup = current_flight_dict.copy()
        new_data_for_record = current_flight_dict.copy()
        changed_fields = False

        for key, value in update_data.items():
            if key in new_data_for_record:
                if new_data_for_record[key] != value:
                    new_data_for_record[key] = value
                    changed_fields = True
            else:
                new_data_for_record[key] = value
                changed_fields = True

        if not changed_fields:
            return flight_to_update

        # Validate foreign keys ONLY if they are actually being changed
        if "Client_ID" in update_data and \
           update_data["Client_ID"] != original_flight_dict_backup["Client_ID"]:
            new_client_id = new_data_for_record.get("Client_ID")
            if not isinstance(new_client_id, int) or \
               not self.client_manager.get_client_by_id(new_client_id):
                print(f"Error: Invalid or non-existent new Client_ID: {new_client_id} "
                      "during flight update.")
                return None
        if "Airline_ID" in update_data and \
           update_data["Airline_ID"] != original_flight_dict_backup["Airline_ID"]:
            new_airline_id = new_data_for_record.get("Airline_ID")
            if not isinstance(new_airline_id, int) or \
               not self.airline_manager.get_airline_by_id(new_airline_id):
                print(f"Error: Invalid or non-existent new Airline_ID: {new_airline_id} "
                      "during flight update.")
                return None

        try:
            updated_flight_obj = FlightRecord.from_dict(new_data_for_record)
            self._flights[flight_index] = updated_flight_obj
            if self._save_flights():
                return updated_flight_obj
            self._flights[flight_index] = FlightRecord.from_dict(original_flight_dict_backup)
            print("Error: Failed to save updates for flight. Changes rolled back.")
            return None
        except ValueError as e:
            print(f"Error: Could not update flight. Invalid data after update: {e}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred while updating flight: {e}")
            return None

    def delete_flight(self, identifying_details: Dict[str, Any]) -> bool:
        """
        Deletes a flight record based on its identifying details.
        Args:
            identifying_details: Dictionary with current key details to find the flight.
        Returns:
            True if deletion was successful, False otherwise.
        """
        flight_index = self._find_flight_index(identifying_details)
        if flight_index is None:
            print(f"Info: No flight found matching details: {identifying_details}. "
                  "Nothing to delete.")
            return False

        flight_to_delete = self._flights.pop(flight_index)
        if self._save_flights():
            return True
        self._flights.insert(flight_index, flight_to_delete)
        print("Error: Failed to save after deleting flight. Deletion rolled back.")
        return False


# This section is for direct testing of the FlightManager.
if __name__ == "__main__":
    print("--- FlightManager Direct Test ---")

    current_script_path = os.path.abspath(__file__)
    record_dir = os.path.dirname(current_script_path)
    src_dir = os.path.dirname(record_dir)
    project_root = os.path.dirname(src_dir)

    TEMP_TEST_OUTPUT_ROOT_DIR_NAME = "temp_test_output"

    # Setup paths for temporary test data for all managers
    CLIENT_TEST_DATA_SUBDIR = "client_manager_test_data_for_flight"
    AIRLINE_TEST_DATA_SUBDIR = "airline_manager_test_data_for_flight"
    FLIGHT_TEST_DATA_SUBDIR = "flight_manager_test_data"

    client_test_data_folder = os.path.join(project_root, TEMP_TEST_OUTPUT_ROOT_DIR_NAME,
                                           CLIENT_TEST_DATA_SUBDIR)
    client_test_file = os.path.join(client_test_data_folder, "client_record.jsonl")

    airline_test_data_folder = os.path.join(project_root, TEMP_TEST_OUTPUT_ROOT_DIR_NAME,
                                            AIRLINE_TEST_DATA_SUBDIR)
    airline_test_file = os.path.join(airline_test_data_folder, "airline_record.jsonl")

    flight_test_data_folder = os.path.join(project_root, TEMP_TEST_OUTPUT_ROOT_DIR_NAME,
                                           FLIGHT_TEST_DATA_SUBDIR)
    flight_test_file = os.path.join(flight_test_data_folder, "flight_record.jsonl")

    for path in [client_test_data_folder, airline_test_data_folder, flight_test_data_folder]:
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
            print(f"Created test data directory: {path}")

    # Initialize dependent managers for testing FlightManager
    test_client_manager = ClientManager(clients_file_path=client_test_file)
    test_airline_manager = AirlineManager(airlines_file_path=airline_test_file)

    # Clear previous test files for client and airline managers
    if os.path.exists(client_test_file):
        os.remove(client_test_file)
    if os.path.exists(airline_test_file):
        os.remove(airline_test_file)
    test_client_manager = ClientManager(clients_file_path=client_test_file) # Re-instantiate
    test_airline_manager = AirlineManager(airlines_file_path=airline_test_file) # Re-instantiate

    print("Test block assumes 'from .flight_record import FlightRecord' is working.")
    # Initialize FlightManager with test instances of other managers
    manager = FlightManager(
        flights_file_path=flight_test_file,
        client_manager=test_client_manager,
        airline_manager=test_airline_manager
    )
    print(f"Flight test data file will be: {manager.flights_file_path}")

    if os.path.exists(manager.flights_file_path):
        os.remove(manager.flights_file_path)
        print(f"Cleared old flight test file: {manager.flights_file_path}")
    # Re-instantiate FlightManager to load from potentially empty file
    manager = FlightManager(
        flights_file_path=flight_test_file,
        client_manager=test_client_manager,
        airline_manager=test_airline_manager
    )

    print(f"\nInitial flights loaded: {len(manager.get_all_flights())}")

    # Add some test clients and airlines for validation
    print("\nSetting up test clients and airlines...")
    test_client1 = test_client_manager.add_client({
        "name": "Test Client Alpha", "address_line_1": "1 Test St", "city": "Testville",
        "state": "TS", "zip_code": "10000", "country": "Testland", "phone_number": "111"
    })
    test_airline1 = test_airline_manager.add_airline({
        "record_type": "Airline", "company_name": "TestAir One"
    })
    test_client2 = test_client_manager.add_client({
        "name": "Test Client Beta", "address_line_1": "2 Test St", "city": "Testville",
        "state": "TS", "zip_code": "10001", "country": "Testland", "phone_number": "222"
    })
    test_airline2 = test_airline_manager.add_airline({
        "record_type": "Airline", "company_name": "TestAir Two"
    })

    if not (test_client1 and test_airline1 and test_client2 and test_airline2):
        print("CRITICAL: Could not set up test clients/airlines. Aborting flight tests.")
        sys.exit(1) # Exit if setup fails

    print("Test clients and airlines set up.")

    print("\n1. Adding new flights...")
    now = datetime.now()
    flight1_details = {
        "record_type": "Flight", "Client_ID": test_client1.client_id,
        "Airline_ID": test_airline1.airline_id,
        "Date": datetime(now.year, now.month, now.day, 10, 0).isoformat(),
        "Start City": "London", "End City": "Paris"
    }
    flight2_details = {
        "record_type": "Flight", "Client_ID": test_client2.client_id,
        "Airline_ID": test_airline2.airline_id,
        "Date": datetime(now.year, now.month, now.day, 15, 30).isoformat(),
        "Start City": "New York", "End City": "London"
    }
    # Flight with non-existent Client_ID (should fail)
    flight_bad_client_details = {
        "record_type": "Flight", "Client_ID": 9999, # Assuming 9999 doesn't exist
        "Airline_ID": test_airline1.airline_id,
        "Date": datetime(now.year, now.month, now.day, 11, 0).isoformat(),
        "Start City": "Fakeville", "End City": "Nowhere"
    }

    added_flight1 = manager.add_flight(flight1_details)
    added_flight2 = manager.add_flight(flight2_details)
    added_flight_bad = manager.add_flight(flight_bad_client_details) # Should fail

    if added_flight1:
        print(f"Added: Flight for Client {added_flight1.client_id} "
              f"from {added_flight1.start_city}")
    if added_flight2:
        print(f"Added: Flight for Client {added_flight2.client_id} "
              f"from {added_flight2.start_city}")
    if not added_flight_bad:
        print("Correctly failed to add flight with non-existent Client_ID.")

    print(f"\nTotal flights now: {len(manager.get_all_flights())}")

    print(f"\n2. Finding flights for Client ID {test_client1.client_id}...")
    client_1_flights = manager.find_flights({"Client_ID": test_client1.client_id})
    print(f"Found {len(client_1_flights)} flights for Client ID {test_client1.client_id}:")
    for f_item in client_1_flights:
        print(f"  {f_item.start_city} to {f_item.end_city} on "
              f"{f_item.flight_date.strftime('%Y-%m-%d')}")

    print("\n3. Updating a flight...")
    if added_flight1:
        identifying_details_for_flight1 = added_flight1.to_dict()
        update_payload = {"End City": "Amsterdam", "Start City": "London Heathrow"}

        updated_flight = manager.update_flight(
            identifying_details_for_flight1, update_payload
            )
        if updated_flight:
            print(f"Updated Flight: Client {updated_flight.client_id}, "
                  f"{updated_flight.start_city} to {updated_flight.end_city}")
        else:
            print(f"Failed to update flight for Client {added_flight1.client_id}")

    print("\n4. Listing all flights again:")
    for f_obj_loop in manager.get_all_flights():
        print(f"  Client: {f_obj_loop.client_id}, Airline: {f_obj_loop.airline_id}, "
              f"{f_obj_loop.start_city} to {f_obj_loop.end_city} on "
              f"{f_obj_loop.flight_date.isoformat()}")

    print("\n5. Deleting a flight...")
    DELETED_FLAG = False
    if added_flight2:
        identifying_details_for_flight2 = added_flight2.to_dict()
        DELETED_FLAG = manager.delete_flight(identifying_details_for_flight2)
        print(f"Flight for Client {added_flight2.client_id} (NY to London) "
              f"deleted: {DELETED_FLAG}")

    print("\nFinal list of flights:")
    for f_obj_final_loop in manager.get_all_flights():
        print(f"  {f_obj_final_loop}")

    print(f"\nTotal flights at end: {len(manager.get_all_flights())}")
    # Corrected: Use string concatenation if no variables are interpolated
    print("Check the file: " + manager.flights_file_path)

    # Clean up test data files for all managers used in this test
    if os.path.exists(client_test_file):
        os.remove(client_test_file)
    if os.path.exists(airline_test_file):
        os.remove(airline_test_file)
    print("Cleaned up temporary client and airline data files for flight manager test.")
