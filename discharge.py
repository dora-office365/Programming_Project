
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
import dashboard
from data import load_database, save_database


# Pink theme colours
PINK_DARK = "#7D3458"
PINK_ACTIVE = "#AD5B82"
PINK_LIGHT = "#FFF4F8"
PINK_PALE = "#FCE7F0"
PINK_BORDER = "#EAC5D5"
TEXT_DARK = "#49323D"
TEXT_LIGHT = "#A45B7D"
WHITE = "#FFFFFF"


# Get patient information using patient ID
def find_patient(patient_id, patients):
    for patient in patients:
        if str(patient.get("patient_id", "")) == patient_id:
            return patient

    return None


# Check whether the patient can be discharged
def check_discharge_eligibility(patient):
    if patient is None:
        return "Patient record could not be found."

    if patient.get("status", "") == "Discharged":
        return "This patient has already been discharged."

    if not patient.get("bed_id", ""):
        return "This patient does not have an assigned bed."

    return ""


# Confirm patient's payment
def confirm_payment(root):
    return messagebox.askyesno(
        "Payment Confirmation",
        "Has the patient's payment been checked and completed?",
        parent=root
    )


# Release the patient's bed
def release_bed(bed_id, beds):
    for bed in beds:
        if str(bed.get("bed_id", "")) == bed_id:
            bed["status"] = "Available"
            bed["patient_id"] = ""
            return


# Update patient's discharge information
def update_discharge_record(patient):
    patient["status"] = "Discharged"
    patient["discharge_date"] = date.today().isoformat()
    patient["payment_confirmed"] = "Yes"
    patient["bed_id"] = ""


# Save updated patient and bed information
def save_discharge_data(data, patient, beds):
    bed_id = str(patient.get("bed_id", ""))

    update_discharge_record(patient)
    release_bed(bed_id, beds)

    save_database(data)


# Display patients in the table
def display_patients(table, search_entry):
    for item in table.get_children():
        table.delete(item)

    latest_data = load_database()
    latest_patients = latest_data["patients"]

    keyword = search_entry.get().strip().lower()

    for patient in latest_patients:
        patient_ic = str(patient.get("patient_ic", ""))
        patient_id = str(patient.get("patient_id", ""))
        patient_name = str(patient.get("name", ""))
        bed_id = str(patient.get("bed_id", ""))
        status = patient.get("status", "Registered")

        if status != "Discharged" and bed_id:
            search_text = (
                patient_ic + " "
                + patient_id + " "
                + patient_name
            ).lower()

            if keyword in search_text:
                table.insert(
                    "",
                    "end",
                    values=(
                        patient_ic or "-",
                        patient_id,
                        patient_name,
                        bed_id,
                        status
                    )
                )


# Clear the search box
def clear_search(search_entry, table):
    search_entry.delete(0, tk.END)
    display_patients(table, search_entry)


# Process the selected patient's discharge
def discharge_patient(root, table, search_entry, data, patients, beds):
    selected = table.selection()

    if not selected:
        messagebox.showwarning(
            "Select Patient",
            "Please select a patient to discharge.",
            parent=root
        )
        return

    values = table.item(selected[0], "values")
    patient_id = str(values[1])

    latest_data = load_database()
    latest_patients = latest_data["patients"]
    latest_beds = latest_data["beds"]

    selected_patient = find_patient(patient_id, latest_patients)

    error_message = check_discharge_eligibility(selected_patient)

    if error_message:
        messagebox.showwarning(
            "Discharge Not Allowed",
            error_message,
            parent=root
        )
        display_patients(table, search_entry)
        return

    if not confirm_payment(root):
        messagebox.showwarning(
            "Discharge Cancelled",
            "Please complete the payment before discharging the patient.",
            parent=root
        )
        return

    save_discharge_data(
        latest_data,
        selected_patient,
        latest_beds
    )

    # Update the local database references
    data.clear()
    data.update(latest_data)
    patients[:] = latest_patients
    beds[:] = latest_beds

    display_patients(table, search_entry)

    messagebox.showinfo(
        "Success",
        "Patient discharged successfully.\n"
        "The bed is now available.",
        parent=root
    )


# Main discharge page
def show_discharge(root):

    data = load_database()
    patients = data["patients"]
    beds = data["beds"]

    # Clear the current page
    for widget in root.winfo_children():
        widget.destroy()

    root.title("Careflow - Discharge Management")
    root.geometry("1100x700")
    root.configure(bg=PINK_LIGHT)

    # Navigation sidebar
    content = dashboard.add_navigation(root, "Discharge")

    # Page heading
    tk.Label(
        content,
        text="Discharge Management",
        font=("Arial", 24, "bold"),
        bg=PINK_LIGHT,
        fg=PINK_DARK
    ).pack(anchor="w", padx=25, pady=(20, 5))

    tk.Label(
        content,
        text="Confirm payment before discharging a patient",
        font=("Arial", 11),
        bg=PINK_LIGHT,
        fg=TEXT_DARK
    ).pack(anchor="w", padx=25, pady=(0, 20))

    # Search section
    search_frame = tk.Frame(
        content,
        bg=WHITE,
        padx=15,
        pady=15
    )
    search_frame.pack(fill="x", padx=25, pady=(0, 15))

    tk.Label(
        search_frame,
        text="Search Patient IC, ID or Name:",
        bg=WHITE,
        fg=TEXT_DARK,
        font=("Arial", 10)
    ).pack(side="left")

    search_entry = tk.Entry(
        search_frame,
        width=30,
        font=("Arial", 10)
    )
    search_entry.pack(side="left", padx=10)

    # Patient table
    table_frame = tk.Frame(content, bg=WHITE)
    table_frame.pack(
        fill="both",
        expand=True,
        padx=25,
        pady=(0, 15)
    )

    columns = (
        "patient_ic",
        "patient_id",
        "name",
        "bed_id",
        "status"
    )

    table = ttk.Treeview(
        table_frame,
        columns=columns,
        show="headings",
        height=15
    )

    # Table headings
    table.heading("patient_ic", text="Patient IC")
    table.heading("patient_id", text="Patient ID")
    table.heading("name", text="Patient Name")
    table.heading("bed_id", text="Bed ID")
    table.heading("status", text="Status")

    # Table column widths
    table.column("patient_ic", width=140, anchor="center")
    table.column("patient_id", width=110, anchor="center")
    table.column("name", width=180, anchor="center")
    table.column("bed_id", width=100, anchor="center")
    table.column("status", width=110, anchor="center")

    scrollbar = ttk.Scrollbar(
        table_frame,
        orient="vertical",
        command=table.yview
    )

    table.configure(yscrollcommand=scrollbar.set)

    table.pack(
        side="left",
        fill="both",
        expand=True,
        padx=10,
        pady=10
    )

    scrollbar.pack(side="right", fill="y", pady=10)

    # Buttons
    button_frame = tk.Frame(content, bg=PINK_LIGHT)
    button_frame.pack(pady=(0, 15))

    tk.Button(
        button_frame,
        text="Confirm Discharge",
        command=lambda: discharge_patient(
            root, table, search_entry, data, patients, beds
        ),
        bg=PINK_DARK,
        fg=WHITE,
        activebackground=PINK_ACTIVE,
        activeforeground=WHITE,
        width=18,
        cursor="hand2"
    ).pack(side="left", padx=5)

    tk.Button(
        button_frame,
        text="Clear Search",
        command=lambda: clear_search(search_entry, table),
        bg=PINK_PALE,
        fg=TEXT_DARK,
        activebackground=PINK_LIGHT,
        width=12,
        cursor="hand2"
    ).pack(side="left", padx=5)

    # Search while typing
    search_entry.bind(
        "<KeyRelease>",
        lambda event: display_patients(table, search_entry)
    )

    # Display patients when the page opens
    display_patients(table, search_entry)
