import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import date
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

# Main application window
root = None
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
    global root

    if root is not None:
        for widget in root.winfo_children():
            widget.destroy()


# Add an admin account after verifying an existing admin
def add_admin_account():
    if root is None:
        return

    admin_username = simpledialog.askstring(
        "Admin Verification",
        "Enter your existing admin username:",
        parent=root
    )

    if admin_username is None:
        return

    admin_username = admin_username.strip()

    if not admin_username:
        messagebox.showwarning(
            "Invalid Username",
            "Please enter your existing admin username.",
            parent=root
        )
        return

    admin_password = simpledialog.askstring(
        "Admin Verification",
        "Enter your existing admin password:",
        show="*",
        parent=root
    )

    if admin_password is None:
        return

    data = load_database()
    admin_verified = False

    for user in data["users"]:
        if (
            user.get("username", "").lower()
            == admin_username.lower()
            and user.get("password", "") == admin_password
        ):
            admin_verified = True
            break

    if not admin_verified:
        messagebox.showerror(
            "Verification Failed",
            "Incorrect admin username or password.",
            parent=root
        )
        return

    new_username = simpledialog.askstring(
        "Add Admin Account",
        "Enter a username for the new admin:",
        parent=root
    )

    if new_username is None:
        return

    new_username = new_username.strip()

    if not new_username:
        messagebox.showwarning(
            "Invalid Username",
            "Username cannot be empty.",
            parent=root
        )
        return

    for user in data["users"]:
        if user.get("username", "").lower() == new_username.lower():
            messagebox.showerror(
                "Username Exists",
                "This username is already in use.",
                parent=root
            )
            return

    new_password = simpledialog.askstring(
        "Add Admin Account",
        "Enter a password for the new admin:",
        show="*",
        parent=root
    )

    if new_password is None:
        return

    if len(new_password) < 6:
        messagebox.showwarning(
            "Invalid Password",
            "Password must contain at least 6 characters.",
            parent=root
        )
        return

    confirm_password = simpledialog.askstring(
        "Confirm Password",
        "Enter the new password again:",
        show="*",
        parent=root
    )

    if confirm_password is None:
        return

    if new_password != confirm_password:
        messagebox.showerror(
            "Password Mismatch",
            "The passwords do not match. Please try again.",
            parent=root
        )
        return

    data["users"].append({
        "username": new_username,
        "password": new_password
    })

    save_database(data)

    messagebox.showinfo(
        "Success",
        "Admin account created successfully!\n"
        "You can now log in with the new account.",
        parent=root
    )


# Display the login page
def show_login():
    global current_username

    if root is None:
        return

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

        if not username or not password:
            messagebox.showwarning(
                "Missing Information",
                "Please enter your username and password.",
                parent=root
            )
            return

        data = load_database()

        for user in data["users"]:
            if (
                user.get("username", "").lower() == username.lower()
                and user.get("password", "") == password
            ):
                current_username = username
                show_dashboard(username)
                return

        messagebox.showerror(
            "Login Failed",
            "Incorrect username or password.",
            parent=root
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
        pady=7,
        cursor="hand2"
    ).pack()

    # Add Admin Account button
    tk.Button(
        login_frame,
        text="Add Admin Account",
        command=add_admin_account,
        bg=PINK_PALE,
        fg=TEXT_DARK,
        activebackground=PINK_LIGHT,
        activeforeground=TEXT_DARK,
        font=("Arial", 10, "bold"),
        width=25,
        pady=7,
        cursor="hand2"
    ).pack(pady=(10, 0))

    tk.Label(
        login_frame,
        text="Demo account: admin / admin123",
        font=("Arial", 9),
        bg=WHITE,
        fg=TEXT_LIGHT
    ).pack(pady=(15, 0))

    password_entry.bind("<Return>", lambda event: login())


# Create the shared navigation menu
def add_navigation(parent, active_page):
    sidebar = tk.Frame(
        parent,
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

    # Open the selected page
    def open_page(page_name):
        global root, current_username

        if root is None:
            messagebox.showerror(
                "Application Error",
                "The main window has not been created."
            )
            return

        try:
            if page_name == "Dashboard":
                show_dashboard(current_username)

            elif page_name == "Patient Information":
                import patient
                patient.show_patients(root)

            elif page_name == "Bed Management":
                import bed_management
                bed_management.show_bed_management(root)

            elif page_name == "Discharge":
                import discharge
                discharge.show_discharge(root)

            elif page_name == "Logout":
                logout()

        except Exception as error:
            messagebox.showerror(
                "Page Error",
                "Could not open " + page_name + ".\n\n"
                + str(error),
                parent=root
            )

    pages = [
        "Dashboard",
        "Patient Information",
        "Bed Management",
        "Discharge"
    ]

    for page in pages:
        button_colour = (
            PINK_ACTIVE if page == active_page else PINK_DARK
        )

        tk.Button(
            sidebar,
            text=page,
            command=lambda name=page: open_page(name),
            bg=button_colour,
            fg=WHITE,
            activebackground=PINK_ACTIVE,
            activeforeground=WHITE,
            font=("Arial", 11),
            anchor="w",
            relief="flat",
            bd=0,
            padx=22,
            pady=13,
            cursor="hand2"
        ).pack(fill="x", padx=10, pady=3)

    tk.Button(
        sidebar,
        text="Logout",
        command=lambda: open_page("Logout"),
        bg=PINK_DARK,
        fg=WHITE,
        activebackground=PINK_ACTIVE,
        activeforeground=WHITE,
        font=("Arial", 11),
        relief="flat",
        anchor="w",
        padx=22,
        pady=13,
        cursor="hand2"
    ).pack(side="bottom", fill="x", padx=10, pady=20)

    content = tk.Frame(parent, bg=PINK_LIGHT)
    content.pack(side="right", fill="both", expand=True)

    return content


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
def show_dashboard(username=None):
    global current_username

    if username:
        current_username = username

    if not current_username:
        show_login()
        return

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

        if (
            patient.get("discharge_date", "")
            == date.today().isoformat()
        ):
            today_discharge_count += 1

    available_count = 0
    occupied_count = 0

    for bed in beds:
        if bed.get("status", "Available") == "Available":
            available_count += 1
        elif bed.get("status") == "Occupied":
            occupied_count += 1

    # Main layout
    main_frame = tk.Frame(root, bg=PINK_LIGHT)
    main_frame.pack(fill="both", expand=True)

    content = add_navigation(main_frame, "Dashboard")

    # Dashboard heading
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
        text="Welcome, " + current_username
        + "! Here is your hospital overview.",
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

    # Patient records heading
    tk.Label(
        content,
        text="Patient Records",
        font=("Arial", 16, "bold"),
        bg=PINK_LIGHT,
        fg=PINK_DARK
    ).pack(anchor="w", padx=25, pady=(20, 10))

    # Patient table
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

    # Display recent patient records
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
    global current_username

    if root is None:
        return

    answer = messagebox.askyesno(
        "Logout",
        "Are you sure you want to log out?",
        parent=root
    )

    if answer:
        current_username = ""
        show_login()


# Start the application
def start_app():
    global root

    root = tk.Tk()
    root.title("Careflow - Hospital Inpatient Management System")
    root.geometry("1150x750")
    root.configure(bg=PINK_LIGHT)

    setup_styles()
    show_login()
    root.mainloop()


if __name__ == "__main__":
    start_app()
