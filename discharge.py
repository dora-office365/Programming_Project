import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from data import load_database, save_database


# Pink theme colours
PINK_DARK = "#7D3458"
PINK_ACTIVE = "#AD5B82"
PINK_LIGHT = "#FFF4F8"
PINK_PALE = "#FCE7F0"
TEXT_DARK = "#49323D"
WHITE = "#FFFFFF"


def show_discharge(root):
    data = load_database()
    patients = data["patients"]
    beds = data["beds"]

    for widget in root.winfo_children():
        widget.destroy()

    root.title("Careflow - Discharge Management")
    root.geometry("1100x700")
    root.configure(bg=PINK_LIGHT)

    # Page heading
    tk.Label(
        root,
        text="Discharge Management",
        font=("Arial", 24, "bold"),
        bg=PINK_LIGHT,
        fg=PINK_DARK
    ).pack(anchor="w", padx=25, pady=(20, 5))

    tk.Label(
        root,
        text="Confirm payment before discharging a patient",
        font=("Arial", 11),
        bg=PINK_LIGHT,
        fg=TEXT_DARK
    ).pack(anchor="w", padx=25, pady=(0, 20))

    # Search section
    search_frame = tk.Frame(root, bg=WHITE, padx=15, pady=15)
    search_frame.pack(fill="x", padx=25, pady=(0, 15))

    tk.Label(
        search_frame,
        text="Search Patient ID or Name:",
        bg=WHITE,
        fg=TEXT_DARK,
        font=("Arial", 10)
    ).pack(side="left")

    search_entry = tk.Entry(search_frame, width=30, font=("Arial", 10))
    search_entry.pack(side="left", padx=10)

    # Patient table
    table_frame = tk.Frame(root, bg=WHITE)
    table_frame.pack(fill="both", expand=True, padx=25, pady=(0, 15))

    columns = ("patient_id", "name", "bed_id", "status")

    table = ttk.Treeview(
        table_frame,
        columns=columns,
        show="headings",
        height=15
    )

    table.heading("patient_id", text="Patient ID")
    table.heading("name", text="Patient Name")
    table.heading("bed_id", text="Bed ID")
    table.heading("status", text="Status")

    table.column("patient_id", width=150, anchor="center")
    table.column("name", width=250, anchor="center")
    table.column("bed_id", width=150, anchor="center")
    table.column("status", width=150, anchor="center")

    scrollbar = ttk.Scrollbar(
        table_frame,
        orient="vertical",
        command=table.yview
    )

    table.configure(yscrollcommand=scrollbar.set)

    table.pack(side="left", fill="both", expand=True, padx=10, pady=10)
    scrollbar.pack(side="right", fill="y", pady=10)

    # Display patients who have an assigned bed
    def display_patients():
        for item in table.get_children():
            table.delete(item)

        keyword = search_entry.get().strip().lower()

        for patient in patients:
            patient_id = patient.get("patient_id", "")
            patient_name = patient.get("name", "")
            bed_id = patient.get("bed_id", "")
            status = patient.get("status", "Registered")

            if status != "Discharged" and bed_id:
                search_text = (patient_id + " " + patient_name).lower()

                if keyword in search_text:
                    table.insert(
                        "",
                        "end",
                        values=(
                            patient_id,
                            patient_name,
                            bed_id,
                            status
                        )
                    )

    # Discharge the selected patient
    def discharge_patient():
        selected = table.selection()

        if not selected:
            messagebox.showwarning(
                "Select Patient",
                "Please select a patient to discharge."
            )
            return

        values = table.item(selected[0], "values")
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
                "Already Discharged",
                "This patient has already been discharged."
            )
            return

        bed_id = selected_patient.get("bed_id", "")

        if not bed_id:
            messagebox.showwarning(
                "No Bed Assigned",
                "This patient does not have an assigned bed."
            )
            return

        # Ask staff to confirm payment
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

        # Update patient information
        selected_patient["status"] = "Discharged"
        selected_patient["discharge_date"] = date.today().isoformat()
        selected_patient["payment_confirmed"] = "Yes"
        selected_patient["bed_id"] = ""

        # Make the bed available again
        for bed in beds:
            if bed.get("bed_id", "") == bed_id:
                bed["status"] = "Available"
                bed["patient_id"] = ""

        # Save changes to the JSON database
        save_database(data)

        display_patients()

        messagebox.showinfo(
            "Success",
            "Patient discharged successfully.\nThe bed is now available."
        )

    # Clear search
    def clear_search():
        search_entry.delete(0, tk.END)
        display_patients()

    # Return to dashboard
    def back_to_dashboard():
        from dashboard import show_dashboard
        show_dashboard("admin")

    # Buttons
    button_frame = tk.Frame(root, bg=PINK_LIGHT)
    button_frame.pack(pady=(0, 15))

    tk.Button(
        button_frame,
        text="Confirm Discharge",
        command=discharge_patient,
        bg=PINK_DARK,
        fg=WHITE,
        width=18
    ).pack(side="left", padx=5)

    tk.Button(
        button_frame,
        text="Clear Search",
        command=clear_search,
        bg=PINK_PALE,
        fg=TEXT_DARK,
        width=12
    ).pack(side="left", padx=5)

    tk.Button(
        button_frame,
        text="Back to Dashboard",
        command=back_to_dashboard,
        bg=PINK_ACTIVE,
        fg=WHITE,
        width=18
    ).pack(side="left", padx=5)

    search_entry.bind("<KeyRelease>", lambda event: display_patients())

    display_patients()