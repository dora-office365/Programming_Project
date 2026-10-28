
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
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


# Main application window
root = tk.Tk()
root.title("Careflow - Hospital Inpatient Management System")
root.geometry("1150x750")
root.configure(bg=PINK_LIGHT)

current_username = ""


# Set the style of tables and dropdowns
def setup_styles():
    style = ttk.Style()

    style.theme_use("clam")

    style.configure(
        "Treeview",
        background=WHITE,
        foreground=TEXT_DARK,
        rowheight=32,
        fieldbackground=WHITE,
        font=("Arial", 10)
    )

    style.configure(
        "Treeview.Heading",
        background=PINK_PALE,
        foreground=PINK_DARK,
        font=("Arial", 10, "bold")
    )

    style.map(
        "Treeview",
        background=[("selected", PINK_ACTIVE)],
        foreground=[("selected", WHITE)]
    )


# Remove the current page
def clear_page():
    for widget in root.winfo_children():
        widget.destroy()


# Display the login page
def show_login():
    clear_page()
    root.title("Careflow - Login")

    login_frame = tk.Frame(
        root,
        bg=WHITE,
        padx=40,
        pady=35,
        highlightbackground=PINK_BORDER,
        highlightthickness=1
    )
    login_frame.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(
        login_frame,
        text="Careflow",
        font=("Arial", 30, "bold"),
        bg=WHITE,
        fg=PINK_DARK
    ).pack(pady=(0, 5))

    tk.Label(
        login_frame,
        text="Hospital Inpatient Management System",
        font=("Arial", 10),
        bg=WHITE,
        fg=TEXT_LIGHT
    ).pack(pady=(0, 25))

    tk.Label(
        login_frame,
        text="Username",
        font=("Arial", 11, "bold"),
        bg=WHITE,
        fg=TEXT_DARK
    ).pack(anchor="w")

    username_entry = tk.Entry(
        login_frame,
        font=("Arial", 12),
        width=28
    )
    username_entry.pack(pady=(5, 15))

    tk.Label(
        login_frame,
        text="Password",
        font=("Arial", 11, "bold"),
        bg=WHITE,
        fg=TEXT_DARK
    ).pack(anchor="w")

    password_entry = tk.Entry(
        login_frame,
        font=("Arial", 12),
        width=28,
        show="*"
    )
    password_entry.pack(pady=(5, 20))

    # Check the username and password
    def login():
        global current_username

        username = username_entry.get().strip()
        password = password_entry.get()

        data = load_database()
        login_successful = False

        for user in data["users"]:
            if (
                user.get("username") == username
                and user.get("password") == password
            ):
                login_successful = True
                break

        if login_successful:
            current_username = username
            show_dashboard(username)
        else:
            messagebox.showerror(
                "Login Failed",
                "Incorrect username or password."
            )

    tk.Button(
        login_frame,
        text="Login",
        command=login,
        bg=PINK_DARK,
        fg=WHITE,
        activebackground=PINK_ACTIVE,
        activeforeground=WHITE,
        font=("Arial", 12, "bold"),
        width=25,
        pady=7
    ).pack()

    tk.Label(
        login_frame,
        text="Demo account: admin / admin123",
        font=("Arial", 9),
        bg=WHITE,
        fg=TEXT_LIGHT
    ).pack(pady=(15, 0))


# Create a dashboard statistic card
def create_card(parent, title, value, row, column):
    card = tk.Frame(
        parent,
        bg=WHITE,
        padx=15,
        pady=15,
        highlightbackground=PINK_BORDER,
        highlightthickness=1
    )

    card.grid(
        row=row,
        column=column,
        sticky="nsew",
        padx=6,
        pady=6
    )

    tk.Label(
        card,
        text=title,
        font=("Arial", 10),
        bg=WHITE,
        fg=TEXT_LIGHT
    ).pack(anchor="w")

    tk.Label(
        card,
        text=str(value),
        font=("Arial", 24, "bold"),
        bg=WHITE,
        fg=PINK_DARK
    ).pack(anchor="w", pady=(8, 0))


# Display the main dashboard
def show_dashboard(username="admin"):
    global current_username

    current_username = username

    clear_page()
    root.title("Careflow - Dashboard")

    data = load_database()
    patients = data["patients"]
    beds = data["beds"]

    # Calculate dashboard statistics
    registered_count = len(patients)

    inpatient_count = 0
    today_discharge_count = 0

    for patient in patients:
        if (
            patient.get("bed_id", "")
            and patient.get("status", "") != "Discharged"
        ):
            inpatient_count += 1

        if patient.get("discharge_date", "") == date.today().isoformat():
            today_discharge_count += 1

    available_count = 0
    occupied_count = 0

    for bed in beds:
        bed_status = bed.get("status", "Available")

        if bed_status == "Available":
            available_count += 1
        elif bed_status == "Occupied":
            occupied_count += 1

    # Main layout
    main_frame = tk.Frame(root, bg=PINK_LIGHT)
    main_frame.pack(fill="both", expand=True)

    # Sidebar
    sidebar = tk.Frame(
        main_frame,
        bg=PINK_DARK,
        width=220
    )
    sidebar.pack(side="left", fill="y")
    sidebar.pack_propagate(False)

    tk.Label(
        sidebar,
        text="Careflow",
        font=("Arial", 24, "bold"),
        bg=PINK_DARK,
        fg=WHITE
    ).pack(pady=(30, 5))

    tk.Label(
        sidebar,
        text="HOSPITAL MANAGEMENT",
        font=("Arial", 8, "bold"),
        bg=PINK_DARK,
        fg=PINK_PALE
    ).pack(pady=(0, 30))

    # Open Patient Information
    def open_patients():
        import patient
        patient.show_patients(root)

    # Open Bed Management
    def open_beds():
        import bed_management
        bed_management.show_bed_management(root)

    # Open Discharge Management
    def open_discharge():
        import discharge
        discharge.show_discharge(root)

    # Show the reports option
    def show_report_message():
        messagebox.showinfo(
            "Reports",
            "The patient summary is displayed on the dashboard.\n\n"
            "Registered patients: " + str(registered_count) + "\n"
            "Current inpatients: " + str(inpatient_count) + "\n"
            "Available beds: " + str(available_count) + "\n"
            "Occupied beds: " + str(occupied_count) + "\n"
            "Today's discharges: " + str(today_discharge_count)
        )

    # Create sidebar navigation buttons
    def navigation_button(text, command, active=False):
        button_colour = PINK_ACTIVE if active else PINK_DARK

        tk.Button(
            sidebar,
            text=text,
            command=command,
            bg=button_colour,
            fg=WHITE,
            activebackground=PINK_ACTIVE,
            activeforeground=WHITE,
            font=("Arial", 11),
            anchor="w",
            relief="flat",
            bd=0,
            padx=22,
            pady=13
        ).pack(fill="x", padx=10, pady=3)

    navigation_button("Dashboard", lambda: show_dashboard(current_username), True)
    navigation_button("Patient Information", open_patients)
    navigation_button("Bed Management", open_beds)
    navigation_button("Discharge", open_discharge)
    navigation_button("Reports", show_report_message)

    # Logout button at the bottom
    tk.Button(
        sidebar,
        text="Logout",
        command=logout,
        bg=PINK_DARK,
        fg=WHITE,
        activebackground=PINK_ACTIVE,
        activeforeground=WHITE,
        font=("Arial", 11),
        relief="flat",
        anchor="w",
        padx=22,
        pady=13
    ).pack(side="bottom", fill="x", padx=10, pady=20)

    # Dashboard content
    content = tk.Frame(main_frame, bg=PINK_LIGHT)
    content.pack(side="right", fill="both", expand=True)

    # Header
    header = tk.Frame(content, bg=PINK_LIGHT)
    header.pack(fill="x", padx=25, pady=(25, 15))

    tk.Label(
        header,
        text="Dashboard",
        font=("Arial", 25, "bold"),
        bg=PINK_LIGHT,
        fg=PINK_DARK
    ).pack(anchor="w")

    tk.Label(
        header,
        text="Welcome, " + username + "! Here is your hospital overview.",
        font=("Arial", 11),
        bg=PINK_LIGHT,
        fg=TEXT_DARK
    ).pack(anchor="w", pady=(5, 0))

    # Statistic cards
    cards_frame = tk.Frame(content, bg=PINK_LIGHT)
    cards_frame.pack(fill="x", padx=18, pady=5)

    for column in range(3):
        cards_frame.grid_columnconfigure(column, weight=1)

    create_card(
        cards_frame, "Registered Patients",
        registered_count, 0, 0
    )

    create_card(
        cards_frame, "Current Inpatients",
        inpatient_count, 0, 1
    )

    create_card(
        cards_frame, "Available Beds",
        available_count, 0, 2
    )

    create_card(
        cards_frame, "Occupied Beds",
        occupied_count, 1, 0
    )

    create_card(
        cards_frame, "Today's Discharges",
        today_discharge_count, 1, 1
    )

    # Recent patient records
    table_title = tk.Label(
        content,
        text="Patient Records",
        font=("Arial", 16, "bold"),
        bg=PINK_LIGHT,
        fg=PINK_DARK
    )
    table_title.pack(anchor="w", padx=25, pady=(20, 10))

    table_frame = tk.Frame(content, bg=WHITE)
    table_frame.pack(
        fill="both",
        expand=True,
        padx=25,
        pady=(0, 10)
    )

    columns = ("patient_id", "name", "bed_id", "status")

    patient_table = ttk.Treeview(
        table_frame,
        columns=columns,
        show="headings",
        height=8
    )

    patient_table.heading("patient_id", text="Patient ID")
    patient_table.heading("name", text="Patient Name")
    patient_table.heading("bed_id", text="Bed ID")
    patient_table.heading("status", text="Status")

    patient_table.column("patient_id", width=110, anchor="center")
    patient_table.column("name", width=200)
    patient_table.column("bed_id", width=110, anchor="center")
    patient_table.column("status", width=130, anchor="center")

    scrollbar = ttk.Scrollbar(
        table_frame,
        orient="vertical",
        command=patient_table.yview
    )

    patient_table.configure(yscrollcommand=scrollbar.set)

    patient_table.pack(
        side="left",
        fill="both",
        expand=True,
        padx=8,
        pady=8
    )

    scrollbar.pack(side="right", fill="y", pady=8)

    # Display the latest patient records
    for patient in patients[-100:]:
        patient_table.insert(
            "",
            "end",
            values=(
                patient.get("patient_id", ""),
                patient.get("name", ""),
                patient.get("bed_id", "") or "-",
                patient.get("status", "Registered")
            )
        )

    # Footer
    tk.Label(
        content,
        text="Careflow | Hospital Inpatient Management System",
        font=("Arial", 9),
        bg=PINK_LIGHT,
        fg=TEXT_LIGHT
    ).pack(pady=(0, 10))


# Log out of the system
def logout():
    answer = messagebox.askyesno(
        "Logout",
        "Are you sure you want to log out?"
    )

    if answer:
        show_login()


# Start the application
setup_styles()
show_login()
root.mainloop()