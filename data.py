import json
import os

# CONFIGURATION & DEFAULT DATA
DATA_FILE = "hospital_database.json"
DEFAULT_DATA = {
    "users": [
        {"username": "admin", "password": "admin123"}
    ],
    "patients": [
        {"patient_id": "", "name": "", "dob": "", "gender": "", "phone": "", 
         "address": "", "emergency_contact": "", "diagnosis": "", 
         "bed_id": "", "admission_date": "", "status": "", 
         "discharge_date": "", "payment_confirmed": ""}
    ],
    "beds": [
        {"bed_id": f"Bed {num}", "status": "Available", "patient_id": ""} 
        for num in range(101, 107)
    ]
}


# LOAD DATA FROM FILE 
def load_database():
    """Loads the entire database from a single JSON file. 
       If the file doesn't exist, it creates one with default data."""
    if not os.path.exists(DATA_FILE):
        save_database(DEFAULT_DATA)
        return DEFAULT_DATA

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        # If the file is corrupted or empty, reset it to default
        return DEFAULT_DATA


#SAVE DATA TO FILE
def save_database(data):
    """Saves the entire database dictionary into the JSON file."""
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        # indent=4 makes the text file nicely formatted and easy to read
        json.dump(data, file, indent=4)


# ==========================================
# MAIN PROGRAM EXECUTION
# ==========================================

# Load the database into a single memory variable
db = load_database()

# Access your data easily using dictionary keys
users = db["users"]
patients = db["patients"]
beds = db["beds"]

print("System loaded successfully using a single JSON file!")
print(f"Loaded: {len(users)} user(s), {len(patients)} patient(s), and {len(beds)} bed(s).")


# ---------- EXAMPLE: HOW TO ADD DATA AND SAVE ----------
# To add a new patient, you just append to the list and call save_database(db)!
#
# new_patient = {
#     "patient_id": "P001",
#     "name": "Jane Doe",
#     "diagnosis": "Checkup",
#     "status": "Admitted"
# }
#
# db["patients"].append(new_patient)
# save_database(db)
# print("New patient saved!")