
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from data import load_database, save_database, PATIENT_FIELDS


# ---------- PATIENT MANAGEMENT ----------

def show_patients(root):

    # Load the shared database.
    data = load_database()
    patients = data["patients"]
    beds = data["beds"]

    # Clear the current page.
    for widget in root.winfo_children():
        widget.destroy()

    root.title("Careflow - Patient Management")

    # Store the ID of the selected patient.
    selected_id = [""]

    # ---------- PAGE TITLE ----------

    tk.Label(
        root,
        text="Patient Management",
        font=("Arial", 20, "bold")
    ).pack(pady=10)

    # ---------- PATIENT INFORMATION FORM ----------

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
        ttk.Label(
            form,
            text=label
        ).grid(row=row, column=0, padx=5, pady=5, sticky="w")

        entry = ttk.Entry(form, width=23)
        entry.grid(row=row, column=1, padx=5, pady=5)

        entries[key] = entry

    # ---------- GENDER SELECTION ----------

    row = len(fields)

    ttk.Label(
        form,
        text="Gender"
    ).grid(row=row, column=0, padx=5, pady=5, sticky="w")

    gender_box = ttk.Combobox(
        form,
        values=["Female", "Male", "Other"],
        state="readonly",
        width=20
    )
    gender_box.grid(row=row, column=1, padx=5, pady=5)

    entries["gender"] = gender_box

    # ---------- BED SELECTION ----------

    row += 1

    ttk.Label(
        form,
        text="Available Bed"
    ).grid(row=row, column=0, padx=5, pady=5, sticky="w")

    bed_box = ttk.Combobox(
        form,
        state="readonly",
        width=20
    )
    bed_box.grid(row=row, column=1, padx=5, pady=5)

    # ---------- PATIENT RECORDS ----------

    result = ttk.LabelFrame(
        root,
        text="Patient Records",
        padding=10
    )
    result.pack(side="left", fill="both", expand=True, padx=10, pady=10)

    search_entry = ttk.Entry(result)
    search_entry.pack(fill="x", pady=5)

    search_entry.insert(0, "Search by Patient ID or Name")

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

    # ---------- UPDATE AVAILABLE BEDS ----------

    def update_beds():

        choices = []

        for bed in beds:
            if bed["status"] == "Available":
                choices.append(bed["bed_id"])

        # During an update, keep the patient's current bed available
        # as a choice for that same patient.
        if selected_id[0]:
            for patient in patients:
                if patient["patient_id"] == selected_id[0]:
                    current_bed = patient.get("bed_id", "")

                    if current_bed and current_bed not in choices:
                        choices.append(current_bed)

        bed_box["values"] = choices

        if bed_box.get() not in choices:
            bed_box.set("")

    # ---------- DISPLAY PATIENTS ----------

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
                        patient.get("bed_id", ""),
                        patient.get("status", "Registered")
                    )
                )

    # ---------- VIEW SELECTED PATIENT ----------

    def view_patient(event=None):

        selected = tree.selection()

        if not selected:
            return

        patient_id = tree.item(
            selected[0],
            "values"
        )[0]

        for patient in patients:
            if patient["patient_id"] == patient_id:

                selected_id[0] = patient_id

                # Display the selected patient's information.
                for key, widget in entries.items():
                    value = patient.get(key, "")

                    if isinstance(widget, ttk.Entry):
                        widget.config(state="normal")
                        widget.delete(0, "end")
                        widget.insert(0, value)

                        # Do not allow the patient ID to be changed.
                        if key == "patient_id":
                            widget.config(state="readonly")
                    else:
                        widget.set(value)

                update_beds()
                bed_box.set(patient.get("bed_id", ""))

                break

    # ---------- SAVE PATIENT AND BED INFORMATION ----------

    def save_patient_data(patient, new_bed_id):

        old_bed_id = patient.get("bed_id", "")

        # Release the old bed if the patient changes beds.
        if old_bed_id != new_bed_id:
            for bed in beds:
                if bed["bed_id"] == old_bed_id:
                    bed["status"] = "Available"
                    bed["patient_id"] = ""

        # Mark the new bed as occupied.
        for bed in beds:
            if bed["bed_id"] == new_bed_id:
                bed["status"] = "Occupied"
                bed["patient_id"] = patient["patient_id"]

        patient["bed_id"] = new_bed_id

        # Keep the patient status as Registered.
        patient["status"] = "Registered"

        # Save the complete shared database.
        save_database(data)

    # ---------- REGISTER PATIENT ----------

    def register_patient():

        patient = {}

        # Read the information entered in the form.
        for key, widget in entries.items():
            patient[key] = widget.get().strip()

        new_bed_id = bed_box.get()

        # Check required information.
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

        # Every patient must have a bed.
        if not new_bed_id:
            messagebox.showerror(
                "Error",
                "Please select an available bed."
            )
            return

        # Check for duplicate patient IDs.
        for old_patient in patients:
            if old_patient["patient_id"] == patient["patient_id"]:
                messagebox.showerror(
                    "Error",
                    "Patient ID already exists."
                )
                return

        # Check that the selected bed is available.
        selected_bed = None

        for bed in beds:
            if bed["bed_id"] == new_bed_id:
                if bed["status"] == "Available":
                    selected_bed = bed
                break

        if selected_bed is None:
            messagebox.showerror(
                "Error",
                "This bed is unavailable. Please select another bed."
            )
            update_beds()
            return

        # Add any missing patient fields.
        for field in PATIENT_FIELDS:
            if field not in patient:
                patient[field] = ""

        patient["bed_id"] = new_bed_id
        patient["admission_date"] = date.today().isoformat()
        patient["status"] = "Registered"
        patient["discharge_date"] = ""
        patient["payment_confirmed"] = ""

        # Add the patient to the database.
        patients.append(patient)

        # Mark the selected bed as occupied.
        selected_bed["status"] = "Occupied"
        selected_bed["patient_id"] = patient["patient_id"]

        # Save patients and beds together.
        save_database(data)

        # Refresh the patient list and available beds.
        display_patients()
        update_beds()
        clear_form()

        messagebox.showinfo(
            "Success",
            "Patient registered successfully and bed assigned."
        )

    # ---------- UPDATE PATIENT ----------

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

        for patient in patients:
            if patient["patient_id"] == selected_id[0]:

                # Prevent editing discharged patients.
                if patient["status"] == "Discharged":
                    messagebox.showwarning(
                        "Warning",
                        "Cannot edit a discharged patient."
                    )
                    return

                # Check whether another patient occupies the selected bed.
                for bed in beds:
                    if (
                        bed["bed_id"] == new_bed_id
                        and bed["status"] == "Occupied"
                        and bed.get("patient_id") != patient["patient_id"]
                    ):
                        messagebox.showerror(
                            "Error",
                            "This bed is already occupied."
                        )
                        return

                # Update the patient's information.
                for key, widget in entries.items():
                    if key != "patient_id":
                        patient[key] = widget.get().strip()

                save_patient_data(patient, new_bed_id)

                display_patients()
                update_beds()
                clear_form()

                messagebox.showinfo(
                    "Success",
                    "Patient information updated."
                )
                return

    # ---------- CLEAR FORM ----------

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

    # ---------- BUTTONS ----------

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
    ).grid(row=row + 1, column=0, columnspan=2, pady=5)

    # ---------- SEARCH AND SELECT EVENTS ----------

    search_entry.bind("<KeyRelease>", display_patients)
    tree.bind("<<TreeviewSelect>>", view_patient)

    # ---------- BACK TO DASHBOARD ----------

    def back_to_dashboard():

        from dashboard import show_dashboard

        # Return to the dashboard using a simple default username.
        show_dashboard("admin")

    tk.Button(
        root,
        text="Back to Dashboard",
        command=back_to_dashboard
    ).pack(side="bottom", pady=5)

    # Display existing records and available beds.
    update_beds()
    display_patients()
