import tkinter as tk
from tkinter import ttk, messagebox
import dashboard
from data import load_database

# Pink theme colours
PINK_DARK = "#7D3458"
PINK_ACTIVE = "#AD5B82"
PINK_LIGHT = "#FFF4F8"
PINK_PALE = "#FCE7F0"
PINK_BORDER = "#EAC5D5"
TEXT_DARK = "#49323D"
TEXT_LIGHT = "#A45B7D"
WHITE = "#FFFFFF"

def show_bed_management(root):
    # Clear the previous page
    for widget in root.winfo_children():
        widget.destroy()

    root.title("Careflow - Bed Management")
    root.geometry("1150x750")
    root.configure(bg=PINK_LIGHT)

    # Add the shared navigation menu
    content = dashboard.add_navigation(
        root,
        "Bed Management"
    )

    # Page heading
    tk.Label(
        content,
        text="Bed Management",
        font=("Arial", 24, "bold"),
        bg=PINK_LIGHT,
        fg=PINK_DARK
    ).pack(anchor="w", padx=25, pady=(20, 5))

    tk.Label(
        content,
        text="View available beds and check current bed assignments",
        font=("Arial", 11),
        bg=PINK_LIGHT,
        fg=TEXT_DARK
    ).pack(anchor="w", padx=25, pady=(0, 20))

    # Statistics
    stats_frame = tk.Frame(content, bg=PINK_LIGHT)
    stats_frame.pack(fill="x", padx=25, pady=5)

    available_label = tk.Label(
        stats_frame,
        text="Available Beds: 0",
        font=("Arial", 14, "bold"),
        bg=WHITE,
        fg=PINK_DARK,
        padx=20,
        pady=18
    )
    available_label.pack(
        side="left",
        fill="x",
        expand=True,
        padx=(0, 10)
    )

    occupied_label = tk.Label(
        stats_frame,
        text="Occupied Beds: 0",
        font=("Arial", 14, "bold"),
        bg=WHITE,
        fg=PINK_ACTIVE,
        padx=20,
        pady=18
    )
    occupied_label.pack(
        side="left",
        fill="x",
        expand=True,
        padx=(10, 0)
    )

    # Search and filter section
    search_frame = tk.Frame(
        content,
        bg=WHITE,
        padx=15,
        pady=15
    )
    search_frame.pack(fill="x", padx=25, pady=20)

    tk.Label(
        search_frame,
        text="Search by Bed ID, Patient ID or Name:",
        bg=WHITE,
        fg=TEXT_DARK,
        font=("Arial", 10)
    ).pack(side="left")

    search_entry = tk.Entry(
        search_frame,
        width=22,
        font=("Arial", 10)
    )
    search_entry.pack(side="left", padx=8)

    tk.Label(
        search_frame,
        text="Status:",
        bg=WHITE,
        fg=TEXT_DARK,
        font=("Arial", 10)
    ).pack(side="left", padx=(5, 5))

    status_box = ttk.Combobox(
        search_frame,
        values=["All", "Available", "Occupied"],
        state="readonly",
        width=10
    )
    status_box.set("All")
    status_box.pack(side="left", padx=5)

    # Bed information table
    table_frame = tk.Frame(content, bg=WHITE)
    table_frame.pack(
        fill="both",
        expand=True,
        padx=25,
        pady=(0, 10)
    )

    columns = (
        "bed_id",
        "status",
        "patient_id",
        "patient_name"
    )

    table = ttk.Treeview(
        table_frame,
        columns=columns,
        show="headings",
        height=12
    )

    table.heading("bed_id", text="Bed ID")
    table.heading("status", text="Bed Status")
    table.heading("patient_id", text="Patient ID")
    table.heading("patient_name", text="Patient Name")

    table.column("bed_id", width=120, anchor="center")
    table.column("status", width=120, anchor="center")
    table.column("patient_id", width=140, anchor="center")
    table.column("patient_name", width=180, anchor="center")

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

    # Find the patient assigned to a bed
    def find_patient(bed, patients):
        bed_id = str(bed.get("bed_id", ""))
        bed_patient_id = str(bed.get("patient_id", ""))

        for patient in patients:
            if patient.get("status", "") == "Discharged":
                continue

            patient_bed_id = str(patient.get("bed_id", ""))
            patient_id = str(patient.get("patient_id", ""))

            if patient_bed_id == bed_id and patient_bed_id:
                return patient

            if bed_patient_id and patient_id == bed_patient_id:
                return patient

        return None

    # Display beds in the table
    def display_beds():
        for item in table.get_children():
            table.delete(item)

        # Reload the shared database
        data = load_database()
        patients = data["patients"]
        beds = data["beds"]

        available_count = 0
        occupied_count = 0

        keyword = search_entry.get().strip().lower()
        selected_status = status_box.get()

        for bed in beds:
            patient = find_patient(bed, patients)

            if patient:
                bed_status = "Occupied"
                patient_id = str(
                    patient.get("patient_id", "")
                )
                patient_name = str(
                    patient.get("name", "")
                )
            else:
                bed_status = "Available"
                patient_id = ""
                patient_name = ""

            # Count all beds before applying filters
            if bed_status == "Available":
                available_count += 1
            else:
                occupied_count += 1

            search_text = (
                str(bed.get("bed_id", "")) + " "
                + patient_id + " "
                + patient_name
            ).lower()

            if keyword and keyword not in search_text:
                continue

            if (
                selected_status != "All"
                and selected_status != bed_status
            ):
                continue

            table.insert(
                "",
                "end",
                values=(
                    bed.get("bed_id", ""),
                    bed_status,
                    patient_id or "-",
                    patient_name or "-"
                )
            )

        available_label.config(
            text="Available Beds: " + str(available_count)
        )

        occupied_label.config(
            text="Occupied Beds: " + str(occupied_count)
        )

    # Clear search and filters
    def reset_filters():
        search_entry.delete(0, tk.END)
        status_box.set("All")
        display_beds()

    # Open the discharge page for an occupied bed
    def discharge_selected():
        selected = table.selection()

        if not selected:
            messagebox.showwarning(
                "Select Bed",
                "Please select a bed first.",
                parent=root
            )
            return

        values = table.item(selected[0], "values")
        bed_status = values[1]

        if bed_status != "Occupied":
            messagebox.showinfo(
                "Available Bed",
                "This bed is already available.",
                parent=root
            )
            return

        from discharge import show_discharge
        show_discharge(root)

    # Buttons
    button_frame = tk.Frame(content, bg=PINK_LIGHT)
    button_frame.pack(pady=(0, 12))

    tk.Button(
        button_frame,
        text="Refresh",
        command=display_beds,
        bg=PINK_ACTIVE,
        fg=WHITE,
        activebackground=PINK_DARK,
        font=("Arial", 10),
        width=10,
        cursor="hand2"
    ).pack(side="left", padx=5)

    tk.Button(
        button_frame,
        text="Clear Search",
        command=reset_filters,
        bg=PINK_PALE,
        fg=TEXT_DARK,
        activebackground=PINK_LIGHT,
        font=("Arial", 10),
        width=12,
        cursor="hand2"
    ).pack(side="left", padx=5)

    tk.Button(
        button_frame,
        text="Discharge Patient",
        command=discharge_selected,
        bg=PINK_DARK,
        fg=WHITE,
        activebackground=PINK_ACTIVE,
        font=("Arial", 10),
        width=16,
        cursor="hand2"
    ).pack(side="left", padx=5)

    # Update the table when searching or changing status
    search_entry.bind(
        "<KeyRelease>",
        lambda event: display_beds()
    )

    status_box.bind(
        "<<ComboboxSelected>>",
        lambda event: display_beds()
    )

    # Show beds when the page opens
    display_beds()
