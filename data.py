import sqlite3
import json
import os

# Name of the SQLite database file
DATA_FILE = "hospital_database.db"

# Name of the old JSON file for migration
OLD_DATA_FILE = "hospital_database.json"

# Fields used to store patient information
PATIENT_FIELDS = [
    "patient_ic",
    "patient_id",
    "name",
    "dob",
    "gender",
    "phone",
    "address",
    "emergency_contact",
    "diagnosis",
    "bed_id",
    "admission_date",
    "status",
    "discharge_date",
    "payment_confirmed",
    "admission_history"
]


# Create the default bed records
DEFAULT_BEDS = []

# ICU beds: 301-310
for number in range(301, 311):
    DEFAULT_BEDS.append({
        "bed_id": f"Bed {number}",
        "room_type": "ICU",
        "status": "Available",
        "patient_id": ""
    })

# Nursery beds: 311-330
for number in range(311, 331):
    DEFAULT_BEDS.append({
        "bed_id": f"Bed {number}",
        "room_type": "Nursery",
        "status": "Available",
        "patient_id": ""
    })

# Single-bedded rooms: 201-206
for number in range(201, 207):
    DEFAULT_BEDS.append({
        "bed_id": f"Bed {number}",
        "room_type": "Single-bedded",
        "status": "Available",
        "patient_id": ""
    })

# Double-bedded rooms: 207-234
for number in range(207, 235):
    DEFAULT_BEDS.append({
        "bed_id": f"Bed {number}",
        "room_type": "Double-bedded",
        "status": "Available",
        "patient_id": ""
    })

# Four-bedded rooms: 101-140
for number in range(101, 141):
    DEFAULT_BEDS.append({
        "bed_id": f"Bed {number}",
        "room_type": "Four-bedded",
        "status": "Available",
        "patient_id": ""
    })


# Default data used when the database does not exist
DEFAULT_DATA = {
    "users": [
        {
            "username": "admin",
            "password": "admin123"
        }
    ],
    "patients": [],
    "beds": DEFAULT_BEDS
}


# Check whether the database has been initialized
DATABASE_INITIALIZED = False


# Connect to the SQLite database
def connect_database():
    connection = sqlite3.connect(DATA_FILE)
    connection.row_factory = sqlite3.Row
    return connection


# Create the database tables
def create_tables():

    connection = connect_database()
    cursor = connection.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
    """)

    # Patients table
    patient_columns = []

    for field in PATIENT_FIELDS:
        if field == "patient_id":
            patient_columns.append("patient_id TEXT PRIMARY KEY")
        else:
            patient_columns.append(f"{field} TEXT")

    cursor.execute(
        "CREATE TABLE IF NOT EXISTS patients (" +
        ", ".join(patient_columns) + ")"
    )

    # Beds table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS beds (
            bed_id TEXT PRIMARY KEY,
            room_type TEXT,
            status TEXT,
            patient_id TEXT
        )
    """)

    connection.commit()
    connection.close()


# Create a separate copy of the default data
def create_default_data():
    return json.loads(json.dumps(DEFAULT_DATA))


# Add missing sections to the database data
def add_missing_sections(data):

    if "users" not in data:
        data["users"] = create_default_data()["users"]

    if "patients" not in data:
        data["patients"] = []

    if "beds" not in data:
        data["beds"] = create_default_data()["beds"]


# Add default beds that are missing
def add_missing_beds(data):

    existing_bed_ids = {
        bed.get("bed_id", "")
        for bed in data["beds"]
    }

    for default_bed in DEFAULT_DATA["beds"]:

        if default_bed["bed_id"] not in existing_bed_ids:
            new_bed = default_bed.copy()
            data["beds"].append(new_bed)

            existing_bed_ids.add(default_bed["bed_id"])


# Add missing fields to existing patient records
def update_patient_fields(data):

    for patient in data["patients"]:

        for field in PATIENT_FIELDS:

            if field not in patient:

                if field == "admission_history":
                    patient[field] = []
                else:
                    patient[field] = ""

        # Give older records a default status
        if not patient["status"]:
            patient["status"] = "Registered"


# Add missing fields to existing bed records
def update_bed_fields(data):

    for bed in data["beds"]:

        if "bed_id" not in bed:
            bed["bed_id"] = ""

        if "status" not in bed:
            bed["status"] = "Available"

        if "patient_id" not in bed:
            bed["patient_id"] = ""

        if "room_type" not in bed:
            bed["room_type"] = "Four-bedded"


# Save data into the SQLite database
def write_database(data):

    add_missing_sections(data)
    add_missing_beds(data)
    update_patient_fields(data)
    update_bed_fields(data)

    connection = connect_database()
    cursor = connection.cursor()

    try:
        # Start a database transaction
        cursor.execute("BEGIN")

        # Replace the existing records with the updated data
        cursor.execute("DELETE FROM users")
        cursor.execute("DELETE FROM patients")
        cursor.execute("DELETE FROM beds")

        # Save user records
        for user in data["users"]:

            cursor.execute("""
                INSERT INTO users (username, password)
                VALUES (?, ?)
            """, (
                user.get("username", ""),
                user.get("password", "")
            ))

        # Save patient records
        patient_columns = ", ".join(PATIENT_FIELDS)
        placeholders = ", ".join(["?"] * len(PATIENT_FIELDS))

        for patient in data["patients"]:

            patient_values = []

            for field in PATIENT_FIELDS:

                value = patient.get(field, "")

                # Store lists and Boolean values safely
                if field in ["admission_history", "payment_confirmed"]:
                    value = json.dumps(value)

                elif value is None:
                    value = ""

                else:
                    value = str(value)

                patient_values.append(value)

            cursor.execute(
                f"INSERT INTO patients ({patient_columns}) "
                f"VALUES ({placeholders})",
                patient_values
            )

        # Save bed records
        for bed in data["beds"]:
            cursor.execute("""
                INSERT INTO beds
                (bed_id, room_type, status, patient_id)
                VALUES (?, ?, ?, ?)
            """, (
                bed.get("bed_id", ""),
                bed.get("room_type", ""),
                bed.get("status", ""),
                bed.get("patient_id", "")
            ))

        connection.commit()
    except sqlite3.Error:
        connection.rollback()
        raise
    finally:
        connection.close()


# Initialize the database and migrate old JSON data if available
def initialize_database():
    global DATABASE_INITIALIZED
    if DATABASE_INITIALIZED:
        return
    database_exists = os.path.exists(DATA_FILE)
    create_tables()
    if not database_exists:
        # Import existing JSON data if available
        if os.path.exists(OLD_DATA_FILE):
            try:
                with open(OLD_DATA_FILE, "r", encoding="utf-8") as file:
                    data = json.load(file)
                add_missing_sections(data)
                add_missing_beds(data)
                update_patient_fields(data)
                update_bed_fields(data)
                write_database(data)
                print("Existing JSON data migrated to SQLite.")

            except (json.JSONDecodeError, OSError, TypeError, ValueError):
                print("Error reading old JSON file. Using default data.")
                write_database(create_default_data())
        else:
            # Create a new database with default records
            write_database(create_default_data())

    DATABASE_INITIALIZED = True


# Save data to the SQLite database
def save_database(data):
    initialize_database()
    write_database(data)


# Load data from the SQLite database
def load_database():
    initialize_database()
    connection = connect_database()
    cursor = connection.cursor()
    data = {
        "users": [],
        "patients": [],
        "beds": []
    }

    # Load user records
    cursor.execute("SELECT * FROM users")
    for row in cursor.fetchall():
        data["users"].append(dict(row))

    # Load patient records
    cursor.execute("SELECT * FROM patients")
    for row in cursor.fetchall():
        patient = dict(row)

        # Restore admission history and payment values
        for field in ["admission_history", "payment_confirmed"]:
            try:
                patient[field] = json.loads(patient[field])
            except (json.JSONDecodeError, TypeError):
                if field == "admission_history":
                    patient[field] = []
                else:
                    patient[field] = ""
        data["patients"].append(patient)

    # Load bed records
    cursor.execute("SELECT * FROM beds")
    for row in cursor.fetchall():
        data["beds"].append(dict(row))
    connection.close()
    return data


# Get all patient records
def get_all_patients():
    data = load_database()
    return data["patients"]


# Get all bed records
def get_all_beds():
    data = load_database()
    return data["beds"]


# Get only available beds
def get_available_beds():
    data = load_database()
    available_beds = []
    for bed in data["beds"]:
        if bed.get("status") == "Available":
            available_beds.append(bed)
    return available_beds


# Find a patient using a specific field
def find_patient(value, patients, field="patient_id"):
    for patient in patients:
        if str(patient.get(field, "")).lower() == str(value).lower():
            return patient
    return None


# Search records using a keyword
def search_records(records, keyword, fields):
    results = []
    keyword = keyword.lower().strip()

    for record in records:
        for field in fields:
            value = str(record.get(field, "")).lower()
            if keyword in value:
                results.append(record)
                break

    return results
    
