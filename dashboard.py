import tkinter as tk
from tkinter import messagebox
import json
import os
from datetime import date

# ---------- MAIN WINDOW ----------

root = tk.Tk()
root.title("Careflow - Hospital Inpatient Management System")
root.geometry("900x600")


# ---------- CLEAR WINDOW ----------

def clear_window():
    for widget in root.winfo_children():
        widget.destroy()


# ---------- LOGIN PAGE ----------

def show_login():
    clear_window()

    frame = tk.Frame(root, padx=30, pady=30)
    frame.pack(expand=True)

    tk.Label(
        frame, text="Careflow", font=("Arial", 24, "bold")
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

        for user in users:
            if (user["username"] == username
                    and user["password"] == password):
                show_dashboard(username)
                return

        messagebox.showerror(
            "Error", "Incorrect username or password."
        )

    tk.Button(frame, text="Login", command=login).pack(pady=15)

    tk.Label(
        frame, text="Demo login: admin / admin123"
    ).pack()


# ---------- DASHBOARD ----------

def show_dashboard(username):
    clear_window()

    tk.Label(
        root, text="Careflow Dashboard",
        font=("Arial", 20, "bold")
    ).pack(pady=10)

    tk.Label(root, text=f"Welcome, {username}").pack()

    # Calculate daily statistics
    total_patients = len(patients)
    current_patients = 0
    available_beds = 0
    occupied_beds = 0
    discharged_today = 0

    for patient in patients:
        if patient["status"] == "Admitted":
            current_patients += 1

        if patient["discharge_date"] == date.today().isoformat():
            discharged_today += 1

    for bed in beds:
        if bed["status"] == "Available":
            available_beds += 1
        else:
            occupied_beds += 1

    # Display statistics
    
    tk.Label(
        root, text=f"Registered Patients: {total_patients}"
    ).pack(pady=5)

    tk.Label(
        root, text=f"Current Inpatients: {current_patients}"
    ).pack(pady=5)

    tk.Label(
        root, text=f"Available Beds: {available_beds}"
    ).pack(pady=5)

    tk.Label(
        root, text=f"Occupied Beds: {occupied_beds}"
    ).pack(pady=5)

    tk.Label(
        root, text=f"Discharges Today: {discharged_today}"
    ).pack(pady=5)

    # Navigation buttons
    tk.Label(
        root, text="Navigation", font=("Arial", 14, "bold")
    ).pack(pady=10)

    tk.Button(
        root, text="Patient Management",
        command=lambda: messagebox.showinfo(
            "Information", "Patient module will be added here."
        )
    ).pack(pady=3)

    tk.Button(
        root, text="Bed Management",
        command=lambda: messagebox.showinfo(
            "Information", "Bed module will be added here."
        )
    ).pack(pady=3)

    tk.Button(
        root, text="Discharge",
        command=lambda: messagebox.showinfo(
            "Information", "Discharge module will be added here."
        )
    ).pack(pady=3)

    # Daily patient report
    tk.Label(
        root, text="Patient Report",
        font=("Arial", 14, "bold")
    ).pack(pady=10)

    for patient in patients:
        tk.Label(
            root,
            text=(
                f'{patient["patient_id"]} - '
                f'{patient["name"]} - {patient["status"]}'
            )
        ).pack()

    # Logout button
    tk.Button(
        root, text="Logout", command=show_login
    ).pack(pady=15)

# ---------- START PROGRAM ----------

show_login()
root.mainloop()
