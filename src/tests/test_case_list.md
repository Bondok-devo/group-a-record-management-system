# Test Case List for Backend Logic (Unit & Integration)

This document lists all implemented and planned test cases for the backend logic of the Specialist Travel Agent Records system. Use this as a checklist or submission to show what is covered and what is not.

## ClientManager (client_manager.py)
- [x] test_create_client_record: Add a valid client (success)
- [x] test_read_client_record: Retrieve a client by ID (success)
- [x] test_update_client_record: Update a client (success)
- [x] test_delete_client_record: Delete a client (success)
- [x] test_init_with_missing_file: Load with missing file (should be empty)
- [x] test_init_with_empty_file: Load with empty file (should be empty)
- [x] test_init_with_malformed_file: Load with malformed file (should skip bad lines)
- [x] test_id_uniqueness: Ensure unique client IDs
- [x] test_add_invalid_data: Add client with missing required field (should fail)
- [x] test_update_nonexistent_client: Update non-existent client (should fail)
- [x] test_delete_nonexistent_client: Delete non-existent client (should fail)
- [x] test_search_by_city: Filter/search by city
- [x] test_serialization_deserialization: to_dict/from_dict roundtrip

## AirlineManager (airline_manager.py)
- [x] test_airline_create_and_read: Add and retrieve airline (currently intentionally fails)
- [x] test_airline_update_and_delete: Update and delete airline (currently intentionally fails)
- [x] test_airline_add_invalid_data: Add airline with missing required field (should fail)
- [x] test_airline_id_uniqueness: Ensure unique airline IDs (currently intentionally fails)
- [x] test_airline_serialization: to_dict/from_dict roundtrip (currently intentionally fails)

## FlightManager (flight_manager.py)
- [x] test_flight_create_and_read: Add and retrieve flight (currently fails: missing required field 'Start City')
- [x] test_flight_update_and_delete: Update and delete flight (currently fails: missing required field 'Start City')
- [x] test_flight_add_invalid_data: Add flight with missing required field (should fail)
- [x] test_flight_id_uniqueness: Ensure unique flight IDs (currently fails: missing required field 'Start City')
- [x] test_flight_serialization: to_dict/from_dict roundtrip (currently fails: missing required field 'Start City')

## Legend
- [x] = Test implemented (see test_data_manager.py)
- (success) = Test passes
- (should fail) = Test is expected to fail for invalid input
- (currently intentionally fails) = Test is intentionally broken for demonstration
- (currently fails: ...) = Test fails due to missing required field or logic

---

This list can be submitted to show exactly which backend logic test cases are implemented, which pass, and which are currently failing or intentionally broken.
