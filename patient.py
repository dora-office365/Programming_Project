import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
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
    # Load the shared database
    data = load_database()
    patients = data["patients"]
    beds = data["beds"]

    # Clear the previous page
    for widget in root.winfo_children():
        widget.destroy()

    root.title("Careflow - Patient Information")
    root.geometry("1150x750")
    root.configure(bg=PINK_LIGHT)

    # Page heading
    tk.Label(
        root,
        text="Patient Information",
        font=("Arial", 24, "bold"),
        bg=PINK_LIGHT,
        fg=PINK_DARK
    ).pack(anchor="w", padx=25, pady=(20, 5))

    tk.Label(
        root,
        text="Register, search and update patient records",
        font=("Arial", 11),
        bg=PINK_LIGHT,
        fg=TEXT_DARK
    ).pack(anchor="w", padx=25, pady=(0, 15))

    # Main content area
    content = tk.Frame(root, bg=PINK_LIGHT)
    content.pack(fill="both", expand=True, padx=20, pady=10)

    # Patient information form
    form = tk.LabelFrame(
        content,
        text="Patient Details",
        font=("Arial", 12, "bold"),
        bg=WHITE,
        fg=PINK_DARK,
        padx=12,
        pady=10
    )
    form.pack(side="left", fill="y", padx=(0, 15))

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
            font=("Arial", 10)
        ).grid(row=row, column=0, sticky="w", pady=5)

        entry = tk.Entry(form, width=23, font=("Arial", 10))
        entry.grid(row=row, column=1, padx=(8, 0), pady=5)

        entries[field_name] = entry

    # Gender selection
    tk.Label(
        form,
        text="Gender",
        bg=WHITE,
        fg=TEXT_DARK
    ).grid(row=7, column=0, sticky="w", pady=5)

    gender_box = ttk.Combobox(
        form,
        values=["Female", "Male", "Other"],
        state="readonly",
        width=20
    )
    gender_box.grid(row=7, column=1, padx=(8, 0), pady=5)

    # Bed selection
    tk.Label(
        form,
        text="Assign Bed",
        bg=WHITE,
        fg=TEXT_DARK
    ).grid(row=8, column=0, sticky="w", pady=5)

    bed_box = ttk.Combobox(
        form,
        state="readonly",
        width=20
    )
    bed_box.grid(row=8, column=1, padx=(8, 0), pady=5)

    # Remember the selected patient
    selected_id = [""]

    # Patient records section
    result = tk.LabelFrame(
        content,
        text="Patient Records",
        font=("Arial", 12, "bold"),
        bg=WHITE,
        fg=PINK_DARK,
        padx=10,
        pady=10
    )
    result.pack(side="right", fill="both", expand=True)

    # Search box
    tk.Label(
        result,
        text="Search by Patient ID or Name",
        bg=WHITE,
        fg=TEXT_DARK
    ).pack(anchor="w")

    search = tk.Entry(result, font=("Arial", 10))
    search.pack(fill="x", pady=(5, 10))

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

    tree.column("id", width=90, anchor="center")
    tree.column("name", width=130)
    tree.column("gender", width=75, anchor="center")
    tree.column("bed", width=90, anchor="center")
    tree.column("status", width=100, anchor="center")

    scrollbar = ttk.Scrollbar(
        result,
        orient="vertical",
        command=tree.yview
    )

    tree.configure(yscrollcommand=scrollbar.set)

    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Update the available bed choices
    def update_beds():
        choices = ["No bed"]

        for bed in beds:
            if bed.get("status") == "Available":
                choices.append(bed.get("bed_id", ""))

        # Keep the current patient's bed available in the dropdown
        # when editing an existing patient
        for patient in patients:
            if patient.get("patient_id") == selected_id[0]:
                current_bed = patient.get("bed_id", "")

                if current_bed and current_bed not in choices:
                    choices.append(current_bed)

        bed_box["values"] = choices

        if bed_box.get() not in choices:
            bed_box.set("No bed")

    # Display and search patient records
    def display_patients():
        for item in tree.get_children():
            tree.delete(item)

        keyword = search.get().strip().lower()

        for patient in patients:
            patient_id = patient.get("patient_id", "")
            patient_name = patient.get("name", "")

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

        patient_id = tree.item(selected[0], "values")[0]

        for patient in patients:
            if patient.get("patient_id", "") == patient_id:
                selected_id[0] = patient_id

                # Fill in the form
                for key, entry in entries.items():
                    entry.delete(0, tk.END)
                    entry.insert(0, patient.get(key, ""))

                gender_box.set(patient.get("gender", ""))

                # Refresh the bed choices for this patient
                update_beds()

                if patient.get("bed_id", ""):
                    bed_box.set(patient["bed_id"])
                else:
                    bed_box.set("No bed")

                break

    # Check the date format
    def valid_date(dob):
        if not dob:
            return True

        try:
            date.fromisoformat(dob)
            return True
        except ValueError:
            return False

    # Register a new patient
    def register_patient():
        patient = {}

        # Collect the form information
        for key, entry in entries.items():
            patient[key] = entry.get().strip()

        patient["gender"] = gender_box.get()

        if not patient["patient_id"] or not patient["name"]:
            messagebox.showwarning(
                "Missing Information",
                "Patient ID and Full Name are required."
            )
            return

        if not valid_date(patient["dob"]):
            messagebox.showwarning(
                "Invalid Date",
                "Enter the date of birth in YYYY-MM-DD format."
            )
            return

        # Check for duplicate Patient IDs
        for old_patient in patients:
            if old_patient.get("patient_id", "") == patient["patient_id"]:
                messagebox.showerror(
                    "Duplicate ID",
                    "This Patient ID already exists."
                )
                return

        selected_bed = bed_box.get()

        if selected_bed == "No bed":
            selected_bed = ""

        # Check that the selected bed is available
        if selected_bed:
            bed_available = False

            for bed in beds:
                if bed.get("bed_id") == selected_bed:
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

        patient["bed_id"] = selected_bed
        patient["admission_date"] = date.today().isoformat()
        patient["status"] = (
            "Admitted" if selected_bed else "Registered"
        )
        patient["discharge_date"] = ""
        patient["payment_confirmed"] = ""

        # Add any missing fields
        for field in PATIENT_FIELDS:
            if field not in patient:
                patient[field] = ""

        # Update bed status
        if selected_bed:
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

        if selected_patient.get("status") == "Discharged":
            messagebox.showwarning(
                "Discharged Patient",
                "A discharged patient's record cannot be updated here."
            )
            return

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
                "Enter the date of birth in YYYY-MM-DD format."
            )
            return

        old_bed = selected_patient.get("bed_id", "")
        new_bed = bed_box.get()

        if new_bed == "No bed":
            new_bed = ""

        # Check the new bed if the assignment changes
        if new_bed and new_bed != old_bed:
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

        # Release the old bed if the assignment changes
        if old_bed != new_bed:
            for bed in beds:
                if (
                    bed.get("bed_id") == old_bed
                    and bed.get("patient_id") == patient_id
                ):
                    bed["status"] = "Available"
                    bed["patient_id"] = ""

            # Assign the new bed
            for bed in beds:
                if bed.get("bed_id") == new_bed:
                    bed["status"] = "Occupied"
                    bed["patient_id"] = patient_id
                    break

        # Update patient details
        for key, entry in entries.items():
            selected_patient[key] = entry.get().strip()

        selected_patient["gender"] = gender_box.get()
        selected_patient["bed_id"] = new_bed

        if new_bed:
            selected_patient["status"] = "Admitted"
        else:
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
        bed_box.set("No bed")
        selected_id[0] = ""

        for item in tree.selection():
            tree.selection_remove(item)

        update_beds()

    # Return to the dashboard
    def back_to_dashboard():
        import dashboard

        username = getattr(dashboard, "current_username", "admin")
        dashboard.show_dashboard(username)

    # Buttons
    button_frame = tk.Frame(form, bg=WHITE)
    button_frame.grid(
        row=9,
        column=0,
        columnspan=2,
        pady=15
    )

    tk.Button(
        button_frame,
        text="Register",
        command=register_patient,
        bg=PINK_DARK,
        fg=WHITE,
        activebackground=PINK_ACTIVE,
        activeforeground=WHITE,
        width=10
    ).pack(side="left", padx=3)

    tk.Button(
        button_frame,
        text="Update",
        command=update_patient,
        bg=PINK_ACTIVE,
        fg=WHITE,
        activebackground=PINK_DARK,
        activeforeground=WHITE,
        width=10
    ).pack(side="left", padx=3)

    tk.Button(
        button_frame,
        text="Clear",
        command=clear_form,
        bg=PINK_PALE,
        fg=TEXT_DARK,
        width=8
    ).pack(side="left", padx=3)

    # Search and table selection
    search.bind("<KeyRelease>", display_patients)
    tree.bind("<<TreeviewSelect>>", view_patient)

    # Back button
    tk.Button(
        root,
        text="Back to Dashboard",
        command=back_to_dashboard,
        bg=PINK_DARK,
        fg=WHITE,
        activebackground=PINK_ACTIVE,
        activeforeground=WHITE,
        font=("Arial", 10, "bold"),
        padx=15,
        pady=6
    ).pack(pady=(0, 15))

    # Show initial data
    update_beds()
    display_patients()