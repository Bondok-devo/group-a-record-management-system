# src/record/client_record.py
"""
Defines the ClientRecord class, representing a single client's information.
This module is responsible for the structure and basic validation of client data.
"""

from typing import Dict, Any, Optional

class ClientRecord:
    """
    Represents a single client's information in the system.

    This class holds all the details for a client and provides methods
    to convert the client's data to and from a dictionary format, which
    is handy for saving to files like JSON.
    """
    def __init__(self,
                 name: str,
                 address_line_1: str,
                 city: str,
                 state: str,
                 zip_code: str,
                 country: str,
                 phone_number: str,
                 client_id: Optional[int] = None, # Usually assigned by the manager
                 record_type: str = "Client",     # Should consistently be "Client"
                 address_line_2: str = "",
                 address_line_3: str = ""):
        """
        Initializes a new ClientRecord.

        Args:
            name (str): The client's full name.
            address_line_1 (str): The primary line of the client's address.
            city (str): The city where the client resides.
            state (str): The state or province.
            zip_code (str): The postal or ZIP code.
            country (str): The client's country.
            phone_number (str): The client's contact phone number.
            client_id (Optional[int]): The unique ID for this client. Typically assigned
                                       by a ClientManager when the record is added.
            record_type (str): The type of this record, defaults to "Client". This helps
                               differentiate record types if they are stored together.
            address_line_2 (str): Optional second line of the address.
            address_line_3 (str): Optional third line of the address.
        """
        # Let's do some basic checks to ensure we're getting reasonable data.
        if not name or not isinstance(name, str):
            raise ValueError("Client name must be a non-empty string.")
        if not address_line_1 or not isinstance(address_line_1, str):
            raise ValueError("Address Line 1 must be a non-empty string.")
        # ... you can add more validation for other mandatory fields (city, state, etc.)

        self.client_id: Optional[int] = client_id
        self.record_type: str = record_type # Should always be "Client" for this class
        self.name: str = name
        self.address_line_1: str = address_line_1
        self.address_line_2: str = address_line_2 if address_line_2 else ""
        self.address_line_3: str = address_line_3 if address_line_3 else ""
        self.city: str = city
        self.state: str = state
        self.zip_code: str = zip_code
        self.country: str = country
        self.phone_number: str = phone_number

    def __str__(self) -> str:
        """
        Provides a user-friendly string representation of the client.
        Great for printing client details in a readable way.
        """
        address_parts = [self.address_line_1, self.address_line_2, self.address_line_3]
        # Only join parts that have content
        full_address = ", ".join(part for part in address_parts if part)
        client_id_str = str(self.client_id) if self.client_id is not None else 'N/A'
        return (
            f"Client ID: {client_id_str}\n"
            f"  Name: {self.name}\n"
            f"  Type: {self.record_type}\n"
            f"  Address: {full_address}\n"
            f"           {self.city}, {self.state} {self.zip_code}\n"
            f"           {self.country}\n"
            f"  Phone: {self.phone_number}"
        )

    def __repr__(self) -> str:
        """
        Provides an unambiguous string representation of the client object.
        This is super helpful for developers during debugging.
        """
        return (
            f"ClientRecord(client_id={self.client_id!r}, "
            f"record_type={self.record_type!r}, name={self.name!r}, "
            f"address_line_1={self.address_line_1!r}, "
            f"address_line_2={self.address_line_2!r}, "
            f"address_line_3={self.address_line_3!r}, city={self.city!r}, "
            f"state={self.state!r}, zip_code={self.zip_code!r}, "
            f"country={self.country!r}, phone_number={self.phone_number!r})"
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the ClientRecord object into a dictionary.
        This is perfect for when you need to save the data to JSON.
        """
        return {
            "client_id": self.client_id,
            "record_type": self.record_type, # Consistently "Client"
            "name": self.name,
            "address_line_1": self.address_line_1,
            "address_line_2": self.address_line_2,
            "address_line_3": self.address_line_3,
            "city": self.city,
            "state": self.state,
            "zip_code": self.zip_code,
            "country": self.country,
            "phone_number": self.phone_number,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ClientRecord':
        """
        Creates a ClientRecord object from a dictionary.
        This is used when loading data, for example, from a JSON file.
        It expects the dictionary to have keys that match the ClientRecord attributes.
        """
        if not isinstance(data, dict):
            raise TypeError("To create a ClientRecord from_dict, data must be a dictionary.")

        required_fields = [
            "name", "address_line_1", "city", "state", "zip_code", "country", "phone_number"
        ]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Cannot create ClientRecord. Missing required field: "
                                 f"'{field}' in data: {data}")

        if data.get("record_type") and data.get("record_type") != "Client":
            print(f"Warning: ClientRecord.from_dict received record_type "
                  f"'{data.get('record_type')}', expected 'Client'.")

        return cls(
            client_id=data.get("client_id"),
            record_type="Client", # Enforce or default to "Client"
            name=data["name"],
            address_line_1=data["address_line_1"],
            address_line_2=data.get("address_line_2", ""),
            address_line_3=data.get("address_line_3", ""),
            city=data["city"],
            state=data["state"],
            zip_code=data["zip_code"],
            country=data["country"],
            phone_number=data["phone_number"],
        )

# This part is just for a quick test if you run this file directly.
if __name__ == "__main__":
    print("--- ClientRecord Class Direct Test ---")
    try:
        # Example 1: Creating a new client
        client1 = ClientRecord(
            name="Alice Wonderland",
            address_line_1="123 Rabbit Hole Lane",
            address_line_2="Apt 1A",
            city="Curious City",
            state="WONDER",
            zip_code="12345",
            country="Wonderland",
            phone_number="555-ALICE",
            client_id=1 # Manually setting ID for this test
        )
        print("\nClient 1 (created directly):")
        print(client1)
        # Breaking up the repr print for line length
        client1_repr = repr(client1)
        print(f"\nRepresentation (part 1): {client1_repr[:80]}")
        if len(client1_repr) > 80:
            print(f"Representation (part 2): {client1_repr[80:]}")


        # Example 2: Converting to dictionary
        client1_dict = client1.to_dict()
        print("\nClient 1 as dictionary:")
        print(client1_dict)

        # Example 3: Creating from a dictionary (simulating loading from JSON)
        client2_data = {
            "client_id": 2,
            "record_type": "Client",
            "name": "Bob The Builder",
            "address_line_1": "456 Construction Ave",
            "city": "Buildsville",
            "state": "TOOL",
            "zip_code": "67890",
            "country": "Constructland",
            "phone_number": "555-BOB"
        }
        client2 = ClientRecord.from_dict(client2_data)
        print("\nClient 2 (created from dictionary):")
        print(client2)

        # Example 4: Missing required field in from_dict
        print("\nAttempting to create client with missing 'name' (should fail):")
        try:
            bad_data = client2_data.copy()
            del bad_data["name"]
            ClientRecord.from_dict(bad_data)
        except ValueError as e:
            print(f"Successfully caught error: {e}")

    except (ValueError, TypeError) as e:
        print(f"An error occurred during testing: {e}")
