import json
import os

# ---------- DATABASE FILE ----------

# Store the data in a JSON file in the same folder.
DATA_FILE = "hospital_database.json"


# ---------- PATIENT FIELDS ----------

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


# ---------- DEFAULT DATABASE ----------

# Default login account and empty patient records.
DEFAULT_DATA = {
    "users": [
        {
            "username": "admin",
            "password": "admin123"
        }
    ],

    "patients": [],

    "beds": [
        {
            "bed_id": "Bed 101",
            "status": "Available",
            "patient_id": ""
        },
        {
            "bed_id": "Bed 102",
            "status": "Available",
            "patient_id": ""
        },
        {
            "bed_id": "Bed 103",
            "status": "Available",
            "patient_id": ""
        },
        {
            "bed_id": "Bed 104",
            "status": "Available",
            "patient_id": ""
        },
        {
            "bed_id": "Bed 105",
            "status": "Available",
            "patient_id": ""
        },
        {
            "bed_id": "Bed 106",
            "status": "Available",
            "patient_id": ""
        }
    ]
}


# ---------- LOAD DATABASE ----------

def load_database():

    # Check whether the JSON file exists.
    if not os.path.exists(DATA_FILE):

        # Create the file if it does not exist.
        save_database(DEFAULT_DATA)

        return json.loads(json.dumps(DEFAULT_DATA))

    # Open and read the existing JSON file.
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

    except (json.JSONDecodeError, OSError):
        # Show an error if the file cannot be read.
        print("Error: Unable to read the database file.")

        # Return an empty copy of the default data.
        return json.loads(json.dumps(DEFAULT_DATA))

    # Make sure all sections exist.
    if "users" not in data:
        data["users"] = DEFAULT_DATA["users"]

    if "patients" not in data:
        data["patients"] = []

    if "beds" not in data:
        data["beds"] = DEFAULT_DATA["beds"]

    # Add any missing fields to existing patient records.
    for patient in data["patients"]:
        for field in PATIENT_FIELDS:
            if field not in patient:
                patient[field] = ""

    # Add missing information to existing beds.
    for bed in data["beds"]:
        if "bed_id" not in bed:
            bed["bed_id"] = ""
        if "status" not in bed:
            bed["status"] = "Available"
        if "patient_id" not in bed:
            bed["patient_id"] = ""

    # Save the updated database structure.
    save_database(data)
    return data


# ---------- SAVE DATABASE ----------

def save_database(data):

    # Open the JSON file in write mode.
    with open(DATA_FILE, "w", encoding="utf-8") as file:

        # Convert the dictionary into readable JSON.
        json.dump(data, file, indent=4, ensure_ascii=False)
