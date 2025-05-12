"""
GUI class definition for the Travel Records Management application.

Constructs tkinter interface and binds widgets to event functions
for managing Client, Airline, and Flight records.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from . import events

class TravelApp:
    def __init__(self, root, client_mgr, airline_mgr, flight_mgr):
        """
        A GUI application for managing travel records, including Clients, Airlines, and Flights.

        This class initializes the tkinter interface, sets up widgets, and binds them to event
        handling functions for CRUD operations.
        """

        self.root = root
        self.client_mgr = client_mgr
        self.airline_mgr = airline_mgr
        self.flight_mgr = flight_mgr
        # Initialize the rest of the GUI components here
        self.root.title("Specialist Travel Agent Records")
        self.selected_index = None

        self.fields_config = {
            "Client": ["ID", "Name", "Address Line 1", "Address Line 2", "Address Line 3",
                       "City", "State", "Zip Code", "Country", "Phone Number"],
            "Airline": ["ID", "Company Name"],
            "Flight": ["Client_ID", "Airline_ID", "Date", "Time"]
        }

        self.selected_category = tk.StringVar(value="Client")
        self.entries = []
        self.setup_widgets()
        events.load_records(self)

    def setup_widgets(self):
        """
        Set up the GUI widgets, including labels, combobox, listbox, and buttons.

        This method initializes and arranges all the widgets in the application,
        such as the category selector, form fields, record listbox, and action buttons.
        """
        ttk.Label(self.root, text="Category:").grid(row=0, column=0, padx=5, pady=(10, 5),
                                                    sticky="e")
        category_combo = ttk.Combobox(self.root, textvariable=self.selected_category,
                                      values=list(self.fields_config.keys()),
                                      state="readonly", width=30)
        category_combo.grid(row=0, column=1, padx=5, pady=(10, 5), sticky="w")
        category_combo.bind("<<ComboboxSelected>>", lambda e: events.update_fields(self))

        self.form_frame = ttk.Frame(self.root)
        self.form_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5)
        events.update_fields(self)

        self.record_listbox = tk.Listbox(self.root, height=10, width=80)
        self.record_listbox.grid(row=2, column=0, columnspan=2, padx=5, pady=5)
        self.record_listbox.bind("<<ListboxSelect>>", lambda e: events.on_select(self))

        button_frame = ttk.Frame(self.root)
        button_frame.grid(row=3, column=0, columnspan=2, pady=5)

        actions = [("Add", events.add_record), ("Update", events.update_record),
                   ("Delete", events.delete_record), ("Search", events.search_records),
                   ("Clear", events.clear_form)]
        for i, (text, cmd) in enumerate(actions):
            ttk.Button(button_frame, text=text, command=lambda
                c=cmd: c(self)).grid(row=0, column=i, padx=3)

    def on_close(self):
        """
        Handle the application close event by destroying the root window.
        """
        self.root.destroy()
