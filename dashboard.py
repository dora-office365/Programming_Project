
import tkinter as tk
from tkinter import messagebox
from datetime import date
from data import load_database, save_database

# ---------- MAIN WINDOW ----------
root = tk.Tk()
root.title("Careflow - Hospital Inpatient Management System")
root.geometry("900x600")

data = load_database()
users = data["users"]
patients = data["patients"]
beds = data["beds"]


# ---------- CLEAR WINDOW ----------
def clear_window():
    for widget in root.winfo_children():
        widget.destroy()


# ---------- REFRESH DATABASE ----------
def refresh_data():
    global data, users, patients, beds

    data = load_database()
    users = data["users"]
    patients = data["patients"]
    beds = data["beds"]


# ---------- SAVE DATABASE ----------
def save_data():
    data["users"] = users
    data["patients"] = patients
    data["beds"] = beds
    save_database(data)


# ---------- LOGIN PAGE ----------
def show_login():
    refresh_data()
    clear_window()

    frame = tk.Frame(root, padx=30, pady=30)
    frame.pack(expand=True)

    tk.Label(
        frame,
        text="Careflow",
        font=("Arial", 24, "bold")
    ).pack(pady=10)

    tk.Label(frame, text="Username").pack()
    username_entry = tk.Entry(frame)
    username_entry.pack(pady=5)

    tk.Label(frame, text="Password").pack()
    password_entry = tk.Entry(frame, show="*")
    password_entry.pack(pady=5)

    def login():
        username = username_entry.get().strip()
        password = password_entry.get()

        refresh_data()

        for user in users:
            if (
                user["username"] == username
                and user["password"] == password
            ):
                show_dashboard(username)
                return

        messagebox.showerror(
            "Error",
            "Incorrect username or password."
        )

    tk.Button(
        frame,
        text="Login",
        command=login
    ).pack(pady=15)

    tk.Label(
        frame,
        text="Demo login: admin / admin123"
    ).pack()

    password_entry.bind(
        "<Return>",
        lambda event: login()
    )


# ---------- OPEN PATIENT MANAGEMENT ----------
def open_patient_management():
    refresh_data()

    try:
        from patient import show_patients
        show_patients(root)
    except Exception as error:
        messagebox.showerror(
            "Error",
            "Unable to open Patient Management.\n" + str(error)
        )


# ---------- OPEN BED MANAGEMENT ----------
def open_bed_management():
    refresh_data()

    try:
        from bed_management import show_bed_management
        show_bed_management(root)
    except Exception as error:
        messagebox.showerror(
            "Error",
            "Unable to open Bed Management.\n" + str(error)
        )


# ---------- OPEN DISCHARGE ----------
def open_discharge():
    refresh_data()

    try:
        from discharge import show_discharge
        show_discharge(root)
    except Exception as error:
        messagebox.showerror(
            "Error",
            "Unable to open Discharge.\n" + str(error)
        )


# ---------- DASHBOARD PAGE ----------
def show_dashboard(username):
    refresh_data()
    clear_window()

    tk.Label(
        root,
        text="Careflow Dashboard",
        font=("Arial", 20, "bold")
    ).pack(pady=10)

    tk.Label(
        root,
        text=f"Welcome, {username}"
    ).pack()

    # Calculate dashboard statistics
    total_patients = len(patients)
    current_patients = 0
    available_beds = 0
    occupied_beds = 0
    discharged_today = 0

    for patient in patients:
        # A current inpatient must have a bed and not be discharged
        if (
            patient.get("bed_id", "")
            and patient.get("status", "") != "Discharged"
        ):
            current_patients += 1

        if patient.get("discharge_date", "") == date.today().isoformat():
            discharged_today += 1

    for bed in beds:
        if bed.get("status", "") == "Available":
            available_beds += 1
        elif bed.get("status", "") == "Occupied":
            occupied_beds += 1

    # Display dashboard statistics
    tk.Label(
        root,
        text=f"Registered Patients: {total_patients}"
    ).pack(pady=5)

    tk.Label(
        root,
        text=f"Current Inpatients: {current_patients}"
    ).pack(pady=5)

    tk.Label(
        root,
        text=f"Available Beds: {available_beds}"
    ).pack(pady=5)

    tk.Label(
        root,
        text=f"Occupied Beds: {occupied_beds}"
    ).pack(pady=5)

    tk.Label(
        root,
        text=f"Discharges Today: {discharged_today}"
    ).pack(pady=5)

    # Navigation buttons
    tk.Label(
        root,
        text="Navigation",
        font=("Arial", 14, "bold")
    ).pack(pady=10)

    tk.Button(
        root,
        text="Patient Management",
        command=open_patient_management
    ).pack(pady=3)

    tk.Button(
        root,
        text="Bed Management",
        command=open_bed_management
    ).pack(pady=3)

    tk.Button(
        root,
        text="Discharge",
        command=open_discharge
    ).pack(pady=3)

    # Patient report
    tk.Label(
        root,
        text="Patient Report",
        font=("Arial", 14, "bold")
    ).pack(pady=10)

    report_frame = tk.Frame(root)
    report_frame.pack(
        fill="both",
        expand=True,
        padx=20
    )

    scrollbar = tk.Scrollbar(report_frame)
    scrollbar.pack(side="right", fill="y")

    report_list = tk.Listbox(
        report_frame,
        height=5,
        yscrollcommand=scrollbar.set
    )
    report_list.pack(
        side="left",
        fill="both",
        expand=True
    )

    scrollbar.config(command=report_list.yview)

    if len(patients) == 0:
        report_list.insert(
            "end",
            "No patient records available."
        )
    else:
        for patient in patients:
            report_list.insert(
                "end",
                patient.get("patient_id", "")
                + " - "
                + patient.get("name", "")
                + " - "
                + patient.get("status", "Registered")
            )

    # Logout button
    tk.Button(
        root,
        text="Logout",
        command=show_login
    ).pack(pady=10)


# ---------- START PROGRAM ----------
show_login()
root.mainloop()
