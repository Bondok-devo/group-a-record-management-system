"""
GUI class definition for the Travel Records Management application.

This module constructs a tkinter-based interface and binds widgets to event functions
for managing Client, Airline, and Flight records.
"""

import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
from . import events


# For GUI classes, a larger number of instance attributes (widgets, vars) is common.
class TravelApp:
    """
    A GUI application for managing travel records, including Clients, Airlines, and Flights.

    This class initializes the tkinter interface, sets up widgets, and binds them to event
    handling functions for CRUD operations.
    """

    def __init__(self, root, client_mgr, airline_mgr, flight_mgr):
        """
        Initialize the TravelApp GUI.

        Args:
            root (tk.Tk): The root tkinter window.
            client_mgr: The manager for handling client records.
            airline_mgr: The manager for handling airline records.
            flight_mgr: The manager for handling flight records.
        """
        self.root = root
        self.client_mgr = client_mgr
        self.airline_mgr = airline_mgr
        self.flight_mgr = flight_mgr
        self.root.title("Specialist Travel Agent Records")
        self.selected_index = None

        self.hour_spinbox = None
        self.minute_spinbox = None

        self.selected_category = tk.StringVar(value="Client")
        self.entries = []  # Will store simple ttk.Entry widgets

        self.airline_var = tk.StringVar()
        self.client_var = tk.StringVar()

        # Initialize dropdown attributes
        self.client_dropdown = None
        self.airline_dropdown = None
        self.calendar = None

        self.fields_config = {
            "Client": {
                "Name": "name",
                "Address Line 1": "address_line_1",
                "Address Line 2": "address_line_2",
                "Address Line 3": "address_line_3",
                "City": "city",
                "State": "state",
                "Zip Code": "zip_code",
                "Country": "country",
                "Phone Number": "phone_number"
            },
            "Airline": {
                "Company Name": "company_name"
            },
            "Flight": {
                "Select Client": "client_selection",
                "Select Airline": "airline_selection",
                "Date & Time": "flight_date_time",
                "Start City": "start_city",
                "End City": "end_city"
            }
        }

        self.setup_widgets()
        self.update_fields()

    def setup_widgets(self):
        """
        Set up the GUI widgets, including labels, combobox, listbox, and buttons.
        """
        # Category Row
        ttk.Label(
            self.root, text="Category:"
        ).grid(row=0, column=0, padx=5, pady=(10, 5), sticky="e")
        category_combo = ttk.Combobox(
            self.root,
            textvariable=self.selected_category,
            values=list(self.fields_config.keys()),
            state="readonly",
            width=30
        )
        category_combo.grid(row=0, column=1, padx=5, pady=(10, 5), sticky="w")
        category_combo.bind("<<ComboboxSelected>>",
                            lambda e: self.update_fields())

        # Main Form Frame
        self.form_frame = ttk.Frame(self.root)
        self.form_frame.grid(
            row=1, column=0, columnspan=2, padx=5, pady=5, sticky="ew"
        )

        # Configure columns for the form_frame
        self.form_frame.columnconfigure(0, weight=0)  # Label column
        self.form_frame.columnconfigure(1, weight=1)  # Input area column

        # Record Listbox
        self.record_listbox = tk.Listbox(
            self.root, height=10, width=80
        )
        self.record_listbox.grid(
            row=2, column=0, columnspan=2, padx=5, pady=5, sticky="ew"
        )
        # The `if events:` check is a guard, often intentional.
        if events:
            self.record_listbox.bind("<<ListboxSelect>>",
                                     lambda e: events.on_select(self))

        # Button Frame
        button_frame = ttk.Frame(self.root)
        button_frame.grid(row=3, column=0, columnspan=2, pady=5)

        actions = []
        # The `if events:` check is a guard.
        if events:
            actions = [
                ("Add", events.add_record),
                ("Update", events.update_record),
                ("Delete", events.delete_record),
                ("Search", events.search_records),
                ("Clear", events.clear_form)
            ]
        for i, (text, cmd) in enumerate(actions):
            ttk.Button(
                button_frame, text=text, command=lambda c=cmd: c(self)
            ).grid(row=0, column=i, padx=3)

    def update_fields(self):
        """
        Dynamically update the form fields based on the selected category
        and reload the records in the listbox.
        """

        for widget in self.form_frame.winfo_children():
            widget.destroy()
        self.entries.clear()  # Clear list of simple entry widgets
        # Reset references to specific input widgets
        self.client_dropdown = None
        self.airline_dropdown = None
        self.calendar = None
        self.hour_spinbox = None
        self.minute_spinbox = None

        category = self.selected_category.get()
        config = self.fields_config.get(category, {})
        # Internal field names for data handling
        self.field_names = list(config.values())

        for i, (label_text, field_identifier) in enumerate(config.items()):
            # Create Label in form_frame (column 0)
            label = ttk.Label(self.form_frame, text=f"{label_text}:")
            label.grid(row=i, column=0, sticky="e", padx=(0, 5), pady=2)

            # Create a container Frame for input widgets in form_frame (column 1)
            input_area = ttk.Frame(self.form_frame)
            input_area.grid(row=i, column=1, sticky="ew", pady=2)

            if category == "Flight":
                if field_identifier == "client_selection":
                    input_area.columnconfigure(0, weight=1)  # Make combobox expand
                    self.client_dropdown = ttk.Combobox(
                        input_area,  # Parent is now input_area
                        textvariable=self.client_var,
                        state="readonly",
                    )
                    all_clients = self.client_mgr.get_all_clients()
                    client_names = [
                        c.name for c in all_clients
                    ] if all_clients else []
                    self.client_dropdown["values"] = client_names
                    if client_names:
                        self.client_var.set(client_names[0])
                    else:
                        self.client_var.set("")
                    self.client_dropdown.grid(row=0, column=0, sticky="ew")
                elif field_identifier == "airline_selection":
                    input_area.columnconfigure(0, weight=1)
                    self.airline_dropdown = ttk.Combobox(
                        input_area,
                        textvariable=self.airline_var,
                        state="readonly",
                    )
                    all_airlines = self.airline_mgr.get_all_airlines()
                    airline_names = [
                        a.company_name for a in all_airlines
                    ] if all_airlines else []
                    self.airline_dropdown["values"] = airline_names
                    if airline_names:
                        self.airline_var.set(airline_names[0])
                    else:
                        self.airline_var.set("")
                    self.airline_dropdown.grid(row=0, column=0, sticky="ew")
                elif field_identifier == "flight_date_time":
                    # DateEntry
                    self.calendar = DateEntry(
                        input_area,
                        width=10, background='darkblue', foreground='white',
                        borderwidth=2, date_pattern='yyyy-mm-dd'
                    )
                    self.calendar.grid(
                        row=0, column=0, sticky="w", padx=(0, 5)
                    )

                    # Time Label and Spinboxes
                    ttk.Label(
                        input_area, text="Time:"
                    ).grid(row=0, column=1, sticky="w", padx=(5, 2))
                    self.hour_spinbox = ttk.Spinbox(
                        input_area, from_=0, to=23, width=3,
                        format="%02.0f", wrap=True
                    )
                    self.hour_spinbox.grid(row=0, column=2, sticky="w")
                    ttk.Label(
                        input_area, text=":"
                    ).grid(row=0, column=3, sticky="w")
                    self.minute_spinbox = ttk.Spinbox(
                        input_area, from_=0, to=59, width=3,
                        format="%02.0f", wrap=True
                    )
                    self.minute_spinbox.grid(row=0, column=4, sticky="w")
                elif field_identifier in ["start_city", "end_city"]:
                    input_area.columnconfigure(0, weight=1)
                    entry = ttk.Entry(input_area)
                    entry.grid(row=0, column=0, sticky="ew")
                    self.entries.append(entry)
            else:  # For "Client" and "Airline" categories
                input_area.columnconfigure(0, weight=1)
                entry = ttk.Entry(input_area)
                entry.grid(row=0, column=0, sticky="ew")
                self.entries.append(entry)

        # The `if events:` check is a guard.
        if events:
            events.load_records(self)

    def update_dropdowns(self):
        """
        Update the choice lists for Client and Airline dropdowns.
        """
        if self.client_dropdown:
            all_clients = self.client_mgr.get_all_clients()
            client_names = [
                c.name for c in all_clients
            ] if all_clients else []
            current_selection = self.client_var.get()
            self.client_dropdown["values"] = client_names
            if client_names:
                if current_selection in client_names:
                    self.client_var.set(current_selection)
                else:
                    self.client_var.set(client_names[0])
            else:
                self.client_var.set("")

        if self.airline_dropdown:
            all_airlines = self.airline_mgr.get_all_airlines()
            airline_names = [
                a.company_name for a in all_airlines
            ] if all_airlines else []
            current_selection = self.airline_var.get()
            self.airline_dropdown["values"] = airline_names
            if airline_names:
                if current_selection in airline_names:
                    self.airline_var.set(current_selection)
                else:
                    self.airline_var.set(airline_names[0])
            else:
                self.airline_var.set("")

    def on_close(self):
        """
        Handle the application close event by destroying the root window.
        """
        self.root.destroy()
