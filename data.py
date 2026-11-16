import json
import os

# Name of the database file
DATA_FILE = "hospital_database.json"

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
    "admission_history",
    "bed_transfer_history"
]

# Default data
DEFAULT_DATA = {
    "users": [
        {
            "username": "admin",
            "password": "admin123"
        }
    ],
    "patients": [],
    "beds": []
}

# Generate default bed records
for number in range(301, 311):
    DEFAULT_DATA["beds"].append({
        "bed_id": f"Bed {number}",
        "room_type": "ICU",
        "status": "Available",
        "patient_id": ""
    })

for number in range(311, 331):
    DEFAULT_DATA["beds"].append({
        "bed_id": f"Bed {number}",
        "room_type": "Nursery",
        "status": "Available",
        "patient_id": ""
    })

for number in range(201, 207):
    DEFAULT_DATA["beds"].append({
        "bed_id": f"Bed {number}",
        "room_type": "Single-bedded",
        "status": "Available",
        "patient_id": ""
    })

for number in range(207, 235):
    DEFAULT_DATA["beds"].append({
        "bed_id": f"Bed {number}",
        "room_type": "Double-bedded",
        "status": "Available",
        "patient_id": ""
    })

for number in range(101, 141):
    DEFAULT_DATA["beds"].append({
        "bed_id": f"Bed {number}",
        "room_type": "Four-bedded",
        "status": "Available",
        "patient_id": ""
    })


# Create a separate copy of the default data
def create_default_data():
    return json.loads(json.dumps(DEFAULT_DATA))


# Save data to the JSON file
def save_database(data):
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


# Add missing sections to the database
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

                if field in ["admission_history", "bed_transfer_history"]:
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


# Load data from the JSON file
def load_database():

    # Create the database if it does not exist
    if not os.path.exists(DATA_FILE):
        data = create_default_data()
        save_database(data)
        return data

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

    except (json.JSONDecodeError, OSError):
        print("Error: Unable to read the database file.")
        return create_default_data()

    # Check and update database structure
    add_missing_sections(data)
    add_missing_beds(data)
    update_patient_fields(data)
    update_bed_fields(data)

    # Save any updates to the database structure
    save_database(data)

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
