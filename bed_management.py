import tkinter as tk
from tkinter import ttk
from data import load_database


def show_bed_management(root):
    data = load_database()
    patients = data["patients"]
    beds = data["beds"]

    # Clear the current page
    for widget in root.winfo_children():
        widget.destroy()

    root.title("Careflow - Bed Management")

    # Page title
    tk.Label(
        root,
        text="Bed Management",
        font=("Arial", 20, "bold")
    ).pack(pady=15)

    # Search section
    search_frame = ttk.Frame(root)
    search_frame.pack(fill="x", padx=20, pady=5)

    ttk.Label(
        search_frame,
        text="Search by Bed ID, Patient ID or Name:"
    ).pack(side="left", padx=5)

    search_entry = ttk.Entry(search_frame, width=30)
    search_entry.pack(side="left", padx=5)

    # Bed information table
    table_frame = ttk.Frame(root)
    table_frame.pack(fill="both", expand=True, padx=20, pady=10)

    columns = ("bed_id", "status", "patient_id", "patient_name")

    tree = ttk.Treeview(
        table_frame,
        columns=columns,
        show="headings"
    )

    tree.heading("bed_id", text="Bed ID")
    tree.heading("status", text="Bed Status")
    tree.heading("patient_id", text="Patient ID")
    tree.heading("patient_name", text="Patient Name")

    tree.column("bed_id", width=120, anchor="center")
    tree.column("status", width=120, anchor="center")
    tree.column("patient_id", width=150, anchor="center")
    tree.column("patient_name", width=220, anchor="center")

    scrollbar = ttk.Scrollbar(
        table_frame,
        orient="vertical",
        command=tree.yview
    )
    tree.configure(yscrollcommand=scrollbar.set)

    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    def display_beds(keyword=""):
        for item in tree.get_children():
            tree.delete(item)

        keyword = keyword.lower().strip()

        for bed in beds:
            bed_id = bed.get("bed_id", "")
            status = bed.get("status", "Available")
            patient_id = bed.get("patient_id", "")
            patient_name = ""

            # Find the patient assigned to this bed
            for patient in patients:
                if (
                    patient.get("patient_id", "") == patient_id
                    or (
                        patient.get("bed_id", "") == bed_id
                        and patient.get("status", "") != "Discharged"
                    )
                ):
                    patient_id = patient.get("patient_id", "")
                    patient_name = patient.get("name", "")
                    break

            # Show only matching beds when searching
            if (
                keyword in bed_id.lower()
                or keyword in status.lower()
                or keyword in patient_id.lower()
                or keyword in patient_name.lower()
            ):
                tree.insert(
                    "",
                    "end",
                    values=(
                        bed_id,
                        status,
                        patient_id if status == "Occupied" else "-",
                        patient_name if status == "Occupied" else "-"
                    )
                )

    def search_beds(event=None):
        display_beds(search_entry.get())

    def back_to_dashboard():
        from dashboard import show_dashboard
        show_dashboard("admin")

    # Search when the user types
    search_entry.bind("<KeyRelease>", search_beds)

    # Back button
    ttk.Button(
        root,
        text="Back to Dashboard",
        command=back_to_dashboard
    ).pack(pady=10)

    # Display all beds when the page opens
    display_beds()
