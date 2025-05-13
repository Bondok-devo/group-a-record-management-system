import pytest

# Assuming you have a module named data_manager.py with CRUD functions
from data_manager import (
    create_client_record,
    read_client_record,
    update_client_record,
    delete_client_record,
)

@pytest.fixture
def sample_client():
    return {
        "ID": 1,
        "Type": "Regular",
        "Name": "Walter",
        "Address Line 1": "123 Main St",
        "Address Line 2": "",
        "Address Line 3": "",
        "City": "New York",
        "State": "StateX",
        "Zip Code": "12345",
        "Country": "CountryY",
        "Phone Number": "1234567890"
    }

def test_create_client_record(sample_client):
    records = []
    create_client_record(records, sample_client)
    assert len(records) == 1
    assert records[0]["Name"] == "John Doe"

def test_read_client_record(sample_client):
    records = [sample_client]
    result = read_client_record(records, 1)
    assert result["ID"] == 1

def test_update_client_record(sample_client):
    records = [sample_client]
    update_data = {"Name": "Jane Doe"}
    update_client_record(records, 1, update_data)
    assert records[0]["Name"] == "Jane Doe"

def test_delete_client_record(sample_client):
    records = [sample_client]
    delete_client_record(records, 1)
    assert len(records) == 0