import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
import dashboard
from data import PATIENT_FIELDS, load_database, save_database

# Pink theme colours
PINK_DARK = "#7D3458"
PINK_ACTIVE = "#AD5B82"
PINK_LIGHT = "#FFF4F8"
PINK_PALE = "#FCE7F0"
PINK_BORDER = "#EAC5D5"
TEXT_DARK = "#49323D"
TEXT_LIGHT = "#A45B7D"
WHITE = "#FFFFFF"


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

    fields = [
        ("Patient ID", "patient_id"),
        ("Full Name", "name"),
        ("Date of Birth", "dob"),
        ("Phone", "phone"),
        ("Address", "address"),
        ("Emergency Contact", "emergency_contact"),
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

        entry = tk.Entry(form, width=19, font=("Arial", 9))
        entry.grid(
            row=row, column=1, padx=(6, 0), pady=4
        )
        entries[field_name] = entry

    # Gender selection
    tk.Label(
        form,
        text="Gender",
        bg=WHITE,
        fg=TEXT_DARK,
        font=("Arial", 9)
    ).grid(row=7, column=0, sticky="w", pady=4)

    gender_box = ttk.Combobox(
        form,
        values=["Female", "Male", "Other"],
        state="readonly",
        width=17
    )
    gender_box.grid(
        row=7, column=1, padx=(6, 0), pady=4
    )

    # Bed selection
    tk.Label(
        form,
        text="Assign Bed",
        bg=WHITE,
        fg=TEXT_DARK,
        font=("Arial", 9)
    ).grid(row=8, column=0, sticky="w", pady=4)

    bed_box = ttk.Combobox(
        form,
        state="readonly",
        width=17
    )
    bed_box.grid(
        row=8, column=1, padx=(6, 0), pady=4
    )

    # Remember the selected patient
    selected_id = [""]

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
    result.pack(side="right", fill="both", expand=True)

    # Search box
    tk.Label(
        result,
        text="Search by Patient ID or Name",
        bg=WHITE,
        fg=TEXT_DARK,
        font=("Arial", 9)
    ).pack(anchor="w")

    search = tk.Entry(result, font=("Arial", 10))
    search.pack(fill="x", pady=(5, 8))

    # Patient table
    columns = ("id", "name", "gender", "bed", "status")

    tree = ttk.Treeview(
        result,
        columns=columns,
        show="headings"
    )

    tree.heading("id", text="Patient ID")
    tree.heading("name", text="Patient Name")
    tree.heading("gender", text="Gender")
    tree.heading("bed", text="Bed")
    tree.heading("status", text="Status")

    tree.column("id", width=75, anchor="center")
    tree.column("name", width=105)
    tree.column("gender", width=65, anchor="center")
    tree.column("bed", width=75, anchor="center")
    tree.column("status", width=85, anchor="center")

    scrollbar = ttk.Scrollbar(
        result,
        orient="vertical",
        command=tree.yview
    )
    tree.configure(yscrollcommand=scrollbar.set)

    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Refresh data from the shared JSON file
    def refresh_data():
        nonlocal data, patients, beds

        data = load_database()
        patients = data["patients"]
        beds = data["beds"]

    # Update available bed choices
    def update_beds():
        refresh_data()
        choices = []

        for bed in beds:
            if bed.get("status") == "Available":
                choices.append(bed.get("bed_id", ""))

        # Keep the selected patient's current bed selectable
        for patient in patients:
            if patient.get("patient_id") == selected_id[0]:
                current_bed = patient.get("bed_id", "")

                if current_bed and current_bed not in choices:
                    choices.append(current_bed)

        bed_box["values"] = choices

        if bed_box.get() not in choices:
            bed_box.set("")

    # Display and search patient records
    def display_patients(event=None):
        refresh_data()

        for item in tree.get_children():
            tree.delete(item)

        keyword = search.get().strip().lower()

        for patient in patients:
            patient_id = str(patient.get("patient_id", ""))
            patient_name = str(patient.get("name", ""))

            if (
                keyword in patient_id.lower()
                or keyword in patient_name.lower()
            ):
                tree.insert(
                    "",
                    "end",
                    values=(
                        patient_id,
                        patient_name,
                        patient.get("gender", ""),
                        patient.get("bed_id", "") or "-",
                        patient.get("status", "Registered")
                    )
                )

    # Show the selected patient's information
    def view_patient(event=None):
        selected = tree.selection()

        if not selected:
            return

        patient_id = tree.item(
            selected[0], "values"
        )[0]

        refresh_data()

        for patient in patients:
            if patient.get("patient_id", "") == patient_id:
                selected_id[0] = patient_id

                for key, entry in entries.items():
                    entry.delete(0, tk.END)
                    entry.insert(
                        0, patient.get(key, "")
                    )

                gender_box.set(patient.get("gender", ""))

                update_beds()

                if patient.get("bed_id", ""):
                    bed_box.set(patient["bed_id"])
                else:
                    bed_box.set("")

                break

    # Validate date of birth
    def valid_date(dob):
        if not dob:
            return True

        try:
            birth_date = date.fromisoformat(dob)
            return birth_date <= date.today()
        except ValueError:
            return False

    # Register a new patient
    def register_patient():
        refresh_data()

        patient = {}

        for key, entry in entries.items():
            patient[key] = entry.get().strip()

        patient["gender"] = gender_box.get()

        # Check required information
        if not patient["patient_id"] or not patient["name"]:
            messagebox.showwarning(
                "Missing Information",
                "Patient ID and Full Name are required."
            )
            return

        if not valid_date(patient["dob"]):
            messagebox.showwarning(
                "Invalid Date",
                "Enter a valid date of birth in YYYY-MM-DD format. "
                "The date cannot be in the future."
            )
            return

        # Check for duplicate patient IDs
        for old_patient in patients:
            if (
                old_patient.get("patient_id", "")
                == patient["patient_id"]
            ):
                messagebox.showerror(
                    "Duplicate ID",
                    "This Patient ID already exists."
                )
                return

        # Every new patient must have a bed
        selected_bed = bed_box.get().strip()

        if not selected_bed:
            messagebox.showwarning(
                "Bed Required",
                "Please select an available bed for this patient."
            )
            return

        # Confirm that the selected bed is still available
        bed_available = False

        for bed in beds:
            if bed.get("bed_id") == selected_bed:
                if bed.get("status") == "Available":
                    bed_available = True
                break

        if not bed_available:
            messagebox.showwarning(
                "Bed Unavailable",
                "This bed is no longer available. "
                "Please select another bed."
            )
            update_beds()
            return

        patient["bed_id"] = selected_bed
        patient["admission_date"] = date.today().isoformat()
        patient["status"] = "Registered"
        patient["discharge_date"] = ""
        patient["payment_confirmed"] = ""

        # Add any missing fields required by data.py
        for field in PATIENT_FIELDS:
            if field not in patient:
                patient[field] = ""

        # Mark the bed as occupied
        for bed in beds:
            if bed.get("bed_id") == selected_bed:
                bed["status"] = "Occupied"
                bed["patient_id"] = patient["patient_id"]
                break

        patients.append(patient)
        save_database(data)

        display_patients()
        clear_form()

        messagebox.showinfo(
            "Success",
            "Patient registered successfully."
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

        selected_patient = None

        for patient in patients:
            if patient.get("patient_id", "") == patient_id:
                selected_patient = patient
                break

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

        # Patient ID must not change
        entered_id = entries["patient_id"].get().strip()

        if entered_id != patient_id:
            messagebox.showwarning(
                "Patient ID Cannot Be Changed",
                "Please keep the original Patient ID."
            )
            return

        # Check required information
        if not entries["name"].get().strip():
            messagebox.showwarning(
                "Missing Information",
                "Full Name is required."
            )
            return

        dob = entries["dob"].get().strip()

        if not valid_date(dob):
            messagebox.showwarning(
                "Invalid Date",
                "Enter a valid date of birth in YYYY-MM-DD format. "
                "The date cannot be in the future."
            )
            return

        old_bed = selected_patient.get("bed_id", "")
        new_bed = bed_box.get().strip()

        # A patient must always have a bed
        if not new_bed:
            messagebox.showwarning(
                "Bed Required",
                "Please select a bed for this patient."
            )
            return

        # Check availability if the bed is changing
        if new_bed != old_bed:
            bed_available = False

            for bed in beds:
                if bed.get("bed_id") == new_bed:
                    if bed.get("status") == "Available":
                        bed_available = True
                    break

            if not bed_available:
                messagebox.showwarning(
                    "Bed Unavailable",
                    "Please select an available bed."
                )
                update_beds()
                return

        # Release the old bed and occupy the new bed
        if old_bed != new_bed:
            for bed in beds:
                if bed.get("bed_id") == old_bed:
                    if bed.get("patient_id") == patient_id:
                        bed["status"] = "Available"
                        bed["patient_id"] = ""

            for bed in beds:
                if bed.get("bed_id") == new_bed:
                    bed["status"] = "Occupied"
                    bed["patient_id"] = patient_id
                    break

        # Update patient details without changing the ID
        for key, entry in entries.items():
            if key != "patient_id":
                selected_patient[key] = entry.get().strip()

        selected_patient["gender"] = gender_box.get()
        selected_patient["bed_id"] = new_bed
        selected_patient["status"] = "Registered"

        save_database(data)

        display_patients()
        clear_form()

        messagebox.showinfo(
            "Success",
            "Patient information updated successfully."
        )

    # Clear the form
    def clear_form():
        for entry in entries.values():
            entry.delete(0, tk.END)

        gender_box.set("")
        bed_box.set("")
        selected_id[0] = ""

        for item in tree.selection():
            tree.selection_remove(item)

        update_beds()

    # Buttons
    button_frame = tk.Frame(form, bg=WHITE)
    button_frame.grid(
        row=9,
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

    # Search and table selection
    search.bind("<KeyRelease>", display_patients)
    tree.bind("<<TreeviewSelect>>", view_patient)

    # Show initial data
    update_beds()
    display_patients()
