import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from data import load_database, save_database


def show_discharge(root):
    data = load_database()
    patients = data["patients"]
    beds = data["beds"]

    # Clear the current page
    for widget in root.winfo_children():
        widget.destroy()

    root.title("Careflow - Discharge Management")

    # Page title
    tk.Label(
        root,
        text="Discharge Management",
        font=("Arial", 20, "bold")
    ).pack(pady=15)

    tk.Label(
        root,
        text="Select a patient and confirm payment before discharge."
    ).pack(pady=5)

    # Patient table
    table_frame = ttk.Frame(root)
    table_frame.pack(fill="both", expand=True, padx=20, pady=10)

    columns = ("patient_id", "name", "bed_id", "status")

    tree = ttk.Treeview(
        table_frame,
        columns=columns,
        show="headings"
    )

    tree.heading("patient_id", text="Patient ID")
    tree.heading("name", text="Patient Name")
    tree.heading("bed_id", text="Bed ID")
    tree.heading("status", text="Status")

    tree.column("patient_id", width=130, anchor="center")
    tree.column("name", width=220, anchor="center")
    tree.column("bed_id", width=120, anchor="center")
    tree.column("status", width=130, anchor="center")

    scrollbar = ttk.Scrollbar(
        table_frame,
        orient="vertical",
        command=tree.yview
    )
    tree.configure(yscrollcommand=scrollbar.set)

    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    def display_patients():
        for item in tree.get_children():
            tree.delete(item)

        for patient in patients:
            if (
                patient.get("status", "Registered") != "Discharged"
                and patient.get("bed_id", "")
            ):
                tree.insert(
                    "",
                    "end",
                    values=(
                        patient.get("patient_id", ""),
                        patient.get("name", ""),
                        patient.get("bed_id", ""),
                        patient.get("status", "Registered")
                    )
                )

    def discharge_patient():
        selected = tree.selection()

        if not selected:
            messagebox.showwarning(
                "Warning",
                "Please select a patient to discharge."
            )
            return

        values = tree.item(selected[0], "values")
        patient_id = values[0]

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

        if selected_patient.get("status", "") == "Discharged":
            messagebox.showwarning(
                "Warning",
                "This patient has already been discharged."
            )
            return

        bed_id = selected_patient.get("bed_id", "")

        if not bed_id:
            messagebox.showerror(
                "Error",
                "This patient does not have an assigned bed."
            )
            return

        payment_complete = messagebox.askyesno(
            "Payment Confirmation",
            "Has the patient's payment been checked and completed?"
        )

        if not payment_complete:
            messagebox.showwarning(
                "Discharge Cancelled",
                "Please complete the payment before discharging the patient."
            )
            return

        # Update the patient record
        selected_patient["status"] = "Discharged"
        selected_patient["discharge_date"] = date.today().isoformat()
        selected_patient["payment_confirmed"] = "Yes"
        selected_patient["bed_id"] = ""

        # Make the bed available again
        for bed in beds:
            if (
                bed.get("bed_id", "") == bed_id
                and bed.get("patient_id", "") == patient_id
            ):
                bed["status"] = "Available"
                bed["patient_id"] = ""
                break

        # Save changes to the shared database
        save_database(data)

        display_patients()

        messagebox.showinfo(
            "Success",
            "Patient discharged successfully.\nThe bed is now available."
        )

    def back_to_dashboard():
        from dashboard import show_dashboard
        show_dashboard("admin")

    # Buttons
    button_frame = ttk.Frame(root)
    button_frame.pack(pady=10)

    ttk.Button(
        button_frame,
        text="Confirm Discharge",
        command=discharge_patient
    ).pack(side="left", padx=10)

    ttk.Button(
        button_frame,
        text="Back to Dashboard",
        command=back_to_dashboard
    ).pack(side="left", padx=10)

    # Show patients who can be discharged
    display_patients()
