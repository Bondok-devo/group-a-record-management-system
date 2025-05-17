# src/gui/events.py
"""
Event handling functions for the Travel Agent Record Management System GUI.

This module contains functions that are bound to GUI widget events,
such as button clicks and listbox selections. It orchestrates interactions
between the GUI (TravelApp instance) and the data managers.
"""
import tkinter as tk
from tkinter import messagebox, simpledialog
import datetime


# --- Helper Functions ---

def get_manager(category, app):
    """
    Retrieves the appropriate data manager based on the selected category.

    Args:
        category (str): The currently selected record category (e.g., "Client").
        app (TravelApp): The main application instance.

    Returns:
        An instance of ClientManager, AirlineManager, or FlightManager,
        or None if the category is unrecognized.
    """
    if category == "Client":
        return app.client_mgr
    if category == "Airline":
        return app.airline_mgr
    if category == "Flight":
        return app.flight_mgr
    return None


def get_form_data_for_simple_categories(app):
    """
    Collects data from ttk.Entry widgets for Client and Airline categories.

    Args:
        app (TravelApp): The main application instance.

    Returns:
        dict: A dictionary of field identifiers and their values.
    """
    data = {}
    for i, field_name in enumerate(app.field_names):
        if i < len(app.entries):
            data[field_name] = app.entries[i].get()
        else:
            print(f"Warning: Mismatch for {field_name} in simple form data.")
            data[field_name] = ""
    return data


def _format_record_for_listbox(category, record_obj):
    """Helper to format a record object into a display string for the listbox."""
    display_string = "Unknown Record"
    if category == "Client":
        name = getattr(record_obj, 'name', 'N/A')
        client_id = getattr(record_obj, 'client_id', 'N/A')
        display_string = f"Client: {name} (ID: {client_id})"
    elif category == "Airline":
        company_name = getattr(record_obj, 'company_name', 'N/A')
        airline_id = getattr(record_obj, 'airline_id', 'N/A')
        display_string = f"Airline: {company_name} (ID: {airline_id})"
    elif category == "Flight":
        flight_id = getattr(record_obj, 'flight_id', 'N/A') # Added flight_id to display
        client_id = getattr(record_obj, 'client_id', 'N/A')
        airline_id = getattr(record_obj, 'airline_id', 'N/A')
        date_val = record_obj.flight_date
        date_str = date_val.strftime('%Y-%m-%d %H:%M') if isinstance(date_val, datetime.datetime) else str(date_val)
        start_city = getattr(record_obj, 'start_city', 'N/A')
        end_city = getattr(record_obj, 'end_city', 'N/A')
        display_string = (
            f"Flight ID: {flight_id}, Client: {client_id}, Airline: {airline_id}, "
            f"{start_city} to {end_city} on {date_str}"
        )
    return display_string


def _clear_form_widgets(app):
    """Helper to clear all input widgets in the form."""
    for entry in app.entries:
        entry.delete(0, tk.END)

    if hasattr(app, 'client_var'):
        app.client_var.set("")
    if hasattr(app, 'airline_var'):
        app.airline_var.set("")

    if hasattr(app, 'calendar') and app.calendar:
        app.calendar.set_date(datetime.date.today())
    if hasattr(app, 'hour_spinbox') and app.hour_spinbox:
        app.hour_spinbox.set("00")
    if hasattr(app, 'minute_spinbox') and app.minute_spinbox:
        app.minute_spinbox.set("00")

# --- Core GUI Event Handlers ---

def load_records(app):
    """
    Loads records for the currently selected category into the listbox.
    """
    category = app.selected_category.get()
    manager = get_manager(category, app)

    if not manager:
        messagebox.showerror(
            "Load Error", f"No manager configured for {category}."
        )
        refresh_listbox(app, [])  # Clear listbox
        return

    try:
        records = []
        if category == "Client" and hasattr(manager, 'get_all_clients'):
            records = manager.get_all_clients()
        elif category == "Airline" and hasattr(manager, 'get_all_airlines'):
            records = manager.get_all_airlines()
        elif category == "Flight" and hasattr(manager, 'get_all_flights'):
            records = manager.get_all_flights()
        elif hasattr(manager, 'get_all'):  # Fallback
            records = manager.get_all()
        else:
            messagebox.showerror(
                "Load Error",
                f"Manager for {category} missing 'get_all' method."
            )
        refresh_listbox(app, records or [])
    except (IOError, ValueError) as e:
        messagebox.showerror(
            "Load Error",
            f"Error loading {category.lower()} records: {e}"
        )
        refresh_listbox(app, [])
    except Exception as e:
        messagebox.showerror(
            "Unexpected Load Error",
            f"An unexpected error occurred while loading records: {e}"
        )
        refresh_listbox(app, [])


def refresh_listbox(app, records):
    """
    Clears and repopulates the record_listbox with the provided records.
    """
    if not (hasattr(app, 'record_listbox') and
            app.record_listbox.winfo_exists()): # C0325: Unnecessary parens removed
        return

    try:
        app.record_listbox.delete(0, tk.END)
    except tk.TclError:
        return # Listbox might not be ready or already destroyed

    category = app.selected_category.get()

    for record_obj in records:
        try:
            display_string = _format_record_for_listbox(category, record_obj)
            app.record_listbox.insert(tk.END, display_string)
        except tk.TclError:
            break # Listbox likely destroyed
        except AttributeError as ae:
            error_msg = f"Error displaying: {ae} - {str(record_obj)}"
            app.record_listbox.insert(tk.END, error_msg)


def clear_form(app):
    """
    Clears all input fields in the form and resets selections.
    """
    _clear_form_widgets(app)

    app.selected_index = None
    if hasattr(app, 'record_listbox') and app.record_listbox.winfo_exists():
        app.record_listbox.selection_clear(0, tk.END)

    if hasattr(app, 'filtered_records'):
        app.filtered_records = None
    load_records(app)


def _populate_flight_client_dropdown(app, record_obj):
    """Helper to populate the client dropdown for a selected flight."""
    if app.client_dropdown and hasattr(record_obj, 'client_id'):
        try:
            client_obj = app.client_mgr.get_client_by_id(record_obj.client_id)
            if client_obj and client_obj.name in app.client_dropdown['values']:
                app.client_var.set(client_obj.name)
            elif app.client_dropdown['values']: # Default if not found or not in list
                app.client_var.set(app.client_dropdown['values'][0])
        except Exception as e:
            print(f"Error finding client for flight: {e}")
            if app.client_dropdown['values']:
                app.client_var.set(app.client_dropdown['values'][0])

def _populate_flight_airline_dropdown(app, record_obj):
    """Helper to populate the airline dropdown for a selected flight."""
    if app.airline_dropdown and hasattr(record_obj, 'airline_id'):
        try:
            airline_obj = app.airline_mgr.get_airline_by_id(record_obj.airline_id)
            if airline_obj and airline_obj.company_name in app.airline_dropdown['values']:
                app.airline_var.set(airline_obj.company_name)
            elif app.airline_dropdown['values']: # Default
                app.airline_var.set(app.airline_dropdown['values'][0])
        except Exception as e:
            print(f"Error finding airline for flight: {e}")
            if app.airline_dropdown['values']:
                app.airline_var.set(app.airline_dropdown['values'][0])

def _populate_flight_datetime_widgets(app, record_obj):
    """Helper to populate date and time widgets for a selected flight."""
    flight_dt_obj = record_obj.flight_date
    if isinstance(flight_dt_obj, datetime.datetime) and \
       app.calendar and app.hour_spinbox and app.minute_spinbox:
        app.calendar.set_date(flight_dt_obj.date())
        app.hour_spinbox.set(f"{flight_dt_obj.hour:02d}")
        app.minute_spinbox.set(f"{flight_dt_obj.minute:02d}")

def _populate_flight_route_entries(app, record_obj):
    """Helper to populate start and end city for a selected flight."""
    start_city = getattr(record_obj, 'start_city', "")
    end_city = getattr(record_obj, 'end_city', "")
    if len(app.entries) > 0:
        app.entries[0].insert(0, start_city)
    if len(app.entries) > 1:
        app.entries[1].insert(0, end_city)


def on_select(app, _event=None): # W0613: Unused argument 'event' -> _event
    """
    Handles item selection in the record_listbox.
    Populates the form fields with the data of the selected record.
    """
    if not (hasattr(app, 'record_listbox') and
            app.record_listbox.winfo_exists()):
        return

    selected_indices = app.record_listbox.curselection()
    if not selected_indices:
        app.selected_index = None
        return

    app.selected_index = selected_indices[0]
    category = app.selected_category.get()
    manager = get_manager(category, app)
    if not manager:
        return

    source_records = []
    if hasattr(app, 'filtered_records') and app.filtered_records is not None:
        source_records = app.filtered_records
    else:
        if category == "Client":
            source_records = manager.get_all_clients()
        elif category == "Airline":
            source_records = manager.get_all_airlines()
        elif category == "Flight":
            source_records = manager.get_all_flights()

    if not (0 <= app.selected_index < len(source_records)):
        messagebox.showwarning("Selection Error", "Selected index out of bounds.")
        _clear_form_widgets(app) # Use helper to clear form widgets
        return

    record_obj = source_records[app.selected_index]
    _clear_form_widgets(app) # Clear form before populating

    if category in ("Client", "Airline"): # R1714: consider-using-in
        if hasattr(record_obj, 'to_dict'):
            data_dict = record_obj.to_dict()
            for i, field_key in enumerate(app.field_names):
                if i < len(app.entries):
                    app.entries[i].insert(0, data_dict.get(field_key, ""))
    elif category == "Flight":
        _populate_flight_client_dropdown(app, record_obj)
        _populate_flight_airline_dropdown(app, record_obj)
        _populate_flight_datetime_widgets(app, record_obj)
        _populate_flight_route_entries(app, record_obj)

    if app.record_listbox.winfo_exists():
        app.record_listbox.selection_set(app.selected_index)
        app.record_listbox.activate(app.selected_index)
        app.record_listbox.see(app.selected_index)


def _get_flight_data_from_form(app):
    """Helper to collect and validate flight data from the form."""
    if not (app.client_var.get() and app.airline_var.get()):
        messagebox.showwarning("Input Required", "Client and Airline are required.")
        return None

    client_name = app.client_var.get()
    airline_name = app.airline_var.get()

    client_id_val = None
    found_client = next(
        (c for c in app.client_mgr.get_all_clients() if c.name == client_name),
        None
    )
    if found_client:
        client_id_val = found_client.client_id
    else:
        messagebox.showerror("Error", f"Client '{client_name}' not found.")
        return None

    airline_id_val = None
    found_airline = next(
        (a for a in app.airline_mgr.get_all_airlines()
         if a.company_name == airline_name),
        None
    )
    if found_airline:
        airline_id_val = found_airline.airline_id
    else:
        messagebox.showerror("Error", f"Airline '{airline_name}' not found.")
        return None

    try:
        selected_date = app.calendar.get_date()
        hour = int(app.hour_spinbox.get())
        minute = int(app.minute_spinbox.get())
        flight_datetime = datetime.datetime.combine(
            selected_date, datetime.time(hour, minute)
        )
    except ValueError:
        messagebox.showerror("Input Error", "Invalid hour or minute. Must be numbers.")
        return None
    except AttributeError:
        messagebox.showerror("GUI Error", "Date/Time widgets not found.")
        return None

    start_city = ""
    if len(app.entries) > 0: # C0321: multiple-statements - fixed
        start_city = app.entries[0].get().strip()

    end_city = ""
    if len(app.entries) > 1: # C0321: multiple-statements - fixed
        end_city = app.entries[1].get().strip()


    if not (start_city and end_city): # C0321: multiple-statements - fixed
        messagebox.showwarning("Input Required", "Start and End City are required.")
        return None

    return {
        "record_type": "Flight",
        "Client_ID": client_id_val,
        "Airline_ID": airline_id_val,
        "Date": flight_datetime.isoformat(),
        "Start City": start_city,
        "End City": end_city
    }

# --- CRUD Operations ---

def add_record(app):
    """Adds a new record based on the form data and selected category."""
    category = app.selected_category.get()
    manager = get_manager(category, app)
    if not manager:
        messagebox.showerror("Error", f"No manager for {category}.")
        return

    data_to_add = {}
    if category == "Flight":
        data_to_add = _get_flight_data_from_form(app)
        if data_to_add is None:
            return
    else:  # Client or Airline
        data_to_add = get_form_data_for_simple_categories(app)
        if app.field_names and not data_to_add.get(app.field_names[0], "").strip():
            first_field_label = list(app.fields_config[category].keys())[0]
            messagebox.showwarning(
                "Input Required", f"The field '{first_field_label}' is required."
            )
            return
        if "record_type" not in data_to_add:
            data_to_add["record_type"] = category

    try:
        result = None
        if category == "Client":
            result = manager.add_client(data_to_add)
        elif category == "Airline":
            result = manager.add_airline(data_to_add)
        elif category == "Flight":
            result = manager.add_flight(data_to_add)

        if result:
            messagebox.showinfo("Success", f"{category} record added.")
            clear_form(app)
        else:
            messagebox.showerror("Add Error", f"Failed to add {category.lower()}.")
    except Exception as e: # W0718: Catching too general exception
        messagebox.showerror("Unexpected Add Error", f"Error: {e}")


def update_record(app):
    """Updates the selected record with data from the form."""
    category = app.selected_category.get()
    manager = get_manager(category, app)

    is_valid_selection = (
        app.selected_index is not None and
        hasattr(app, 'record_listbox') and
        0 <= app.selected_index < app.record_listbox.size()
    )
    if not is_valid_selection:
        messagebox.showwarning("Selection Error", "No record selected to update.")
        return
    if not manager:
        messagebox.showerror("Error", f"No manager for {category}.")
        return

    original_record_id_details = None
    source_records = []
    if hasattr(app, 'filtered_records') and app.filtered_records is not None:
        source_records = app.filtered_records
    else:
        if category == "Client":
            source_records = manager.get_all_clients()
        elif category == "Airline":
            source_records = manager.get_all_airlines()
        elif category == "Flight":
            source_records = manager.get_all_flights()

    if 0 <= app.selected_index < len(source_records):
        selected_obj = source_records[app.selected_index]
        if category == "Client":
            original_record_id_details = selected_obj.client_id
        elif category == "Airline":
            original_record_id_details = selected_obj.airline_id
        elif category == "Flight":
            original_record_id_details = selected_obj.to_dict()
            if 'record_type' in original_record_id_details:
                del original_record_id_details['record_type']
    else:
        messagebox.showerror("Error", "Could not retrieve selected record.")
        return

    if original_record_id_details is None:
        messagebox.showerror("Update Error", "Could not identify record to update.")
        return

    updated_data = {}
    if category == "Flight":
        updated_data = _get_flight_data_from_form(app)
        if updated_data is None:
            return
        if 'record_type' in updated_data:
            del updated_data['record_type']
    else:  # Client or Airline
        updated_data = get_form_data_for_simple_categories(app)
        if app.field_names and not updated_data.get(app.field_names[0], "").strip():
            first_field_label = list(app.fields_config[category].keys())[0]
            messagebox.showwarning(
                "Input Required", f"Field '{first_field_label}' is required."
            )
            return
        if "record_type" not in updated_data:
             updated_data["record_type"] = category

    try:
        success = False
        if category == "Client":
            success = manager.update_client(original_record_id_details, updated_data)
        elif category == "Airline":
            success = manager.update_airline(original_record_id_details, updated_data)
        elif category == "Flight":
            success = manager.update_flight(original_record_id_details, updated_data)

        if success:
            messagebox.showinfo("Success", f"{category} record updated.")
            clear_form(app)
        else:
            messagebox.showerror("Update Error", f"Failed to update {category.lower()}.")
    except Exception as e: # W0718: Catching too general exception
        messagebox.showerror("Unexpected Update Error", f"Error: {e}")


def delete_record(app):
    """Deletes the selected record."""
    category = app.selected_category.get()
    manager = get_manager(category, app)

    is_valid_selection = (
        app.selected_index is not None and
        hasattr(app, 'record_listbox') and
        0 <= app.selected_index < app.record_listbox.size()
    )
    if not is_valid_selection:
        messagebox.showwarning("Selection Error", "No record selected to delete.")
        return
    if not manager:
        messagebox.showerror("Error", f"No manager for {category}.")
        return

    record_id_details = None # For flights, this will be a dict
    record_id_to_delete = None # For client/airline, this will be the ID

    source_records = []
    if hasattr(app, 'filtered_records') and app.filtered_records is not None:
        source_records = app.filtered_records
    else:
        if category == "Client":
            source_records = manager.get_all_clients()
        elif category == "Airline":
            source_records = manager.get_all_airlines()
        elif category == "Flight":
            source_records = manager.get_all_flights()

    if 0 <= app.selected_index < len(source_records):
        selected_obj = source_records[app.selected_index]
        if category == "Client":
            record_id_to_delete = selected_obj.client_id
        elif category == "Airline":
            record_id_to_delete = selected_obj.airline_id
        elif category == "Flight":
            record_id_details = selected_obj.to_dict()
            if 'record_type' in record_id_details:
                del record_id_details['record_type']
    else:
        messagebox.showerror("Error", "Could not retrieve selected record.")
        return

    if record_id_to_delete is None and record_id_details is None:
        messagebox.showerror("Delete Error", "Could not identify record to delete.")
        return

    confirm_msg = f"Are you sure you want to delete this {category.lower()} record?"
    confirm_delete = messagebox.askyesno("Confirm Delete", confirm_msg)
    if not confirm_delete:
        return

    try:
        success = False
        if category == "Client":
            success = manager.delete_client(record_id_to_delete)
        elif category == "Airline":
            success = manager.delete_airline(record_id_to_delete)
        elif category == "Flight":
            success = manager.delete_flight(record_id_details)

        if success:
            messagebox.showinfo("Success", f"{category} record deleted.")
            clear_form(app)
        else:
            messagebox.showerror("Delete Error", f"Failed to delete {category.lower()}.")
    except Exception as e: # W0718: Catching too general exception
        messagebox.showerror("Unexpected Delete Error", f"Error: {e}")


def search_records(app):
    """
    Searches records based on a query and updates the listbox.
    """
    category = app.selected_category.get()
    manager = get_manager(category, app)
    if not manager:
        messagebox.showerror("Error", f"No manager for {category}.")
        return

    search_term = simpledialog.askstring(
        "Search", f"Enter search term for {category}s:"
    )
    if search_term is None: # User cancelled
        return
    if not search_term.strip():
        messagebox.showinfo("Search", "Search term empty. Displaying all.")
        app.filtered_records = None
        load_records(app)
        return

    search_term = search_term.lower()
    all_records = []
    if category == "Client":
        all_records = manager.get_all_clients()
    elif category == "Airline":
        all_records = manager.get_all_airlines()
    elif category == "Flight":
        all_records = manager.get_all_flights()

    app.filtered_records = []
    for record in all_records:
        match = False
        searchable_attrs = []
        if category == "Client":
            searchable_attrs = ['name', 'city', 'country', 'phone_number']
        elif category == "Airline":
            searchable_attrs = ['company_name']
        elif category == "Flight":
            searchable_attrs = ['client_id', 'airline_id', 'start_city', 'end_city']
            if search_term in record.flight_date.isoformat():
                match = True
        else: # Default generic search
            if hasattr(record, 'to_dict'):
                for value in record.to_dict().values():
                    if search_term in str(value).lower():
                        match = True
                        break
            elif search_term in str(record).lower():
                match = True

        if not match:
            for attr in searchable_attrs:
                if hasattr(record, attr):
                    attr_value = str(getattr(record, attr, "")).lower()
                    if search_term in attr_value:
                        match = True
                        break
        if match:
            app.filtered_records.append(record)

    # ... previous code in search_records ...

    if not app.filtered_records:
        no_match_msg = f"No {category.lower()} records found matching '{search_term}'."
        messagebox.showinfo("Search Results", no_match_msg)
    else:
        found_msg = (
            f"Found {len(app.filtered_records)} matching "
            f"{category.lower()} record(s)."
        )
        messagebox.showinfo("Search Results", found_msg)

    refresh_listbox(app, app.filtered_records)
    app.selected_index = None
