# Travel Agent Record Management System

A desktop application for managing client, airline, and flight records for a specialist travel agency. This application is built using Python and Tkinter for the graphical user interface.

**Repository:** [https://github.com/Bondok-devo/group-a-record-management-system.git](https://github.com/Bondok-devo/group-a-record-management-system.git)

---

## Features

* Manage Client records (Add, Update, Delete, Search, View All)
* Manage Airline records (Add, Update, Delete, Search, View All)
* Manage Flight records (Add, Update, Delete, Search, View All)
* Data persistence using JSONL files.
* Configuration of data file paths via a committed `.env` file, loaded using `python-dotenv`.

---

## Prerequisites

Before you begin, ensure you have the following installed on your system:

* **Python 3.12.x:** This project requires Python version 3.12.
* **pip:** Python's package installer (usually comes with Python).
* **Git:** For cloning the repository.
* **Visual Studio Code (VS Code):** Recommended editor for this project, with the Python extension installed.

### Installing Python 3.12.x

If you don't have Python 3.12 installed, follow these instructions for your operating system:

* **Windows:**
    1.  Go to the official Python website: [python.org/downloads/windows/](https://www.python.org/downloads/windows/)
    2.  Download the latest Python 3.12.x installer (e.g., "Windows installer (64-bit)").
    3.  Run the installer.
    4.  **Important:** On the first page of the installer, make sure to check the box that says **"Add Python 3.12 to PATH"** or **"Add python.exe to PATH"**.
    5.  Click "Install Now" or choose "Customize installation" if needed.
    6.  After installation, open Command Prompt or PowerShell and type `python --version` or `py --version` to verify it's 3.12.x.

* **macOS:**
    1.  **Using Homebrew (Recommended):**
        * If you don't have Homebrew, install it from [brew.sh](https://brew.sh/).
        * Open Terminal and run:
            ```bash
            brew install python@3.12
            ```
        * After installation, Homebrew might give you instructions on adding Python 3.12 to your `PATH` if it's not already linked. Typically, Homebrew handles this.
        * Verify by opening a new terminal window and typing: `python3.12 --version` (or `python3 --version` if Homebrew made it the default `python3`).
    2.  **Using the official installer:**
        * Go to [python.org/downloads/macos/](https://www.python.org/downloads/macos/)
        * Download the macOS 64-bit universal2 installer for Python 3.12.x.
        * Run the installer package.
        * Verify by opening Terminal and typing `python3 --version`.

* **Linux:**
    * The method varies by distribution.
    * **Debian/Ubuntu:**
        ```bash
        sudo apt update
        sudo apt install python3.12 python3.12-venv python3-pip
        ```
        (You might need to add a PPA like `deadsnakes` if 3.12 isn't in the default repositories: `sudo add-apt-repository ppa:deadsnakes/ppa`)
    * **Fedora:**
        ```bash
        sudo dnf install python3.12 python3.12-venv
        ```
    * Verify by opening a terminal and typing `python3.12 --version` or `python3 --version`.

---

## Getting Started

Follow these instructions to set up the project locally and run the application.

**1. Clone the Repository:**
    Open your terminal or command prompt and run:
    ```bash
    git clone [https://github.com/Bondok-devo/group-a-record-management-system.git](https://github.com/Bondok-devo/group-a-record-management-system.git)
    cd group-a-record-management-system
    ```

**2. Create and Activate a Virtual Environment:**
    Using a virtual environment is crucial for managing project dependencies in isolation. We'll name it `.venv`.
    * **Navigate to the project root directory (`group-a-record-management-system`):**
        * Ensure you are in the cloned project directory.
    * **Create the virtual environment using your Python 3.12 interpreter:**
        * *Note: Replace `python3.12` with the command that runs your Python 3.12 installation. On Windows, it might be `py -3.12` or `python` if `PATH` is set correctly.*
        ```bash
        python3.12 -m venv .venv
        ```
    * **Activate the virtual environment:**
        * macOS/Linux:
            ```bash
            source .venv/bin/activate
            ```
        * Windows (Command Prompt):
            ```bash
            .\.venv\Scripts\activate
            ```
        * Windows (PowerShell):
            ```bash
            .\.venv\Scripts\Activate.ps1
            ```
    Your terminal prompt should change to indicate that the virtual environment is active (e.g., `(.venv) ...`).

**3. Install Dependencies:**
    With the virtual environment activated, install the required Python packages listed in `requirements.txt`:
    ```bash
    pip install -r requirements.txt
    ```

**4. Configure VS Code Python Interpreter (Important for Running from VS Code):**
    To ensure VS Code uses the Python interpreter from your virtual environment (which has the necessary packages like `python-dotenv` installed):
    * **Open your `group-a-record-management-system` folder in VS Code.**
    * **Open the Command Palette:**
        * Menu: **View > Command Palette…**
        * Shortcut (macOS): `Shift + Command + P` (⇧⌘P)
        * Shortcut (Windows/Linux): `Ctrl + Shift + P`
    * **In the Command Palette, type `Python: Select Interpreter` and click on the command when it appears.**
    * **A list of Python interpreters will be shown. Select the one that corresponds to your virtual environment. It will typically include `.venv` in its name or path, for example:**
        * `Python 3.12.x ('.venv')`
        * `./.venv/bin/python` (or the full path to it)
    * **If your `.venv` interpreter is not listed, you can choose "Enter interpreter path..." and manually browse to `.venv/bin/python` (or `.venv\Scripts\python.exe` on Windows) within your project folder.**
    * **After selecting, check the bottom-left corner of the VS Code status bar. It should now display the Python version followed by `('.venv')` or the path to your virtual environment's interpreter.**

**5. Environment Configuration (`.env` file):**
    This application uses an `.env` file located in the project root directory to define the paths for data storage files. A default `.env` file is included in this repository.

    The default `.env` file (e.g., `group-a-record-management-system/.env`) specifies paths like:
    ```ini
    # group-a-record-management-system/.env
    TRMS_CLIENT_DATA_FILE="src/data/client_record.jsonl"
    TRMS_AIRLINE_DATA_FILE="src/data/airline_record.jsonl"
    TRMS_FLIGHT_DATA_FILE="src/data/flight_record.jsonl"
    ```

    No action is required if these default paths are suitable for your setup. The application will use these paths to read and write data. The `src/data/` directory and the empty data files are expected to be part of the repository or created by the application on first run if the managers are designed to do so.

    If you need to use different paths (e.g., absolute paths or a different directory structure for your local development), you can modify this `.env` file locally (be careful not to commit these personal changes if they are not intended for everyone). For deployment-specific scenarios, setting actual system environment variables would override the `.env` file values.

    Data Format: The application expects data files to be in JSONL format (one JSON object per line).

**6. Ensure Data Directory and Files Exist (Initial Run):**
    Based on the default paths in the `.env` file, ensure the `src/data/` directory exists within your project structure.

    If the data files (`client_record.jsonl`, etc.) do not exist upon first run, the ClientManager (and presumably other managers) are designed to handle this gracefully, typically by starting with an empty set of records and creating the files upon the first save operation.

**7. Running the Application:**
    There are two primary ways to run the application:

    * **Method 1: From the Terminal (Recommended for initial setup verification)**
        * Ensure your virtual environment is activated (you should see `(.venv)` in your terminal prompt).
        * Make sure you are in the project root directory (e.g., `group-a-record-management-system/`) in your terminal.
        * Execute the main script:
            ```bash
            python3 src/main.py
            ```

    * **Method 2: From VS Code (Using the "Run" button)**
        * Ensure the correct Python interpreter is selected in VS Code (as described in step 4 of "Getting Started"). This is crucial.
        * Open the `src/main.py` file in the VS Code editor.
        * **You can run the file in several ways:**
            * Click the **Run Python File** button (often a green triangle icon) in the top-right of the editor window.
            * Right-click anywhere in the `main.py` editor window and select **Run Python File in Terminal**.
            * Open the **Run and Debug** view (the icon with a play button and a bug on the sidebar) and click the green play button (usually "Run Python File").

    The application GUI should launch.

**8. Project Structure:**
    A brief overview of the project's directory layout:
    ```text
    group-a-record-management-system/
    ├── .env                      # Environment variables for data paths (committed)
    ├── .gitignore                # Specifies intentionally untracked files
    ├── requirements.txt          # Project dependencies
    ├── src/
    │   ├── __init__.py           # Makes 'src' a package
    │   ├── main.py               # Main application entry point
    │   ├── conf/
    │   │   ├── __init__.py       # Makes 'conf' a sub-package
    │   │   └── config_loader.py  # Loads paths from .env or defaults
    │   ├── data/                 # Default directory for JSONL data files
    │   │   ├── client_record.jsonl
    │   │   ├── airline_record.jsonl
    │   │   └── flight_record.jsonl
    │   ├── gui/
    │   │   ├── __init__.py       # Makes 'gui' a sub-package
    │   │   ├── gui.py            # Defines the TravelApp GUI class (Tkinter)
    │   │   └── events.py         # Event handling logic for the GUI
    │   └── record/
    │       ├── __init__.py       # Makes 'record' a sub-package
    │       ├── client_manager.py
    │       ├── client_record.py
    │       ├── airline_manager.py
    │       ├── airline_record.py
    │       ├── flight_manager.py
    │       └── flight_record.py
    └── .venv/                    # Virtual environment directory (should be in .gitignore)
    ```

**9. Development:**
    * **Virtual Environment:** Always activate your virtual environment (`source .venv/bin/activate` or equivalent) before running the application or installing new packages.
    * **Dependencies:** If you add new dependencies to the project, update the `requirements.txt` file:
        ```bash
        pip freeze > requirements.txt
        ```
        Then commit the updated `requirements.txt`.
    * **Code Quality:** `Pylint` is recommended for checking code quality.

---