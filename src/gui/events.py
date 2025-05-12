"""
Event handling functions for the Travel Records Management GUI.

This module manages CRUD operations and GUI listbox updates
based on the selected record category: Client, Airline, or Flight.
"""
import tkinter as tk
from tkinter import messagebox
from record.client_manager import ClientManager
from record.airline_manager import AirlineManager
from record.flight_manager import FlightManager


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
    Load records into the GUI based on the selected category.

    Args:
        app: The main application instance containing the selected category and managers.
    """
    manager = get_manager(app.selected_category.get(), app)
    # Additional logic for loading records

def update_fields(app):
    """
    Update the form fields in the GUI based on the selected category.

    Args:
        app: The main application instance containing the form configuration.
    """
    for widget in app.form_frame.winfo_children():
        widget.destroy()
    app.entries.clear()
    fields = app.fields_config[app.selected_category.get()]
    for i, field in enumerate(fields):
        label = tk.Label(app.form_frame, text=field + ":")
        label.grid(row=i, column=0, sticky="e", padx=5, pady=2)
        entry = tk.Entry(app.form_frame)
        entry.grid(row=i, column=1, padx=5, pady=2)
        app.entries.append(entry)

def on_select(app):
    """
    Handle the selection of a record in the listbox and populate the form fields.

    Args:
        app: The main application instance containing the listbox and form data.
    """
    try:
        index = app.record_listbox.curselection()[0]
        app.selected_index = index
        selected = app.filtered_records[index]
        for entry, value in zip(app.entries, selected.values()):
            entry.delete(0, 'end')
            entry.insert(0, value)
    except IndexError:
        pass

def get_form_data(app):
    """
    Retrieve data entered in the form fields.

    Args:
        app: The main application instance containing the form entries.

    Returns:
        list: A list of values entered in the form fields.
    """
    return [entry.get() for entry in app.entries]

def clear_form(app):
    """
    Clear the form fields and reset the selected index.

    Args:
        app: The main application instance containing the form entries.
    """
    for entry in app.entries:
        entry.delete(0, 'end')
    app.selected_index = None
    load_records(app)

def add_record(app):
    """
    Add a new record based on the form data.

    Args:
        app: The main application instance containing the form data and managers.
    """
    data = get_form_data(app)
    manager = get_manager(app.selected_category.get(), app)
    if manager.add(data):
        load_records(app)
        clear_form(app)
    else:
        messagebox.showerror("Error", "Failed to add record.")

def update_record(app):
    """
    Update the selected record with the data from the form.

    Args:
        app: The main application instance containing the selected record and form data.
    """
    if app.selected_index is not None:
        data = get_form_data(app)
        manager = get_manager(app.selected_category.get(), app)
        record = app.filtered_records[app.selected_index]
        if manager.update(record, data):
            load_records(app)
            clear_form(app)
        else:
            messagebox.showerror("Error", "Failed to update record.")

def delete_record(app):
    """
    Delete the selected record.

    Args:
        app: The main application instance containing the selected record and managers.
    """
    if app.selected_index is not None:
        manager = get_manager(app.selected_category.get(), app)
        record = app.filtered_records[app.selected_index]
        if manager.delete(record):
            load_records(app)
            clear_form(app)
        else:
            messagebox.showerror("Error", "Failed to delete record.")

def search_records(app):
    """
    Search for records based on the form data.

    Args:
        app: The main application instance containing the search query and managers.
    """
    query = get_form_data(app)
    manager = get_manager(app.selected_category.get(), app)
    app.filtered_records = manager.search(query)
    refresh_listbox(app)

def refresh_listbox(app):
    """
    Refresh the listbox with the filtered records.

    Args:
        app: The main application instance containing the filtered records.
    """
    app.record_listbox.delete(0, 'end')
    for record in app.filtered_records:
        app.record_listbox.insert('end', list(record.values()))
