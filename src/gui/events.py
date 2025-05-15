"""
Event handling functions for the Travel Records Management GUI.

This module manages CRUD operations and GUI listbox updates
based on the selected record category: Client, Airline, or Flight.
"""
import tkinter as tk
from tkinter import ttk, messagebox # ttk used for consistency in update_fields
# These imports are present in your file but not directly used by the functions
# as manager instances are accessed via the 'app' object.
# from record.client_manager import ClientManager
# from record.airline_manager import AirlineManager
# from record.flight_manager import FlightManager


def get_manager(category, app):
    """
    Retrieve the appropriate manager instance based on the selected category.

    Args:
        category (str): The selected category ('Client', 'Airline', or 'Flight').
        app: The main application instance containing manager references.

    Returns:
        object: The manager instance corresponding to the selected category.
    """
    managers = {
        "Client": app.client_mgr,
        "Airline": app.airline_mgr,
        "Flight": app.flight_mgr,
    }
    return managers.get(category)

def load_records(app):
    """
    Load all records into the GUI listbox for the selected category.
    This populates app.filtered_records.

    Args:
        app: The main application instance (TravelApp).
    """
    category = app.selected_category.get()
    manager = get_manager(category, app)

    if not manager:
        messagebox.showerror("Error", f"No manager found for category: {category}")
        app.filtered_records = []
        refresh_listbox(app) # Attempt to refresh even if manager is missing (to clear listbox)
        return

    try:
        if category == "Client":
            # Assumes client_mgr has get_all_clients() returning List[ClientRecord]
            app.filtered_records = manager.get_all_clients()
        elif category == "Airline":
            # Assumes airline_mgr has a similar get_all_airlines() method
            if hasattr(manager, "get_all_airlines"):
                app.filtered_records = manager.get_all_airlines()
            elif hasattr(manager, "get_all"): # Fallback
                app.filtered_records = manager.get_all()
            else:
                raise AttributeError(
                    "Manager for Airline missing get_all_airlines() or get_all()"
                )
        elif category == "Flight":
            # Assumes flight_mgr has a similar get_all_flights() method
            if hasattr(manager, "get_all_flights"):
                app.filtered_records = manager.get_all_flights()
            elif hasattr(manager, "get_all"): # Fallback
                app.filtered_records = manager.get_all()
            else:
                raise AttributeError(
                    "Manager for Flight missing get_all_flights() or get_all()"
                )
        else:
            app.filtered_records = []

        if app.filtered_records is None: # Ensure it's always a list
            app.filtered_records = []

    except AttributeError as ae:
        messagebox.showerror("Load Error",
                             f"Manager for {category} missing 'get_all' method: {ae}")
        app.filtered_records = []
    except (IOError, ValueError) as e: # More specific exceptions
        messagebox.showerror("Load Error", f"Failed to load {category.lower()} records: {e}")
        app.filtered_records = []
    except tk.TclError as e: # Catch Tcl errors specifically if they might occur during load
        messagebox.showerror("GUI Error During Load",
                             f"A GUI-related error occurred while loading: {e}")
        app.filtered_records = []
    except Exception as e: # General fallback for truly unexpected errors
        # Consider logging this e for debugging purposes
        messagebox.showerror("Unexpected Load Error",
                             f"An unexpected error occurred ({type(e).__name__}): {e}")
        app.filtered_records = []


    refresh_listbox(app)
    # It's safer to reset selected_index only if record_listbox exists and was populated
    if hasattr(app, 'record_listbox') and app.record_listbox:
        app.selected_index = None # Reset selection

def update_fields(app):
    """
    Update the form fields in the GUI based on the selected category.

    This method clears the form and dynamically creates label-entry pairs using the
    display names from fields_config. It also stores the corresponding internal field
    keys in app.field_names for consistent record creation.

    Args:
        app: The main application instance containing field configuration and widgets.
    """
    for widget in app.form_frame.winfo_children():
        widget.destroy()
    app.entries.clear()
    category = app.selected_category.get()
    config = app.fields_config.get(category, {}) # Use .get for safety

    app.field_names = list(config.values()) # These are internal attribute names

    for i, (label_text, _field_key_internal_use_only) in enumerate(config.items()):
        # Using ttk.Label and ttk.Entry for a more modern look,
        # consistent with your gui.py's ttk usage
        label = ttk.Label(app.form_frame, text=f"{label_text}:")
        label.grid(row=i, column=0, sticky="e", padx=5, pady=2)
        entry = ttk.Entry(app.form_frame, width=40) # ttk.Entry
        entry.grid(row=i, column=1, padx=5, pady=2, sticky="we")
        app.entries.append(entry)

    # When category changes, load all records for that category and clear form
    load_records(app)
    # clear_form calls load_records again.
    # The call to events.update_fields(self) in gui.py's setup_widgets
    # happens BEFORE self.record_listbox is created. This load_records call
    # will hit the workaround in refresh_listbox.
    # The subsequent events.load_records(self) in gui.py's __init__ (after setup_widgets)
    # should then correctly populate the listbox.

def on_select(app, _event=None): # Added _event as listbox bindings often pass it
    """
    Handle the selection of a record in the listbox and populate the form fields.
    Correctly handles ClientRecord objects.

    Args:
        app: The main application instance containing the listbox and form data.
        _event: The event object passed by the listbox selection binding (unused).
    """
    # Defensive check for record_listbox existence
    if not hasattr(app, 'record_listbox') or not app.record_listbox:
        return # Silently exit if listbox isn't ready

    try:
        selected_indices = app.record_listbox.curselection()
        if not selected_indices:
            app.selected_index = None
            return

        index = selected_indices[0]
        app.selected_index = index

        if hasattr(app, 'filtered_records') and 0 <= index < len(app.filtered_records):
            selected_record_obj = app.filtered_records[index]

            # app.field_names contains internal attribute names like 'name', 'address_line_1'
            # app.entries contains the tk.Entry widgets in the same order
            for i, field_attr_name in enumerate(app.field_names):
                if i < len(app.entries):
                    app.entries[i].delete(0, tk.END)
                    value_to_display = ""
                    # Check if selected_record_obj is an object with the attribute
                    # or a dict with the key
                    if hasattr(selected_record_obj, field_attr_name):
                        value_to_display = getattr(selected_record_obj, field_attr_name, '')
                    elif isinstance(selected_record_obj, dict):
                        value_to_display = selected_record_obj.get(field_attr_name, '')

                    app.entries[i].insert(0, str(value_to_display)) # Ensure value is string
        else:
            app.selected_index = None # Invalid index or filtered_records not set

    except IndexError:
        app.selected_index = None # Should not happen if curselection is valid
    except tk.TclError: # Can happen if widget is destroyed
        app.selected_index = None


def get_form_data(app):
    """
    Retrieve data entered in the form fields as a dictionary.

    This uses the field names stored in app.field_names to build a key-value
    mapping from each entry field. Keys are internal attribute names.

    Args:
        app: The main application instance with form entries and field names.

    Returns:
        dict: A dictionary of field names to user-provided values.
    """
    # app.field_names are the internal attribute names like 'name', 'address_line_1'
    # app.entries are the tk.Entry widgets
    return {field_attr: entry.get() for field_attr, entry in zip(app.field_names, app.entries)}

def clear_form(app):
    """
    Clear the form fields and reset the selected index.
    Reloads all records for the current category.

    Args:
        app: The main application instance containing the form entries.
    """
    for entry in app.entries:
        entry.delete(0, tk.END)
    app.selected_index = None

    # Defensive check for record_listbox
    if hasattr(app, 'record_listbox') and app.record_listbox:
        try:
            if app.record_listbox.curselection(): # If anything is selected, deselect it
                app.record_listbox.selection_clear(0, tk.END)
        except tk.TclError: # Widget might be in a bad state or destroyed
            # Pass silently as the primary goal is to clear form and load records
            pass

    load_records(app) # Reloads all records for the current category

def add_record(app):
    """
    Add a new record based on the form data and selected category.

    Args:
        app: The main application instance containing the form data and managers.
    """
    data = get_form_data(app) # This data dict uses internal attribute names as keys
    category = app.selected_category.get()
    manager = get_manager(category, app)

    if not manager:
        messagebox.showerror("Error", f"No manager configured for {category}.")
        return

    # Basic validation: check if the first field (often a name or primary identifier) is filled
    if app.field_names and data.get(app.field_names[0], "").strip() == "":
        first_field_label = list(app.fields_config[category].keys())[0]
        messagebox.showwarning("Input Required",
                               f"The field '{first_field_label}' is required to add a new record.")
        return

    success = False
    try:
        if category == "Client":
            # Assumes manager.add_client(data_dict)
            result = manager.add_client(data)
            success = bool(result) # True if an object is returned, or if it's literally True
        elif category == "Airline":
            # Assumes manager.add_airline(data_dict)
            if hasattr(manager, "add_airline"):
                result = manager.add_airline(data)
                success = bool(result)
            else:
                raise NotImplementedError("add_airline method not implemented in AirlineManager")
        elif category == "Flight":
            # Assumes manager.add_flight(data_dict)
            if hasattr(manager, "add_flight"):
                result = manager.add_flight(data)
                success = bool(result)
            else:
                raise NotImplementedError("add_flight method not implemented in FlightManager")

        if success:
            messagebox.showinfo("Success", f"{category} record added successfully.")
            load_records(app)
            # User's clear_form reloads records, so this is fine.
            clear_form(app)
        else:
            # This might be hit if add_... returns None or False
            messagebox.showerror("Error",
                                 f"Failed to add {category.lower()} record. "
                                 "Manager reported no success.")
    except ValueError as ve: # For validation errors from manager
        messagebox.showerror("Add Error", f"Could not add {category.lower()}: {ve}")
    except NotImplementedError as nie:
        messagebox.showerror("Error", str(nie))
    except (IOError, tk.TclError) as e: # More specific for add context
        messagebox.showerror("Add Operation Error",
                             f"An error occurred while adding {category.lower()}: {e}")
    except Exception as e: # General fallback
        # Consider logging this 'e' for debugging purposes
        messagebox.showerror("Unexpected Add Error",
                             f"An unexpected error occurred ({type(e).__name__}): {e}")


def update_record(app):
    """
    Update the selected record with the data from the form.
    """
    if app.selected_index is None or not (
            hasattr(app, 'filtered_records') and
            0 <= app.selected_index < len(app.filtered_records)):
        messagebox.showwarning("Selection Error", "No valid record selected to update.")
        return

    data = get_form_data(app) # New data from form, keys are internal attribute names
    category = app.selected_category.get()
    manager = get_manager(category, app)

    if not manager:
        messagebox.showerror("Error", f"No manager configured for {category}.")
        return

    original_record_obj = app.filtered_records[app.selected_index]
    success = False # Initialize success

    try:
        if category == "Client":
            client_id_to_update = getattr(original_record_obj, 'client_id', None)
            if client_id_to_update:
                # ClientManager.update_client expects (client_id, update_info_dict)
                success = manager.update_client(client_id_to_update, data)
            else:
                messagebox.showerror("Error", "Could not find client_id for update.")
                return
        elif category == "Airline":
            if hasattr(manager, "update_airline"):
                airline_id_to_update = getattr(original_record_obj, 'airline_id',
                                               getattr(original_record_obj, 'id', None))
                if airline_id_to_update:
                    success = manager.update_airline(airline_id_to_update, data)
                else: # Fallback to passing object if ID not found easily
                    success = manager.update_airline(original_record_obj, data)
            else:
                raise NotImplementedError(
                    f"update_airline method not implemented in {type(manager).__name__}"
                )
        elif category == "Flight":
            if hasattr(manager, "update_flight"):
                flight_id_to_update = getattr(original_record_obj, 'flight_id',
                                              getattr(original_record_obj, 'id', None))
                if flight_id_to_update:
                    success = manager.update_flight(flight_id_to_update, data)
                else:
                    success = manager.update_flight(original_record_obj, data)
            else:
                raise NotImplementedError(
                    f"update_flight method not implemented in {type(manager).__name__}"
                )
        else: # Should not be reached if category is one of the three
            messagebox.showerror("Error", f"Update logic not defined for category: {category}")
            return

        if success:
            messagebox.showinfo("Success", f"{category} record updated successfully.")
            load_records(app)
            clear_form(app) # clear_form itself calls load_records
        else:
            messagebox.showerror("Error",
                                 f"Failed to update {category.lower()} record. "
                                 "Manager reported failure.")
    except NotImplementedError as nie:
        messagebox.showerror("Error", str(nie))
    except (ValueError, IOError, tk.TclError) as e: # More specific
        messagebox.showerror("Update Operation Error", f"Error updating {category.lower()}: {e}")
    except Exception as e: # General fallback
        # Consider logging this 'e' for debugging purposes
        messagebox.showerror("Unexpected Update Error",
                             f"An unexpected error occurred ({type(e).__name__}): {e}")


def delete_record(app):
    """
    Delete the selected record.
    """
    if app.selected_index is None or not (
            hasattr(app, 'filtered_records') and
            0 <= app.selected_index < len(app.filtered_records)):
        messagebox.showwarning("Selection Error", "No valid record selected to delete.")
        return

    category = app.selected_category.get()
    manager = get_manager(category, app)

    if not manager:
        messagebox.showerror("Error", f"No manager configured for {category}.")
        return

    record_to_delete_obj = app.filtered_records[app.selected_index]
    success = False # Initialize success

    display_name_for_confirm = str(record_to_delete_obj) # Default display
    if hasattr(record_to_delete_obj, 'name'):
        display_name_for_confirm = getattr(record_to_delete_obj, 'name',
                                           str(record_to_delete_obj))
    elif hasattr(record_to_delete_obj, 'company_name'):
        display_name_for_confirm = getattr(record_to_delete_obj, 'company_name',
                                           str(record_to_delete_obj))

    confirm_message = (f"Are you sure you want to delete this {category.lower()} record: "
                       f"'{display_name_for_confirm}'?")
    if not messagebox.askyesno("Confirm Delete", confirm_message):
        return

    try:
        if category == "Client":
            client_id_to_delete = getattr(record_to_delete_obj, 'client_id', None)
            if client_id_to_delete:
                # ClientManager.delete_client expects client_id
                success = manager.delete_client(client_id_to_delete)
            else:
                messagebox.showerror("Error", "Could not find client_id for deletion.")
                return
        elif category == "Airline":
            if hasattr(manager, "delete_airline"):
                airline_id_to_delete = getattr(record_to_delete_obj, 'airline_id',
                                               getattr(record_to_delete_obj, 'id', None))
                if airline_id_to_delete:
                    success = manager.delete_airline(airline_id_to_delete)
                else: # Fallback: some managers might expect the object
                    success = manager.delete_airline(record_to_delete_obj)
            else:
                raise NotImplementedError(
                    f"delete_airline method not implemented in {type(manager).__name__}"
                )
        elif category == "Flight":
            if hasattr(manager, "delete_flight"):
                # Flight manager might expect a dict (as in main.py demo) or an ID
                if hasattr(record_to_delete_obj, 'to_dict'):
                    success = manager.delete_flight(record_to_delete_obj.to_dict())
                else: # Fallback to ID or object
                    flight_id_to_delete = getattr(record_to_delete_obj, 'flight_id',
                                                  getattr(record_to_delete_obj, 'id', None))
                    if flight_id_to_delete:
                        success = manager.delete_flight(flight_id_to_delete)
                    else:
                        success = manager.delete_flight(record_to_delete_obj) # Last resort
            else:
                raise NotImplementedError(
                    f"delete_flight method not implemented in {type(manager).__name__}"
                )
        else:
            messagebox.showerror("Error", f"Delete logic not defined for category: {category}")
            return

        if success:
            messagebox.showinfo("Success", f"{category} record deleted successfully.")
            load_records(app)
            clear_form(app) # clear_form itself calls load_records
        else:
            messagebox.showerror("Error",
                                 f"Failed to delete {category.lower()} record. "
                                 "Manager reported failure.")
    except NotImplementedError as nie:
        messagebox.showerror("Error", str(nie))
    except (IOError, ValueError, tk.TclError) as e: # More specific
        messagebox.showerror("Delete Operation Error", f"Error deleting {category.lower()}: {e}")
    except Exception as e: # General fallback
        # Consider logging this 'e' for debugging purposes
        messagebox.showerror("Unexpected Delete Error",
                             f"An unexpected error occurred ({type(e).__name__}): {e}")


def search_records(app):
    """
    Search for records based on data in any of the form fields.
    Uses the manager's 'search' method.

    Args:
        app: The main application instance (TravelApp).
    """
    category = app.selected_category.get()
    manager = get_manager(category, app)

    if not manager:
        messagebox.showerror("Error", f"No manager configured for category: {category}")
        return

    if not app.entries or not hasattr(app, 'field_names') or not app.field_names:
        messagebox.showwarning("Search Error",
                               "Form fields are not properly initialized for search.")
        return

    # Get all data from the form
    all_form_data = get_form_data(app)

    # Filter out empty fields to create the search criteria
    # The manager's search method (e.g., ClientManager.find_clients)
    # is designed to handle a dictionary of criteria.
    search_criteria = {
        key: value for key, value in all_form_data.items() if value.strip()
    }

    if not search_criteria:
        messagebox.showinfo("Search",
                            "All search fields are empty. Loading all records for the category.")
        load_records(app) # Load all records if no criteria are entered
        return

    try:
        # All managers (Client, Airline, Flight) are expected to have a 'search(criteria_dict)'
        # method. For ClientManager, this is an alias for find_clients(criteria_dict).
        if hasattr(manager, "search"):
            app.filtered_records = manager.search(search_criteria)
        else:
            messagebox.showerror("Error", f"Manager for {category} missing 'search' method.")
            app.filtered_records = [] # Reset if search method is missing

        if app.filtered_records is None: # Ensure filtered_records is a list
            app.filtered_records = []

        refresh_listbox(app) # Update the GUI listbox with search results

        if not app.filtered_records:
            # Create a string of the search criteria for the message
            criteria_parts = []
            for k, v in search_criteria.items():
                # Get display label for the attribute key k
                label = k # fallback to internal key
                if category in app.fields_config:
                    for display_label, internal_key in app.fields_config[category].items():
                        if internal_key == k:
                            label = display_label
                            break
                criteria_parts.append(f"{label}: '{v}'")
            criteria_str = ", ".join(criteria_parts)
            messagebox.showinfo("Search Results",
                                f"No {category.lower()} records found matching: {criteria_str}.")

    except (ValueError, TypeError, tk.TclError) as e: # More specific
        messagebox.showerror("Search Operation Error",
                             f"An error occurred during search for {category.lower()} records: {e}")
        app.filtered_records = [] # Clear results on error
        refresh_listbox(app)
    except Exception as e: # General fallback
        # Consider logging this 'e' for debugging purposes
        messagebox.showerror("Unexpected Search Error",
                             f"An unexpected error occurred ({type(e).__name__}): {e}")
        app.filtered_records = []
        refresh_listbox(app)


def refresh_listbox(app):
    """
    Refresh the listbox with the current content of app.filtered_records.
    Correctly displays ClientRecord objects and provides a fallback for others.

    Args:
        app: The main application instance (TravelApp).
    """
    # Workaround for AttributeError: 'TravelApp' object has no attribute 'record_listbox'
    # This occurs if refresh_listbox is called before app.record_listbox is initialized in gui.py
    if not hasattr(app, 'record_listbox') or not app.record_listbox:
        # print("DEBUG: refresh_listbox called before app.record_listbox was initialized. skip.")
        return

    try:
        app.record_listbox.delete(0, tk.END) # Clear existing items
    except tk.TclError: # Can happen if widget is destroyed or not fully ready
        # print("DEBUG: tk.TclError in refresh_listbox while deleting items. Listbox is not ready.")
        return


    if not hasattr(app, 'filtered_records') or not app.filtered_records:
        app.record_listbox.insert(tk.END, "No records to display.")
        return

    category = app.selected_category.get()

    for record_obj in app.filtered_records:
        display_string = ""
        # Create a display string for the listbox item
        if category == "Client": # Specifically handle ClientRecord objects
            # Check if it's an object and has expected attributes for ClientRecord
            if (isinstance(record_obj, object) and
                    hasattr(record_obj, 'client_id') and hasattr(record_obj, 'name')):
                name = getattr(record_obj, 'name', 'N/A')
                client_id = getattr(record_obj, 'client_id', 'N/A')
                display_string = f"Client: {name} (ID: {client_id})"
            elif isinstance(record_obj, dict): # If it's a dict (e.g. from other managers)
                display_string = (f"Client: {record_obj.get('name', 'N/A')} "
                                  f"(ID: {record_obj.get('client_id', 'N/A')})")
            else:
                display_string = str(record_obj) # Fallback

        elif category == "Airline":
            # Assuming Airline records might be objects or dicts
            if (isinstance(record_obj, object) and
                    hasattr(record_obj, 'airline_id') and hasattr(record_obj, 'company_name')):
                company_name = getattr(record_obj, 'company_name', 'N/A')
                airline_id = getattr(record_obj, 'airline_id', 'N/A')
                display_string = f"Airline: {company_name} (ID: {airline_id})"
            elif isinstance(record_obj, dict):
                airline_id_val = record_obj.get('id', record_obj.get('airline_id', 'N/A'))
                display_string = (f"Airline: {record_obj.get('company_name', 'N/A')} "
                                  f"(ID: {airline_id_val})")
            else:
                display_string = str(record_obj)

        elif category == "Flight":
            # Assuming Flight records might be objects or dicts
            if isinstance(record_obj, object):
                flight_id = getattr(record_obj, 'id',
                                    getattr(record_obj, 'flight_id', 'N/A'))
                client_id = getattr(record_obj, 'client_id', 'N/A')
                airline_id = getattr(record_obj, 'airline_id', 'N/A')
                date = getattr(record_obj, 'date', 'N/A')
                display_string = (f"Flight: ID {flight_id}, Client {client_id}, "
                                  f"Airline {airline_id}, Date {date}")
            elif isinstance(record_obj, dict):
                flight_id = record_obj.get('id', record_obj.get('flight_id', 'N/A'))
                client_id = record_obj.get('client_id', 'N/A')
                airline_id = record_obj.get('airline_id', 'N/A')
                date = record_obj.get('date', 'N/A')
                display_string = (f"Flight: ID {flight_id}, Client {client_id}, "
                                  f"Airline {airline_id}, Date {date}")
            else:
                display_string = str(record_obj)
        else:
            # Generic fallback if category is unknown or record_obj is not as expected
            if isinstance(record_obj, dict):
                # Display first 3 key-value pairs
                items_to_display = list(record_obj.items())[:3]
                display_string = ", ".join(f"{k}: {v}" for k, v in items_to_display)
            else:
                display_string = str(record_obj)
        try:
            app.record_listbox.insert(tk.END, display_string)
        except tk.TclError: # Widget might be destroyed during loop
            # print("DEBUG: tk.TclError in refresh_listbox while inserting items. ")
            break # Exit loop if listbox is no longer usable
