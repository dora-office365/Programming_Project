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
        {"bed_id": "Bed 301", "room_type": "ICU", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 302",  "room_type": "ICU", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 303",  "room_type": "ICU", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 304",  "room_type": "ICU", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 305",  "room_type": "ICU", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 306",  "room_type": "ICU", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 307",  "room_type": "ICU", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 308",  "room_type": "ICU", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 309",  "room_type": "ICU", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 3100",  "room_type": "ICU", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 311",  "room_type": "Nursery", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 312",  "room_type": "Nursery", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 313",  "room_type": "Nursery", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 314",  "room_type": "Nursery", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 315",  "room_type": "Nursery", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 316",  "room_type": "Nursery", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 317",  "room_type": "Nursery", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 318",  "room_type": "Nursery", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 319",  "room_type": "Nursery", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 320",  "room_type": "Nursery", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 321",  "room_type": "Nursery", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 322",  "room_type": "Nursery", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 323",  "room_type": "Nursery", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 324",  "room_type": "Nursery", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 325",  "room_type": "Nursery", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 326",  "room_type": "Nursery", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 327",  "room_type": "Nursery", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 328",  "room_type": "Nursery", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 329",  "room_type": "Nursery", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 330",  "room_type": "Nursery", "status": "Available", "patient_id": ""},        
        {"bed_id": "Bed 201", "room_type": "Single-bedded", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 202",  "room_type": "Single-bedded", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 203",  "room_type": "Single-bedded", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 204",  "room_type": "Single-bedded", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 205",  "room_type": "Single-bedded", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 206",  "room_type": "Single-bedded", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 207",  "room_type": "Double-bedded" "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 208",  "room_type": "Double-bedded""status": "Available", "patient_id": ""},
        {"bed_id": "Bed 209",  "room_type": "Double-bedded", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 210", "room_type": "Double-bedded", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 211", "room_type": "Double-bedded", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 212", "room_type": "Double-bedded", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 213", "room_type": "Double-bedded", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 214", "room_type": "Double-bedded", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 215", "room_type": "Double-bedded", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 216", "room_type": "Double-bedded", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 217", "room_type": "Double-bedded", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 218", "room_type": "Double-bedded", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 219", "room_type": "Double-bedded", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 220", "room_type": "Double-bedded", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 101", "room_type": "Four-bedded", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 102", "room_type": "Four-bedded", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 103", "room_type": "Four-bedded", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 104", "room_type": "Four-bedded", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 105", "room_type": "Four-bedded", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 106", "room_type": "Four-bedded", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 107", "room_type": "Four-bedded", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 108", "room_type": "Four-bedded", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 109", "room_type": "Four-bedded", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 110", "room_type": "Four-bedded", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 111", "room_type": "Four-bedded", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 112", "room_type": "Four-bedded", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 113", "room_type": "Four-bedded", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 114", "room_type": "Four-bedded", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 115", "room_type": "Four-bedded", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 116", "room_type": "Four-bedded", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 117", "room_type": "Four-bedded", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 118", "room_type": "Four-bedded", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 119", "room_type": "Four-bedded", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 120", "room_type": "Four-bedded", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 121", "room_type": "Four-bedded", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 122", "room_type": "Four-bedded", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 123", "room_type": "Four-bedded", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 124", "room_type": "Four-bedded", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 125", "room_type": "Four-bedded", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 126", "room_type": "Four-bedded", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 127", "room_type": "Four-bedded", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 128", "room_type": "Four-bedded", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 129", "room_type": "Four-bedded", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 130", "room_type": "Four-bedded", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 131", "room_type": "Four-bedded", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 132", "room_type": "Four-bedded", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 133", "room_type": "Four-bedded", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 134", "room_type": "Four-bedded", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 135", "room_type": "Four-bedded", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 136", "room_type": "Four-bedded", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 137", "room_type": "Four-bedded", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 138", "room_type": "Four-bedded", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 139", "room_type": "Four-bedded", "status": "Available", "patient_id": ""},
        {"bed_id": "Bed 140", "room_type": "Four-bedded", "status": "Available", "patient_id": ""}
    ]
}


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
