import pytest
import os
from file_handler import save_records, load_records

def test_save_and_load_records(tmp_path):
    records = [{"ID": 1, "Name": "Test"}]
    file_path = tmp_path / "records.json"
    save_records(records, file_path)
    loaded = load_records(file_path)
    assert loaded == records