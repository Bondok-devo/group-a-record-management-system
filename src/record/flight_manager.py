# src/record/flight_manager.py
"""
Manages flight records, including loading, saving, and CRUD operations.
This module provides the FlightManager class to handle all aspects of
flight data persistence and manipulation, including validation of
foreign keys (Client_ID, Airline_ID).
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional, Any

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

    def __init__(
        self,
        flights_file_path: str,
        client_manager: ClientManager,
        airline_manager: AirlineManager
    ):
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
            with open(self.flights_file_path, 'r', encoding='utf-8') as file_handle:
                for line_number, raw_line in enumerate(file_handle, start=1):
                    stripped = raw_line.strip()
                    if not stripped:
                        continue
                    try:
                        record = json.loads(stripped)
                        if record.get('record_type') == 'Flight':
                            flight = FlightRecord.from_dict(record)
                            self._flights.append(flight)
                    except (json.JSONDecodeError, ValueError, TypeError) as load_err:
                        print(f"Warning: Error on line {line_number}: {load_err}. Skipping.")
        except IOError as io_err:
            print(f"Warning: Could not read '{self.flights_file_path}': {io_err}. Starting empty.")
        except Exception as err:
            print(f"Unexpected load error: {err}")

    def _save_flights(self) -> bool:
        """
        Saves the current list of flights to the JSONL file.
        Returns True if successful, False otherwise.

        """
        try:
            directory = os.path.dirname(self.flights_file_path)
            if directory:
                os.makedirs(directory, exist_ok=True)
            with open(self.flights_file_path, 'w', encoding='utf-8') as file_handle:
                for flight in self._flights:
                    json.dump(flight.to_dict(), file_handle)
                    file_handle.write("\n")
            return True
        except Exception as save_err:
            print(f"Error saving flights: {save_err}")
            return False

    def _find_flight_index(self, criteria: Dict[str, Any]) -> Optional[int]:
        """
        Internal helper to locate the index of a flight by its identifying fields.
        Uses a dictionary of key/value pairs as match criteria.
        Returns the index or None if not found.

        """
        for index, flight in enumerate(self._flights):
            data = flight.to_dict()
            match = True
            for key, value in criteria.items():
                if data.get(key) != value:
                    match = False
                    break
            if match:
                return index
        return None

    def add_flight(self, flight_data: Dict[str, Any]) -> Optional[FlightRecord]:
        """
        Adds a new flight after validating client and airline IDs.
        """
        required_keys = ['record_type', 'Client_ID', 'Airline_ID', 'Date', 'Start City', 'End City']
        for key in required_keys:
            if key not in flight_data:
                print(f"Error: Missing '{key}'.")
                return None

        client_id = flight_data['Client_ID']
        airline_id = flight_data['Airline_ID']
        if not isinstance(client_id, int) or not self.client_manager.get_client_by_id(client_id):
            print(f"Error: Invalid Client_ID {client_id}.")
            return None
        if not isinstance(airline_id, int) or not self.airline_manager.get_airline_by_id(airline_id):
            print(f"Error: Invalid Airline_ID {airline_id}.")
            return None

        try:
            new_flight = FlightRecord.from_dict(flight_data)
            self._flights.append(new_flight)
            if self._save_flights():
                return new_flight
            # rollback on save failure
            self._flights.pop()
            print("Error: Save failed, rollback.")
        except Exception as err:
            print(f"Error adding flight: {err}")
        return None

    def get_all_flights(self) -> List[FlightRecord]:
        """Returns a copy of all flights."""
        return list(self._flights)

    def find_flights(self, criteria: Dict[str, Any]) -> List[FlightRecord]:
        """
        Finds and returns flights matching the given criteria.
        Empty criteria returns all flights.
        """
        if not criteria:
            return self.get_all_flights()
        results: List[FlightRecord] = []
        for flight in self._flights:
            match = True
            data = flight.to_dict()
            for key, value in criteria.items():
                if data.get(key) != value:
                    match = False
                    break
            if match:
                results.append(flight)
        return results

    def update_flight(self, identifier: Dict[str, Any], changes: Dict[str, Any]) -> Optional[FlightRecord]:
        """
        Updates fields of an existing flight identified by `identifier`.
        Returns the updated FlightRecord or None.
        """
        flight_index = self._find_flight_index(identifier)
        if flight_index is None:
            print(f"Info: No flight found for {identifier}.")
            return None

        original_data = self._flights[flight_index].to_dict()
        updated_data = original_data.copy()
        has_changes = False
        for key, value in changes.items():
            if key not in original_data or original_data[key] != value:
                updated_data[key] = value
                has_changes = True
        if not has_changes:
            return self._flights[flight_index]

        try:
            updated_record = FlightRecord.from_dict(updated_data)
            self._flights[flight_index] = updated_record
            if self._save_flights():
                return updated_record
            # rollback on save failure
            self._flights[flight_index] = FlightRecord.from_dict(original_data)
            print("Error: Save failed, rollback update.")
        except Exception as err:
            print(f"Error updating flight: {err}")
        return None

    def delete_flight(self, identifier: Dict[str, Any]) -> bool:
        """
        Deletes a flight record based on its identifying details.
        Args:
            identifying_details: Dictionary with current key details to find the flight.
        Returns:
            True if deletion was successful, False otherwise.
        """
        index = self._find_flight_index(identifier)
        if index is None:
            print(f"Info: No flight found for {identifier}.")
            return False

        removed = self._flights.pop(index)
        if self._save_flights():
            return True
        # rollback on save failure
        self._flights.insert(index, removed)
        print("Error: Delete failed, rollback.")
        return False


# This section is for direct testing of the FlightManager.
def run_flight_manager_demo() -> None:
    """
    Demo and manual tests for FlightManager.
    """
    print("--- FlightManager Direct Test ---")
    current_path = os.path.abspath(__file__)
    record_dir = os.path.dirname(current_path)
    src_dir = os.path.dirname(record_dir)
    project_root = os.path.dirname(src_dir)

 # Setup paths for temporary test data for all managers
    TEMP_ROOT = "temp_test_output"
    CLIENT_TEST_SUBDIR = "client_manager_test_data_for_flight"
    AIRLINE_TEST_SUBDIR = "airline_manager_test_data_for_flight"
    FLIGHT_TEST_SUBDIR = "flight_manager_test_data"

    client_dir = os.path.join(project_root, TEMP_ROOT, CLIENT_TEST_SUBDIR)
    airline_dir = os.path.join(project_root, TEMP_ROOT, AIRLINE_TEST_SUBDIR)
    flight_dir = os.path.join(project_root, TEMP_ROOT, FLIGHT_TEST_SUBDIR)
    os.makedirs(client_dir, exist_ok=True)
    os.makedirs(airline_dir, exist_ok=True)
    os.makedirs(flight_dir, exist_ok=True)

    client_file = os.path.join(client_dir, "client_record.jsonl")
    airline_file = os.path.join(airline_dir, "airline_record.jsonl")
    flight_file = os.path.join(flight_dir, "flight_record.jsonl")

    client_mgr = ClientManager(client_file)
    airline_mgr = AirlineManager(airline_file)
    flight_mgr = FlightManager(flight_file, client_mgr, airline_mgr)

    print(f"Initial flights: {len(flight_mgr.get_all_flights())}")

    test_client1 = client_mgr.add_client({
        "name":"Demo Client","address_line_1":"123 Main St","city":"Testville","state":"ST","zip_code":"00000","country":"Testland","phone_number":"123456"
    })
    test_airline1 = airline_mgr.add_airline({"record_type":"Airline","company_name":"DemoAir"})
    if not (test_client1 and test_airline1):
        print("Setup failed")
        return

    print("Adding flights...")
    now = datetime.now()
    test_flight1 = flight_mgr.add_flight({
        "record_type":"Flight","Client_ID":test_client1.client_id,"Airline_ID":test_airline1.airline_id,
        "Date":now.isoformat(),"Start City":"CityA","End City":"CityB"
    })
    if test_flight1:
        print(f"Added: {test_flight1.start_city} to {test_flight1.end_city}")

    print("Final flights:")
    for rec in flight_mgr.get_all_flights():
        print(f"  {rec}")

    print("--- End Test ---")

if __name__ == "__main__":
    run_flight_manager_demo()
