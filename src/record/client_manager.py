# src/record/client_manager.py
"""
Manages client records, including loading, saving, and CRUD operations.
This module provides the ClientManager class to handle all aspects of
client data persistence and manipulation.
"""

import json
import os
from typing import List, Dict, Optional, Any

# client_record.py (with ClientRecord class) is in the same package.
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
            # If the file doesn't exist, that's okay for loading;
            # it will be created when/if _save_clients is called.
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
                            client = ClientRecord.from_dict(data)
                            self._clients.append(client)
                            if client.client_id and client.client_id > highest_id_found:
                                highest_id_found = client.client_id
                    except json.JSONDecodeError:
                        print(f"Warning: Invalid JSON on line {line_number} in "
                              f"'{self.clients_file_path}'. Skipping.")
                    except ValueError as e:
                        print(f"Warning: Invalid data for record on line {line_number} "
                              f"in '{self.clients_file_path}': {e}. Skipping.")
                    except TypeError as e:
                        print(f"Warning: Type error for record on line {line_number} "
                              f"in '{self.clients_file_path}': {e}. Skipping.")
        except IOError as e:
            print(f"Warning: Could not read '{self.clients_file_path}': {e}. "
                  "Starting with no clients.")
        except Exception as e:
            # This broad exception is a last resort to prevent crashing during load.
            print(f"An unexpected error occurred loading clients: {e}")

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
            # Ensure the directory for the specific data file exists
            file_directory = os.path.dirname(self.clients_file_path)
            if file_directory: # Check if there's a directory part (not just filename)
                os.makedirs(file_directory, exist_ok=True)

            with open(self.clients_file_path, 'w', encoding='utf-8') as file:
                for client_item in self._clients:
                    client_dict = client_item.to_dict()
                    client_dict['record_type'] = "Client"
                    json.dump(client_dict, file)
                    file.write('\n')
            return True
        except IOError as e:
            print(f"Error: Could not write to '{self.clients_file_path}': {e}. "
                  "Changes may not be saved.")
            return False
        except Exception as e:
            # This broad exception is a last resort for saving errors.
            print(f"An unexpected error occurred while saving clients: {e}")
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
            # Rollback if save failed
            self._clients.pop()
            self._next_id -= 1
            print("Error: Failed to save after adding client. Client not added.")
            return None
        except ValueError as e:
            print(f"Error: Could not add client. Invalid data: {e}")
            self._next_id -= 1 # Rollback ID
            return None
        except Exception as e:
            # This broad exception is a last resort for add operation errors.
            print(f"An unexpected error occurred while adding client: {e}")
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
        return self._clients[:] # Return a shallow copy

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
            return client_to_update # No changes made

        try:
            updated_client_obj = ClientRecord.from_dict(current_data)
            self._clients[client_index] = updated_client_obj
            if self._save_clients():
                return updated_client_obj
            # Rollback if save failed
            self._clients[client_index] = ClientRecord.from_dict(original_data_backup)
            print(f"Error: Failed to save updates for client ID {client_id}. "
                  "Changes rolled back.")
            return None
        except ValueError as e:
            print(f"Error: Could not update client ID {client_id}. "
                  f"Invalid data after update: {e}")
            return None
        except Exception as e:
            # This broad exception is a last resort for update operation errors.
            print(f"An unexpected error occurred while updating client {client_id}: {e}")
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
            return False # Client not found

        self._clients.pop(client_index)
        if self._save_clients():
            return True
        # Rollback if save failed
        self._clients.insert(client_index, client_to_delete)
        print(f"Error: Failed to save after deleting client ID {client_id}. "
              "Deletion rolled back.")
        return False

# This section is for direct testing of the ClientManager.
if __name__ == "__main__":
    print("--- ClientManager Direct Test ---")

    # Determine the project root directory (GROUP-A) to correctly place temp_test_output
    # This assumes client_manager.py is in src/record/
    current_script_path = os.path.abspath(__file__)
    # Expected structure: .../GROUP-A/src/record/client_manager.py
    # record_dir is .../GROUP-A/src/record/
    record_dir = os.path.dirname(current_script_path)
    # src_dir is .../GROUP-A/src/
    src_dir = os.path.dirname(record_dir)
    # project_root is .../GROUP-A/
    project_root = os.path.dirname(src_dir)

    # Define the path for test data, ensuring it's outside src/
    TEST_DATA_SUBDIR_NAME = "client_manager_test_data"
    TEMP_TEST_OUTPUT_ROOT_DIR_NAME = "temp_test_output" # This folder should be in .gitignore

    # Construct the full path for the temporary test data directory
    test_data_specific_folder = os.path.join(project_root,
                                             TEMP_TEST_OUTPUT_ROOT_DIR_NAME,
                                             TEST_DATA_SUBDIR_NAME)
    # The actual test data file name
    TEST_DATA_FILE_NAME = "client_record.jsonl" # Renamed to UPPER_CASE
    test_file_full_path = os.path.join(test_data_specific_folder, TEST_DATA_FILE_NAME)


    if not os.path.exists(test_data_specific_folder):
        os.makedirs(test_data_specific_folder, exist_ok=True)
        print(f"Created test data directory: {test_data_specific_folder}")

    print("Test block assumes 'from .client_record import ClientRecord' at the top is working.")

    # Initialize manager with the specific test file path
    manager = ClientManager(clients_file_path=test_file_full_path)
    print(f"Test data file will be: {manager.clients_file_path}")

    if os.path.exists(manager.clients_file_path):
        os.remove(manager.clients_file_path)
        print(f"Cleared old test file: {manager.clients_file_path}")
    # Re-instantiate manager to ensure it loads from the (now empty) test file
    # and resets its internal state like _next_id.
    manager = ClientManager(clients_file_path=test_file_full_path)

    print(f"\nInitial clients loaded: {len(manager.get_all_clients())}")

    print("\n1. Adding new clients...")
    client1_data = {
        "name": "Dave Lister", "address_line_1": "JMC Red Dwarf",
        "city": "Deep Space", "state": "N/A", "zip_code": "00000",
        "country": "Jupiter Mining Corporation", "phone_number": "555-RDWARF",
        "address_line_2": "Sleeping Quarters"
    }
    client2_data = {
        "name": "Arnold Rimmer", "address_line_1": "Hologram Suite",
        "city": "Red Dwarf", "state": "N/A", "zip_code": "00001",
        "country": "Jupiter Mining Corporation", "phone_number": "555-SMEGHEAD",
        "address_line_3": "Light Bee Powered"
    }

    dave = manager.add_client(client1_data)
    arnold = manager.add_client(client2_data)

    if dave:
        print(f"Added: {dave.name} with ID {dave.client_id}")
    if arnold:
        print(f"Added: {arnold.name} with ID {arnold.client_id}")

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

    print("\nFinal list of clients:")
    for c_obj_final_loop_var in manager.get_all_clients():
        print(f"  {c_obj_final_loop_var}")

    print(f"\nTotal clients at end: {len(manager.get_all_clients())}")
    print(f"Check the file: {manager.clients_file_path}")
    # To properly clean up, you might want to delete the TEST_DATA_ROOT_TEMP_DIR folder
    # import shutil
    # if os.path.exists(TEST_DATA_ROOT_TEMP_DIR):
    #     shutil.rmtree(TEST_DATA_ROOT_TEMP_DIR)
    #     print(f"Cleaned up test directory: {TEST_DATA_ROOT_TEMP_DIR}")
