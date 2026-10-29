import json
import os

# Name of the database file
DATA_FILE = "hospital_database.json"

# Fields used to store patient information
PATIENT_FIELDS = [
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
    "payment_confirmed"
]

# Default data used when the database does not exist
DEFAULT_DATA = {
    "users": [
        {
            "username": "admin",
            "password": "admin123"
        }
    ],
    "patients": [],
    "beds": [
        {"bed_id": "Bed 101", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 102", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 103", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 104", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 105", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 106", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 107", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 108", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 109", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 110", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 201", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 202", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 203", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 204", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 205", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 206", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 207", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 208", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 209", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 210", "status": "Available", "patient_id": ""}
    ]
}

# Save data to the JSON file
def save_database(data):
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

# Load data from the JSON file
def load_database():

# Create the database if it does not exist
    if not os.path.exists(DATA_FILE):
        save_database(DEFAULT_DATA)
        return json.loads(json.dumps(DEFAULT_DATA))

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

    except (json.JSONDecodeError, OSError):
        print("Error: Unable to read the database file.")
        return json.loads(json.dumps(DEFAULT_DATA))

# Add missing sections if necessary
    if "users" not in data:
        data["users"] = json.loads(json.dumps(DEFAULT_DATA["users"]))

    if "patients" not in data:
        data["patients"] = []

    if "beds" not in data:
        data["beds"] = json.loads(json.dumps(DEFAULT_DATA["beds"]))

# Add missing fields to existing patient records
    for patient in data["patients"]:
        for field in PATIENT_FIELDS:
            if field not in patient:
                patient[field] = ""

# Give older records a default status
        if not patient["status"]:
            patient["status"] = "Registered"

# Add missing fields to existing bed records
    for bed in data["beds"]:
        if "bed_id" not in bed:
            bed["bed_id"] = ""

        if "status" not in bed:
            bed["status"] = "Available"

        if "patient_id" not in bed:
            bed["patient_id"] = ""

# Save any updates to the database structure
    save_database(data)
    return data
