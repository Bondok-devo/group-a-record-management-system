# pylint: disable=redefined-outer-name
"""
Unit tests for the travel agency's record management system,
covering backend logic and some UI event handlers.
"""
import sys
import os
from unittest import mock
import datetime

import pytest # type: ignore
# import tkinter as tk # Not strictly needed for most mocks if using string constants

# Ensuring the 'src' directory is in the Python path for our imports.
# This helps when running tests directly from this file's location.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# pylint: disable=wrong-import-position
# Importing our application's modules.
from src.record.client_manager import ClientManager
from src.record.airline_manager import AirlineManager
from src.record.flight_manager import FlightManager
from src.record.client_record import ClientRecord
from src.record.airline_record import AirlineRecord
from src.record.flight_record import FlightRecord
from src.gui import events as ui_events # Our UI event handling functions
# pylint: enable=wrong-import-position


# --- Backend Logic & Data Management Tests ---

@pytest.fixture
def temp_client_manager_fixture(tmp_path):
    """Provides a ClientManager instance using a temporary file for each test."""
    test_file = tmp_path / "test_clients.jsonl"
    mgr = ClientManager(clients_file_path=str(test_file))
    return mgr

@pytest.fixture
def sample_client_data_fixture():
    """Provides a sample dictionary of client data for tests."""
    return {
        "client_id": 0, # Will be set by the manager
        "name": "Walter",
        "address_line_1": "123 Main St",
        "address_line_2": "",
        "address_line_3": "",
        "city": "New York",
        "state": "StateX",
        "zip_code": "12345",
        "country": "CountryY",
        "phone_number": "1234567890",
        "record_type": "Client"
    }

def test_create_client_record(temp_client_manager_fixture, sample_client_data_fixture):
    """Can we add a new client successfully?"""
    mgr = temp_client_manager_fixture
    client_data = sample_client_data_fixture.copy()
    if "client_id" in client_data:
        del client_data["client_id"]
    client = mgr.add_client(client_data)
    assert client is not None, "Client object should be returned after adding."
    assert client.name == "Walter", "Client name should match input."
    assert len(mgr.get_all_clients()) == 1, "Client list should have one client."

def test_read_client_record(temp_client_manager_fixture, sample_client_data_fixture):
    """Can we retrieve a client by their ID?"""
    mgr = temp_client_manager_fixture
    client_data = sample_client_data_fixture.copy()
    if "client_id" in client_data:
        del client_data["client_id"]
    client = mgr.add_client(client_data)
    assert client is not None
    result = mgr.get_client_by_id(client.client_id)
    assert result is not None, "Client should be found by ID."
    assert result.name == "Walter", "Retrieved client's name should match."

def test_update_client_record(temp_client_manager_fixture, sample_client_data_fixture):
    """Can we update an existing client's information?"""
    mgr = temp_client_manager_fixture
    client_data = sample_client_data_fixture.copy()
    if "client_id" in client_data:
        del client_data["client_id"]
    client = mgr.add_client(client_data)
    assert client is not None
    update_payload = {"city": "Boston"}
    updated_client = mgr.update_client(client.client_id, update_payload)
    assert updated_client is not None, "Update should return the updated client object."
    assert updated_client.city == "Boston", "Client's city should be updated."

def test_update_client_id_ignored(temp_client_manager_fixture, sample_client_data_fixture):
    """Does the update method correctly ignore attempts to change a client_id?"""
    mgr = temp_client_manager_fixture
    client_data = sample_client_data_fixture.copy()
    if "client_id" in client_data:
        del client_data["client_id"]
    client = mgr.add_client(client_data)
    assert client is not None
    original_id = client.client_id
    update_payload = {"client_id": 99999, "name": "Updated Name"} # Attempt to change ID
    updated_client = mgr.update_client(original_id, update_payload)
    assert updated_client is not None
    assert updated_client.client_id == original_id, "Client ID should remain unchanged."
    assert updated_client.name == "Updated Name", "Other fields should update."


def test_delete_client_record(temp_client_manager_fixture, sample_client_data_fixture):
    """Can we delete a client from the system?"""
    mgr = temp_client_manager_fixture
    client_data = sample_client_data_fixture.copy()
    if "client_id" in client_data:
        del client_data["client_id"]
    client = mgr.add_client(client_data)
    assert client is not None
    deleted = mgr.delete_client(client.client_id)
    assert deleted is True, "Delete operation should return True for success."
    assert not mgr.get_all_clients(), "Client list should be empty after deletion."

def test_init_with_missing_file(tmp_path):
    """Does the manager initialize correctly if the data file is missing?"""
    test_file = tmp_path / "missing.jsonl"
    mgr = ClientManager(clients_file_path=str(test_file))
    assert not mgr.get_all_clients(), "Should start with no clients if file is missing."

def test_init_with_empty_file(tmp_path):
    """How does the manager handle an existing but empty data file?"""
    test_file = tmp_path / "empty.jsonl"
    test_file.write_text("")
    mgr = ClientManager(clients_file_path=str(test_file))
    assert not mgr.get_all_clients(), "Should load no clients from an empty file."

def test_init_with_malformed_file(tmp_path):
    """Can the manager gracefully handle a data file with some bad lines?"""
    test_file = tmp_path / "malformed.jsonl"
    test_file.write_text("this is not json\n{\"bad_json\": true") # Invalid content
    mgr = ClientManager(clients_file_path=str(test_file))
    # Expecting it to skip errors and load what it can (which is nothing here).
    assert not mgr.get_all_clients(), "Should not load clients from a malformed file."

def test_init_with_incomplete_data_line(tmp_path):
    """What if a line in the file is valid JSON but missing essential client fields?"""
    test_file = tmp_path / "incomplete_data.jsonl"
    # This client is missing 'name', 'address_line_1', etc.
    test_file.write_text('{"client_id": 1, "record_type": "Client", "city": "TestCityOnly"}\n')
    mgr = ClientManager(clients_file_path=str(test_file))
    # ClientRecord.from_dict should raise an error, so this record won't be loaded.
    assert len(mgr.get_all_clients()) == 0

def test_id_uniqueness(temp_client_manager_fixture, sample_client_data_fixture):
    """Are client IDs generated by the manager unique?"""
    mgr = temp_client_manager_fixture
    sample_data = sample_client_data_fixture.copy()
    if "client_id" in sample_data:
        del sample_data["client_id"]
    ids = set()
    for i in range(10):
        data_payload = dict(sample_data)
        data_payload["name"] = f"Name{i}" # Make each record slightly different
        client = mgr.add_client(data_payload)
        assert client is not None, "Client creation failed during uniqueness test."
        assert client.client_id not in ids, "Generated client ID is not unique."
        ids.add(client.client_id)

def test_add_client_boundary_conditions(temp_client_manager_fixture, sample_client_data_fixture):
    """How does adding clients work with edge-case names (empty or very long)?"""
    mgr = temp_client_manager_fixture

    data_empty_name = sample_client_data_fixture.copy()
    if "client_id" in data_empty_name:
        del data_empty_name["client_id"]
    data_empty_name["name"] = ""
    client_empty_name = mgr.add_client(data_empty_name)
    # This depends on whether ClientRecord validation allows empty names.
    # If it does, the client should be added. If not, client_empty_name should be None.
    if client_empty_name is not None:
        assert client_empty_name.name == "", "Client with empty name should be added (if allowed)."
    else:
        print("Note: Adding client with empty name correctly returned None due to validation.")

    data_long_name = sample_client_data_fixture.copy()
    if "client_id" in data_long_name:
        del data_long_name["client_id"]
    long_name_str = "a" * 255 # A reasonably long string
    data_long_name["name"] = long_name_str
    client_long_name = mgr.add_client(data_long_name)
    assert client_long_name is not None, "Adding client with long name failed."
    assert client_long_name.name == long_name_str, "Long name was not stored correctly."


def test_add_client_save_failure_rollback(temp_client_manager_fixture, sample_client_data_fixture):
    """If saving to file fails, does `add_client` correctly roll back changes?"""
    mgr = temp_client_manager_fixture
    client_data_payload = sample_client_data_fixture.copy()
    if "client_id" in client_data_payload:
        del client_data_payload["client_id"]

    initial_clients_count = len(mgr.get_all_clients())
    initial_next_id = mgr._next_id # pylint: disable=protected-access

    # Simulate a save failure
    with mock.patch.object(mgr, '_save_clients', return_value=False) as mock_save:
        client = mgr.add_client(client_data_payload)
        assert client is None, "Client should not be added if save fails."
        mock_save.assert_called_once()

    assert len(mgr.get_all_clients()) == initial_clients_count, "Client list size should not change."
    assert mgr._next_id == initial_next_id, "_next_id should be rolled back." # pylint: disable=protected-access


def test_add_invalid_data(temp_client_manager_fixture):
    """Does `add_client` handle data missing essential fields?"""
    mgr = temp_client_manager_fixture
    # This data is missing 'name', which ClientRecord.from_dict likely requires.
    bad_data_payload = {"address_line_1": "123 Some Other St", "record_type": "Client"}
    result = mgr.add_client(bad_data_payload)
    assert result is None, "Adding client with invalid data should return None."

def test_update_nonexistent_client(temp_client_manager_fixture):
    """What happens if we try to update a client that isn't there?"""
    mgr = temp_client_manager_fixture
    result = mgr.update_client(99999, {"city": "Nowhereville"}) # 99999 is a non-existent ID
    assert result is None, "Updating a non-existent client should return None."

def test_delete_nonexistent_client(temp_client_manager_fixture):
    """What happens if we try to delete a client that isn't there?"""
    mgr = temp_client_manager_fixture
    result = mgr.delete_client(99999) # 99999 is a non-existent ID
    assert result is False, "Deleting a non-existent client should return False."

def test_search_by_city(temp_client_manager_fixture, sample_client_data_fixture):
    """Can we filter clients based on their city (illustrative test)?"""
    mgr = temp_client_manager_fixture
    client_data = sample_client_data_fixture.copy()
    if "client_id" in client_data:
        del client_data["client_id"]
    mgr.add_client(client_data) # Walter in New York
    # Note: ClientManager doesn't have a direct search method in the provided code,
    # so this test shows how one might filter the results from get_all_clients().
    results_ny = [c for c in mgr.get_all_clients() if c.city == "New York"]
    assert len(results_ny) == 1
    results_boston = [c for c in mgr.get_all_clients() if c.city == "Boston"]
    assert not results_boston, "Should be no clients in Boston yet."

def test_find_clients_non_existent_criteria_key(temp_client_manager_fixture, sample_client_data_fixture):
    """How does `find_clients` behave with a search key that isn't a client attribute?"""
    mgr = temp_client_manager_fixture
    client_data = sample_client_data_fixture.copy()
    if "client_id" in client_data:
        del client_data["client_id"]
    mgr.add_client(client_data)
    # 'favorite_color' isn't a field in ClientRecord.
    results = mgr.find_clients({"favorite_color": "Blue"})
    assert len(results) == 0, "Search with non-existent key should yield no results."

def test_serialization_deserialization(temp_client_manager_fixture, sample_client_data_fixture):
    """Can a ClientRecord be converted to a dict and back without losing data?"""
    mgr = temp_client_manager_fixture
    client_data = sample_client_data_fixture.copy()
    if "client_id" in client_data:
        del client_data["client_id"]
    client = mgr.add_client(client_data)
    assert client is not None
    client_dict = client.to_dict()
    new_client = ClientRecord.from_dict(client_dict)
    assert new_client.name == client.name, "Name mismatch after deserialization."
    assert new_client.client_id == client.client_id, "Client ID mismatch."
    assert new_client.city == client.city, "City mismatch."

def test_client_record_from_dict_missing_key(sample_client_data_fixture):
    """Does `ClientRecord.from_dict` raise an error if essential data is missing?"""
    data_missing_name = sample_client_data_fixture.copy()
    del data_missing_name["name"] # 'name' is crucial.
    # Expecting a ValueError because 'name' is required by ClientRecord.
    with pytest.raises(ValueError, match="Missing required field: 'name'"):
        ClientRecord.from_dict(data_missing_name)


@pytest.fixture
def temp_airline_manager_fixture(tmp_path):
    """Provides an AirlineManager with a temporary file."""
    test_file = tmp_path / "test_airlines.jsonl"
    mgr = AirlineManager(airlines_file_path=str(test_file))
    return mgr

@pytest.fixture
def sample_airline_data_fixture():
    """Provides sample airline data."""
    return {"airline_id":0, "company_name": "TestAir", "record_type": "Airline"}

@pytest.fixture
def temp_flight_manager_fixture(tmp_path, temp_client_manager_fixture, temp_airline_manager_fixture):
    """
    Sets up a FlightManager with temporary, dependent Client and Airline managers.
    It also pre-populates the client and airline managers with one record each.
    """
    client_mgr_instance = temp_client_manager_fixture
    airline_mgr_instance = temp_airline_manager_fixture
    flight_file = tmp_path / "test_flights.jsonl"

    client_details_payload = {
        "name": "Walter FlightTest", "address_line_1": "456 Sky Lane",
        "city": "Cloud City", "state": "Air", "zip_code": "67890", "country": "SkyNation",
        "phone_number": "0987654321", "record_type": "Client"
    }
    sample_client_obj = client_mgr_instance.add_client(client_details_payload)
    assert sample_client_obj is not None, "Setup: Failed to add sample client for flight tests."

    airline_details_payload = {"company_name": "TestAir FlightTest", "record_type": "Airline"}
    sample_airline_obj = airline_mgr_instance.add_airline(airline_details_payload)
    assert sample_airline_obj is not None, "Setup: Failed to add sample airline for flight tests."

    flight_mgr_instance = FlightManager(
        flights_file_path=str(flight_file),
        client_manager=client_mgr_instance,
        airline_manager=airline_mgr_instance
    )
    return flight_mgr_instance, sample_client_obj, sample_airline_obj


def test_airline_create_and_read(temp_airline_manager_fixture, sample_airline_data_fixture):
    """Can we add and then retrieve an airline?"""
    mgr = temp_airline_manager_fixture
    airline_payload = sample_airline_data_fixture.copy()
    if "airline_id" in airline_payload:
        del airline_payload["airline_id"]
    airline = mgr.add_airline(airline_payload)
    assert airline is not None
    assert airline.company_name == "TestAir"
    result = mgr.get_airline_by_id(airline.airline_id)
    assert result is not None
    assert result.company_name == "TestAir"

def test_airline_update_and_delete(temp_airline_manager_fixture, sample_airline_data_fixture):
    """Can we update and then delete an airline?"""
    mgr = temp_airline_manager_fixture
    airline_payload = sample_airline_data_fixture.copy()
    if "airline_id" in airline_payload:
        del airline_payload["airline_id"]
    airline = mgr.add_airline(airline_payload)
    assert airline is not None
    updated = mgr.update_airline(airline.airline_id, {"company_name": "NewName"})
    assert updated is not None
    assert updated.company_name == "NewName"
    deleted = mgr.delete_airline(airline.airline_id)
    assert deleted is True
    assert not mgr.get_all_airlines()

def test_add_airline_boundary_conditions(temp_airline_manager_fixture, sample_airline_data_fixture):
    """How does adding airlines work with empty company names?"""
    mgr = temp_airline_manager_fixture

    data_empty_name = sample_airline_data_fixture.copy()
    if "airline_id" in data_empty_name:
        del data_empty_name["airline_id"]
    data_empty_name["company_name"] = ""
    airline_empty_name = mgr.add_airline(data_empty_name)
    if airline_empty_name is not None:
        assert airline_empty_name.company_name == ""
    else:
        print("Note: Adding airline with empty company_name correctly returned None.")

def test_add_airline_save_failure_rollback(temp_airline_manager_fixture, sample_airline_data_fixture):
    """If saving fails, does `add_airline` roll back changes?"""
    mgr = temp_airline_manager_fixture
    airline_data_payload = sample_airline_data_fixture.copy()
    if "airline_id" in airline_data_payload:
        del airline_data_payload["airline_id"]

    initial_airlines_count = len(mgr.get_all_airlines())
    initial_next_id = mgr._next_id # pylint: disable=protected-access

    with mock.patch.object(mgr, '_save_airlines', return_value=False) as mock_save:
        airline = mgr.add_airline(airline_data_payload)
        assert airline is None
        mock_save.assert_called_once()

    assert len(mgr.get_all_airlines()) == initial_airlines_count
    assert mgr._next_id == initial_next_id # pylint: disable=protected-access

def test_airline_record_from_dict_missing_key(sample_airline_data_fixture):
    """Does `AirlineRecord.from_dict` handle missing essential keys?"""
    data_missing_name = sample_airline_data_fixture.copy()
    del data_missing_name["company_name"] # 'company_name' is essential.
    with pytest.raises(ValueError, match="Missing required field: 'company_name'"):
        AirlineRecord.from_dict(data_missing_name)


def test_airline_add_invalid_data(temp_airline_manager_fixture):
    """Does `add_airline` handle data missing required fields?"""
    mgr = temp_airline_manager_fixture
    # Missing 'company_name'.
    bad_airline_payload = {"record_type": "Airline", "some_other_field": "oops"}
    result = mgr.add_airline(bad_airline_payload)
    assert result is None

def test_airline_id_uniqueness(temp_airline_manager_fixture):
    """Are airline IDs generated by the manager unique?"""
    mgr = temp_airline_manager_fixture
    ids = set()
    for i in range(5):
        airline_payload = {"company_name": f"Air{i}", "record_type": "Airline"}
        airline = mgr.add_airline(airline_payload)
        assert airline is not None
        assert airline.airline_id not in ids
        ids.add(airline.airline_id)

def test_airline_serialization(temp_airline_manager_fixture, sample_airline_data_fixture):
    """Can an AirlineRecord be converted to a dict and back correctly?"""
    mgr = temp_airline_manager_fixture
    airline_payload = sample_airline_data_fixture.copy()
    if "airline_id" in airline_payload:
        del airline_payload["airline_id"]
    airline = mgr.add_airline(airline_payload)
    assert airline is not None
    airline_dict_data = airline.to_dict()
    new_airline = AirlineRecord.from_dict(airline_dict_data)
    assert new_airline.company_name == airline.company_name
    assert new_airline.airline_id == airline.airline_id

def test_flight_create_and_read(temp_flight_manager_fixture):
    """Can we create a flight and then find it?"""
    mgr, client_fixture_obj, airline_fixture_obj = temp_flight_manager_fixture
    flight_payload = {
        "Client_ID": client_fixture_obj.client_id,
        "Airline_ID": airline_fixture_obj.airline_id,
        "Date": "2025-05-17T12:00:00",
        "Start City": "Origin City",
        "End City": "Destination City",
        "record_type": "Flight"
    }
    flight = mgr.add_flight(flight_payload)
    assert flight is not None, "Flight should be added successfully."
    assert flight.flight_date.isoformat().startswith("2025-05-17T12:00:00")

    search_criteria = flight_payload.copy() # Search using the same details
    found_flights = mgr.find_flights(search_criteria)
    assert len(found_flights) == 1, "Should find exactly one matching flight."
    retrieved_flight = found_flights[0]
    assert retrieved_flight is not None
    assert retrieved_flight.flight_date.isoformat().startswith("2025-05-17T12:00:00")
    assert retrieved_flight.client_id == client_fixture_obj.client_id
    assert retrieved_flight.airline_id == airline_fixture_obj.airline_id
    assert retrieved_flight.start_city == "Origin City"


def test_flight_update_and_delete(temp_flight_manager_fixture):
    """Can we update a flight's details and then delete it?"""
    mgr, client_fixture_obj, airline_fixture_obj = temp_flight_manager_fixture
    flight_payload = {
        "Client_ID": client_fixture_obj.client_id,
        "Airline_ID": airline_fixture_obj.airline_id,
        "Date": "2025-05-17T12:00:00",
        "Start City": "Origin City",
        "End City": "Destination City",
        "record_type": "Flight"
    }
    flight = mgr.add_flight(flight_payload)
    assert flight is not None

    flight_identifier_dict = flight.to_dict() # Get details for identifying the flight

    updated = mgr.update_flight(flight_identifier_dict, {"Date": "2025-06-01T14:00:00"})
    assert updated is not None, "Flight update should return the updated object."
    assert updated.flight_date.isoformat().startswith("2025-06-01T14:00:00")

    # Use the updated flight's details to identify it for deletion
    updated_flight_identifier_dict = updated.to_dict()
    deleted = mgr.delete_flight(updated_flight_identifier_dict)
    assert deleted is True, "Flight deletion should succeed."
    assert not mgr.get_all_flights(), "Flight list should be empty after deletion."

def test_add_flight_non_existent_client(temp_flight_manager_fixture):
    """Does adding a flight fail if the Client_ID doesn't exist?"""
    mgr, _client_obj, airline_obj = temp_flight_manager_fixture
    flight_payload = {
        "Client_ID": 99999, # This ID should not exist
        "Airline_ID": airline_obj.airline_id,
        "Date": "2025-05-17T12:00:00",
        "Start City": "Origin City", "End City": "Destination City", "record_type": "Flight"
    }
    flight = mgr.add_flight(flight_payload)
    assert flight is None, "Flight addition should fail with non-existent Client_ID."

def test_add_flight_non_existent_airline(temp_flight_manager_fixture):
    """Does adding a flight fail if the Airline_ID doesn't exist?"""
    mgr, client_obj, _airline_obj = temp_flight_manager_fixture
    flight_payload = {
        "Client_ID": client_obj.client_id,
        "Airline_ID": 88888, # This ID should not exist
        "Date": "2025-05-17T12:00:00",
        "Start City": "Origin City", "End City": "Destination City", "record_type": "Flight"
    }
    flight = mgr.add_flight(flight_payload)
    assert flight is None, "Flight addition should fail with non-existent Airline_ID."

def test_add_flight_invalid_date_format(temp_flight_manager_fixture):
    """How is an invalid date format handled when adding a flight?"""
    mgr, client_obj, airline_obj = temp_flight_manager_fixture
    flight_payload = {
        "Client_ID": client_obj.client_id, "Airline_ID": airline_obj.airline_id,
        "Date": "17-05-2025 12:00", # Incorrect format
        "Start City": "Origin", "End City": "Destination", "record_type": "Flight"
    }
    # The FlightManager's add_flight is expected to catch the ValueError
    # from FlightRecord.from_dict due to the bad date and return None.
    result = mgr.add_flight(flight_payload)
    assert result is None, "Adding flight with invalid date format should return None."


def test_add_flight_save_failure_rollback(temp_flight_manager_fixture):
    """If saving fails, does `add_flight` roll back correctly?"""
    mgr, client_obj, airline_obj = temp_flight_manager_fixture
    initial_flights_count = len(mgr.get_all_flights())
    flight_payload = {
        "Client_ID": client_obj.client_id, "Airline_ID": airline_obj.airline_id,
        "Date": "2025-05-17T12:00:00", "Start City": "Test", "End City": "Case",
        "record_type": "Flight"
    }

    with mock.patch.object(mgr, '_save_flights', return_value=False) as mock_save:
        flight = mgr.add_flight(flight_payload)
        assert flight is None
        mock_save.assert_called_once()

    assert len(mgr.get_all_flights()) == initial_flights_count, "Flight list size should not change."


def test_update_flight_non_existent_linked_id(temp_flight_manager_fixture):
    """Can we prevent updating a flight to use a Client_ID or Airline_ID that doesn't exist?"""
    mgr, client_obj, airline_obj = temp_flight_manager_fixture
    flight_payload = {
        "Client_ID": client_obj.client_id, "Airline_ID": airline_obj.airline_id,
        "Date": "2025-07-01T10:00:00", "Start City": "Initial", "End City": "Point",
        "record_type": "Flight"
    }
    flight = mgr.add_flight(flight_payload)
    assert flight is not None
    flight_identifier = flight.to_dict()

    # Try updating to a non-existent Client_ID
    updated_flight_bad_client = mgr.update_flight(flight_identifier, {"Client_ID": 77777})
    assert updated_flight_bad_client is None, "Update with bad Client_ID should fail."

    # Try updating to a non-existent Airline_ID
    updated_flight_bad_airline = mgr.update_flight(flight_identifier, {"Airline_ID": 66666})
    assert updated_flight_bad_airline is None, "Update with bad Airline_ID should fail."

    # Ensure original flight is unchanged after failed update attempts
    found_flights = mgr.find_flights(flight_identifier)
    assert len(found_flights) == 1, "Original flight should still exist."
    assert found_flights[0].client_id == client_obj.client_id, "Client_ID should not have changed."


def test_find_flights_multiple_criteria(temp_flight_manager_fixture):
    """Does `find_flights` work correctly with multiple search terms?"""
    mgr, client_obj, airline_obj = temp_flight_manager_fixture
    mgr.add_flight({
        "Client_ID": client_obj.client_id, "Airline_ID": airline_obj.airline_id,
        "Date": "2025-08-01T10:00:00", "Start City": "London", "End City": "Paris",
        "record_type": "Flight"
    })
    mgr.add_flight({
        "Client_ID": client_obj.client_id, "Airline_ID": airline_obj.airline_id,
        "Date": "2025-08-02T14:00:00", "Start City": "London", "End City": "Amsterdam",
        "record_type": "Flight"
    })

    results = mgr.find_flights({"Start City": "London", "End City": "Paris"})
    assert len(results) == 1, "Should find one flight from London to Paris."
    assert results[0].end_city == "Paris"

    results_no_match = mgr.find_flights({"Start City": "London", "End City": "Berlin"})
    assert not results_no_match, "Should find no flights from London to Berlin."


def test_flight_add_invalid_data(temp_flight_manager_fixture):
    """Does `add_flight` handle data missing essential fields?"""
    mgr, _client_fixture_obj, _airline_fixture_obj = temp_flight_manager_fixture
    # Missing Client_ID, Airline_ID, Date, etc.
    bad_flight_payload = {"Start City": "Nowhere", "record_type": "Flight"}
    result = mgr.add_flight(bad_flight_payload)
    assert result is None

def test_flight_id_uniqueness(temp_flight_manager_fixture):
    """
    Can we add multiple, distinct flights successfully?
    (Note: This doesn't test for a simple 'flight_id' attribute, as flights
    seem to be identified by their combined details rather than a single ID.)
    """
    mgr, client_fixture_obj, airline_fixture_obj = temp_flight_manager_fixture
    initial_flight_count = len(mgr.get_all_flights())

    for i in range(5):
        flight_payload = {
            "Client_ID": client_fixture_obj.client_id,
            "Airline_ID": airline_fixture_obj.airline_id,
            "Date": f"2025-05-{10+i:02d}T{10+i:02d}:00:00", # Vary date & time
            "Start City": f"Origin City {i}", # Vary cities
            "End City": f"Destination City {i}",
            "record_type": "Flight"
        }
        flight = mgr.add_flight(flight_payload)
        assert flight is not None, f"Failed to add flight number {i+1}"

    assert len(mgr.get_all_flights()) == initial_flight_count + 5
    print("Note: Flight ID uniqueness test verified adding multiple distinct flights.")


def test_flight_serialization(temp_flight_manager_fixture):
    """Can a FlightRecord be converted to a dict and back without losing data?"""
    mgr, client_fixture_obj, airline_fixture_obj = temp_flight_manager_fixture
    flight_payload = {
        "Client_ID": client_fixture_obj.client_id,
        "Airline_ID": airline_fixture_obj.airline_id,
        "Date": "2025-05-17T12:00:00",
        "Start City": "Origin City",
        "End City": "Destination City",
        "record_type": "Flight"
    }
    flight = mgr.add_flight(flight_payload)
    assert flight is not None
    flight_dict_data = flight.to_dict()
    new_flight = FlightRecord.from_dict(flight_dict_data)

    assert new_flight.flight_date == flight.flight_date
    # 'flight_id' is not an attribute on FlightRecord based on previous errors.
    # assert new_flight.flight_id == flight.flight_id # pylint: disable=no-member
    assert new_flight.start_city == flight.start_city
    assert new_flight.end_city == flight.end_city
    assert new_flight.client_id == flight.client_id
    assert new_flight.airline_id == flight.airline_id
    print(
        "Note: Flight ID serialization check skipped due to absence of 'flight_id' "
        "attribute on FlightRecord objects from manager."
    )


# --- UI Event Handling Test Types ---

class MockTkRoot:
    """Mocks the Tkinter root window for UI tests."""
    def __init__(self):
        """Initializes the mock root."""
        self.title_val = ""
        self.geometry_val = ""

    def title(self, title_val=None):
        """Simulates setting or getting the window title."""
        if title_val:
            self.title_val = title_val
        return self.title_val

    def geometry(self, geometry_val=None):
        """Simulates setting or getting the window geometry."""
        if geometry_val:
            self.geometry_val = geometry_val
        return self.geometry_val

    def mainloop(self):
        """Simulates starting the Tkinter event loop."""
        # print("MockTkRoot.mainloop() called")

    def update_idletasks(self):
        """Simulates processing pending Tkinter tasks."""
        # print("MockTkRoot.update_idletasks() called")

    def destroy(self):
        """Simulates destroying the window."""
        # print("MockTkRoot.destroy() called")

class MockTkWidget:
    """
    Mocks common Tkinter widgets like Entry, StringVar, Label, Listbox.
    This helps test UI logic without a real GUI.
    """

    def __init__(self, master=None, text="", listbox_items=None):
        """Initializes the mock widget."""
        self._master = master
        self._value = text # For Entry, StringVar, Spinbox-like get/set
        self._text = text  # For Label-like text content
        self._items: list = listbox_items if listbox_items is not None else [] # For Listbox/Combobox
        self.curselection_val: list = [] # For Listbox selection
        self.widget_name = "mocklistbox" if listbox_items is not None else "mockwidget"
        self._exists_val = True # To simulate if a widget exists

    def get(self):
        """Simulates getting the value from an Entry, StringVar, or Spinbox."""
        return self._value

    def set(self, value):
        """Simulates setting the value for an Entry, StringVar, or Spinbox."""
        self._value = str(value) # Ensure it's a string, like Tkinter often does

    def cget(self, option):
        """Simulates getting a configuration option, like a Label's text."""
        if option == "text":
            return self._text
        return "" # Default for other options

    def config(self, **kwargs):
        """Simulates configuring widget options."""
        if "text" in kwargs:
            self._text = kwargs["text"]
        if "values" in kwargs: # For Combobox-like behavior
            self._items = list(kwargs["values"])

    configure = config # Alias for convenience

    def __getitem__(self, key):
        """Allows dictionary-style access, e.g., combobox['values']."""
        if key == 'values':
            return self._items # pylint: disable=protected-access
        raise KeyError(f"MockTkWidget does not support subscripting for key: {key}")


    def delete(self, first, last=None):
        """Simulates deleting content from an Entry or Listbox."""
        # Using "end" string, as tk.END might not be available if tkinter not fully imported
        if self.widget_name == "mocklistbox" and first == 0 and (last == "end"):
            self._items = [] # Clear all items from mock listbox
        elif self.widget_name != "mocklistbox" and first == 0 and (last == "end"):
            self._value = "" # Clear value for mock entry/stringvar


    def insert(self, index, *elements):
        """Simulates inserting items into a Listbox or text into an Entry."""
        if self.widget_name == "mocklistbox":
            actual_index = len(self._items) if index == "end" else int(index)
            for element in reversed(elements): # Insert multiple elements correctly
                self._items.insert(actual_index, element)
        else: # For Entry-like behavior
            idx = len(self._value) if index == "end" else int(index)
            self._value = self._value[:idx] + str(elements[0]) + self._value[idx:]


    def curselection(self):
        """Simulates getting the current selection indices from a Listbox."""
        return self.curselection_val

    def selection_clear(self, _first, _last=None): # _first, _last marked as unused
        """Simulates clearing the selection in a Listbox."""
        self.curselection_val = []

    def selection_set(self, index):
        """Simulates setting a selection in a Listbox."""
        if index not in self.curselection_val:
            try:
                int_index = int(index) # Ensure index is an integer
                if int_index not in self.curselection_val:
                    self.curselection_val.append(int_index)
                    self.curselection_val.sort() # Keep selection ordered
            except ValueError:
                # Handle cases where index might not be a convertible string
                print(f"MockTkWidget: Could not convert selection_set index '{index}' to int.")


    def activate(self, _index): # _index marked as unused
        """Simulates activating an item in a Listbox."""
        # No specific behavior needed for this mock.

    def see(self, _index): # _index marked as unused
        """Simulates ensuring an item is visible in a Listbox."""
        # No specific behavior needed for this mock.

    def size(self):
        """Simulates getting the number of items in a Listbox."""
        return len(self._items) # pylint: disable=protected-access

    def winfo_exists(self):
        """Simulates checking if the widget still exists in the UI."""
        return self._exists_val # Allows tests to simulate widget destruction


# Mock for tkcalendar.DateEntry
class MockDateEntry:
    """Mocks the tkcalendar.DateEntry widget for UI tests."""
    def __init__(self, master=None, **_kwargs): # _kwargs marked as unused
        """Initializes the mock DateEntry."""
        self._master = master
        self._date = datetime.date.today()
        self.widget_name = "mockdateentry"

    def get_date(self):
        """Simulates getting the selected date."""
        return self._date

    def set_date(self, date_obj):
        """Simulates setting the date on the widget."""
        if isinstance(date_obj, datetime.datetime):
            self._date = date_obj.date()
        elif isinstance(date_obj, datetime.date):
            self._date = date_obj
        else:
            # This helps catch incorrect usage in tests or event handlers
            raise TypeError("MockDateEntry.set_date expects a date or datetime object.")


class MockTravelApp:
    """
    A mock version of our main TravelApp GUI.
    This lets us test UI event logic without a real GUI.
    """
    def __init__(self):
        """Sets up the mock application with mock UI elements and managers."""
        self.root = MockTkRoot() # The main window

        # Mocking our backend managers
        self.client_mgr = mock.MagicMock(spec=ClientManager)
        self.airline_mgr = mock.MagicMock(spec=AirlineManager)
        self.flight_mgr = mock.MagicMock(spec=FlightManager)

        # Mocking UI elements that events.py interacts with
        self.selected_category = MockTkWidget() # For the category dropdown (e.g., Client, Airline)
        self.selected_category.set("Client") # Default starting category

        self.record_listbox = MockTkWidget(listbox_items=[]) # The list of records

        # Mocking form entry fields. Assuming up to 8 fields for the most complex form.
        self.entries = [MockTkWidget() for _ in range(8)]
        # Default field names, typically for the Client category
        self.field_names = [
            "name", "address_line_1", "city", "state", "zip_code", "country", "phone_number"
        ]

        # Mocks for the Flight form's specific dropdowns and date/time inputs
        self.client_var = MockTkWidget()      # For selected client in flight form
        self.airline_var = MockTkWidget()     # For selected airline in flight form
        self.calendar = MockDateEntry()       # For the flight date
        self.hour_spinbox = MockTkWidget()    # For flight hour
        self.minute_spinbox = MockTkWidget()  # For flight minute
        self.hour_spinbox.set("00")           # Default hour
        self.minute_spinbox.set("00")         # Default minute

        # Mocking the actual dropdown widgets for client/airline in the flight form
        self.client_dropdown = MockTkWidget(listbox_items=["Client Alpha", "Client Beta"])
        self.client_dropdown.widget_name = "mockclientdropdown"

        self.airline_dropdown = MockTkWidget(listbox_items=["Airline Zulu", "Airline Yankee"])
        self.airline_dropdown.widget_name = "mockairlinedropdown"

        self.selected_index = None # To track what's selected in the record_listbox
        self.filtered_records = None # To hold search results

        # Configuration for fields, used by events.py to know what's required
        self.fields_config = {
            "Client": {"Name*": "name", "Address": "address_line_1", "City": "city",
                       "State": "state", "Zip": "zip_code", "Country": "country",
                       "Phone": "phone_number"},
            "Airline": {"Company Name*": "company_name"},
            "Flight": { # Flight form is handled more directly in events.py
                "Start City": "start_city_entry_mock",
                "End City": "end_city_entry_mock"
            }
        }


@pytest.fixture
def mock_app_fixture():
    """Provides a fresh MockTravelApp instance for each UI test."""
    app = MockTravelApp()
    return app

# --- UI Event Tests ---

@mock.patch('src.gui.events.messagebox')
def test_load_records_clients(mock_messagebox, mock_app_fixture, sample_client_data_fixture):
    """Does `load_records` correctly fill the listbox with client data?"""
    app = mock_app_fixture
    app.selected_category.set("Client")

    # Prepare full data for ClientRecord.from_dict
    client1_full_data = sample_client_data_fixture.copy()
    client1_full_data.update({"client_id": 1, "name": "Test Client 1"})

    client2_full_data = sample_client_data_fixture.copy()
    client2_full_data.update({"client_id": 2, "name": "Test Client 2", "city": "Another Town"})

    mock_clients = [
        ClientRecord.from_dict(client1_full_data),
        ClientRecord.from_dict(client2_full_data)
    ]
    app.client_mgr.get_all_clients.return_value = mock_clients

    ui_events.load_records(app)

    app.client_mgr.get_all_clients.assert_called_once()
    assert app.record_listbox.size() == 2, "Listbox should contain two client records."
    # Check if the display strings are in the listbox (order might vary or be specific)
    assert "Test Client 1" in app.record_listbox._items[0], "First client missing or malformed." # pylint: disable=protected-access
    assert "Test Client 2" in app.record_listbox._items[1], "Second client missing or malformed."# pylint: disable=protected-access
    mock_messagebox.showerror.assert_not_called()


@mock.patch('src.gui.events.messagebox')
def test_load_records_no_manager(mock_messagebox, mock_app_fixture):
    """How does `load_records` handle an invalid category with no manager?"""
    app = mock_app_fixture
    app.selected_category.set("InvalidCategory") # This category shouldn't have a manager

    # Make get_manager return None when called with "InvalidCategory"
    with mock.patch('src.gui.events.get_manager', return_value=None) as mock_get_mgr:
        ui_events.load_records(app)
        mock_get_mgr.assert_called_once_with("InvalidCategory", app)

    mock_messagebox.showerror.assert_called_once_with(
        "Load Error", "No manager configured for InvalidCategory."
    )
    assert app.record_listbox.size() == 0, "Listbox should be empty after error."


@mock.patch('src.gui.events.messagebox')
def test_clear_form_resets_fields_and_reloads(mock_messagebox, mock_app_fixture):
    """Does `clear_form` empty the input fields and trigger a data reload?"""
    app = mock_app_fixture
    app.entries[0].set("Some Name") # Put some data in a field
    app.client_var.set("Client A")  # And in a flight-specific field
    app.record_listbox.insert(0, "An item") # Add something to the listbox
    app.selected_index = 0 # Simulate a selection

    # We want to check if load_records is called by clear_form
    with mock.patch('src.gui.events.load_records') as mock_load_records:
        ui_events.clear_form(app)

        # Check that all general entry fields are cleared
        for entry in app.entries:
            assert entry.get() == "", f"Entry field should be empty but was '{entry.get()}'"

        # Check flight-specific fields
        assert app.client_var.get() == "", "Client var for flight form should be cleared."
        assert app.airline_var.get() == "", "Airline var for flight form should be cleared."

        assert app.selected_index is None, "Selected index should be reset."
        assert not app.record_listbox.curselection_val, "Listbox selection should be cleared."
        mock_load_records.assert_called_once_with(app)
    mock_messagebox.showerror.assert_not_called()


@mock.patch('src.gui.events.messagebox')
def test_add_client_record_success(mock_messagebox, mock_app_fixture, sample_client_data_fixture):
    """Can we successfully add a new client through the UI event flow?"""
    app = mock_app_fixture
    app.selected_category.set("Client")

    app.field_names = list(app.fields_config["Client"].values())
    if len(app.field_names) > len(app.entries): # Ensure enough mock entries
        app.entries.extend([MockTkWidget() for _ in range(len(app.field_names) - len(app.entries))])

    # Simulate user filling the form
    app.entries[app.field_names.index("name")].set("New Client Alpha")
    app.entries[app.field_names.index("address_line_1")].set("1 Test Rd")
    app.entries[app.field_names.index("city")].set("Testville")
    app.entries[app.field_names.index("state")].set("TS")
    app.entries[app.field_names.index("zip_code")].set("12345")
    app.entries[app.field_names.index("country")].set("Testland")
    app.entries[app.field_names.index("phone_number")].set("555-0100")

    # This is the data we expect ClientRecord.from_dict to receive
    expected_record_data = sample_client_data_fixture.copy()
    expected_record_data.update({
        "client_id": 100, "name": "New Client Alpha", "address_line_1": "1 Test Rd",
        "city": "Testville", "state": "TS", "zip_code": "12345",
        "country": "Testland", "phone_number": "555-0100",
    })
    mock_added_client = ClientRecord.from_dict(expected_record_data)
    app.client_mgr.add_client.return_value = mock_added_client # Manager "succeeds"

    with mock.patch('src.gui.events.clear_form') as mock_clear_form:
        ui_events.add_record(app)

        app.client_mgr.add_client.assert_called_once()
        # Check the data that was passed to the manager's add_client method
        call_args_dict = app.client_mgr.add_client.call_args[0][0]
        assert call_args_dict["name"] == "New Client Alpha"
        assert call_args_dict["city"] == "Testville"
        assert call_args_dict["record_type"] == "Client" # events.py adds this

        mock_messagebox.showinfo.assert_called_once_with("Success", "Client record added.")
        mock_clear_form.assert_called_once_with(app) # Form should clear on success


@mock.patch('src.gui.events.messagebox')
def test_add_client_record_missing_required_field_ui(mock_messagebox, mock_app_fixture):
    """Does the UI show a warning if a required client field is empty?"""
    app = mock_app_fixture
    app.selected_category.set("Client")
    # 'Name*' is required according to app.fields_config["Client"]
    app.field_names = list(app.fields_config["Client"].values())
    app.entries[app.field_names.index("name")].set("") # Name is empty
    app.entries[app.field_names.index("address_line_1")].set("Some Address")

    ui_events.add_record(app)

    app.client_mgr.add_client.assert_not_called()
    mock_messagebox.showwarning.assert_called_once_with(
        "Input Required", "The field 'Name*' is required."
    )

@mock.patch('src.gui.events.messagebox')
def test_add_record_manager_failure(mock_messagebox, mock_app_fixture, sample_client_data_fixture):
    """How does `add_record` behave if the backend manager fails to add?"""
    app = mock_app_fixture
    app.selected_category.set("Client")
    app.field_names = list(app.fields_config["Client"].values())
    if len(app.field_names) > len(app.entries): # Ensure enough mock entries
        app.entries.extend([MockTkWidget() for _ in range(len(app.field_names) - len(app.entries))])

    # Fill form with valid data
    for i, field_key in enumerate(app.field_names):
        if field_key in sample_client_data_fixture:
            app.entries[i].set(str(sample_client_data_fixture[field_key]))
        else:
            app.entries[i].set(f"Value for {field_key}") # Default if not in sample


    app.client_mgr.add_client.return_value = None # Simulate manager failure

    with mock.patch('src.gui.events.clear_form') as mock_clear_form:
        ui_events.add_record(app)
        app.client_mgr.add_client.assert_called_once()
        mock_messagebox.showerror.assert_called_once_with("Add Error", "Failed to add client.")
        mock_clear_form.assert_not_called()

@mock.patch('src.gui.events.messagebox')
def test_delete_record_no_selection(mock_messagebox, mock_app_fixture):
    """What happens if 'Delete' is clicked with no record selected?"""
    app = mock_app_fixture
    app.selected_index = None # No item selected

    ui_events.delete_record(app)

    mock_messagebox.showwarning.assert_called_once_with(
        "Selection Error", "No record selected to delete."
    )
    app.client_mgr.delete_client.assert_not_called()

@mock.patch('src.gui.events.messagebox')
def test_delete_record_confirmation_no(mock_messagebox, mock_app_fixture, sample_client_data_fixture):
    """What if the user cancels the delete confirmation?"""
    app = mock_app_fixture
    app.selected_category.set("Client")
    app.selected_index = 0 # An item is selected
    # Provide a record for the selection
    client_data = sample_client_data_fixture.copy()
    client_data["client_id"] = 1 # Give it an ID
    app.client_mgr.get_all_clients.return_value = [ClientRecord.from_dict(client_data)]
    app.record_listbox._items = [f"Client: {client_data['name']} (ID: {client_data['client_id']})"] # pylint: disable=protected-access

    mock_messagebox.askyesno.return_value = False # User clicks "No"

    ui_events.delete_record(app)

    mock_messagebox.askyesno.assert_called_once()
    app.client_mgr.delete_client.assert_not_called()

@mock.patch('src.gui.events.messagebox')
def test_delete_record_manager_failure(mock_messagebox, mock_app_fixture, sample_client_data_fixture):
    """How does the UI handle it if the manager fails to delete a record?"""
    app = mock_app_fixture
    app.selected_category.set("Client")
    app.selected_index = 0
    client_to_delete_data = sample_client_data_fixture.copy()
    client_to_delete_data["client_id"] = 1
    client_to_delete = ClientRecord.from_dict(client_to_delete_data)

    app.client_mgr.get_all_clients.return_value = [client_to_delete]
    app.record_listbox._items = [ # pylint: disable=protected-access
        f"Client: {client_to_delete.name} (ID: {client_to_delete.client_id})"
    ]

    mock_messagebox.askyesno.return_value = True # User confirms
    app.client_mgr.delete_client.return_value = False # Manager reports failure

    with mock.patch('src.gui.events.clear_form') as mock_clear_form:
        ui_events.delete_record(app)
        app.client_mgr.delete_client.assert_called_once_with(client_to_delete.client_id)
        mock_messagebox.showerror.assert_called_once_with("Delete Error", "Failed to delete client.")
        mock_clear_form.assert_not_called()

@mock.patch('src.gui.events.messagebox')
def test_update_record_no_selection(mock_messagebox, mock_app_fixture):
    """What if 'Update' is clicked with no record selected?"""
    app = mock_app_fixture
    app.selected_index = None
    ui_events.update_record(app)
    mock_messagebox.showwarning.assert_called_once_with(
        "Selection Error", "No record selected to update."
    )
    app.client_mgr.update_client.assert_not_called()

@mock.patch('src.gui.events.messagebox')
def test_on_select_populates_form_client(mock_messagebox, mock_app_fixture, sample_client_data_fixture):
    """When a client is selected, are the form fields filled correctly?"""
    app = mock_app_fixture
    app.selected_category.set("Client")
    client_data = sample_client_data_fixture.copy()
    client_data["client_id"] = 1
    mock_client_record = ClientRecord.from_dict(client_data)
    app.client_mgr.get_all_clients.return_value = [mock_client_record]
    app.record_listbox._items = [f"Client: {mock_client_record.name} (ID: 1)"] # pylint: disable=protected-access
    app.record_listbox.curselection_val = [0] # Simulate listbox selection

    app.field_names = list(app.fields_config["Client"].values())
    if len(app.field_names) > len(app.entries): # Ensure enough mock entries
        app.entries.extend([MockTkWidget() for _ in range(len(app.field_names) - len(app.entries))])

    ui_events.on_select(app)

    # Check that form entries received the correct data
    for i, field_key in enumerate(app.field_names):
        if hasattr(mock_client_record, field_key):
            expected_value = getattr(mock_client_record, field_key)
            assert app.entries[i].get() == str(expected_value if expected_value is not None else "")
    mock_messagebox.showerror.assert_not_called()

@mock.patch('src.gui.events.messagebox')
def test_on_select_populates_form_flight(mock_messagebox, mock_app_fixture, sample_client_data_fixture, sample_airline_data_fixture): # pylint: disable=line-too-long
    """When a flight is selected, are its specific form fields (dropdowns, date/time) filled?"""
    app = mock_app_fixture
    app.selected_category.set("Flight")

    mock_client = ClientRecord.from_dict(sample_client_data_fixture)
    mock_airline = AirlineRecord.from_dict(sample_airline_data_fixture)
    app.client_mgr.get_client_by_id.return_value = mock_client
    app.airline_mgr.get_airline_by_id.return_value = mock_airline

    # Set up values for the mock dropdowns
    app.client_dropdown.config(values=[mock_client.name, "Other Client"])
    app.airline_dropdown.config(values=[mock_airline.company_name, "Other Airline"])

    flight_datetime_obj = datetime.datetime(2025, 10, 20, 14, 30)
    # Keys for FlightRecord.from_dict must match its expectations
    flight_data_for_record = {
        "record_type": "Flight",
        "Client_ID": mock_client.client_id, # Use the correct key "Client_ID"
        "Airline_ID": mock_airline.airline_id, # Use the correct key "Airline_ID"
        "Date": flight_datetime_obj.isoformat(), # Pass ISO string
        "Start City": "Testville",
        "End City": "Destination X"
    }
    mock_flight_record = FlightRecord.from_dict(flight_data_for_record)
    app.flight_mgr.get_all_flights.return_value = [mock_flight_record]
    app.record_listbox._items = [ # pylint: disable=protected-access
        f"Flight from Testville to Destination X" # Simplified display string
    ]
    app.record_listbox.curselection_val = [0] # Simulate selection

    app.entries = [MockTkWidget(), MockTkWidget()] # For Start City, End City

    ui_events.on_select(app)

    assert app.client_var.get() == mock_client.name, "Client dropdown not set correctly."
    assert app.airline_var.get() == mock_airline.company_name, "Airline dropdown not set."
    assert app.calendar.get_date() == flight_datetime_obj.date(), "Calendar date not set."
    assert app.hour_spinbox.get() == f"{flight_datetime_obj.hour:02d}", "Hour not set."
    assert app.minute_spinbox.get() == f"{flight_datetime_obj.minute:02d}", "Minute not set."
    assert app.entries[0].get() == "Testville", "Start City not populated."
    assert app.entries[1].get() == "Destination X", "End City not populated."
    mock_messagebox.showerror.assert_not_called()


@mock.patch('src.gui.events.simpledialog.askstring')
@mock.patch('src.gui.events.messagebox')
def test_search_records_user_cancel(mock_messagebox, mock_askstring, mock_app_fixture):
    """What if the user cancels the search input dialog?"""
    app = mock_app_fixture
    mock_askstring.return_value = None # Simulate cancel

    ui_events.search_records(app)

    mock_askstring.assert_called_once()
    app.client_mgr.get_all_clients.assert_not_called()
    mock_messagebox.showinfo.assert_not_called()


@mock.patch('src.gui.events.simpledialog.askstring')
@mock.patch('src.gui.events.messagebox')
def test_search_records_no_results(mock_messagebox, mock_askstring, mock_app_fixture, sample_client_data_fixture): # pylint: disable=line-too-long
    """How does search behave when no matching records are found?"""
    app = mock_app_fixture
    app.selected_category.set("Client")
    search_term_original = "NonExistentSearchTerm"
    search_term_lower = search_term_original.lower() # events.py lowercases the search term
    mock_askstring.return_value = search_term_original

    # Make sure get_all_clients returns data that won't match the search term
    client_data = sample_client_data_fixture.copy()
    client_data["name"] = "Walter" # This won't match "NonExistentSearchTerm"
    app.client_mgr.get_all_clients.return_value = [ClientRecord.from_dict(client_data)]

    with mock.patch('src.gui.events.refresh_listbox') as mock_refresh:
        ui_events.search_records(app)
        # Check that the "no results" message box is shown
        mock_messagebox.showinfo.assert_any_call(
            "Search Results", f"No client records found matching '{search_term_lower}'."
        )
        # Ensure the listbox is refreshed with an empty list
        mock_refresh.assert_called_once_with(app, [])


def test_on_select_listbox_does_not_exist(mock_app_fixture):
    """Is `on_select` robust if the listbox widget somehow doesn't exist?"""
    app = mock_app_fixture
    app.record_listbox._exists_val = False # pylint: disable=protected-access

    # This call should ideally not crash the application.
    ui_events.on_select(app)
    # No specific assertion other than it completed without error.
    # We can also check that no manager calls were made, as it should have exited early.
    app.client_mgr.get_all_clients.assert_not_called()
