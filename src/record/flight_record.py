# src/record/flight_record.py
"""
Defines the FlightRecord class, representing a single flight's information.
This module is responsible for the structure and basic validation of flight data,
including linking to client and airline records.
"""

from datetime import datetime
from typing import Dict, Any # Removed Optional as it's not used

class FlightRecord:
    """
    Represents a single flight record in the system.

    This class holds details for a flight, including associated client and
    airline IDs, date, and route. It provides methods for data conversion
    suitable for storage and retrieval.
    """
    def __init__(self,
                 client_id: int,    # Internal attribute name
                 airline_id: int,   # Internal attribute name
                 flight_date: datetime, # Internally a datetime object
                 start_city: str,
                 end_city: str,
                 record_type: str = "flight" # Should consistently be "flight"
                 # Flight records don't have their own primary ID in the requirements,
                 # they are identified by their association and details.
                 ):
        """
        Initializes a new FlightRecord.

        Args:
            record_type (str): The type of record (e.g., "Flight").
            client_id (int): The ID of the client associated with this flight.
            airline_id (int): The ID of the airline associated with this flight.
            flight_date (datetime): The date and time of the flight.
            start_city (str): The departure city of the flight.
            end_city (str): The arrival city of the flight.
        """
        if not record_type or not isinstance(record_type, str):
            raise ValueError("Record type must be a non-empty string.")
        if not isinstance(client_id, int):
            raise ValueError("Client ID must be an integer.")
        if not isinstance(airline_id, int):
            raise ValueError("Airline ID must be an integer.")
        if not isinstance(flight_date, datetime):
            raise ValueError("Flight date must be a datetime object.")
        if not start_city or not isinstance(start_city, str):
            raise ValueError("Start city must be a non-empty string.")
        if not end_city or not isinstance(end_city, str):
            raise ValueError("End city must be a non-empty string.")

        self.record_type: str = record_type
        self.client_id: int = client_id     # Internal attribute
        self.airline_id: int = airline_id    # Internal attribute
        self.flight_date: datetime = flight_date
        self.start_city: str = start_city
        self.end_city: str = end_city

    def __str__(self) -> str:
        """
        Provides a user-friendly string representation of the flight.
        """
        date_str = self.flight_date.strftime("%Y-%m-%d %H:%M:%S") # Readable date format
        return (
            f"Flight Record (Type: {self.record_type})\n"
            f"  Client ID: {self.client_id}\n"
            f"  Airline ID: {self.airline_id}\n"
            f"  Date: {date_str}\n"
            f"  Route: {self.start_city} to {self.end_city}"
        )

    def __repr__(self) -> str:
        """
        Provides an unambiguous string representation of the flight object.
        Helpful for debugging.
        """
        return (
            f"FlightRecord(record_type={self.record_type!r}, "
            f"client_id={self.client_id!r}, airline_id={self.airline_id!r}, "
            f"flight_date={self.flight_date!r}, start_city={self.start_city!r}, "
            f"end_city={self.end_city!r})"
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the FlightRecord object into a dictionary.
        The date is converted to an ISO 8601 string format for JSON compatibility.
        Uses "Client_ID" and "Airline_ID" as keys for external consistency.
        """
        return {
            "record_type": self.record_type,
            "Client_ID": self.client_id, # External key as per requirements
            "Airline_ID": self.airline_id, # External key as per requirements
            "Date": self.flight_date.isoformat(), # Store date as ISO string
            "Start City": self.start_city,    # Using spaces as per requirements
            "End City": self.end_city         # Using spaces as per requirements
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FlightRecord':
        """
        Creates a FlightRecord object from a dictionary.
        Converts an ISO 8601 date string back to a datetime object.
        Expects "Client_ID", "Airline_ID", "Start City", "End City" as keys.
        """
        if not isinstance(data, dict):
            raise TypeError("To create a FlightRecord from_dict, data must be a dictionary.")

        required_fields = [
            "record_type", "Client_ID", "Airline_ID", "Date", "Start City", "End City"
        ]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Cannot create FlightRecord. Missing required field: "
                                 f"'{field}' in data: {data}")

        try:
            # Convert ISO date string back to datetime object
            flight_date_obj = datetime.fromisoformat(data["Date"])
        except (TypeError, ValueError) as e:
            raise ValueError(f"Invalid date format for 'Date'. Expected ISO format. "
                             f"Error: {e}") from e

        return cls(
            record_type=data["record_type"],
            client_id=data["Client_ID"],   # Expects "Client_ID" from data
            airline_id=data["Airline_ID"],  # Expects "Airline_ID" from data
            flight_date=flight_date_obj,
            start_city=data["Start City"],
            end_city=data["End City"]
        )

# This part is for a quick test if you run this file directly.
if __name__ == "__main__":
    print("--- FlightRecord Class Direct Test ---")
    try:
        # Example 1: Creating a new flight
        now = datetime.now()
        flight1_date = datetime(now.year, now.month, now.day, 14, 30) # Example: Today at 2:30 PM

        flight1 = FlightRecord(
            record_type="Flight",
            client_id=101,
            airline_id=201,
            flight_date=flight1_date,
            start_city="London",
            end_city="Paris"
        )
        print("\nFlight 1 (created directly):")
        print(flight1)
        print(f"Representation: {repr(flight1)}")

        # Example 2: Converting to dictionary
        flight1_dict = flight1.to_dict()
        print("\nFlight 1 as dictionary:")
        print(flight1_dict)
        # Check that the date is an ISO string
        assert isinstance(flight1_dict["Date"], str)

        # Example 3: Creating from a dictionary
        flight2_data = {
            "record_type": "Flight",
            "Client_ID": 102,
            "Airline_ID": 202,
            "Date": datetime(now.year + 1, 1, 15, 9, 0).isoformat(), # Next year Jan 15th 9 AM
            "Start City": "New York",
            "End City": "Tokyo"
        }
        flight2 = FlightRecord.from_dict(flight2_data)
        print("\nFlight 2 (created from dictionary):")
        print(flight2)
        # Check that the date is a datetime object
        assert isinstance(flight2.flight_date, datetime)
        print(f"Flight 2 Date Object: {flight2.flight_date}")


        # Example 4: Missing required field in from_dict
        print("\nAttempting to create flight with missing 'Start City' (should fail):")
        try:
            bad_data = flight2_data.copy()
            del bad_data["Start City"]
            FlightRecord.from_dict(bad_data)
        except ValueError as e:
            print(f"Successfully caught error: {e}")

        # Example 5: Invalid date format
        print("\nAttempting to create flight with invalid date format (should fail):")
        try:
            invalid_date_data = flight2_data.copy()
            invalid_date_data["Date"] = "Not A Date"
            FlightRecord.from_dict(invalid_date_data)
        except ValueError as e:
            print(f"Successfully caught error: {e}")

    except (ValueError, TypeError) as e:
        print(f"An error occurred during testing: {e}")
