import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
import dashboard

from data import (
    PATIENT_FIELDS,
    load_database,
    save_database,
    get_available_beds,
    find_patient,
    search_records
)


# Pink theme colours
PINK_DARK = "#7D3458"
PINK_ACTIVE = "#AD5B82"
PINK_LIGHT = "#FFF4F8"
PINK_PALE = "#FCE7F0"
PINK_BORDER = "#EAC5D5"
TEXT_DARK = "#49323D"
TEXT_LIGHT = "#A45B7D"
WHITE = "#FFFFFF"


# Generate Patient ID automatically
def generate_patient_id():
    data = load_database()
    patients = data.get("patients", [])

    highest_number = 0

    for patient in patients:
        patient_id = str(patient.get("patient_id", ""))

        if patient_id.startswith("P") and patient_id[1:].isdigit():
            number = int(patient_id[1:])

            if number > highest_number:
                highest_number = number

    return f"P{highest_number + 1:04d}"


def show_patients(root):
    # Load the shared JSON database
    data = load_database()
    patients = data["patients"]
    beds = data["beds"]

    # Clear the previous page
    for widget in root.winfo_children():
        widget.destroy()

    root.title("Careflow - Patient Information")
    root.geometry("1150x750")
    root.configure(bg=PINK_LIGHT)

    # Shared navigation menu
    content = dashboard.add_navigation(
        root, "Patient Information"
    )

    # Page heading
    tk.Label(
        content,
        text="Patient Information",
        font=("Arial", 24, "bold"),
        bg=PINK_LIGHT,
        fg=PINK_DARK
    ).pack(anchor="w", padx=20, pady=(15, 5))

    tk.Label(
        content,
        text="Register, search and update patient records",
        font=("Arial", 11),
        bg=PINK_LIGHT,
        fg=TEXT_DARK
    ).pack(anchor="w", padx=20, pady=(0, 10))

    # Main content area
    main_content = tk.Frame(content, bg=PINK_LIGHT)
    main_content.pack(
        fill="both",
        expand=True,
        padx=15,
        pady=(0, 12)
    )

    # Patient information form
    form = tk.LabelFrame(
        main_content,
        text="Patient Details",
        font=("Arial", 11, "bold"),
        bg=WHITE,
        fg=PINK_DARK,
        padx=10,
        pady=8
    )
    form.pack(side="left", fill="y", padx=(0, 12))

    # Patient fields
    fields = [
        ("Patient IC (without '-')", "patient_ic"),
        ("Patient ID", "patient_id"),
        ("Full Name", "name"),
        ("Date of Birth (e.g. 2005-08-21)", "dob"),
        ("Phone (e.g. 0123456789)", "phone"),
        ("Address", "address"),
        ("Emergency Contact (e.g. 0123456789)", "emergency_contact"),
        ("Diagnosis", "diagnosis")
    ]

    entries = {}

    # Create text fields
    for row, (label_text, field_name) in enumerate(fields):
        tk.Label(
            form,
            text=label_text,
            bg=WHITE,
            fg=TEXT_DARK,
            font=("Arial", 9)
        ).grid(row=row, column=0, sticky="w", pady=4)

        # Patient ID is read-only
        if field_name == "patient_id":
            entry = tk.Entry(
                form,
                width=19,
                font=("Arial", 9),
                state="readonly"
            )
        else:
            entry = tk.Entry(
                form,
                width=19,
                font=("Arial", 9)
            )

        entry.grid(
            row=row,
            column=1,
            padx=(6, 0),
            pady=4
        )

        entries[field_name] = entry

    # Display a Patient ID in the read-only field
    def set_patient_id(patient_id):
        entry = entries["patient_id"]

        entry.config(state="normal")
        entry.delete(0, tk.END)
        entry.insert(0, patient_id)
        entry.config(state="readonly")

    # Gender selection
    tk.Label(
        form,
        text="Gender",
        bg=WHITE,
        fg=TEXT_DARK,
        font=("Arial", 9)
    ).grid(row=8, column=0, sticky="w", pady=4)

    gender_box = ttk.Combobox(
        form,
        values=["Female", "Male", "Other"],
        state="readonly",
        width=17
    )
    gender_box.grid(
        row=8,
        column=1,
        padx=(6, 0),
        pady=4
    )

    # Room type selection
    tk.Label(
        form,
        text="Room Type",
        bg=WHITE,
        fg=TEXT_DARK,
        font=("Arial", 9)
    ).grid(row=9, column=0, sticky="w", pady=4)

    room_type_box = ttk.Combobox(
        form,
        values=[
            "Four-bedded",
            "Double-bedded",
            "Single-bedded",
            "Nursery",
            "ICU"
        ],
        state="readonly",
        width=17
    )
    room_type_box.grid(
        row=9,
        column=1,
        padx=(6, 0),
        pady=4
    )

    # Automatically assigned bed
    tk.Label(
        form,
        text="Assigned Bed",
        bg=WHITE,
        fg=TEXT_DARK,
        font=("Arial", 9)
    ).grid(row=10, column=0, sticky="w", pady=4)

    bed_var = tk.StringVar()

    bed_entry = ttk.Entry(
        form,
        textvariable=bed_var,
        state="readonly",
        width=19
    )
    bed_entry.grid(
        row=10,
        column=1,
        padx=(6, 0),
        pady=4
    )

    # Remember the selected patient
    selected_id = [""]

    # Remember whether the selected row is a previous admission
    selected_record_type = [""]

    # Remember the IC of the automatically retrieved patient
    lookup_ic = [""]

    # Patient records section
    result = tk.LabelFrame(
        main_content,
        text="Patient Records",
        font=("Arial", 11, "bold"),
        bg=WHITE,
        fg=PINK_DARK,
        padx=8,
        pady=8
    )
    result.pack(
        side="right",
        fill="both",
        expand=True
    )

    # Search box
    tk.Label(
        result,
        text="Search by Patient ID, Name or IC",
        bg=WHITE,
        fg=TEXT_DARK,
        font=("Arial", 9)
    ).pack(anchor="w")

    search = tk.Entry(
        result,
        font=("Arial", 10)
    )
    search.pack(fill="x", pady=(5, 8))

    # Patient table
    columns = (
        "ic", "id", "name", "gender", "bed",
        "status", "admission_date", "discharge_date"
    )

    tree = ttk.Treeview(
        result,
        columns=columns,
        show="headings"
    )

    tree.heading("ic", text="Patient IC")
    tree.heading("id", text="Patient ID")
    tree.heading("name", text="Patient Name")
    tree.heading("gender", text="Gender")
    tree.heading("bed", text="Bed")
    tree.heading("status", text="Status")
    tree.heading("admission_date", text="Admission Date")
    tree.heading("discharge_date", text="Discharge Date")

    tree.column("ic", width=110, anchor="center")
    tree.column("id", width=75, anchor="center")
    tree.column("name", width=105)
    tree.column("gender", width=65, anchor="center")
    tree.column("bed", width=75, anchor="center")
    tree.column("status", width=85, anchor="center")
    tree.column("admission_date", width=105, anchor="center")
    tree.column("discharge_date", width=105, anchor="center")

    scrollbar = ttk.Scrollbar(
        result,
        orient="vertical",
        command=tree.yview
    )
    tree.configure(yscrollcommand=scrollbar.set)

    tree.pack(
        side="left",
        fill="both",
        expand=True
    )
    scrollbar.pack(side="right", fill="y")

    # Store the exact admission associated with each table row
    admission_selection = {}

    # Refresh data from the shared JSON file
    def refresh_data():
        nonlocal data, patients, beds

        data = load_database()
        patients = data["patients"]
        beds = data["beds"]

    # Automatically assign the first available bed
    def auto_assign_bed(event=None):
        selected_room = room_type_box.get()

        # Clear the previous bed assignment
        bed_var.set("")

        if not selected_room:
            return

        refresh_data()

        # Keep the current bed when updating a patient
        if selected_id[0]:
            current_patient = find_patient(
                selected_id[0],
                patients
            )

            if current_patient:
                current_bed = current_patient.get("bed_id", "")

                for bed in beds:
                    if bed.get("bed_id") == current_bed:
                        if bed.get("room_type") == selected_room:
                            bed_var.set(current_bed)
                            return

        # Get available beds in the selected room type
        available_beds = [
            bed for bed in get_available_beds()
            if bed.get("room_type") == selected_room
        ]

        # Sort beds by their numerical Bed ID
        available_beds.sort(
            key=lambda bed: int(
                bed.get("bed_id", "Bed 0").replace("Bed ", "")
            )
        )

        # Assign the first available bed
        if available_beds:
            bed_var.set(
                available_beds[0].get("bed_id", "")
            )
        else:
            messagebox.showwarning(
                "No Available Beds",
                "There are no available beds in the selected room type.",
                parent=root
            )

    # Automatically retrieve existing patient information using IC
    def find_existing_patient(event=None):
        current_ic = entries["patient_ic"].get().strip()

        # Refresh the latest patient records
        refresh_data()

        if not current_ic:
            return

        existing_patient = find_patient(
            current_ic,
            patients,
            "patient_ic"
        )

        # If the IC number is not found
        if existing_patient is None:

            # Clear previously retrieved information when IC changes
            if lookup_ic[0] and current_ic != lookup_ic[0]:
                for key in [
                    "name",
                    "dob",
                    "phone",
                    "address",
                    "emergency_contact"
                ]:
                    entries[key].delete(0, tk.END)

                gender_box.set("")
                room_type_box.set("")
                bed_var.set("")

                set_patient_id(generate_patient_id())

                lookup_ic[0] = ""

            return

        # Do not repeatedly fill the form for the same IC
        if lookup_ic[0] == current_ic:
            return

        # Remember this IC number
        lookup_ic[0] = current_ic

        # Retrieve the original Patient ID
        set_patient_id(
            str(existing_patient.get("patient_id", ""))
        )

        # Automatically fill personal information
        for key in [
            "name",
            "dob",
            "phone",
            "address",
            "emergency_contact"
        ]:
            entries[key].delete(0, tk.END)
            entries[key].insert(
                0,
                str(existing_patient.get(key, ""))
            )

        # Retrieve the patient's gender
        gender_box.set(
            existing_patient.get("gender", "")
        )

        # Diagnosis and bed are for the new admission
        entries["diagnosis"].delete(0, tk.END)
        room_type_box.set("")
        bed_var.set("")

        # Inform staff if the patient is already active
        if existing_patient.get("status") != "Discharged":
            messagebox.showwarning(
                "Patient Already Registered",
                "This patient already has an active record.\n"
                "Duplicate registration is not allowed."
            )

    # Display and search all patient admission records
    def display_patients(event=None):
        refresh_data()

        for item in tree.get_children():
            tree.delete(item)

        # Clear the previous admission selection information
        admission_selection.clear()

        keyword = search.get().strip()

        filtered_patients = search_records(
            patients,
            keyword,
            ["patient_id", "name", "patient_ic"]
        )

        for patient in filtered_patients:
            patient_id = str(patient.get("patient_id", ""))
            patient_name = str(patient.get("name", ""))
            patient_ic = str(patient.get("patient_ic", ""))

            # Display previous admission records
            history = patient.get("admission_history", [])

            if not isinstance(history, list):
                history = []

            for index, record in enumerate(history):
                if not isinstance(record, dict):
                    continue

                # Give each previous admission its own row ID
                row_id = f"{patient_id}_history_{index}"

                # Discharged records should show a dash
                if record.get("status", "Discharged") == "Discharged":
                    record_bed = "-"
                else:
                    record_bed = record.get("bed_id", "") or "-"

                tree.insert(
                    "",
                    "end",
                    iid=row_id,
                    values=(
                        patient_ic,
                        patient_id,
                        patient_name,
                        patient.get("gender", ""),
                        record_bed,
                        record.get("status", "Discharged"),
                        record.get("admission_date", ""),
                        record.get("discharge_date", "") or "-"
                    )
                )

                # Remember which historical admission this row represents
                admission_selection[row_id] = {
                    "patient_id": patient_id,
                    "history_index": index,
                    "record_type": "history"
                }

            # Check whether the current admission has already been archived
            current_admission = (
                patient.get("admission_date", ""),
                patient.get("discharge_date", "")
            )

            already_archived = any(
                isinstance(record, dict)
                and (
                    record.get("admission_date", ""),
                    record.get("discharge_date", "")
                ) == current_admission
                for record in history
            )

            # Display the current admission only if it is not already archived
            if not already_archived:
                current_status = patient.get(
                    "status", "Registered"
                )

                if current_status == "Discharged":
                    current_bed = "-"
                else:
                    current_bed = patient.get("bed_id", "") or "-"

                row_id = f"{patient_id}_current"

                tree.insert(
                    "",
                    "end",
                    iid=row_id,
                    values=(
                        patient_ic,
                        patient_id,
                        patient_name,
                        patient.get("gender", ""),
                        current_bed,
                        current_status,
                        patient.get("admission_date", ""),
                        patient.get("discharge_date", "") or "-"
                    )
                )

                # Remember that this row represents the current admission
                admission_selection[row_id] = {
                    "patient_id": patient_id,
                    "history_index": None,
                    "record_type": "current"
                }

    # Show the selected patient's information
    def view_patient(event=None):
        selected = tree.selection()

        if not selected:
            return

        row_id = selected[0]

        # Identify the exact admission record selected
        selection_info = admission_selection.get(row_id)

        if selection_info is None:
            return

        patient_id = selection_info["patient_id"]
        record_type = selection_info["record_type"]
        history_index = selection_info["history_index"]

        refresh_data()

        # Find the selected patient using data.py
        patient = find_patient(patient_id, patients)

        if patient is None:
            messagebox.showerror(
                "Record Error",
                "Patient record could not be found."
            )
            return

        selected_id[0] = patient_id
        selected_record_type[0] = record_type

        # Clear automatic lookup state
        lookup_ic[0] = ""

        # Start with the patient's personal information
        for key, entry in entries.items():
            if key == "patient_id":
                set_patient_id(
                    str(patient.get("patient_id", ""))
                )
            else:
                entry.delete(0, tk.END)

                entry.insert(
                    0,
                    str(patient.get(key, ""))
                )

        gender_box.set(
            patient.get("gender", "")
        )

        if record_type == "history":
            # Retrieve the exact previous admission
            history = patient.get("admission_history", [])

            if (
                not isinstance(history, list)
                or history_index is None
                or history_index >= len(history)
            ):
                messagebox.showerror(
                    "Record Error",
                    "The selected admission record could not be found."
                )
                return

            previous_record = history[history_index]

            # Display the diagnosis from the previous admission
            entries["diagnosis"].delete(0, tk.END)
            entries["diagnosis"].insert(
                0,
                str(previous_record.get("diagnosis", ""))
            )

            # Previous admission records cannot be edited
            room_type_box.set("")
            bed_var.set("")

        else:
            # Display the diagnosis from the current admission
            entries["diagnosis"].delete(0, tk.END)
            entries["diagnosis"].insert(
                0,
                str(patient.get("diagnosis", ""))
            )

            current_bed = patient.get("bed_id", "")

            if current_bed:
                # Find the room type of the patient's current bed
                for bed in beds:
                    if bed.get("bed_id") == current_bed:
                        room_type_box.set(
                            bed.get("room_type", "")
                        )
                        break

                bed_var.set(current_bed)

            else:
                room_type_box.set("")
                bed_var.set("")

    # Display the selected patient's bed transfer history
    def show_transfer_history():
        selected = tree.selection()

        if not selected:
            messagebox.showwarning(
                "Select Patient",
                "Please select a patient from the table first."
            )
            return

        selection_info = admission_selection.get(selected[0])

        if selection_info is None:
            return

        patient_id = selection_info["patient_id"]

        refresh_data()
        patient = find_patient(patient_id, patients)

        if patient is None:
            messagebox.showerror(
                "Record Error",
                "Patient record could not be found."
            )
            return

        transfer_history = patient.get("bed_transfer_history", [])

        if not isinstance(transfer_history, list):
            transfer_history = []

        history_window = tk.Toplevel(root)
        history_window.title("Bed Transfer History")
        history_window.geometry("850x420")
        history_window.configure(bg=PINK_LIGHT)
        history_window.transient(root)

        tk.Label(
            history_window,
            text="Bed Transfer History",
            font=("Arial", 20, "bold"),
            bg=PINK_LIGHT,
            fg=PINK_DARK
        ).pack(anchor="w", padx=20, pady=(18, 5))

        tk.Label(
            history_window,
            text=(
                f"Patient ID: {patient.get('patient_id', '')}    "
                f"Patient Name: {patient.get('name', '')}"
            ),
            font=("Arial", 11),
            bg=PINK_LIGHT,
            fg=TEXT_DARK
        ).pack(anchor="w", padx=20, pady=(0, 12))

        history_frame = tk.Frame(history_window, bg=WHITE)
        history_frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0, 12)
        )

        history_columns = (
            "date",
            "from_bed",
            "from_room",
            "to_bed",
            "to_room"
        )

        history_tree = ttk.Treeview(
            history_frame,
            columns=history_columns,
            show="headings"
        )

        history_tree.heading("date", text="Transfer Date")
        history_tree.heading("from_bed", text="Previous Bed")
        history_tree.heading("from_room", text="Previous Room Type")
        history_tree.heading("to_bed", text="New Bed")
        history_tree.heading("to_room", text="New Room Type")

        history_tree.column("date", width=115, anchor="center")
        history_tree.column("from_bed", width=110, anchor="center")
        history_tree.column("from_room", width=155, anchor="center")
        history_tree.column("to_bed", width=110, anchor="center")
        history_tree.column("to_room", width=155, anchor="center")

        history_scrollbar = ttk.Scrollbar(
            history_frame,
            orient="vertical",
            command=history_tree.yview
        )
        history_tree.configure(
            yscrollcommand=history_scrollbar.set
        )

        history_tree.pack(
            side="left",
            fill="both",
            expand=True
        )
        history_scrollbar.pack(side="right", fill="y")

        if transfer_history:
            for record in transfer_history:
                if not isinstance(record, dict):
                    continue

                history_tree.insert(
                    "",
                    "end",
                    values=(
                        record.get("transfer_date", ""),
                        record.get("from_bed", ""),
                        record.get("from_room_type", ""),
                        record.get("to_bed", ""),
                        record.get("to_room_type", "")
                    )
                )
        else:
            tk.Label(
                history_window,
                text="No bed transfers have been recorded for this patient.",
                font=("Arial", 10),
                bg=PINK_LIGHT,
                fg=TEXT_LIGHT
            ).pack(pady=(0, 12))

        tk.Button(
            history_window,
            text="Close",
            command=history_window.destroy,
            bg=PINK_DARK,
            fg=WHITE,
            activebackground=PINK_ACTIVE,
            activeforeground=WHITE,
            width=12,
            font=("Arial", 10, "bold")
        ).pack(pady=(0, 15))

    # Validate patient information
    def valid_date(dob):
        if not dob:
            return True

        try:
            birth_date = date.fromisoformat(dob)
            return birth_date <= date.today()
        except ValueError:
            return False

    def validate_patient_details(patient):
        if patient["patient_ic"] != "-" and not patient["patient_ic"].isdigit():
            return False, "Patient IC must contain numbers only."

        if not patient["name"].replace(" ", "").isalpha():
            return False, "Patient name must contain alphabets only."

        if not patient["phone"].isdigit():
            return False, "Phone number must contain numbers only."

        if not patient["emergency_contact"].isdigit():
            return False, "Emergency contact must contain numbers only."

        return True, ""

    # Register a new patient or readmit a discharged patient
    def register_patient():
        refresh_data()

        # Do not register over an existing selected record
        if selected_id[0]:
            messagebox.showwarning(
                "Clear Form First",
                "Please click Clear before registering a new patient."
            )
            return

        patient = {}

        # Collect all form information
        for key, entry in entries.items():
            patient[key] = entry.get().strip()

        # Generate the Patient ID automatically
        patient["patient_id"] = generate_patient_id()
        patient["gender"] = gender_box.get()

        # Check required information
        if (
            not patient["patient_ic"]
            or not patient["name"]
            or not patient["dob"]
            or not patient["gender"]
            or not patient["phone"]
            or not patient["address"]
            or not patient["emergency_contact"]
            or not patient["diagnosis"]
        ):
            messagebox.showwarning(
                "Missing Information",
                "Please fill in all fields before registering the patient."
            )
            return

        # Validate patient information
        if not valid_date(patient["dob"]):
            messagebox.showwarning(
                "Invalid Date",
                "Enter a valid date of birth in YYYY-MM-DD format. "
                "The date cannot be in the future."
            )
            return

        is_valid, error_message = validate_patient_details(patient)
        if not is_valid:
            messagebox.showwarning(
                "Invalid Information",
                error_message
            )
            return

        # Check whether the patient already exists
        existing_patient = find_patient(
            patient["patient_ic"],
            patients,
            "patient_ic"
        )

        # Prevent duplicate registration of an active patient
        if existing_patient:
            if existing_patient.get("status") != "Discharged":
                messagebox.showwarning(
                    "Patient Already Registered",
                    "This patient already has an active record."
                )
                return

            # Reuse the existing Patient ID
            patient["patient_id"] = existing_patient["patient_id"]

        # Get the selected room type
        selected_room = room_type_box.get()

        if not selected_room:
            messagebox.showwarning(
                "Room Type Required",
                "Please select a room type."
            )
            return

        # Automatically assign the first available bed
        auto_assign_bed()

        selected_bed = bed_var.get()

        if not selected_bed:
            messagebox.showwarning(
                "No Available Beds",
                "Please select a room type with available beds."
            )
            return

        # Refresh the database before confirming bed availability
        refresh_data()

        # Confirm that the selected bed is still available
        available_bed_ids = {
            bed.get("bed_id", "")
            for bed in get_available_beds()
            if bed.get("room_type") == selected_room
        }

        if selected_bed not in available_bed_ids:
            messagebox.showwarning(
                "Bed Unavailable",
                "The assigned bed is no longer available. "
                "Please select the room type again."
            )
            bed_var.set("")
            return

        # Set patient admission information
        patient["bed_id"] = selected_bed
        patient["admission_date"] = date.today().isoformat()
        patient["status"] = "Registered"
        patient["discharge_date"] = ""
        patient["payment_confirmed"] = ""

        # Add missing fields required by data.py
        for field in PATIENT_FIELDS:
            if field not in patient:
                patient[field] = ""

        # Initialise both histories for a new patient
        if not existing_patient:
            patient["admission_history"] = []
            patient["bed_transfer_history"] = []

        # Mark the bed as occupied
        for bed in beds:
            if bed.get("bed_id") == selected_bed:
                bed["status"] = "Occupied"
                bed["patient_id"] = patient["patient_id"]
                break

        # Add a new patient or update an existing discharged patient
        if existing_patient:

            # Preserve previous admission and bed transfer records
            admission_history = existing_patient.get(
                "admission_history", []
            )
            bed_transfer_history = existing_patient.get(
                "bed_transfer_history", []
            )

            if not isinstance(admission_history, list):
                admission_history = []

            if not isinstance(bed_transfer_history, list):
                bed_transfer_history = []

            # Update the existing patient record for readmission
            existing_patient.update(patient)

            # Restore both histories
            existing_patient["admission_history"] = admission_history
            existing_patient["bed_transfer_history"] = bed_transfer_history

            message = (
                "Patient readmitted successfully.\n"
                f"Patient ID: {patient['patient_id']}\n"
                f"Assigned Bed: {selected_bed}\n"
                "Previous admission records have been preserved."
            )

        else:
            # Add a completely new patient
            patients.append(patient)

            message = (
                "Patient registered successfully.\n"
                f"Patient ID: {patient['patient_id']}\n"
                f"Assigned Bed: {selected_bed}"
            )

        # Save patient and bed information
        save_database(data)

        display_patients()
        clear_form()

        messagebox.showinfo(
            "Success",
            message
        )

    # Update an existing patient
    def update_patient():
        refresh_data()

        patient_id = selected_id[0]

        if not patient_id:
            messagebox.showwarning(
                "Select Patient",
                "Please select a patient from the table first."
            )
            return

        # Prevent editing a previous admission
        if selected_record_type[0] == "history":
            messagebox.showwarning(
                "Previous Admission",
                "A previous admission record cannot be updated here."
            )
            return

        # Find the selected patient
        selected_patient = find_patient(patient_id, patients)

        if selected_patient is None:
            messagebox.showerror(
                "Error",
                "Patient record could not be found."
            )
            return

        # Do not edit discharged patients
        if selected_patient.get("status") == "Discharged":
            messagebox.showwarning(
                "Discharged Patient",
                "A discharged patient's record cannot be updated here."
            )
            return

        # Collect the updated information
        updated_patient = {}

        for key, entry in entries.items():
            updated_patient[key] = entry.get().strip()

        updated_patient["gender"] = gender_box.get()

        # Check all required fields
        required_fields = [
            "patient_ic",
            "name",
            "dob",
            "phone",
            "address",
            "emergency_contact",
            "diagnosis"
        ]

        for field in required_fields:
            if not updated_patient[field]:
                messagebox.showwarning(
                    "Missing Information",
                    "Please fill in all required fields."
                )
                return

        if not updated_patient["gender"]:
            messagebox.showwarning(
                "Missing Information",
                "Please select the patient's gender."
            )
            return

        # Keep the patient's original IC unchanged
        old_ic = str(selected_patient.get("patient_ic", ""))

        if updated_patient["patient_ic"] != old_ic:
            messagebox.showwarning(
                "IC Cannot Be Changed",
                "The patient's IC number cannot be changed "
                "during an update."
            )
            return

        # Validate the patient's date of birth
        if not valid_date(updated_patient["dob"]) or not updated_patient["dob"]:
            messagebox.showwarning(
                "Invalid Date",
                "Enter a valid date of birth in YYYY-MM-DD format. "
                "The date cannot be in the future."
            )
            return

        # Validate IC, name and contact numbers
        is_valid, error_message = validate_patient_details(
            updated_patient
        )

        if not is_valid:
            messagebox.showwarning(
                "Invalid Information",
                error_message
            )
            return

        old_bed = selected_patient.get("bed_id", "")
        new_bed = bed_var.get().strip()
        selected_room = room_type_box.get()

        # A patient must always have a room type and bed
        if not selected_room or not new_bed:
            messagebox.showwarning(
                "Bed Required",
                "Please select a room type with an available bed."
            )
            return

        # Check availability if the bed is changing
        if new_bed != old_bed:
            available_bed_ids = {
                bed.get("bed_id", "")
                for bed in get_available_beds()
                if bed.get("room_type") == selected_room
            }

            if new_bed not in available_bed_ids:
                messagebox.showwarning(
                    "Bed Unavailable",
                    "The assigned bed is no longer available. "
                    "Please select the room type again."
                )
                bed_var.set("")
                return

        # Record the bed transfer before changing the bed assignment
        if old_bed and old_bed != new_bed:
            old_room_type = ""
            new_room_type = selected_room

            for bed in beds:
                if bed.get("bed_id") == old_bed:
                    old_room_type = bed.get("room_type", "")
                    break

            for bed in beds:
                if bed.get("bed_id") == new_bed:
                    new_room_type = bed.get("room_type", selected_room)
                    break

            transfer_history = selected_patient.get(
                "bed_transfer_history", []
            )

            if not isinstance(transfer_history, list):
                transfer_history = []

            transfer_history.append({
                "from_bed": old_bed,
                "from_room_type": old_room_type,
                "to_bed": new_bed,
                "to_room_type": new_room_type,
                "transfer_date": date.today().isoformat(),
                "admission_date": selected_patient.get(
                    "admission_date", ""
                )
            })

            selected_patient["bed_transfer_history"] = transfer_history

        # Release the old bed and occupy the new bed
        if old_bed != new_bed:
            for bed in beds:
                if (
                    bed.get("bed_id") == old_bed
                    and bed.get("patient_id") == patient_id
                ):
                    bed["status"] = "Available"
                    bed["patient_id"] = ""

            for bed in beds:
                if bed.get("bed_id") == new_bed:
                    bed["status"] = "Occupied"
                    bed["patient_id"] = patient_id
                    break

        # Update patient details without changing Patient ID
        for key in [
            "name",
            "dob",
            "phone",
            "address",
            "emergency_contact",
            "diagnosis"
        ]:
            selected_patient[key] = updated_patient[key]

        selected_patient["gender"] = updated_patient["gender"]
        selected_patient["bed_id"] = new_bed
        selected_patient["status"] = "Registered"

        # Save updated information
        save_database(data)

        display_patients()
        clear_form()

        messagebox.showinfo(
            "Success",
            "Patient information updated successfully."
        )

    # Clear the form and show the next Patient ID
    def clear_form():
        for key, entry in entries.items():
            if key != "patient_id":
                entry.delete(0, tk.END)

        gender_box.set("")
        room_type_box.set("")
        bed_var.set("")
        selected_id[0] = ""
        selected_record_type[0] = ""
        lookup_ic[0] = ""

        for item in tree.selection():
            tree.selection_remove(item)

        set_patient_id(generate_patient_id())

    # Automatically assign a bed when room type is selected
    room_type_box.bind(
        "<<ComboboxSelected>>",
        auto_assign_bed
    )

    # Buttons
    button_frame = tk.Frame(
        form,
        bg=WHITE
    )
    button_frame.grid(
        row=11,
        column=0,
        columnspan=2,
        pady=12
    )

    tk.Button(
        button_frame,
        text="Register",
        command=register_patient,
        bg=PINK_DARK,
        fg=WHITE,
        activebackground=PINK_ACTIVE,
        activeforeground=WHITE,
        width=8,
        font=("Arial", 9)
    ).pack(side="left", padx=2)

    tk.Button(
        button_frame,
        text="Update",
        command=update_patient,
        bg=PINK_ACTIVE,
        fg=WHITE,
        activebackground=PINK_DARK,
        activeforeground=WHITE,
        width=8,
        font=("Arial", 9)
    ).pack(side="left", padx=2)

    tk.Button(
        button_frame,
        text="Clear",
        command=clear_form,
        bg=PINK_PALE,
        fg=TEXT_DARK,
        width=7,
        font=("Arial", 9)
    ).pack(side="left", padx=2)

    tk.Button(
        form,
        text="View Bed Transfer History",
        command=show_transfer_history,
        bg=PINK_PALE,
        fg=TEXT_DARK,
        activebackground=PINK_BORDER,
        width=28,
        font=("Arial", 9)
    ).grid(
        row=12,
        column=0,
        columnspan=2,
        pady=(0, 12)
    )

    # Search and table selection
    search.bind("<KeyRelease>", display_patients)
    tree.bind("<<TreeviewSelect>>", view_patient)

    # Automatically retrieve patient information when IC is entered
    entries["patient_ic"].bind(
        "<KeyRelease>",
        find_existing_patient
    )

    # Show initial data and next Patient ID
    display_patients()
    set_patient_id(generate_patient_id())
