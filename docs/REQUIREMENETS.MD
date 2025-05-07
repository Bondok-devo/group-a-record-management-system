# Software Requirements: Travel Agent Record Management System

This document outlines the functional and non-functional requirements for the Travel Agent Record Management System software.

## 1. Functional Requirements (FR)

These describe what the system must **do**.

### FR1: Record Type Management
The system shall manage three distinct types of records:
* **FR1.1:** Client Records
* **FR1.2:** Airline Company Records
* **FR1.3:** Flight Records

### FR2: Core Record Operations (CRUD)
The system shall allow users, via a Graphical User Interface (GUI), to perform the following operations for **each** of the three record types (Client, Airline, Flight):
* **FR2.1: Create Record:** Allow users to input and save new records.
* **FR2.2: Delete Record:** Allow users to select and remove existing records.
* **FR2.3: Update Record:** Allow users to modify the details of existing records.
* **FR2.4: Search and Display Record:**
    * **FR2.4.1:** Allow users to search for records based on specified criteria (e.g., Client Name, Airline Name, Flight by Client/Airline ID).
    * **FR2.4.2:** Allow users to display the details of a specific record.
    * **FR2.4.3:** Allow users to display a list of all records of a chosen type.

### FR3: Data Storage and Persistence
* **FR3.1: Internal Storage Format:** Records shall be managed internally as a list of dictionaries (e.g., `records: list = [{}, {}]`).
* **FR3.2: File System Storage Format:** Records shall be stored on the file system. The chosen format is **JSON Lines (JSONL)**.
* **FR3.3: Data Loading:** The application shall check for the existence of record files upon startup and load any existing records into memory.
* **FR3.4: Data Saving:** The application shall save all current records to the file system when the application is closed.

### FR4: Record Data Structures
The system shall adhere to the following formats for each record type:

* **FR4.1: Client Record**
    * `ID`: int (Unique identifier for the client)
    * `Type`: str (Constant string, e.g., "Client")
    * `Name`: str
    * `Address Line 1`: str
    * `Address Line 2`: str (Optional)
    * `Address Line 3`: str (Optional)
    * `City`: str
    * `State`: str
    * `Zip Code`: str
    * `Country`: str
    * `Phone Number`: str

* **FR4.2: Airline Record**
    * `ID`: int (Unique identifier for the airline)
    * `Type`: str (Constant string, e.g., "Airline")
    * `Company Name`: str

* **FR4.3: Flight Record**
    * `Client_ID`: int (Foreign key referencing a Client Record ID)
    * `Airline_ID`: int (Foreign key referencing an Airline Record ID)
    * `Type`: str (Constant string, e.g., "Flight")
    * `Date`: date/time (Specific format to be decided, e.g., ISO 8601 string `YYYY-MM-DDTHH:MM:SS`)
    * `Start City`: str
    * `End City`: str

### FR5: Unique Identifiers
* **FR5.1:** The system shall ensure unique `ID` values for each Client Record.
* **FR5.2:** The system shall ensure unique `ID` values for each Airline Record.

## 2. Non-Functional Requirements (NFR)

These describe the **qualities** of the system.

### NFR1: User Interface
* **NFR1.1:** The system shall provide a Graphical User Interface (GUI) for all user interactions.

### NFR2: Data Integrity
* **NFR2.1:** `Client_ID` in Flight Records must refer to a valid, existing Client Record.
* **NFR2.2:** `Airline_ID` in Flight Records must refer to a valid, existing Airline Record.
* **NFR2.3:** The system should prevent data loss or corruption during save/load operations.

### NFR3: Usability
* **NFR3.1:** The GUI should be intuitive and allow users to perform the required tasks (FR2) without undue difficulty.
* **NFR3.2:** Error messages displayed to the user should be clear and helpful.

### NFR4: Maintainability & Code Quality
* **NFR4.1:** The codebase should be well-organized into modules.
* **NFR4.2:** Code should be readable and understandable, adhering to PEP 8 Python style guidelines.
* **NFR4.3:** Code should include comments and docstrings where appropriate to explain logic.
* **NFR4.4:** The software design should support unit testing of its modules to ensure correctness and facilitate maintenance.

### NFR5: Reliability
* **NFR5.1:** The application should handle common user errors gracefully (e.g., invalid input in forms) without crashing.
* **NFR5.2:** Data saving and loading operations should be reliable.

---