# src/record/airline_record.py
"""
Defines the AirlineRecord class, representing a single airline's information.
This module is responsible for the structure and basic validation of airline data.
"""

from typing import Dict, Any, Optional

class AirlineRecord:
    """
    Represents a single airline company's information in the system.

    This class holds the details for an airline and provides methods
    to convert the airline's data to and from a dictionary format,
    which is useful for saving to files like JSON.
    """
    def __init__(self,
                 record_type: str, # Type of record as per requirements
                 company_name: str,
                 airline_id: Optional[int] = None): # Pylint friendly naming
        """
        Initializes a new AirlineRecord.

        Args:
            record_type (str): The type of record (e.g., "Airline").
            company_name (str): The official name of the airline company.
            airline_id (Optional[int]): The unique ID for this airline. Typically
                                      assigned by an AirlineManager.
        """
        if not record_type or not isinstance(record_type, str):
            raise ValueError("Record type must be a non-empty string.")
        if not company_name or not isinstance(company_name, str):
            raise ValueError("Airline company name must be a non-empty string.")
        if airline_id is not None and not isinstance(airline_id, int):
            raise ValueError("Airline ID must be an integer if provided.")

        self.airline_id: Optional[int] = airline_id # Internal attribute reverted
        self.record_type: str = record_type
        self.company_name: str = company_name

    def __str__(self) -> str:
        """
        Provides a user-friendly string representation of the airline.
        """
        id_str = str(self.airline_id) if self.airline_id is not None else 'N/A'
        return (
            f"Airline ID: {id_str}\n" # Displayed as "Airline ID"
            f"  Type: {self.record_type}\n"
            f"  Company Name: {self.company_name}"
        )

    def __repr__(self) -> str:
        """
        Provides an unambiguous string representation of the airline object.
        Helpful for debugging.
        """
        return (
            f"AirlineRecord(airline_id={self.airline_id!r}, " # Constructor uses airline_id
            f"record_type={self.record_type!r}, "
            f"company_name={self.company_name!r})"
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the AirlineRecord object into a dictionary.
        The key for the identifier is "airline_id" for consistency.
        Suitable for JSON serialization.
        """
        return {
            "airline_id": self.airline_id, # Key is "airline_id"
            "record_type": self.record_type,
            "company_name": self.company_name,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AirlineRecord':
        """
        Creates an AirlineRecord object from a dictionary.
        Expects the identifier key to be "airline_id" from the data source.
        Used when loading data, e.g., from a JSON file.
        """
        if not isinstance(data, dict):
            raise TypeError("To create an AirlineRecord from_dict, data must be a dictionary.")

        required_fields = ["record_type", "company_name"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Cannot create AirlineRecord. Missing required field: "
                                 f"'{field}' in data: {data}")

        return cls(
            # Expects "airline_id" key from data, passes it as airline_id to constructor
            airline_id=data.get("airline_id"),
            record_type=data["record_type"],
            company_name=data["company_name"]
        )

# This part is for a quick test if you run this file directly.
if __name__ == "__main__":
    print("--- AirlineRecord Class Direct Test ---")
    try:
        # Example 1: Creating a new airline
        airline1 = AirlineRecord(
            record_type="Airline",
            company_name="Galaxy Airlines",
            airline_id=201 # Using airline_id for constructor
        )
        print("\nAirline 1 (created directly):")
        print(airline1) # __str__ will show "Airline ID: 201"
        print(f"Internal self.airline_id: {airline1.airline_id}")
        print(f"Representation: {repr(airline1)}")

        # Example 2: Converting to dictionary
        airline1_dict = airline1.to_dict()
        print("\nAirline 1 as dictionary (should have 'airline_id' key):")
        print(airline1_dict)

        # Example 3: Creating from a dictionary (expects "airline_id" key)
        airline2_data = {
            "airline_id": 202, # Data from file/external source uses "airline_id"
            "record_type": "Airline",
            "company_name": "Cosmic Cruiselines"
        }
        airline2 = AirlineRecord.from_dict(airline2_data)
        print("\nAirline 2 (created from dictionary):")
        print(airline2) # __str__ will show "Airline ID: 202"
        print(f"Internal self.airline_id: {airline2.airline_id}")


        # Example 4: Missing required field 'company_name' in from_dict
        print("\nAttempting to create airline with missing 'company_name' (should fail):")
        try:
            bad_data_name = airline2_data.copy()
            del bad_data_name["company_name"]
            AirlineRecord.from_dict(bad_data_name)
        except ValueError as e:
            print(f"Successfully caught error for missing company_name: {e}")

        # Example 5: Missing required field 'record_type' in from_dict
        print("\nAttempting to create airline with missing 'record_type' (should fail):")
        try:
            bad_data_type = airline2_data.copy()
            del bad_data_type["record_type"]
            AirlineRecord.from_dict(bad_data_type)
        except ValueError as e:
            print(f"Successfully caught error for missing record_type: {e}")

    except (ValueError, TypeError) as e:
        print(f"An error occurred during testing: {e}")
