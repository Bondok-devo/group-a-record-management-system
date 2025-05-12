# src/main.py
"""
Main application file for the Travel Agent Record Management System.

This script serves as the entry point for the application. It initializes
the core components, such as data managers using settings from a
configuration file, and launches the Graphical User Interface (GUI).
"""

import sys
# import os # Removed as os is not used in the current version of this file
from datetime import datetime # Used in the demonstration function
import tkinter as tk
from gui.gui import TravelApp

# --- Path Setup ---
# This ensures that the 'src' directory is treated as a package root,
# allowing for imports like 'from record.client_manager import ClientManager'
# when running main.py from the project's root directory (e.g., GROUP-A/).
# Uncomment if you encounter import errors.
# current_dir = os.path.dirname(os.path.abspath(__file__)) # src/
# project_root = os.path.dirname(current_dir) # GROUP-A/
# if project_root not in sys.path:
#     sys.path.insert(0, project_root)

try:
    # Import the manager classes for each record type.
    from record.client_manager import ClientManager
    from record.airline_manager import AirlineManager
    from record.flight_manager import FlightManager
    # Import the configuration loader
    from conf import config_loader # Assumes __init__.py in src/conf/
except ImportError as import_error:
    print(f"Fatal Error: Could not import necessary modules: {import_error}")
    print("Troubleshooting tips:")
    print("- Ensure this script is run from the project's root directory (GROUP-A).")
    print("- Verify that __init__.py files exist in 'src/', 'src/record/', "
          "and 'src/conf/' directories.") # Line broken for length
    print("- Check your PYTHONPATH environment variable if issues persist.")
    sys.exit(1) # Exit if core components can't be loaded.

def initialize_managers(app_config):
    """
    Creates and returns instances of all data managers, using paths from config.

    Args:
        app_config (configparser.ConfigParser): The loaded application configuration.
    """
    print("Initializing data managers...")
    # Get specific file paths from the loaded configuration
    client_file = config_loader.get_client_data_file(app_config)
    airline_file = config_loader.get_airline_data_file(app_config)
    flight_file = config_loader.get_flight_data_file(app_config)

    print(f"Using Client data file: '{client_file}'")
    print(f"Using Airline data file: '{airline_file}'")
    print(f"Using Flight data file: '{flight_file}'")

    # Pass the specific file paths to the managers
    client_mgr = ClientManager(clients_file_path=client_file)
    airline_mgr = AirlineManager(airlines_file_path=airline_file)
    # FlightManager needs the other managers for validation
    flight_mgr = FlightManager(
        flights_file_path=flight_file,
        client_manager=client_mgr,
        airline_manager=airline_mgr
    )
    print("Data managers initialized successfully.")
    return client_mgr, airline_mgr, flight_mgr


def run_gui_application(client_mgr, airline_mgr, flight_mgr):
    """
    Initializes and runs the Graphical User Interface.

    This function sets up the main application window and starts the
    GUI event loop. The managers are passed to the GUI to enable data interaction.

    print("\n--- GUI Application (Placeholder) ---")
    print("The graphical user interface would start here, using the managers.")
    print(f"Current client records: {len(client_mgr.get_all_clients())}")
    print(f"Current airline records: {len(airline_mgr.get_all_airlines())}")
    print(f"Current flight records: {len(flight_mgr.get_all_flights())}")
    """
    root = tk.Tk()
    app = TravelApp(root, client_mgr, airline_mgr, flight_mgr)  # Pass managers here
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
    """
    print("--- End of GUI Placeholder ---")    
    """


def demonstrate_manager_interactions(client_mgr, airline_mgr, flight_mgr):
    """
    Performs basic operations using the data managers for demonstration.

    This function interacts with the managers initialized with paths from
    config.ini, affecting the actual data files specified there.
    Includes cleanup of created test data. Use only for testing/demo purposes.
    """
    print("\n--- Demonstrating Manager Interactions (using configured paths) ---")

    # --- Client Operations Demonstration ---
    print("\n* Client Operations Demo *")
    initial_clients_count = len(client_mgr.get_all_clients())
    demo_client_data = {
        "name": "Config Demo User", "address_line_1": "789 Config Ave",
        "city": "Settingsville", "state": "CF", "zip_code": "30303",
        "country": "ConfigLand", "phone_number": "555-CONF"
    }
    added_demo_client = client_mgr.add_client(demo_client_data)
    if added_demo_client:
        print(f"Added Client: {added_demo_client.name} "
              f"(ID: {added_demo_client.client_id})")
    current_clients_count = len(client_mgr.get_all_clients())
    print(f"Total clients: {current_clients_count}")
    # Clean up the added demo client
    if current_clients_count > initial_clients_count and added_demo_client:
        client_mgr.delete_client(added_demo_client.client_id)
        print(f"Cleaned up demo client: {added_demo_client.name}")

    # --- Airline Operations Demonstration ---
    print("\n* Airline Operations Demo *")
    initial_airlines_count = len(airline_mgr.get_all_airlines())
    demo_airline_data = {"record_type": "Airline", "company_name": "Config Airways"}
    added_demo_airline = airline_mgr.add_airline(demo_airline_data)
    if added_demo_airline:
        print(f"Added Airline: {added_demo_airline.company_name} "
              f"(ID: {added_demo_airline.airline_id})")
    current_airlines_count = len(airline_mgr.get_all_airlines())
    print(f"Total airlines: {current_airlines_count}")
    # Clean up the added demo airline
    if current_airlines_count > initial_airlines_count and added_demo_airline:
        airline_mgr.delete_airline(added_demo_airline.airline_id)
        print(f"Cleaned up demo airline: {added_demo_airline.company_name}")

    # --- Flight Operations Demonstration ---
    print("\n* Flight Operations Demo *")
    # Flights require existing client and airline IDs. Create temporary ones for this demo.
    temp_client_for_flight = client_mgr.add_client({
        "name": "Temp ConfigFlight Client", "address_line_1": "N/A", "city": "N/A",
        "state": "N/A", "zip_code": "N/A", "country": "N/A", "phone_number": "N/A"
    })
    temp_airline_for_flight = airline_mgr.add_airline({
        "record_type": "Airline", "company_name": "Temp ConfigFlight Air"
    })

    initial_flights_count = len(flight_mgr.get_all_flights())
    added_demo_flight = None

    if temp_client_for_flight and temp_airline_for_flight:
        print(f"Using Temp Client ID: {temp_client_for_flight.client_id}, "
              f"Temp Airline ID: {temp_airline_for_flight.airline_id}")
        current_time = datetime.now()
        demo_flight_data = {
            "record_type": "Flight", "Client_ID": temp_client_for_flight.client_id,
            "Airline_ID": temp_airline_for_flight.airline_id,
            "Date": datetime(
                current_time.year, current_time.month, current_time.day, 14, 0
            ).isoformat(),
            "Start City": "Config Origin", "End City": "Config Destination"
        }
        added_demo_flight = flight_mgr.add_flight(demo_flight_data)
        if added_demo_flight:
            print(f"Added Flight: For Client {added_demo_flight.client_id} "
                  f"with Airline {added_demo_flight.airline_id}")
    else:
        print("Could not create temporary client/airline for flight demo.")

    current_flights_count = len(flight_mgr.get_all_flights())
    print(f"Total flights: {current_flights_count}")

    # Clean up the added demo flight
    if current_flights_count > initial_flights_count and added_demo_flight:
        # delete_flight requires the identifying details dictionary
        flight_mgr.delete_flight(added_demo_flight.to_dict())
        print("Cleaned up demo flight.")

    # Clean up temporary client and airline used for the flight demo
    if temp_client_for_flight:
        client_mgr.delete_client(temp_client_for_flight.client_id)
        print(f"Cleaned up temporary client: {temp_client_for_flight.name}")
    if temp_airline_for_flight:
        airline_mgr.delete_airline(temp_airline_for_flight.airline_id)
        print(f"Cleaned up temporary airline: {temp_airline_for_flight.company_name}")

    print("--- End of Manager Interactions Demo ---")


def main():
    """
    Main function to initialize and start the application.
    """
    print("Starting Travel Agent Record Management System...")

    # Load application configuration from src/conf/config.ini
    app_config = config_loader.load_configuration()
    if not app_config.sections():
        print("Critical: Configuration could not be loaded or is empty. "
              "Application may not function correctly or use default paths.")
        # Consider exiting if config is essential: sys.exit(1)

    # Initialize all the data managers using the loaded configuration
    client_mgr, airline_mgr, flight_mgr = initialize_managers(app_config)

    # Uncomment the line below to run the demonstration of manager interactions.
    # Note: This affects the actual data files specified in config.ini.
    # demonstrate_manager_interactions(client_mgr, airline_mgr, flight_mgr)

    # Launch the Graphical User Interface (currently a placeholder).
    run_gui_application(client_mgr, airline_mgr, flight_mgr)

    print("\nTravel Agent Record Management System finished.")
    # Note on data saving: The current managers save data immediately on
    # add/update/delete operations. A final save on close is not currently
    # implemented here but could be added if the saving strategy changes.

if __name__ == "__main__":
    # Ensures main() is called only when this script is executed directly.
    main()
