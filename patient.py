import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from data import load_database, save_database


# Pink theme colours
PINK_DARK = "#7D3458"
PINK_ACTIVE = "#AD5B82"
PINK_LIGHT = "#FFF4F8"
PINK_PALE = "#FCE7F0"
PINK_BORDER = "#EAC5D5"
TEXT_DARK = "#49323D"
WHITE = "#FFFFFF"


def show_patients(root):
    data = load_database()
    patients = data["patients"]
    beds = data["beds"]

    for widget in root.winfo_children():
        widget.destroy()

    root.title("Careflow - Patient Information")
    root.geometry("1100x700")
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

    # Main content
    content = tk.Frame(root, bg=PINK_LIGHT)
    content.pack(fill="both", expand=True, padx=25, pady=10)

    # Patient form
    form = tk.LabelFrame(
        content,
        text="Patient Details",
        font=("Arial", 12, "bold"),
        bg=WHITE,
        fg=PINK_DARK,
        padx=15,
        pady=10
    )
    form.pack(side="left", fill="y", padx=(0, 15))

    fields = [
        ("Patient ID", "patient_id"),
        ("Full Name", "name"),
        ("Date of Birth (YYYY-MM-DD)", "dob"),
        ("Phone", "phone"),
        ("Address", "address"),
        ("Emergency Contact", "emergency_contact"),
        ("Diagnosis", "diagnosis")
    ]

    entries = {}

    for row, field in enumerate(fields):
        label_text, field_name = field

        tk.Label(
            form,
            text=label_text,
            bg=WHITE,
            fg=TEXT_DARK,
            font=("Arial", 10)
        ).grid(row=row, column=0, sticky="w", pady=5)

        entry = tk.Entry(
            form,
            width=27,
            font=("Arial", 10),
            relief="solid",
            bd=1
        )
        entry.grid(row=row, column=1, pady=5, padx=(10, 0))
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
        values=["Male", "Female", "Other"],
        state="readonly",
        width=24
    )
    gender_box.grid(row=7, column=1, pady=5, padx=(10, 0))

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
        width=24
    )
    bed_box.grid(row=8, column=1, pady=5, padx=(10, 0))

    # Search and patient table
    right_frame = tk.Frame(content, bg=PINK_LIGHT)
    right_frame.pack(side="right", fill="both", expand=True)

    search_frame = tk.Frame(right_frame, bg=WHITE, padx=10, pady=10)
    search_frame.pack(fill="x", pady=(0, 10))

    tk.Label(
        search_frame,
        text="Search ID or Name:",
        bg=WHITE,
        fg=TEXT_DARK
    ).pack(side="left")

    search_entry = tk.Entry(search_frame, width=25)
    search_entry.pack(side="left", padx=8)

    columns = ("patient_id", "name", "gender", "bed_id", "status")

    table = ttk.Treeview(
        right_frame,
        columns=columns,
        show="headings",
        height=18
    )

    table.heading("patient_id", text="Patient ID")
    table.heading("name", text="Patient Name")
    table.heading("gender", text="Gender")
    table.heading("bed_id", text="Bed")
    table.heading("status", text="Status")

    table.column("patient_id", width=90, anchor="center")
    table.column("name", width=140)
    table.column("gender", width=75, anchor="center")
    table.column("bed_id", width=90, anchor="center")
    table.column("status", width=100, anchor="center")

    table.pack(fill="both", expand=True)

    # Update the list of available beds
    def update_beds():
        available_beds = []

        for bed in beds:
            if bed.get("status") == "Available":
                available_beds.append(bed.get("bed_id", ""))

        bed_box["values"] = ["None"] + available_beds

        if bed_box.get() not in bed_box["values"]:
            bed_box.set("None")

    # Display patient records
    def display_patients():
        for item in table.get_children():
            table.delete(item)

        keyword = search_entry.get().strip().lower()

        for patient in patients:
            patient_id = patient.get("patient_id", "")
            name = patient.get("name", "")

            if keyword in patient_id.lower() or keyword in name.lower():
                table.insert(
                    "",
                    "end",
                    values=(
                        patient_id,
                        name,
                        patient.get("gender", ""),
                        patient.get("bed_id", "") or "-",
                        patient.get("status", "Registered")
                    )
                )

        update_beds()

    # Fill the form when a patient is selected
    def view_patient(event=None):
        selected = table.selection()

        if not selected:
            return

        values = table.item(selected[0], "values")
        patient_id = values[0]

        for patient in patients:
            if patient.get("patient_id", "") == patient_id:
                for field in fields:
                    field_name = field[1]
                    entries[field_name].delete(0, tk.END)
                    entries[field_name].insert(
                        0, patient.get(field_name, "")
                    )

                gender_box.set(patient.get("gender", ""))
                bed_box.set(patient.get("bed_id", "") or "None")
                break

    # Register a new patient
    def register_patient():
        patient_id = entries["patient_id"].get().strip()
        name = entries["name"].get().strip()

        if not patient_id or not name:
            messagebox.showwarning(
                "Missing Information",
                "Please enter the Patient ID and Full Name."
            )
            return

        for patient in patients:
            if patient.get("patient_id", "") == patient_id:
                messagebox.showwarning(
                    "Duplicate ID",
                    "This Patient ID already exists."
                )
                return

        dob = entries["dob"].get().strip()

        if dob:
            try:
                date.fromisoformat(dob)
            except ValueError:
                messagebox.showwarning(
                    "Invalid Date",
                    "Please enter the date as YYYY-MM-DD."
                )
                return

        selected_bed = bed_box.get()
        if selected_bed == "None":
            selected_bed = ""

        new_patient = {
            "patient_id": patient_id,
            "name": name,
            "dob": dob,
            "gender": gender_box.get(),
            "phone": entries["phone"].get().strip(),
            "address": entries["address"].get().strip(),
            "emergency_contact": entries["emergency_contact"].get().strip(),
            "diagnosis": entries["diagnosis"].get().strip(),
            "bed_id": selected_bed,
            "admission_date": date.today().isoformat(),
            "status": "Admitted" if selected_bed else "Registered",
            "discharge_date": "",
            "payment_confirmed": ""
        }

        if selected_bed:
            for bed in beds:
                if bed.get("bed_id") == selected_bed:
                    if bed.get("status") != "Available":
                        messagebox.showwarning(
                            "Bed Unavailable",
                            "This bed is no longer available."
                        )
                        update_beds()
                        return

                    bed["status"] = "Occupied"
                    bed["patient_id"] = patient_id
                    break

        patients.append(new_patient)
        save_database(data)
        display_patients()
        clear_form()

        messagebox.showinfo(
            "Success",
            "Patient registered successfully."
        )

    # Update an existing patient
    def update_patient():
        patient_id = entries["patient_id"].get().strip()

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
            messagebox.showwarning(
                "Patient Not Found",
                "Please select an existing patient."
            )
            return

        dob = entries["dob"].get().strip()

        if dob:
            try:
                date.fromisoformat(dob)
            except ValueError:
                messagebox.showwarning(
                    "Invalid Date",
                    "Please enter the date as YYYY-MM-DD."
                )
                return

        old_bed = selected_patient.get("bed_id", "")
        new_bed = bed_box.get()

        if new_bed == "None":
            new_bed = ""

        # Check whether the new bed is available
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
                    "Please choose an available bed."
                )
                update_beds()
                return

        # Release the old bed if the assignment changes
        if old_bed != new_bed:
            for bed in beds:
                if bed.get("bed_id") == old_bed:
                    bed["status"] = "Available"
                    bed["patient_id"] = ""

            for bed in beds:
                if bed.get("bed_id") == new_bed:
                    bed["status"] = "Occupied"
                    bed["patient_id"] = patient_id

        # Update patient details without resetting discharge status
        for field in fields:
            field_name = field[1]
            selected_patient[field_name] = entries[field_name].get().strip()

        selected_patient["gender"] = gender_box.get()
        selected_patient["bed_id"] = new_bed

        if selected_patient.get("status") != "Discharged":
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
        bed_box.set("None")

        for item in table.selection():
            table.selection_remove(item)

    # Return to dashboard
    def back_to_dashboard():
        from dashboard import show_dashboard
        show_dashboard("admin")

    # Buttons
    button_frame = tk.Frame(form, bg=WHITE)
    button_frame.grid(row=9, column=0, columnspan=2, pady=15)

    tk.Button(
        button_frame,
        text="Register",
        command=register_patient,
        bg=PINK_DARK,
        fg=WHITE,
        width=12
    ).pack(side="left", padx=4)

    tk.Button(
        button_frame,
        text="Update",
        command=update_patient,
        bg=PINK_ACTIVE,
        fg=WHITE,
        width=12
    ).pack(side="left", padx=4)

    tk.Button(
        button_frame,
        text="Clear",
        command=clear_form,
        bg=PINK_PALE,
        fg=TEXT_DARK,
        width=10
    ).pack(side="left", padx=4)

    tk.Button(
        root,
        text="Back to Dashboard",
        command=back_to_dashboard,
        bg=PINK_DARK,
        fg=WHITE,
        font=("Arial", 10, "bold"),
        padx=15,
        pady=6
    ).pack(pady=(0, 15))

    search_entry.bind("<KeyRelease>", lambda event: display_patients())
    table.bind("<<TreeviewSelect>>", view_patient)

    display_patients()
