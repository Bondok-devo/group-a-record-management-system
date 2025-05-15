# src/record/client_manager.py
"""
Manages client records, including loading, saving, and CRUD operations.
This module provides the ClientManager class to handle all aspects of
client data persistence and manipulation.
"""

import json
import os
from typing import List, Dict, Optional, Any

# Assumes client_record.py (with ClientRecord class) is in the same package.
# An empty __init__.py in 'src/record/' makes 'record' a package.
from .client_record import ClientRecord


class ClientManager:
    """
    Handles all operations related to client records.

    This class loads client data from a JSONL file, allows for
    Create, Read, Update, and Delete (CRUD) operations, and saves
    changes back to the file.
    """

    def __init__(self, clients_file_path: str):
        """
        Initializes the ClientManager.

        Loads existing client data from the specified file path.

        Args:
            clients_file_path (str): The full path to the client data file
                                     (e.g., 'src/data/client_record.jsonl').
        """
        if not clients_file_path:
            raise ValueError("ClientManager requires a valid clients_file_path.")

        self.clients_file_path = clients_file_path
        self._clients: List[ClientRecord] = []
        self._next_id: int = 1  # Used for generating unique client IDs.
        self._load_clients()

    def _load_clients(self) -> None:
        """
        Loads client records from the JSONL file into memory.

        Reads each line, expecting a JSON object representing a client.
        Updates the internal list of clients and determines the next
        available ID for new clients.
        """
        self._clients = []
        if not os.path.exists(self.clients_file_path):
            return

        highest_id_found = 0
        try:
            with open(self.clients_file_path, 'r', encoding='utf-8') as file:
                for line_number, line in enumerate(file, 1):
                    line_content = line.strip()
                    if not line_content:
                        continue

                    try:
                        data = json.loads(line_content)
                        if data.get("record_type") == "Client":
                            client_obj = ClientRecord.from_dict(data)
                            self._clients.append(client_obj)
                            if client_obj.client_id and client_obj.client_id > highest_id_found:
                                highest_id_found = client_obj.client_id
                    except json.JSONDecodeError:
                        print(f"Warning: Invalid JSON on line {line_number} in "
                              f"'{self.clients_file_path}'. Skipping.")
                    except ValueError as e:
                        print(f"Warning: Invalid data for record on line {line_number} "
                              f"in '{self.clients_file_path}': {e}. Skipping.")
                    except TypeError as e: # Catching TypeError specifically
                        print(f"Warning: Type error for record on line {line_number} "
                              f"in '{self.clients_file_path}': {e}. Skipping.")
        except OSError as e: # Catches IOError, FileNotFoundError, PermissionError etc.
            print(f"OS error occurred loading '{self.clients_file_path}' "
                  f"({type(e).__name__}): {e}. Starting with no clients.")
        except Exception as e: # General fallback for truly unexpected errors during load
            print(f"An unexpected error occurred loading clients ({type(e).__name__}): {e}")

        self._next_id = highest_id_found + 1

    def _save_clients(self) -> bool:
        """
        Saves the current list of clients to the JSONL file.

        Each client is written as a JSON object on a new line, overwriting
        the existing file content. Ensures the directory for the file exists.

        Returns:
            True if saving was successful, False otherwise.
        """
        try:
            file_directory = os.path.dirname(self.clients_file_path)
            if file_directory:
                os.makedirs(file_directory, exist_ok=True)

            with open(self.clients_file_path, 'w', encoding='utf-8') as file:
                for client_item in self._clients:
                    client_dict = client_item.to_dict()
                    client_dict['record_type'] = "Client"
                    json.dump(client_dict, file)
                    file.write('\n')
            return True
        except OSError as e: # Catches IOError, PermissionError etc.
            print(f"OS error occurred while saving to '{self.clients_file_path}' "
                  f"({type(e).__name__}): {e}. Changes may not be saved.")
            return False
        except Exception as e: # General fallback for truly unexpected errors during save
            print(f"An unexpected error occurred while saving clients ({type(e).__name__}): {e}")
            return False

    def _generate_id(self) -> int:
        """Generates a new, unique ID for a client."""
        new_id = self._next_id
        self._next_id += 1
        return new_id

    def add_client(self, client_data: Dict[str, Any]) -> Optional[ClientRecord]:
        """
        Adds a new client to the system.

        A unique ID is generated, and 'record_type' is set to "Client".

        Args:
            client_data: Dictionary of client information.

        Returns:
            The created ClientRecord object if successful, else None.
        """
        new_id = self._generate_id()
        data_for_record = client_data.copy()
        data_for_record['client_id'] = new_id
        data_for_record['record_type'] = "Client"

        try:
            new_client = ClientRecord.from_dict(data_for_record)
            self._clients.append(new_client)
            if self._save_clients():
                return new_client
            self._clients.pop()
            self._next_id -= 1 # Rollback ID increment if save failed
            print("Error: Failed to save after adding client. Client not added.")
            return None
        except ValueError as e:
            print(f"Error: Could not add client. Invalid data: {e}")
            self._next_id -= 1
            return None
        except TypeError as e:
            print(f"Error: Could not add client due to type issue: {e}")
            self._next_id -= 1
            return None
        except OSError as e: # Specific exception for save issues if not caught by _save_clients
            print(f"Error: OS error during add client operation ({type(e).__name__}): {e}")
            self._next_id -= 1
            return None
        except Exception as e: # General fallback for truly unexpected errors
            print(f"An unexpected error occurred while adding client ({type(e).__name__}): {e}")
            self._next_id -= 1
            return None


    def get_client_by_id(self, client_id: int) -> Optional[ClientRecord]:
        """
        Retrieves a client by their unique ID.

        Args:
            client_id: The integer ID of the client.

        Returns:
            The ClientRecord object if found, otherwise None.
        """
        if not isinstance(client_id, int):
            return None
        for client_item in self._clients:
            if client_item.client_id == client_id:
                return client_item
        return None

    def get_all_clients(self) -> List[ClientRecord]:
        """
        Returns a list of all client records.

        Returns:
            A list of ClientRecord objects (a copy of the internal list).
        """
        return self._clients[:]

    def find_clients(self, criteria: Dict[str, Any]) -> List[ClientRecord]:
        """
        Finds clients matching all provided criteria.

        For string fields, performs a case-insensitive "contains" search.
        For other fields (like 'client_id'), performs an exact match.

        Args:
            criteria: A dictionary where keys are attribute names of ClientRecord
                      (e.g., "name", "city", "client_id") and values are the
                      search terms.

        Returns:
            A list of ClientRecord objects that match all criteria.
            Returns an empty list if no matches are found.
        """
        if not criteria:
            return self.get_all_clients()

        results: List[ClientRecord] = []
        for client_record in self._clients:
            match_all_criteria = True
            for key, search_value in criteria.items():
                if not hasattr(client_record, key):
                    match_all_criteria = False
                    break

                client_value = getattr(client_record, key)

                if search_value is None:
                    if client_value is not None:
                        match_all_criteria = False
                        break
                    continue

                if client_value is None:
                    match_all_criteria = False
                    break

                if isinstance(client_value, str) and isinstance(search_value, str):
                    if search_value.lower() not in client_value.lower():
                        match_all_criteria = False
                        break
                elif not isinstance(client_value, str):
                    try:
                        typed_search_value = type(client_value)(search_value)
                        if client_value != typed_search_value:
                            match_all_criteria = False
                            break
                    except (ValueError, TypeError):
                        match_all_criteria = False
                        break
                elif isinstance(client_value, str) and not isinstance(search_value, str):
                    match_all_criteria = False
                    break
            if match_all_criteria:
                results.append(client_record)
        return results

    search = find_clients

    def update_client(self, client_id: int,
                      update_info: Dict[str, Any]) -> Optional[ClientRecord]:
        """
        Updates an existing client's information.

        'client_id' and 'record_type' in update_info will be ignored.

        Args:
            client_id: The ID of the client to update.
            update_info: Dictionary with fields to update.

        Returns:
            The updated ClientRecord object if successful, else None.
        """
        client_to_update = None
        client_index = -1
        for i, c_item_loop1 in enumerate(self._clients):
            if c_item_loop1.client_id == client_id:
                client_to_update = c_item_loop1
                client_index = i
                break

        if not client_to_update:
            print(f"Info: No client found with ID {client_id} to update.")
            return None

        current_data = client_to_update.to_dict()
        original_data_backup = current_data.copy()
        changed_fields = False

        for key, value in update_info.items():
            if key in current_data and key not in ["client_id", "record_type"]:
                if current_data[key] != value:
                    current_data[key] = value
                    changed_fields = True

        if not changed_fields:
            return client_to_update

        try:
            updated_client_obj = ClientRecord.from_dict(current_data)
            self._clients[client_index] = updated_client_obj
            if self._save_clients():
                return updated_client_obj
            self._clients[client_index] = ClientRecord.from_dict(original_data_backup)
            print(f"Error: Failed to save updates for client ID {client_id}. "
                  "Changes rolled back.")
            return None
        except ValueError as e:
            print(f"Error: Could not update client ID {client_id}. "
                  f"Invalid data after update: {e}")
            return None
        except TypeError as e:
            print(f"Error: Could not update client ID {client_id} due to type issue: {e}")
            return None
        except OSError as e: # Specific exception for save/OS issues
            print(f"Error: OS error during update client operation for ID {client_id} "
                  f"({type(e).__name__}): {e}")
            self._clients[client_index] = ClientRecord.from_dict(original_data_backup)
            return None
        except Exception as e: # General fallback
            error_msg = (f"An unexpected error occurred while updating client "
                         f"{client_id} ({type(e).__name__}): {e}")
            print(error_msg)
            self._clients[client_index] = ClientRecord.from_dict(original_data_backup)
            return None


    def delete_client(self, client_id: int) -> bool:
        """
        Removes a client from the system.

        Args:
            client_id: The ID of the client to delete.

        Returns:
            True if deletion was successful (including save), False otherwise.
        """
        client_to_delete = None
        client_index = -1
        for i, c_item_loop2 in enumerate(self._clients):
            if c_item_loop2.client_id == client_id:
                client_to_delete = c_item_loop2
                client_index = i
                break

        if not client_to_delete:
            return False

        self._clients.pop(client_index)
        if self._save_clients():
            return True
        self._clients.insert(client_index, client_to_delete)
        print(f"Error: Failed to save after deleting client ID {client_id}. "
              "Deletion rolled back.")
        return False

# This section is for direct testing of the ClientManager.
if __name__ == "__main__":
    print("--- ClientManager Direct Test ---")

    current_script_path = os.path.abspath(__file__)
    record_dir = os.path.dirname(current_script_path)
    src_dir = os.path.dirname(record_dir)
    project_root = os.path.dirname(src_dir)

    TEST_DATA_SUBDIR_NAME = "client_manager_test_data"
    TEMP_TEST_OUTPUT_ROOT_DIR_NAME = "temp_test_output"

    test_data_specific_folder = os.path.join(project_root,
                                             TEMP_TEST_OUTPUT_ROOT_DIR_NAME,
                                             TEST_DATA_SUBDIR_NAME)
    TEST_DATA_FILE_NAME = "client_record.jsonl"
    test_file_full_path = os.path.join(test_data_specific_folder, TEST_DATA_FILE_NAME)

    if not os.path.exists(test_data_specific_folder):
        os.makedirs(test_data_specific_folder, exist_ok=True)
        print(f"Created test data directory: {test_data_specific_folder}")

    print("Test block assumes 'from .client_record import ClientRecord' at the top is working.")

    manager = ClientManager(clients_file_path=test_file_full_path)
    print(f"Test data file will be: {manager.clients_file_path}")

    if os.path.exists(manager.clients_file_path):
        os.remove(manager.clients_file_path)
        print(f"Cleared old test file: {manager.clients_file_path}")
    manager = ClientManager(clients_file_path=test_file_full_path)


    print(f"\nInitial clients loaded: {len(manager.get_all_clients())}")

    print("\n1. Adding new clients...")
    client1_data = {
        "name": "Dave Lister", "address_line_1": "JMC Red Dwarf, Bunk 3",
        "city": "Deep Space", "state": "N/A", "zip_code": "00000",
        "country": "Jupiter Mining Corp", "phone_number": "555-RDWARF",
        "address_line_2": "Sleeping Quarters"
    }
    client2_data = {
        "name": "Arnold Rimmer", "address_line_1": "Hologram Suite 7",
        "city": "Red Dwarf", "state": "N/A", "zip_code": "00001",
        "country": "Jupiter Mining Corp", "phone_number": "555-SMEGHEAD",
        "address_line_3": "Light Bee Powered"
    }
    client3_data = {
        "name": "Kristine Kochanski", "address_line_1": "Officer Quarters",
        "city": "Red Dwarf", "state": "N/A", "zip_code": "00002",
        "country": "Jupiter Mining Corp", "phone_number": "555-NAVIGATION"
    }


    dave = manager.add_client(client1_data)
    arnold = manager.add_client(client2_data)
    kristine = manager.add_client(client3_data)

    if dave:
        print(f"Added: {dave.name} with ID {dave.client_id}")
    if arnold:
        print(f"Added: {arnold.name} with ID {arnold.client_id}")
    if kristine:
        print(f"Added: {kristine.name} with ID {kristine.client_id}")


    print(f"\nTotal clients now: {len(manager.get_all_clients())}")

    print("\n2. Getting a client by ID...")
    if dave:
        retrieved_dave = manager.get_client_by_id(dave.client_id)
        if retrieved_dave:
            PHONE_NUM_DAVE = getattr(retrieved_dave, 'phone_number', 'N/A')
            print(f"Found: {retrieved_dave.name}, Phone: {PHONE_NUM_DAVE}")

    print("\n3. Updating a client...")
    if arnold:
        update_payload = {"phone_number": "555-ACE", "city": "Io (Hologram Projection)"}
        updated_arnold = manager.update_client(arnold.client_id, update_payload)
        if updated_arnold:
            PHONE_NUM_ARNOLD = getattr(updated_arnold, 'phone_number', 'N/A')
            CITY_NAME_ARNOLD = getattr(updated_arnold, 'city', 'N/A')
            print(f"Updated Arnold: Name - {updated_arnold.name}, New Phone - {PHONE_NUM_ARNOLD}, "
                  f"City - {CITY_NAME_ARNOLD}")
        else:
            print(f"Failed to update Arnold (ID: {arnold.client_id})")

    print("\n4. Listing all clients again:")
    for c_obj_loop_var1 in manager.get_all_clients():
        PHONE_NUM_LOOP = getattr(c_obj_loop_var1, 'phone_number', 'N/A')
        CITY_NAME_LOOP = getattr(c_obj_loop_var1, 'city', 'N/A')
        print(f"  ID: {c_obj_loop_var1.client_id}, Name: {c_obj_loop_var1.name}, "
              f"Phone: {PHONE_NUM_LOOP}, City: {CITY_NAME_LOOP}")

    print("\n5. Deleting a client...")
    DELETED_CLIENT_FLAG = False
    if dave:
        DELETED_CLIENT_FLAG = manager.delete_client(dave.client_id)
        print(f"Dave (ID: {dave.client_id}) deleted: {DELETED_CLIENT_FLAG}")

    print("\n6. Searching clients (New Tests)...")
    print("\n  Searching for name containing 'rimm' (case-insensitive):")
    rimmer_search_alias = manager.search({"name": "rimm"})
    for found_client_obj in rimmer_search_alias:
        print(f"    Found via alias: {found_client_obj.name} (ID: {found_client_obj.client_id})")


    print("\n  Searching for country 'Jupiter Mining Corp' and city 'Red Dwarf':")
    red_dwarf_search = manager.find_clients(
        {"country": "Jupiter Mining Corp", "city": "Red Dwarf"}
    )
    for found_client_obj_2 in red_dwarf_search:
        print(f"    Found: {found_client_obj_2.name}, City: {found_client_obj_2.city}, "
              f"Country: {found_client_obj_2.country}")

    print("\n  Searching for non-existent name 'Zaphod':")
    zaphod_search = manager.find_clients({"name": "Zaphod"})
    if not zaphod_search:
        print("    Correctly found no clients named 'Zaphod'.")

    print("\n  Searching by client_id=2 (exact match):")
    # Renamed 'test_id_to_search_for' to 'TEST_ID_TO_SEARCH_FOR' to conform to C0103
    TEST_ID_TO_SEARCH_FOR = 2
    id_search_results = []
    if arnold and arnold.client_id == 2:
        id_search_results = manager.find_clients({"client_id": 2})
    elif kristine and kristine.client_id == 2:
        id_search_results = manager.find_clients({"client_id": 2})
        TEST_ID_TO_SEARCH_FOR = kristine.client_id # Update if Kristine is ID 2
    else:
        client_with_id_2 = manager.get_client_by_id(2)
        if client_with_id_2:
            print(f"    Note: Client with ID 2 is actually {client_with_id_2.name}")
            id_search_results = [client_with_id_2]
        else:
            print("    Note: No client currently has ID 2 for exact match test.")


    if id_search_results:
        for found_client_obj_3 in id_search_results:
            print(f"    Found by ID ({TEST_ID_TO_SEARCH_FOR}): {found_client_obj_3.name}")
    else:
        print(f"    No client found with ID {TEST_ID_TO_SEARCH_FOR} for exact match test.")


    print("\nFinal list of clients:")
    for c_obj_final_loop_var in manager.get_all_clients():
        print(f"  {c_obj_final_loop_var}")

    print(f"\nTotal clients at end: {len(manager.get_all_clients())}")
    print(f"Check the file: {manager.clients_file_path}")
