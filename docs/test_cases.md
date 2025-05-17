# Guide to Unit Tests: Travel Record Management System

This document provides an overview of the unit tests developed for the Travel Record Management System. It covers tests for the backend data management components (Client, Airline, and Flight managers) and the UI event handling logic. The objective of these tests is to ensure that individual parts of the application function correctly and reliably under various conditions.

## I. Backend Logic & Data Management Tests (`ClientManager`, `AirlineManager`, `FlightManager`)

This section details the tests focused on the core logic for handling data records, encompassing Create, Read, Update, Delete (CRUD) operations, and general data management. `pytest` fixtures are utilized to establish temporary, isolated environments for each test. This ensures that each test operates with a fresh set of data files and manager instances, preventing interference between tests or with actual application data.

### A. `ClientManager` Tests

These tests verify the functionality of the `ClientManager` class, which is responsible for client records.

1.  **`test_create_client_record(...)`**
    * **Objective**: To ensure that a new client record can be successfully created and added to the system.
    * **Methodology**: A temporary `ClientManager` and sample client data are used. `mgr.add_client()` is called. Assertions verify that a `ClientRecord` object is returned, its name matches the input, and the total client count increases.

2.  **`test_read_client_record(...)`**
    * **Objective**: To verify that an existing client record can be retrieved by its unique ID.
    * **Methodology**: A sample client is added. `mgr.get_client_by_id()` is called. Assertions verify that a `ClientRecord` object is returned and its name matches the original.

3.  **`test_update_client_record(...)`**
    * **Objective**: To check if a client's details can be updated correctly.
    * **Methodology**: A sample client is added. `mgr.update_client()` is called with the client's ID and new data. Assertions verify the return of an updated `ClientRecord` and that specified fields reflect the update.

4.  **`test_update_client_id_ignored(...)`**
    * **Objective**: To confirm that an attempt to change a client's `client_id` via `update_client` is ignored.
    * **Methodology**: A client is added. `mgr.update_client()` is called with a payload attempting to change `client_id`. Assertions verify the `client_id` remains unchanged while other fields are updated.

5.  **`test_delete_client_record(...)`**
    * **Objective**: To verify that a client record can be successfully removed.
    * **Methodology**: A sample client is added. `mgr.delete_client()` is called. Assertions verify a `True` return value and that the client is no longer in the manager's list.

6.  **`test_init_with_missing_file(...)`**
    * **Objective**: To observe `ClientManager` behavior when its data file is missing upon initialization.
    * **Methodology**: `ClientManager` is initialized with a path to a non-existent file. It's asserted that the manager starts with an empty client list.

7.  **`test_init_with_empty_file(...)`**
    * **Objective**: To test initialization when the data file exists but is empty.
    * **Methodology**: An empty temporary file is created. `ClientManager` is initialized. It's asserted that no clients are loaded.

8.  **`test_init_with_malformed_file(...)`**
    * **Objective**: To ensure `ClientManager` robustly handles a data file with invalid JSON.
    * **Methodology**: A temporary file with invalid JSON lines is created. `ClientManager` is initialized. It's asserted that errors are handled gracefully (bad lines skipped) and no clients (or only valid ones) are loaded.

9.  **`test_init_with_incomplete_data_line(...)`**
    * **Objective**: To test loading a record from a file where a line is valid JSON but missing fields essential for `ClientRecord.from_dict`.
    * **Methodology**: A file is created with a JSON line missing key client information. `ClientManager` is initialized. It's asserted this incomplete record is not loaded.

10. **`test_id_uniqueness(...)`**
    * **Objective**: To ensure every new client receives a unique `client_id`.
    * **Methodology**: Multiple clients are added. For each, its `client_id` is asserted to be unique by checking against a set of previously seen IDs.

11. **`test_add_client_boundary_conditions(...)`**
    * **Objective**: To check `add_client` behavior with boundary values, such as an empty or very long name string.
    * **Methodology**: Attempts are made to add clients with an empty name and a very long name. Assertions are based on whether this is allowed or results in `None` (if validation prevents it).

12. **`test_add_client_save_failure_rollback(...)`**
    * **Objective**: To ensure that if a file save operation fails during `add_client`, the system state remains consistent (the new client is not added in-memory, and the next ID is reset).
    * **Methodology**: `unittest.mock.patch` simulates a `_save_clients` failure. `add_client` is called. Assertions verify `add_client` returns `None`, the client list size is unchanged, and the internal `_next_id` is rolled back.

13. **`test_add_invalid_data(...)`**
    * **Objective**: To test adding a client with data missing key information required by `ClientRecord.from_dict`.
    * **Methodology**: `mgr.add_client()` is called with an incomplete data dictionary. It's asserted that `add_client` returns `None`.

14. **`test_update_nonexistent_client(...)`**
    * **Objective**: To observe behavior when attempting to update a non-existent client ID.
    * **Methodology**: `mgr.update_client()` is called with a non-existent ID. It's asserted that the method returns `None`.

15. **`test_delete_nonexistent_client(...)`**
    * **Objective**: To test deleting a non-existent client ID.
    * **Methodology**: `mgr.delete_client()` is called with a non-existent ID. It's asserted that the method returns `False`.

16. **`test_find_clients_non_existent_criteria_key(...)`**
    * **Objective**: To ensure `find_clients` handles search criteria with keys not present in `ClientRecord`.
    * **Methodology**: A sample client is added. `mgr.find_clients()` is called with criteria containing a non-existent attribute. An empty list is asserted as the result.

17. **`test_serialization_deserialization(...)`**
    * **Objective**: To ensure `ClientRecord` objects can be converted to a dictionary (`to_dict`) and recreated (`from_dict`) without data alteration.
    * **Methodology**: A client is added, converted to a dict, then back to an object. Key attributes are asserted to match the original.

18. **`test_client_record_from_dict_missing_key(...)`**
    * **Objective**: To test `ClientRecord.from_dict` for robustness against missing essential data in the input dictionary.
    * **Methodology**: Sample client data is modified to remove an essential key (e.g., `name`). `pytest.raises(ValueError)` asserts that `ClientRecord.from_dict` triggers the expected exception.

### B. `AirlineManager` Tests

These tests mirror the structure and intent of `ClientManager` tests, applied to `AirlineManager` and `AirlineRecord` objects. They cover: creation, reading, updating, deletion, boundary conditions for company names, save failure rollbacks, handling of missing keys in `from_dict`, adding invalid data, ID uniqueness, and serialization/deserialization.

### C. `FlightManager` Tests

`FlightManager` tests account for dependencies on `ClientManager` and `AirlineManager` for referential integrity.

* **`test_flight_create_and_read(...)`**: Verifies flight creation and retrieval using `mgr.find_flights()` with the original payload as search criteria, as no direct `get_flight_by_id` method exists.
* **`test_flight_update_and_delete(...)`**: Checks updating and deleting flights, using `flight.to_dict()` for identification.
* **`test_add_flight_non_existent_client(...)` / `test_add_flight_non_existent_airline(...)`**: Ensure referential integrity by attempting to add flights with invalid `Client_ID` or `Airline_ID`. `add_flight` should return `None`.
* **`test_add_flight_invalid_date_format(...)`**: Verifies graceful handling of improperly formatted date strings, expecting `add_flight` to return `None`.
* **`test_add_flight_save_failure_rollback(...)`**: Ensures no in-memory addition if `_save_flights` fails.
* **`test_update_flight_non_existent_linked_id(...)`**: Checks that `update_flight` prevents changing `Client_ID` or `Airline_ID` to non-existent ones.
* **`test_find_flights_multiple_criteria(...)`**: Tests `find_flights` with multiple search terms.
* **`test_flight_add_invalid_data(...)`**: Tests adding flights with fundamentally incomplete data.
* **`test_flight_id_uniqueness(...)`**: Adapted to verify that multiple distinct flight records can be added, as simple `flight_id`s are not generated for flights.
* **`test_flight_serialization(...)`**: Checks `to_dict` and `from_dict` for `FlightRecord`, noting the absence of a simple `flight_id`.

## II. UI Event Handling Tests (`events.py`)

These tests focus on functions within `src/gui/events.py`. Mocking is used to simulate the Tkinter application (`TravelApp`), UI widgets, and backend managers, allowing isolated testing of event handling logic.

### A. Mocking Strategy

* **`MockTkRoot`**: Simulates the main Tkinter window.
* **`MockTkWidget`**: A versatile mock for common Tkinter widgets (`Entry`, `StringVar`, `Label`, `Listbox`, `Spinbox`, `Combobox`-like `['values']` access).
* **`MockDateEntry`**: Mocks the `tkcalendar.DateEntry` widget.
* **`MockTravelApp`**: Simulates the main GUI application, holding mocked UI elements and backend managers.
* **`@mock.patch`**: Used to replace actual Tkinter dialogs (`messagebox`, `simpledialog`) with mocks for assertion and to prevent UI popups.

### B. Specific UI Event Tests

1.  **`test_load_records_clients(...)`**
    * **Objective**: Verifies `load_records` correctly populates the listbox with client data from the mocked `ClientManager`.
    * **Methodology**: Sets category to "Client", mocks `client_mgr.get_all_clients()`, calls `ui_events.load_records()`. Asserts manager call, listbox content, and no error dialogs.

2.  **`test_load_records_no_manager(...)`**
    * **Objective**: Checks `load_records` handling of an invalid category.
    * **Methodology**: Sets an invalid category, mocks `get_manager` to return `None`. Asserts an error dialog is shown and the listbox is cleared.

3.  **`test_clear_form_resets_fields_and_reloads(...)`**
    * **Objective**: Ensures `clear_form` clears input fields, resets selections, and triggers `load_records`.
    * **Methodology**: Populates mock fields, mocks `load_records`. Calls `ui_events.clear_form()`. Asserts fields are empty, selections reset, and `load_records` was called.

4.  **`test_add_client_record_success(...)`**
    * **Objective**: Tests successful client addition via `add_record`.
    * **Methodology**: Sets category to "Client", simulates form input. Mocks `client_mgr.add_client` to return a record. Mocks `clear_form`. Calls `ui_events.add_record()`. Asserts manager call with correct data, success dialog, and `clear_form` call.

5.  **`test_add_client_record_missing_required_field_ui(...)`**
    * **Objective**: Verifies `add_record` UI validation for missing required client fields.
    * **Methodology**: Sets category to "Client", simulates form input with a required field empty. Calls `ui_events.add_record()`. Asserts backend manager was not called and a warning dialog was shown.

6.  **`test_add_record_manager_failure(...)`**
    * **Objective**: Tests `add_record` UI behavior when the backend manager fails to add the record.
    * **Methodology**: Simulates valid form input. Mocks the relevant manager's `add_` method to return `None`. Calls `ui_events.add_record()`. Asserts an error dialog is shown and `clear_form` is not called.

7.  **`test_delete_record_no_selection(...)`**
    * **Objective**: Verifies `delete_record` behavior when no item is selected.
    * **Methodology**: Ensures `app.selected_index` is `None`. Calls `ui_events.delete_record()`. Asserts a warning dialog is shown and no manager delete method is called.

8.  **`test_delete_record_confirmation_no(...)`**
    * **Objective**: Tests the workflow where the user cancels the delete confirmation dialog.
    * **Methodology**: Simulates a selected record. Mocks `messagebox.askyesno` to return `False`. Calls `ui_events.delete_record()`. Asserts the confirmation was shown but the manager's delete method was not called.

9.  **`test_delete_record_manager_failure(...)`**
    * **Objective**: Checks UI response if the backend manager fails to delete a confirmed record.
    * **Methodology**: Simulates selection and "Yes" to confirmation. Mocks the manager's delete method to return `False`. Calls `ui_events.delete_record()`. Asserts an error dialog is shown and `clear_form` is not called.

10. **`test_update_record_no_selection(...)`**
    * **Objective**: Verifies `update_record` behavior when no item is selected.
    * **Methodology**: Ensures `app.selected_index` is `None`. Calls `ui_events.update_record()`. Asserts a warning dialog and no manager update call.

11. **`test_on_select_populates_form_client(...)`**
    * **Objective**: Ensures that when a "Client" record is selected in the listbox, the UI form fields are correctly populated with the client's data.
    * **Methodology**: Mocks a selected client record. Simulates listbox selection. Calls `ui_events.on_select()`. Asserts that the mock entry fields in the app now contain the corresponding data from the selected client.

12. **`test_on_select_populates_form_flight(...)`**
    * **Objective**: Verifies correct form population when a "Flight" record is selected, including specialized fields like dropdowns (Client, Airline) and date/time widgets.
    * **Methodology**: Mocks selected flight, client, and airline records. Mocks manager methods to return these records. Simulates listbox selection. Calls `ui_events.on_select()`. Asserts that client/airline dropdown variables, calendar date, hour/minute spinboxes, and start/end city entries are populated with the flight's data.

13. **`test_search_records_user_cancel(...)`**
    * **Objective**: Tests the `search_records` flow when the user cancels the search term input dialog.
    * **Methodology**: Mocks `simpledialog.askstring` to return `None`. Calls `ui_events.search_records()`. Asserts the dialog was shown but no search (manager calls) or "no results" messages occur.

14. **`test_search_records_no_results(...)`**
    * **Objective**: Checks behavior of `search_records` when a search term is entered but yields no matching records from the backend.
    * **Methodology**: Mocks `simpledialog.askstring` to return a search term. Mocks the relevant manager's `get_all_...` method to return records that won't match. Calls `ui_events.search_records()`. Asserts a "no results found" `showinfo` dialog is displayed and the listbox is refreshed with an empty list.

15. **`test_on_select_listbox_does_not_exist(...)`**
    * **Objective**: Tests the robustness of the `on_select` handler if the listbox UI element it tries to access does not exist (e.g., due to a UI setup issue).
    * **Methodology**: The mock listbox's `winfo_exists()` method is made to return `False`. `ui_events.on_select()` is called. The primary assertion is that the function does not raise an unhandled exception. It's also checked that no backend manager calls were made, as the function should exit early.

---