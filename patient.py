import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from data import load_database, save_database, PATIENT_FIELDS


def show_patients(root):
    data = load_database()
    patients = data["patients"]
    beds = data["beds"]

    # Clear the current page
    for widget in root.winfo_children():
        widget.destroy()

    root.title("Careflow - Patient Management")
    selected_id = [""]

    # Page title
    tk.Label(
        root,
        text="Patient Management",
        font=("Arial", 20, "bold")
    ).pack(pady=10)

    # Patient information form
    form = ttk.LabelFrame(
        root,
        text="Patient Information",
        padding=10
    )
    form.pack(side="left", fill="y", padx=10, pady=10)

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

    for row, (label, key) in enumerate(fields):
        ttk.Label(form, text=label).grid(
            row=row, column=0, padx=5, pady=5, sticky="w"
        )

        entry = ttk.Entry(form, width=23)
        entry.grid(row=row, column=1, padx=5, pady=5)
        entries[key] = entry

    # Gender selection
    row = len(fields)

    ttk.Label(form, text="Gender").grid(
        row=row, column=0, padx=5, pady=5, sticky="w"
    )

    gender_box = ttk.Combobox(
        form,
        values=["Female", "Male", "Other"],
        state="readonly",
        width=20
    )
    gender_box.grid(row=row, column=1, padx=5, pady=5)
    entries["gender"] = gender_box

    # Bed selection
    row += 1

    ttk.Label(form, text="Available Bed").grid(
        row=row, column=0, padx=5, pady=5, sticky="w"
    )

    bed_box = ttk.Combobox(
        form,
        state="readonly",
        width=20
    )
    bed_box.grid(row=row, column=1, padx=5, pady=5)

    # Patient records section
    result = ttk.LabelFrame(
        root,
        text="Patient Records",
        padding=10
    )
    result.pack(
        side="left",
        fill="both",
        expand=True,
        padx=10,
        pady=10
    )

    search_entry = ttk.Entry(result)
    search_entry.pack(fill="x", pady=5)

    tree = ttk.Treeview(
        result,
        columns=("id", "name", "bed", "status"),
        show="headings"
    )

    tree.heading("id", text="Patient ID")
    tree.heading("name", text="Name")
    tree.heading("bed", text="Bed")
    tree.heading("status", text="Status")

    tree.column("id", width=90)
    tree.column("name", width=140)
    tree.column("bed", width=90)
    tree.column("status", width=100)

    tree.pack(fill="both", expand=True)

    # Update the available bed list
    def update_beds():
        choices = []

        for bed in beds:
            if bed.get("status", "") == "Available":
                choices.append(bed["bed_id"])

        # Keep the selected patient's current bed available
        # in the dropdown when editing that patient.
        if selected_id[0]:
            for patient in patients:
                if patient.get("patient_id", "") == selected_id[0]:
                    current_bed = patient.get("bed_id", "")

                    if (
                        current_bed
                        and current_bed not in choices
                        and patient.get("status", "") != "Discharged"
                    ):
                        choices.append(current_bed)

        bed_box["values"] = choices

        if bed_box.get() not in choices:
            bed_box.set("")

    # Display and search patient records
    def display_patients(event=None):
        for item in tree.get_children():
            tree.delete(item)

        keyword = search_entry.get().lower().strip()

        if keyword == "search by patient id or name":
            keyword = ""

        for patient in patients:
            patient_id = patient.get("patient_id", "")
            name = patient.get("name", "")

            if (
                keyword in patient_id.lower()
                or keyword in name.lower()
            ):
                tree.insert(
                    "",
                    "end",
                    values=(
                        patient_id,
                        name,
                        patient.get("bed_id", "") or "-",
                        patient.get("status", "Registered")
                    )
                )

    # Display the selected patient's information
    def view_patient(event=None):
        selected = tree.selection()

        if not selected:
            return

        patient_id = tree.item(selected[0], "values")[0]

        for patient in patients:
            if patient.get("patient_id", "") == patient_id:
                selected_id[0] = patient_id

                for key, widget in entries.items():
                    value = patient.get(key, "")

                    if isinstance(widget, ttk.Entry):
                        widget.config(state="normal")
                        widget.delete(0, "end")
                        widget.insert(0, value)

                        if key == "patient_id":
                            widget.config(state="readonly")
                    else:
                        widget.set(value)

                update_beds()
                bed_box.set(patient.get("bed_id", ""))
                break

    # Register a new patient
    def register_patient():
        patient = {}

        for key, widget in entries.items():
            patient[key] = widget.get().strip()

        new_bed_id = bed_box.get()

        if not patient["patient_id"] or not patient["name"]:
            messagebox.showerror(
                "Error",
                "Patient ID and name are required."
            )
            return

        if not patient["gender"]:
            messagebox.showerror(
                "Error",
                "Please select the patient's gender."
            )
            return

        if not new_bed_id:
            messagebox.showerror(
                "Error",
                "Every patient must be assigned an available bed."
            )
            return

        # Check for duplicate patient IDs
        for old_patient in patients:
            if old_patient.get("patient_id", "") == patient["patient_id"]:
                messagebox.showerror(
                    "Error",
                    "Patient ID already exists."
                )
                return

        # Check whether the selected bed is still available
        selected_bed = None

        for bed in beds:
            if bed.get("bed_id", "") == new_bed_id:
                if bed.get("status", "") == "Available":
                    selected_bed = bed
                break

        if selected_bed is None:
            messagebox.showerror(
                "Error",
                "This bed is unavailable. Please select another bed."
            )
            update_beds()
            return

        # Add any missing database fields
        for field in PATIENT_FIELDS:
            if field not in patient:
                patient[field] = ""

        patient["bed_id"] = new_bed_id
        patient["admission_date"] = date.today().isoformat()
        patient["status"] = "Registered"
        patient["discharge_date"] = ""
        patient["payment_confirmed"] = ""

        # Assign the bed to the patient
        selected_bed["status"] = "Occupied"
        selected_bed["patient_id"] = patient["patient_id"]

        patients.append(patient)
        save_database(data)

        display_patients()
        update_beds()
        clear_form()

        messagebox.showinfo(
            "Success",
            "Patient registered successfully and bed assigned."
        )

    # Update an existing patient
    def update_patient():
        if not selected_id[0]:
            messagebox.showwarning(
                "Warning",
                "Select a patient from the list first."
            )
            return

        new_bed_id = bed_box.get()

        if not new_bed_id:
            messagebox.showerror(
                "Error",
                "Every patient must have an assigned bed."
            )
            return

        selected_patient = None

        for patient in patients:
            if patient.get("patient_id", "") == selected_id[0]:
                selected_patient = patient
                break

        if selected_patient is None:
            messagebox.showerror(
                "Error",
                "Patient record could not be found."
            )
            return

        if selected_patient.get("status", "") == "Discharged":
            messagebox.showwarning(
                "Warning",
                "Cannot edit a discharged patient."
            )
            return

        old_bed_id = selected_patient.get("bed_id", "")

        # Check that the new bed is available or belongs
        # to this patient already.
        selected_bed = None

        for bed in beds:
            if bed.get("bed_id", "") == new_bed_id:
                if (
                    bed.get("status", "") == "Available"
                    or bed.get("patient_id", "") == selected_id[0]
                ):
                    selected_bed = bed
                break

        if selected_bed is None:
            messagebox.showerror(
                "Error",
                "This bed is already occupied. Please select another bed."
            )
            update_beds()
            return

        # Check required fields
        if not entries["name"].get().strip():
            messagebox.showerror(
                "Error",
                "Patient name is required."
            )
            return

        if not entries["gender"].get().strip():
            messagebox.showerror(
                "Error",
                "Please select the patient's gender."
            )
            return

        # Release the old bed if the patient changes beds
        if old_bed_id != new_bed_id:
            for bed in beds:
                if (
                    bed.get("bed_id", "") == old_bed_id
                    and bed.get("patient_id", "") == selected_id[0]
                ):
                    bed["status"] = "Available"
                    bed["patient_id"] = ""

        # Update the patient information
        for key, widget in entries.items():
            if key != "patient_id":
                selected_patient[key] = widget.get().strip()

        selected_patient["bed_id"] = new_bed_id
        selected_patient["status"] = "Registered"

        # Make sure the selected bed is occupied by this patient
        selected_bed["status"] = "Occupied"
        selected_bed["patient_id"] = selected_id[0]

        save_database(data)

        display_patients()
        update_beds()
        clear_form()

        messagebox.showinfo(
            "Success",
            "Patient information updated successfully."
        )

    # Clear the form
    def clear_form():
        selected_id[0] = ""

        for widget in entries.values():
            if isinstance(widget, ttk.Entry):
                widget.config(state="normal")
                widget.delete(0, "end")
            else:
                widget.set("")

        bed_box.set("")
        update_beds()

    # Buttons
    row += 1

    ttk.Button(
        form,
        text="Register",
        command=register_patient
    ).grid(row=row, column=0, padx=5, pady=10)

    ttk.Button(
        form,
        text="Update",
        command=update_patient
    ).grid(row=row, column=1, padx=5, pady=10)

    ttk.Button(
        form,
        text="Clear",
        command=clear_form
    ).grid(
        row=row + 1,
        column=0,
        columnspan=2,
        pady=5
    )

    # Search and select events
    search_entry.bind("<KeyRelease>", display_patients)
    tree.bind("<<TreeviewSelect>>", view_patient)

    # Return to dashboard
    def back_to_dashboard():
        from dashboard import show_dashboard
        show_dashboard("admin")

    tk.Button(
        root,
        text="Back to Dashboard",
        command=back_to_dashboard
    ).pack(side="bottom", pady=5)

    # Initial display
    update_beds()
    display_patients()
