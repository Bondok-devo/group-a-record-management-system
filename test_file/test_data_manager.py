import sys
import os
# Add the project root to sys.path so 'src' is importable
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import pytest
from src.record.client_manager import ClientManager

@pytest.fixture
def temp_client_manager(tmp_path):
    # Use a temporary file for testing
    test_file = tmp_path / "test_clients.jsonl"
    mgr = ClientManager(clients_file_path=str(test_file))
    return mgr

@pytest.fixture
def sample_client_data():
    return {
        "name": "Walter",
        "address_line_1": "123 Main St",
        "address_line_2": "",
        "address_line_3": "",
        "city": "New York",
        "state": "StateX",
        "zip_code": "12345",
        "country": "CountryY",
        "phone_number": "1234567890"
    }

def test_create_client_record(temp_client_manager, sample_client_data):
    mgr = temp_client_manager
    client = mgr.add_client(sample_client_data)
    assert client is not None
    assert client.name == "Walter"
    assert len(mgr.get_all_clients()) == 1

def test_read_client_record(temp_client_manager, sample_client_data):
    mgr = temp_client_manager
    client = mgr.add_client(sample_client_data)
    result = mgr.get_client_by_id(client.client_id)
    assert result is not None
    assert result.name == "Walter"

def test_update_client_record(temp_client_manager, sample_client_data):
    mgr = temp_client_manager
    client = mgr.add_client(sample_client_data)
    update_data = {"city": "Boston"}
    updated = mgr.update_client(client.client_id, update_data)
    assert updated is not None
    assert updated.city == "Boston"

def test_delete_client_record(temp_client_manager, sample_client_data):
    mgr = temp_client_manager
    client = mgr.add_client(sample_client_data)
    deleted = mgr.delete_client(client.client_id)
    assert deleted is True
    assert len(mgr.get_all_clients()) == 0

def test_init_with_missing_file(tmp_path):
    # Should initialize with empty client list if file does not exist
    test_file = tmp_path / "missing.jsonl"
    mgr = ClientManager(clients_file_path=str(test_file))
    assert mgr.get_all_clients() == []

def test_init_with_empty_file(tmp_path):
    test_file = tmp_path / "empty.jsonl"
    test_file.write_text("")
    mgr = ClientManager(clients_file_path=str(test_file))
    assert mgr.get_all_clients() == []

def test_init_with_malformed_file(tmp_path):
    test_file = tmp_path / "malformed.jsonl"
    test_file.write_text("not a json line\n{bad json}")
    mgr = ClientManager(clients_file_path=str(test_file))
    # Should skip bad lines and not crash
    assert mgr.get_all_clients() == []

def test_id_uniqueness(temp_client_manager, sample_client_data):
    mgr = temp_client_manager
    ids = set()
    for i in range(10):
        data = dict(sample_client_data)
        data["name"] = f"Name{i}"
        client = mgr.add_client(data)
        assert client.client_id not in ids
        ids.add(client.client_id)

def test_add_invalid_data(temp_client_manager):
    mgr = temp_client_manager
    # Missing required field
    bad_data = {"address_line_1": "123"}
    result = mgr.add_client(bad_data)
    assert result is None

def test_update_nonexistent_client(temp_client_manager):
    mgr = temp_client_manager
    result = mgr.update_client("nonexistent_id", {"city": "Nowhere"})
    assert result is None

def test_delete_nonexistent_client(temp_client_manager):
    mgr = temp_client_manager
    result = mgr.delete_client("nonexistent_id")
    assert result is False

def test_search_by_city(temp_client_manager, sample_client_data):
    mgr = temp_client_manager
    mgr.add_client(sample_client_data)
    results = [c for c in mgr.get_all_clients() if c.city == "New York"]
    assert len(results) == 1
    results = [c for c in mgr.get_all_clients() if c.city == "Boston"]
    assert len(results) == 0

def test_serialization_deserialization(temp_client_manager, sample_client_data):
    mgr = temp_client_manager
    client = mgr.add_client(sample_client_data)
    d = client.to_dict()
    from src.record.client_record import ClientRecord
    new_client = ClientRecord.from_dict(d)
    assert new_client.name == client.name
    assert new_client.client_id == client.client_id

# --- AirlineManager and FlightManager tests ---
from src.record.airline_manager import AirlineManager
from src.record.flight_manager import FlightManager

@pytest.fixture
def temp_airline_manager(tmp_path):
    test_file = tmp_path / "test_airlines.jsonl"
    mgr = AirlineManager(airlines_file_path=str(test_file))
    return mgr

@pytest.fixture
def sample_airline_data():
    return {"company_name": "TestAir", "record_type": "Airline"}

@pytest.fixture
def temp_flight_manager(tmp_path):
    client_file = tmp_path / "test_clients.jsonl"
    airline_file = tmp_path / "test_airlines.jsonl"
    flight_file = tmp_path / "test_flights.jsonl"
    client_mgr = ClientManager(clients_file_path=str(client_file))
    airline_mgr = AirlineManager(airlines_file_path=str(airline_file))
    # Add a client and airline for referential integrity
    client = client_mgr.add_client({"name": "Walter", "address_line_1": "123 Main St", "address_line_2": "", "address_line_3": "", "city": "New York", "state": "StateX", "zip_code": "12345", "country": "CountryY", "phone_number": "1234567890"})
    airline = airline_mgr.add_airline({"company_name": "TestAir", "record_type": "Airline"})
    mgr = FlightManager(flights_file_path=str(flight_file), client_manager=client_mgr, airline_manager=airline_mgr)
    return mgr, client, airline

def test_airline_create_and_read(temp_airline_manager, sample_airline_data):
    mgr = temp_airline_manager
    # Intentionally break: remove 'record_type' to cause failure
    broken_data = {"company_name": "TestAir"}
    airline = mgr.add_airline(broken_data)
    assert airline is not None
    assert airline.company_name == "TestAir"
    result = mgr.get_airline_by_id(airline.airline_id)
    assert result is not None
    assert result.company_name == "TestAir"

def test_airline_update_and_delete(temp_airline_manager, sample_airline_data):
    mgr = temp_airline_manager
    # Intentionally break: remove 'record_type' to cause failure
    broken_data = {"company_name": "TestAir"}
    airline = mgr.add_airline(broken_data)
    updated = mgr.update_airline(airline.airline_id, {"company_name": "NewName"})
    assert updated is not None
    assert updated.company_name == "NewName"
    deleted = mgr.delete_airline(airline.airline_id)
    assert deleted is True
    assert mgr.get_all_airlines() == []

def test_airline_add_invalid_data(temp_airline_manager):
    mgr = temp_airline_manager
    bad_data = {"bad_field": "oops"}
    result = mgr.add_airline(bad_data)
    assert result is None

def test_airline_id_uniqueness(temp_airline_manager, sample_airline_data):
    mgr = temp_airline_manager
    ids = set()
    for i in range(5):
        # Intentionally break: remove 'record_type' to cause failure
        data = {"company_name": f"Air{i}"}
        airline = mgr.add_airline(data)
        assert airline.airline_id not in ids
        ids.add(airline.airline_id)

def test_airline_serialization(temp_airline_manager, sample_airline_data):
    mgr = temp_airline_manager
    # Intentionally break: remove 'record_type' to cause failure
    broken_data = {"company_name": "TestAir"}
    airline = mgr.add_airline(broken_data)
    d = airline.to_dict()
    from src.record.airline_record import AirlineRecord
    new_airline = AirlineRecord.from_dict(d)
    assert new_airline.company_name == airline.company_name
    assert new_airline.airline_id == airline.airline_id

def test_flight_create_and_read(temp_flight_manager):
    mgr, client, airline = temp_flight_manager
    data = {"Client_ID": client.client_id, "Airline_ID": airline.airline_id, "Date": "2025-05-17", "Time": "12:00", "record_type": "Flight"}
    flight = mgr.add_flight(data)
    assert flight is not None
    assert flight.Date == "2025-05-17"
    result = mgr.get_flight_by_id(flight.flight_id)
    assert result is not None
    assert result.Date == "2025-05-17"

def test_flight_update_and_delete(temp_flight_manager):
    mgr, client, airline = temp_flight_manager
    data = {"Client_ID": client.client_id, "Airline_ID": airline.airline_id, "Date": "2025-05-17", "Time": "12:00", "record_type": "Flight"}
    flight = mgr.add_flight(data)
    updated = mgr.update_flight(flight.flight_id, {"Date": "2025-06-01"})
    assert updated is not None
    assert updated.Date == "2025-06-01"
    deleted = mgr.delete_flight(flight.flight_id)
    assert deleted is True
    assert mgr.get_all_flights() == []

def test_flight_add_invalid_data(temp_flight_manager):
    mgr, client, airline = temp_flight_manager
    bad_data = {"bad_field": "oops"}
    result = mgr.add_flight(bad_data)
    assert result is None

def test_flight_id_uniqueness(temp_flight_manager):
    mgr, client, airline = temp_flight_manager
    ids = set()
    for i in range(5):
        data = {"Client_ID": client.client_id, "Airline_ID": airline.airline_id, "Date": f"2025-05-{10+i}", "Time": "10:00", "record_type": "Flight"}
        flight = mgr.add_flight(data)
        assert flight.flight_id not in ids
        ids.add(flight.flight_id)

def test_flight_serialization(temp_flight_manager):
    mgr, client, airline = temp_flight_manager
    data = {"Client_ID": client.client_id, "Airline_ID": airline.airline_id, "Date": "2025-05-17", "Time": "12:00", "record_type": "Flight"}
    flight = mgr.add_flight(data)
    d = flight.to_dict()
    from src.record.flight_record import FlightRecord
    new_flight = FlightRecord.from_dict(d)
    assert new_flight.Date == flight.Date
    assert new_flight.flight_id == flight.flight_id