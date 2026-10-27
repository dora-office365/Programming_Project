import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from data import load_database


# --------------------------------------------------
# COLOUR THEME
# --------------------------------------------------

PINK_DARK = "#7D3458"
PINK_ACTIVE = "#AD5B82"
PINK_LIGHT = "#FFF4F8"
PINK_PALE = "#FCE7F0"
PINK_BORDER = "#EAC5D5"
TEXT_DARK = "#49323D"
TEXT_LIGHT = "#A45B7D"
WHITE = "#FFFFFF"
GREEN = "#47876B"
ORANGE = "#C47A19"


# Main application window
root = tk.Tk()
root.title("Careflow - Hospital Inpatient Management System")
root.geometry("1120x720")
root.minsize(900, 600)

current_username = ""


# --------------------------------------------------
# COMMON STYLES
# --------------------------------------------------

def setup_styles():
    style = ttk.Style()

    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure(
        "Treeview",
        background=WHITE,
        foreground=TEXT_DARK,
        fieldbackground=WHITE,
        rowheight=32,
        font=("Arial", 10),
        borderwidth=0
    )

    style.configure(
        "Treeview.Heading",
        background=PINK_PALE,
        foreground=PINK_DARK,
        font=("Arial", 10, "bold"),
        padding=10,
        relief="flat"
    )

    style.map(
        "Treeview",
        background=[("selected", "#F4D5E3")],
        foreground=[("selected", PINK_DARK)]
    )

    style.configure(
        "TButton",
        font=("Arial", 10),
        padding=7
    )

    style.configure(
        "TCombobox",
        padding=5
    )


# --------------------------------------------------
# CLEAR CURRENT PAGE
# --------------------------------------------------

def clear_page():
    for widget in root.winfo_children():
        widget.destroy()

    root.configure(bg=PINK_LIGHT)


# --------------------------------------------------
# LOGIN PAGE
# --------------------------------------------------

def show_login():
    clear_page()
    root.title("Careflow - Login")

    login_frame = tk.Frame(
        root,
        bg=WHITE,
        padx=45,
        pady=35,
        highlightbackground=PINK_BORDER,
        highlightthickness=1
    )
    login_frame.place(
        relx=0.5,
        rely=0.5,
        anchor="center"
    )

    tk.Label(
        login_frame,
        text="♡ CAREFLOW",
        bg=WHITE,
        fg=PINK_DARK,
        font=("Arial", 27, "bold")
    ).pack(pady=(0, 8))

    tk.Label(
        login_frame,
        text="Hospital Inpatient Management System",
        bg=WHITE,
        fg=TEXT_LIGHT,
        font=("Arial", 10)
    ).pack(pady=(0, 25))

    tk.Label(
        login_frame,
        text="Username",
        bg=WHITE,
        fg=TEXT_DARK,
        font=("Arial", 10, "bold")
    ).pack(anchor="w")

    username_entry = ttk.Entry(
        login_frame,
        width=35
    )
    username_entry.pack(pady=(6, 15), ipady=5)

    tk.Label(
        login_frame,
        text="Password",
        bg=WHITE,
        fg=TEXT_DARK,
        font=("Arial", 10, "bold")
    ).pack(anchor="w")

    password_entry = ttk.Entry(
        login_frame,
        width=35,
        show="*"
    )
    password_entry.pack(pady=(6, 20), ipady=5)

    def login():
        global current_username

        username = username_entry.get().strip()
        password = password_entry.get()

        if not username or not password:
            messagebox.showwarning(
                "Missing Information",
                "Please enter your username and password."
            )
            return

        data = load_database()

        for user in data["users"]:
            if (
                user.get("username") == username
                and user.get("password") == password
            ):
                current_username = username
                show_dashboard(username)
                return

        messagebox.showerror(
            "Login Failed",
            "Incorrect username or password."
        )

    tk.Button(
        login_frame,
        text="Login",
        command=login,
        bg=PINK_ACTIVE,
        fg=WHITE,
        activebackground=PINK_DARK,
        activeforeground=WHITE,
        font=("Arial", 11, "bold"),
        relief="flat",
        cursor="hand2",
        width=28,
        pady=9
    ).pack(fill="x")

    tk.Label(
        login_frame,
        text="Careflow • Authorised Staff Only",
        bg=WHITE,
        fg=TEXT_LIGHT,
        font=("Arial", 9)
    ).pack(pady=(20, 0))

    password_entry.bind("<Return>", lambda event: login())
    username_entry.bind("<Return>", lambda event: password_entry.focus_set())

    username_entry.focus_set()


# --------------------------------------------------
# CREATE STATISTIC CARD
# --------------------------------------------------

def create_card(parent, title, value, accent):
    card = tk.Frame(
        parent,
        bg=WHITE,
        padx=15,
        pady=12,
        highlightbackground=PINK_BORDER,
        highlightthickness=1
    )

    card.pack(
        side="left",
        fill="both",
        expand=True,
        padx=(0, 10)
    )

    tk.Frame(
        card,
        bg=accent,
        height=4
    ).pack(fill="x", pady=(0, 12))

    tk.Label(
        card,
        text=title,
        bg=WHITE,
        fg=TEXT_LIGHT,
        font=("Arial", 9, "bold")
    ).pack(anchor="w")

    value_label = tk.Label(
        card,
        text=str(value),
        bg=WHITE,
        fg=PINK_DARK,
        font=("Arial", 24, "bold")
    )

    value_label.pack(anchor="w", pady=(5, 0))

    return value_label


# --------------------------------------------------
# DASHBOARD PAGE
# --------------------------------------------------

def show_dashboard(username="admin"):
    global current_username

    current_username = username

    clear_page()
    root.title("Careflow - Dashboard")

    data = load_database()
    patients = data["patients"]
    beds = data["beds"]

    # Calculate dashboard statistics
    registered_patients = len(patients)

    current_inpatients = sum(
        1 for patient in patients
        if patient.get("bed_id", "")
        and patient.get("status", "Registered") != "Discharged"
    )

    available_beds = sum(
        1 for bed in beds
        if bed.get("status", "").strip().title() == "Available"
    )

    occupied_beds = sum(
        1 for bed in beds
        if bed.get("status", "").strip().title() == "Occupied"
    )

    today = date.today().isoformat()

    discharges_today = sum(
        1 for patient in patients
        if patient.get("status") == "Discharged"
        and patient.get("discharge_date") == today
    )

    # --------------------------------------------------
    # SIDEBAR
    # --------------------------------------------------

    sidebar = tk.Frame(
        root,
        bg=PINK_DARK,
        width=225
    )

    sidebar.pack(side="left", fill="y")
    sidebar.pack_propagate(False)

    tk.Label(
        sidebar,
        text="♡ CAREFLOW",
        bg=PINK_DARK,
        fg=WHITE,
        font=("Arial", 21, "bold"),
        pady=25
    ).pack(fill="x")

    tk.Label(
        sidebar,
        text="HOSPITAL MANAGEMENT",
        bg=PINK_DARK,
        fg="#F7DDE8",
        font=("Arial", 8, "bold")
    ).pack(pady=(0, 25))

    # --------------------------------------------------
    # MAIN CONTENT
    # --------------------------------------------------

    content = tk.Frame(
        root,
        bg=PINK_LIGHT
    )

    content.pack(
        side="left",
        fill="both",
        expand=True
    )

    # Header
    header = tk.Frame(
        content,
        bg=WHITE,
        height=75
    )

    header.pack(fill="x")
    header.pack_propagate(False)

    tk.Label(
        header,
        text="Dashboard",
        bg=WHITE,
        fg=PINK_DARK,
        font=("Arial", 21, "bold")
    ).pack(side="left", padx=25, pady=18)

    tk.Label(
        header,
        text=f"Welcome, {username} ♡",
        bg=WHITE,
        fg=TEXT_LIGHT,
        font=("Arial", 10, "bold")
    ).pack(side="right", padx=25)

    # Main body
    body = tk.Frame(
        content,
        bg=PINK_LIGHT
    )

    body.pack(
        fill="both",
        expand=True,
        padx=25,
        pady=20
    )

    tk.Label(
        body,
        text="Hospital Overview",
        bg=PINK_LIGHT,
        fg=TEXT_DARK,
        font=("Arial", 15, "bold")
    ).pack(anchor="w")

    tk.Label(
        body,
        text="Monitor patient records, bed availability and daily discharges.",
        bg=PINK_LIGHT,
        fg=TEXT_LIGHT,
        font=("Arial", 10)
    ).pack(anchor="w", pady=(5, 17))

    # --------------------------------------------------
    # STATISTIC CARDS
    # --------------------------------------------------

    cards = tk.Frame(
        body,
        bg=PINK_LIGHT
    )

    cards.pack(fill="x", pady=(0, 20))

    create_card(
        cards,
        "REGISTERED PATIENTS",
        registered_patients,
        PINK_ACTIVE
    )

    create_card(
        cards,
        "CURRENT INPATIENTS",
        current_inpatients,
        GREEN
    )

    create_card(
        cards,
        "AVAILABLE BEDS",
        available_beds,
        "#6D9E83"
    )

    create_card(
        cards,
        "OCCUPIED BEDS",
        occupied_beds,
        ORANGE
    )

    create_card(
        cards,
        "DISCHARGES TODAY",
        discharges_today,
        "#B47BA2"
    )

    # --------------------------------------------------
    # PATIENT REPORT
    # --------------------------------------------------

    report_panel = tk.Frame(
        body,
        bg=WHITE,
        padx=15,
        pady=15,
        highlightbackground=PINK_BORDER,
        highlightthickness=1
    )

    report_panel.pack(
        fill="both",
        expand=True
    )

    report_header = tk.Frame(
        report_panel,
        bg=WHITE
    )

    report_header.pack(fill="x", pady=(0, 12))

    tk.Label(
        report_header,
        text="Patient Report",
        bg=WHITE,
        fg=PINK_DARK,
        font=("Arial", 13, "bold")
    ).pack(side="left")

    tk.Label(
        report_header,
        text=f"{registered_patients} patient records",
        bg=WHITE,
        fg=TEXT_LIGHT,
        font=("Arial", 9)
    ).pack(side="right")

    table_frame = tk.Frame(
        report_panel,
        bg=WHITE
    )

    table_frame.pack(
        fill="both",
        expand=True
    )

    columns = (
        "patient_id",
        "name",
        "bed_id",
        "status"
    )

    tree = ttk.Treeview(
        table_frame,
        columns=columns,
        show="headings"
    )

    tree.heading("patient_id", text="PATIENT ID")
    tree.heading("name", text="PATIENT NAME")
    tree.heading("bed_id", text="BED ID")
    tree.heading("status", text="STATUS")

    tree.column("patient_id", width=130, anchor="center")
    tree.column("name", width=200, anchor="center")
    tree.column("bed_id", width=120, anchor="center")
    tree.column("status", width=150, anchor="center")

    scrollbar = ttk.Scrollbar(
        table_frame,
        orient="vertical",
        command=tree.yview
    )

    tree.configure(yscrollcommand=scrollbar.set)

    tree.pack(
        side="left",
        fill="both",
        expand=True
    )

    scrollbar.pack(side="right", fill="y")

    tree.tag_configure(
        "Discharged",
        foreground="#8A7180"
    )

    tree.tag_configure(
        "Registered",
        foreground=PINK_DARK
    )

    for patient in patients:
        patient_id = patient.get("patient_id", "")
        name = patient.get("name", "")
        bed_id = patient.get("bed_id", "") or "-"
        status = patient.get("status", "Registered")

        tree.insert(
            "",
            "end",
            values=(
                patient_id,
                name,
                bed_id,
                status
            ),
            tags=(status,)
        )

    # --------------------------------------------------
    # NAVIGATION BUTTONS
    # --------------------------------------------------

    def navigation_button(text, command, active=False):
        button = tk.Button(
            sidebar,
            text=text,
            command=command,
            bg=PINK_ACTIVE if active else PINK_DARK,
            fg=WHITE if active else "#FBEAF1",
            activebackground=PINK_ACTIVE,
            activeforeground=WHITE,
            font=("Arial", 10, "bold" if active else "normal"),
            anchor="w",
            padx=18,
            pady=12,
            relief="flat",
            cursor="hand2",
            bd=0
        )

        button.pack(
            fill="x",
            padx=10,
            pady=2
        )

    navigation_button(
        "▦   Dashboard",
        lambda: show_dashboard(username),
        True
    )

    navigation_button(
        "▣   Patient Information",
        lambda: open_patients()
    )

    navigation_button(
        "▤   Bed Management",
        lambda: open_beds()
    )

    navigation_button(
        "↗   Discharge",
        lambda: open_discharge()
    )

    navigation_button(
        "▧   Reports",
        lambda: show_report_message()
    )

    # Sidebar footer
    tk.Frame(
        sidebar,
        bg="#AA6686",
        height=1
    ).pack(fill="x", padx=18, pady=20)

    tk.Label(
        sidebar,
        text="CAREFLOW v1.0\nHospital Inpatient System",
        bg=PINK_DARK,
        fg="#F7DDE8",
        font=("Arial", 9),
        justify="left"
    ).pack(side="bottom", anchor="w", padx=20, pady=22)

    # Footer
    footer = tk.Frame(
        body,
        bg=PINK_LIGHT
    )

    footer.pack(fill="x", pady=(10, 0))

    tk.Label(
        footer,
        text="CAREFLOW | Hospital Inpatient Management",
        bg=PINK_LIGHT,
        fg=TEXT_LIGHT,
        font=("Arial", 9)
    ).pack(side="left")

    tk.Button(
        footer,
        text="Logout",
        command=logout,
        bg=PINK_ACTIVE,
        fg=WHITE,
        activebackground=PINK_DARK,
        activeforeground=WHITE,
        font=("Arial", 9, "bold"),
        relief="flat",
        cursor="hand2",
        padx=18,
        pady=6
    ).pack(side="right")


# --------------------------------------------------
# NAVIGATION FUNCTIONS
# --------------------------------------------------

def open_patients():
    import patient
    patient.show_patients(root)


def open_beds():
    import bed_management
    bed_management.show_bed_management(root)


def open_discharge():
    import discharge
    discharge.show_discharge(root)


def show_report_message():
    messagebox.showinfo(
        "Patient Report",
        "The current patient report is displayed on the Dashboard."
    )


def logout():
    global current_username

    answer = messagebox.askyesno(
        "Logout",
        "Are you sure you want to log out?"
    )

    if answer:
        current_username = ""
        show_login()


# --------------------------------------------------
# START PROGRAM
# --------------------------------------------------

setup_styles()
show_login()
root.mainloop()
