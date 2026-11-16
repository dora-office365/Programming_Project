import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from datetime import date
import calendar
from data import load_database, save_database, find_patient

# Pink theme colours
PINK_DARK = "#7D3458"
PINK_ACTIVE = "#AD5B82"
PINK_LIGHT = "#FFF4F8"
PINK_PALE = "#FCE7F0"
PINK_BORDER = "#EAC5D5"
TEXT_DARK = "#49323D"
TEXT_LIGHT = "#A45B7D"
WHITE = "#FFFFFF"

ROOM_TYPES = [
    "ICU",
    "Nursery",
    "Single-bedded",
    "Double-bedded",
    "Four-bedded"
]

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
        text="Default account: admin / admin123",
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


# Collect previous and current admission records
def get_all_admission_records(patients):
    records = []

    for patient in patients:
        patient_id = patient.get("patient_id", "")
        patient_name = patient.get("name", "")
        patient_ic = patient.get("patient_ic", "")

        history = patient.get("admission_history", [])

        if isinstance(history, list):
            for record in history:
                if isinstance(record, dict):
                    records.append({
                        "patient_id": patient_id,
                        "name": patient_name,
                        "patient_ic": patient_ic,
                        "bed_id": record.get("bed_id", "") or "-",
                        "admission_date": record.get("admission_date", ""),
                        "discharge_date": record.get("discharge_date", ""),
                        "status": record.get("status", "Discharged")
                    })

        current_admission = (
            patient.get("admission_date", ""),
            patient.get("discharge_date", "")
        )

        already_archived = any(
            isinstance(record, dict)
            and (
                record.get("admission_date", ""),
                record.get("discharge_date", "")
            ) == current_admission
            for record in history
        ) if isinstance(history, list) else False

        if not already_archived and patient.get("admission_date", ""):
            records.append({
                "patient_id": patient_id,
                "name": patient_name,
                "patient_ic": patient_ic,
                "bed_id": patient.get("bed_id", "") or "-",
                "admission_date": patient.get("admission_date", ""),
                "discharge_date": patient.get("discharge_date", ""),
                "status": patient.get("status", "Registered")
            })

    return records


# Count patient transfers for each room type
def get_room_transfer_summary(patients, start_date, end_date):
    transfer_summary = {}

    for room_type in ROOM_TYPES:
        transfer_summary[room_type] = {
            "in": 0,
            "out": 0
        }

    for patient in patients:
        transfer_history = patient.get("bed_transfer_history", [])

        if not isinstance(transfer_history, list):
            continue

        for transfer in transfer_history:
            if not isinstance(transfer, dict):
                continue

            transfer_date = transfer.get("transfer_date", "")

            # Count only transfers within the reporting period
            if not transfer_date:
                continue

            try:
                date.fromisoformat(transfer_date)
            except ValueError:
                continue

            if start_date <= transfer_date <= end_date:
                from_room = transfer.get("from_room_type", "")
                to_room = transfer.get("to_room_type", "")

                if from_room in transfer_summary:
                    transfer_summary[from_room]["out"] += 1

                if to_room in transfer_summary:
                    transfer_summary[to_room]["in"] += 1

    return transfer_summary


# Escape text for PDF format
def pdf_escape(value):
    value = str(value)
    value = value.encode("latin-1", "replace").decode("latin-1")
    value = value.replace("\\", "\\\\")
    value = value.replace("(", "\\(")
    value = value.replace(")", "\\)")
    return value


# Create a PDF report
def create_pdf_file(
    output_path,
    report_title,
    period_label,
    summary,
    records,
    transfer_summary
):
    page_objects = []

    page_width = 842
    page_height = 595

    # Leave space on the first page for the transfer summary
    first_page_limit = 10
    other_page_limit = 22

    pages = [records[:first_page_limit]]
    remaining_records = records[first_page_limit:]

    while remaining_records:
        pages.append(remaining_records[:other_page_limit])
        remaining_records = remaining_records[other_page_limit:]

    for page_number, page_records in enumerate(pages):
        content = []

        # Report title
        content.append("BT")
        content.append("/F1 19 Tf")
        content.append("50 550 Td")
        content.append(
            "(" + pdf_escape("Careflow - " + report_title) + ") Tj"
        )
        content.append("ET")

        # Reporting period
        content.append("BT")
        content.append("/F1 11 Tf")
        content.append("50 525 Td")
        content.append(
            "(" + pdf_escape("Reporting Period: " + period_label) + ") Tj"
        )
        content.append("ET")

        if page_number == 0:
            # Report summary
            content.append("BT")
            content.append("/F1 10 Tf")
            content.append("50 495 Td")
            content.append(
                "(" + pdf_escape(
                    "Total Admissions: " + str(summary["admissions"])
                ) + ") Tj"
            )
            content.append("0 -17 Td")
            content.append(
                "(" + pdf_escape(
                    "Total Discharges: " + str(summary["discharges"])
                ) + ") Tj"
            )
            content.append("0 -17 Td")
            content.append(
                "(" + pdf_escape(
                    "Inpatients at Period End: "
                    + str(summary["inpatients"])
                ) + ") Tj"
            )
            content.append("ET")

            # Room transfer summary heading
            content.append("BT")
            content.append("/F1 11 Tf")
            content.append("50 435 Td")
            content.append(
                "(" + pdf_escape("Patient Transfers by Room Type") + ") Tj"
            )
            content.append("ET")

            # Transfer table headings
            content.append("BT")
            content.append("/F1 9 Tf")
            content.append("50 415 Td")
            content.append("(Room Type) Tj")
            content.append("200 0 Td")
            content.append("(Transfers In) Tj")
            content.append("150 0 Td")
            content.append("(Transfers Out) Tj")
            content.append("ET")

            content.append("0.5 w")
            content.append("50 407 m 500 407 l S")

            # Transfer table records
            for index, room_type in enumerate(ROOM_TYPES):
                y_position = 390 - (index * 16)

                transfer_in = transfer_summary[room_type]["in"]
                transfer_out = transfer_summary[room_type]["out"]

                content.append("BT")
                content.append("/F1 9 Tf")
                content.append("50 " + str(y_position) + " Td")
                content.append(
                    "(" + pdf_escape(room_type) + ") Tj"
                )
                content.append("200 0 Td")
                content.append(
                    "(" + str(transfer_in) + ") Tj"
                )
                content.append("150 0 Td")
                content.append(
                    "(" + str(transfer_out) + ") Tj"
                )
                content.append("ET")

            table_y = 290

        else:
            table_y = 495

        # Patient record table heading
        content.append("BT")
        content.append("/F1 9 Tf")
        content.append("50 " + str(table_y) + " Td")

        headings = [
            "Patient ID",
            "Patient Name",
            "Patient IC",
            "Bed ID",
            "Admission Date",
            "Discharge Date",
            "Status"
        ]

        x_positions = [0, 75, 205, 315, 385, 490, 595]

        for index, heading in enumerate(headings):
            if index > 0:
                content.append(
                    str(x_positions[index] - x_positions[index - 1])
                    + " 0 Td"
                )

            content.append(
                "(" + pdf_escape(heading) + ") Tj"
            )

        content.append("ET")

        content.append("0.5 w")
        content.append(
            "50 " + str(table_y - 8) + " m 790 "
            + str(table_y - 8) + " l S"
        )

        # Patient records
        for row_index, record in enumerate(page_records):
            y_position = table_y - 25 - (row_index * 22)

            values = [
                record.get("patient_id", ""),
                record.get("name", "")[:18],
                record.get("patient_ic", "")[:17],
                record.get("bed_id", "")[:10],
                record.get("admission_date", "")[:10],
                record.get("discharge_date", "") or "-",
                record.get("status", "")
            ]

            content.append("BT")
            content.append("/F1 8 Tf")
            content.append("50 " + str(y_position) + " Td")

            for index, value in enumerate(values):
                if index > 0:
                    content.append(
                        str(x_positions[index] - x_positions[index - 1])
                        + " 0 Td"
                    )

                content.append(
                    "(" + pdf_escape(value) + ") Tj"
                )

            content.append("ET")

        # Page number
        content.append("BT")
        content.append("/F1 8 Tf")
        content.append("750 25 Td")
        content.append(
            "(" + pdf_escape(
                "Page " + str(page_number + 1)
                + " of " + str(len(pages))
            ) + ") Tj"
        )
        content.append("ET")

        page_content = "\n".join(content).encode("latin-1")
        page_objects.append(page_content)

    # Build PDF objects
    objects = []

    objects.append(
        b"<< /Type /Catalog /Pages 2 0 R >>"
    )

    page_references = []

    for index in range(len(page_objects)):
        page_references.append(
            str(4 + index * 2) + " 0 R"
        )

    objects.append(
        (
            "<< /Type /Pages /Kids ["
            + " ".join(page_references)
            + "] /Count " + str(len(page_objects)) + " >>"
        ).encode("ascii")
    )

    objects.append(
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"
    )

    for index, page_content in enumerate(page_objects):
        page_object_number = 4 + index * 2
        content_object_number = page_object_number + 1

        page_object = (
            "<< /Type /Page "
            "/Parent 2 0 R "
            "/MediaBox [0 0 842 595] "
            "/Resources << /Font << /F1 3 0 R >> >> "
            "/Contents " + str(content_object_number) + " 0 R >>"
        ).encode("ascii")

        content_object = (
            b"<< /Length " + str(len(page_content)).encode("ascii")
            + b" >>\nstream\n"
            + page_content
            + b"\nendstream"
        )

        objects.append(page_object)
        objects.append(content_object)

    # Write the PDF file
    with open(output_path, "wb") as pdf_file:
        pdf_file.write(b"%PDF-1.4\n")

        offsets = [0]

        for index, obj in enumerate(objects):
            offsets.append(pdf_file.tell())

            pdf_file.write(
                str(index + 1).encode("ascii")
                + b" 0 obj\n"
            )
            pdf_file.write(obj)
            pdf_file.write(b"\nendobj\n")

        xref_position = pdf_file.tell()

        pdf_file.write(
            b"xref\n0 " + str(len(objects) + 1).encode("ascii")
            + b"\n"
        )

        pdf_file.write(b"0000000000 65535 f \n")

        for offset in offsets[1:]:
            pdf_file.write(
                ("%010d 00000 n \n" % offset).encode("ascii")
            )

        pdf_file.write(
            b"trailer\n<< /Size "
            + str(len(objects) + 1).encode("ascii")
            + b" /Root 1 0 R >>\n"
        )

        pdf_file.write(b"startxref\n")
        pdf_file.write(str(xref_position).encode("ascii"))
        pdf_file.write(b"\n%%EOF")


# Generate a report for a selected date range
def generate_report(start_date, end_date, report_type, period_label):
    try:
        data = load_database()
        patients = data.get("patients", [])

        all_records = get_all_admission_records(patients)

        admission_count = 0
        discharge_count = 0
        inpatient_count = 0
        report_records = []

        for record in all_records:
            admission_date = record.get("admission_date", "")
            discharge_date = record.get("discharge_date", "")

            admitted_in_period = (
                admission_date
                and start_date <= admission_date <= end_date
            )

            discharged_in_period = (
                discharge_date
                and start_date <= discharge_date <= end_date
            )

            if admitted_in_period:
                admission_count += 1

            if discharged_in_period:
                discharge_count += 1

            if admitted_in_period or discharged_in_period:
                report_records.append(record)

            # Count patients who were still admitted at the end date
            if (
                admission_date
                and admission_date <= end_date
                and (
                    not discharge_date
                    or discharge_date > end_date
                )
            ):
                inpatient_count += 1

        report_records.sort(
            key=lambda record: record.get("admission_date", "")
        )

        # Count transfers in and out for each room type
        transfer_summary = get_room_transfer_summary(
            patients,
            start_date,
            end_date
        )

        summary = {
            "admissions": admission_count,
            "discharges": discharge_count,
            "inpatients": inpatient_count
        }

        safe_period = period_label.replace(" ", "_")
        safe_period = safe_period.replace("/", "-")

        output_path = filedialog.asksaveasfilename(
            parent=root,
            title="Save " + report_type + " Report",
            initialfile=(
                "Careflow_" + report_type.replace(" ", "_")
                + "_Report_" + safe_period + ".pdf"
            ),
            defaultextension=".pdf",
            filetypes=[
                ("PDF Files", "*.pdf")
            ]
        )

        if not output_path:
            return

        create_pdf_file(
            output_path,
            report_type + " Report",
            period_label,
            summary,
            report_records,
            transfer_summary
        )

        messagebox.showinfo(
            "Report Generated",
            report_type + " report generated successfully!\n\n"
            + "Reporting Period: " + period_label
            + "\nTotal Admissions: " + str(admission_count)
            + "\nTotal Discharges: " + str(discharge_count)
            + "\nInpatients at Period End: " + str(inpatient_count)
            + "\n\nSaved to:\n" + output_path,
            parent=root
        )

    except (OSError, ValueError, KeyError, TypeError) as error:
        messagebox.showerror(
            "Report Error",
            "Unable to generate the report.\n\n" + str(error),
            parent=root
        )


# Get the actual calendar weeks for a selected month
def get_calendar_weeks(year, month):
    month_calendar = calendar.Calendar(
        firstweekday=calendar.MONDAY
    )

    weeks = month_calendar.monthdatescalendar(year, month)
    week_options = []

    today = date.today()

    for index, week in enumerate(weeks, start=1):
        week_start = week[0]
        week_end = week[6]

        # Do not include weeks that are entirely in the future
        if week_start > today:
            continue

        # Limit the current week to today's date
        if week_end > today:
            week_end = today

        start_text = week_start.strftime("%d %b")
        end_text = week_end.strftime("%d %b")

        week_label = (
            str(index) + ordinal_suffix(index)
            + " Week (" + start_text + " - " + end_text + ")"
        )

        week_options.append({
            "label": week_label,
            "start": week_start,
            "end": week_end
        })

    return week_options


# Get the correct ordinal suffix for a week number
def ordinal_suffix(number):
    if 10 <= number % 100 <= 20:
        return "th"

    suffixes = {
        1: "st",
        2: "nd",
        3: "rd"
    }

    return suffixes.get(number % 10, "th")


# Display the report selection pop-up
def show_report_selection():
    report_window = tk.Toplevel(root)
    report_window.title("Print Report")
    report_window.geometry("410x370")
    report_window.configure(bg=PINK_LIGHT)
    report_window.resizable(False, False)
    report_window.transient(root)
    report_window.grab_set()

    tk.Label(
        report_window,
        text="Print Report",
        font=("Arial", 16, "bold"),
        bg=PINK_LIGHT,
        fg=PINK_DARK
    ).pack(pady=(20, 8))

    tk.Label(
        report_window,
        text="Select the type and reporting period.",
        font=("Arial", 10),
        bg=PINK_LIGHT,
        fg=TEXT_LIGHT
    ).pack(pady=(0, 15))

    form_frame = tk.Frame(
        report_window,
        bg=PINK_LIGHT
    )
    form_frame.pack()

    # Report type
    tk.Label(
        form_frame,
        text="Report Type:",
        font=("Arial", 10, "bold"),
        bg=PINK_LIGHT,
        fg=TEXT_DARK
    ).grid(row=0, column=0, sticky="w", pady=8)

    report_type_box = ttk.Combobox(
        form_frame,
        values=["Monthly Report", "Weekly Report"],
        state="readonly",
        width=20
    )
    report_type_box.grid(row=0, column=1, padx=10, pady=8)
    report_type_box.set("Monthly Report")

    # Month selection
    tk.Label(
        form_frame,
        text="Month:",
        font=("Arial", 10, "bold"),
        bg=PINK_LIGHT,
        fg=TEXT_DARK
    ).grid(row=1, column=0, sticky="w", pady=8)

    month_box = ttk.Combobox(
        form_frame,
        values=list(calendar.month_name)[1:],
        state="readonly",
        width=20
    )
    month_box.grid(row=1, column=1, padx=10, pady=8)
    month_box.set(calendar.month_name[date.today().month])

    # Year selection
    tk.Label(
        form_frame,
        text="Year:",
        font=("Arial", 10, "bold"),
        bg=PINK_LIGHT,
        fg=TEXT_DARK
    ).grid(row=2, column=0, sticky="w", pady=8)

    year_entry = ttk.Entry(
        form_frame,
        width=23
    )
    year_entry.grid(row=2, column=1, padx=10, pady=8)
    year_entry.insert(0, str(date.today().year))

    # Week selection
    week_label = tk.Label(
        form_frame,
        text="Select Week:",
        font=("Arial", 10, "bold"),
        bg=PINK_LIGHT,
        fg=TEXT_DARK
    )

    week_box = ttk.Combobox(
        form_frame,
        state="readonly",
        width=25
    )

    week_options = []

    # Update the available weeks automatically
    def update_week_options(event=None):
        nonlocal week_options

        selected_month = month_box.current()
        year_text = year_entry.get().strip()

        if selected_month < 0 or not year_text.isdigit():
            week_options = []
            week_box["values"] = []
            week_box.set("")
            return

        selected_year = int(year_text)
        selected_month += 1

        if selected_year < 2000 or selected_year > date.today().year:
            week_options = []
            week_box["values"] = []
            week_box.set("")
            return

        if (
            selected_year == date.today().year
            and selected_month > date.today().month
        ):
            week_options = []
            week_box["values"] = []
            week_box.set("")
            return

        week_options = get_calendar_weeks(
            selected_year,
            selected_month
        )

        labels = [
            week["label"] for week in week_options
        ]

        week_box["values"] = labels

        if labels:
            week_box.current(0)
        else:
            week_box.set("")

    # Show or hide the week selection
    def change_report_type(event=None):
        if report_type_box.get() == "Weekly Report":
            week_label.grid(
                row=3,
                column=0,
                sticky="w",
                pady=8
            )

            week_box.grid(
                row=3,
                column=1,
                padx=10,
                pady=8
            )

            update_week_options()

        else:
            week_label.grid_remove()
            week_box.grid_remove()

    month_box.bind(
        "<<ComboboxSelected>>",
        update_week_options
    )

    year_entry.bind(
        "<KeyRelease>",
        update_week_options
    )

    report_type_box.bind(
        "<<ComboboxSelected>>",
        change_report_type
    )

    # Confirm the selected report
    def confirm_report():
        selected_month = month_box.current() + 1
        year_text = year_entry.get().strip()

        if selected_month == 0:
            messagebox.showwarning(
                "Missing Month",
                "Please select a month.",
                parent=report_window
            )
            return

        if not year_text.isdigit():
            messagebox.showwarning(
                "Invalid Year",
                "Please enter a valid year.",
                parent=report_window
            )
            return

        selected_year = int(year_text)
        today = date.today()

        if selected_year < 2000 or selected_year > today.year:
            messagebox.showwarning(
                "Invalid Year",
                "Please enter a year between 2000 and "
                + str(today.year) + ".",
                parent=report_window
            )
            return

        if (
            selected_year == today.year
            and selected_month > today.month
        ):
            messagebox.showwarning(
                "Invalid Month",
                "You cannot generate a report for a future month.",
                parent=report_window
            )
            return

        selected_type = report_type_box.get()

        if selected_type == "Monthly Report":
            start_date = date(
                selected_year,
                selected_month,
                1
            )

            last_day = calendar.monthrange(
                selected_year,
                selected_month
            )[1]

            end_date = date(
                selected_year,
                selected_month,
                last_day
            )

            # Do not include future dates in the current month
            if end_date > today:
                end_date = today

            period_label = (
                calendar.month_name[selected_month]
                + " " + str(selected_year)
                + " (" + start_date.strftime("%d %b")
                + " - " + end_date.strftime("%d %b") + ")"
            )

        else:
            # Refresh the weeks before using the selected week
            update_week_options()

            selected_week = week_box.current()

            if selected_week < 0 or selected_week >= len(week_options):
                messagebox.showwarning(
                    "Missing Week",
                    "Please select a valid week.",
                    parent=report_window
                )
                return

            selected_week_data = week_options[selected_week]

            start_date = selected_week_data["start"]
            end_date = selected_week_data["end"]

            period_label = (
                selected_week_data["label"]
                + " - " + str(selected_year)
            )

        report_window.destroy()

        generate_report(
            start_date.isoformat(),
            end_date.isoformat(),
            selected_type,
            period_label
        )

    button_frame = tk.Frame(
        report_window,
        bg=PINK_LIGHT
    )
    button_frame.pack(pady=22)

    tk.Button(
        button_frame,
        text="Cancel",
        command=report_window.destroy,
        bg=PINK_PALE,
        fg=TEXT_DARK,
        font=("Arial", 10, "bold"),
        width=10,
        cursor="hand2"
    ).pack(side="left", padx=5)

    tk.Button(
        button_frame,
        text="Generate PDF",
        command=confirm_report,
        bg=PINK_DARK,
        fg=WHITE,
        activebackground=PINK_ACTIVE,
        activeforeground=WHITE,
        font=("Arial", 10, "bold"),
        width=13,
        cursor="hand2"
    ).pack(side="left", padx=5)

    change_report_type()


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
    today = date.today().isoformat()

    for patient in patients:
        if (
            patient.get("bed_id", "")
            and patient.get("status", "") != "Discharged"
        ):
            inpatient_count += 1

        history = patient.get("admission_history", [])

        if isinstance(history, list):
            for record in history:
                if (
                    isinstance(record, dict)
                    and record.get("discharge_date") == today
                ):
                    today_discharge_count += 1

        if (
            patient.get("status") == "Discharged"
            and patient.get("discharge_date") == today
        ):
            today_discharge_count += 1

    # Calculate occupied beds
    occupied_count = 0

    for bed in beds:
        bed_id = str(bed.get("bed_id", ""))
        bed_patient_id = str(bed.get("patient_id", ""))

        patient = find_patient(
            bed_id,
            patients,
            "bed_id"
        )

        if (
            patient is None
            or patient.get("status") == "Discharged"
        ):
            if bed_patient_id:
                patient = find_patient(
                    bed_patient_id,
                    patients
                )

        if patient and patient.get("status") != "Discharged":
            occupied_count += 1

    available_count = len(beds) - occupied_count

    content = add_navigation(root, "Dashboard")

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

    columns = (
        "patient_ic",
        "patient_id",
        "name",
        "bed_id",
        "status",
        "admission_date",
        "discharge_date"
    )

    patient_table = ttk.Treeview(
        table_frame,
        columns=columns,
        show="headings",
        height=8
    )

    patient_table.heading("patient_ic", text="Patient IC")
    patient_table.heading("patient_id", text="Patient ID")
    patient_table.heading("name", text="Patient Name")
    patient_table.heading("bed_id", text="Bed ID")
    patient_table.heading("status", text="Status")
    patient_table.heading("admission_date", text="Admission Date")
    patient_table.heading("discharge_date", text="Discharge Date")

    patient_table.column("patient_ic", width=140, anchor="center")
    patient_table.column("patient_id", width=110, anchor="center")
    patient_table.column("name", width=180)
    patient_table.column("bed_id", width=110, anchor="center")
    patient_table.column("status", width=130, anchor="center")
    patient_table.column("admission_date", width=110, anchor="center")
    patient_table.column("discharge_date", width=110, anchor="center")

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

    # Display previous and current patient admission records
    for patient in patients[-100:]:
        patient_ic = patient.get("patient_ic", "")
        patient_id = patient.get("patient_id", "")
        patient_name = patient.get("name", "")

        history = patient.get("admission_history", [])

        if isinstance(history, list):
            for record in history:
                if not isinstance(record, dict):
                    continue

                record_status = record.get("status", "Discharged")

                if record_status == "Discharged":
                    record_bed_id = "-"
                else:
                    record_bed_id = record.get("bed_id", "") or "-"

                patient_table.insert(
                    "",
                    "end",
                    values=(
                        patient_ic,
                        patient_id,
                        patient_name,
                        record_bed_id,
                        record_status,
                        record.get("admission_date", ""),
                        record.get("discharge_date", "") or "-"
                    )
                )

        current_admission = (
            patient.get("admission_date", ""),
            patient.get("discharge_date", "")
        )

        already_archived = any(
            isinstance(record, dict)
            and (
                record.get("admission_date", ""),
                record.get("discharge_date", "")
            ) == current_admission
            for record in history
        ) if isinstance(history, list) else False

        if not already_archived:
            current_status = patient.get("status", "Registered")

            if current_status == "Discharged":
                current_bed_id = "-"
            else:
                current_bed_id = patient.get("bed_id", "") or "-"

            patient_table.insert(
                "",
                "end",
                values=(
                    patient_ic,
                    patient_id,
                    patient_name,
                    current_bed_id,
                    current_status,
                    patient.get("admission_date", ""),
                    patient.get("discharge_date", "") or "-"
                )
            )

    # Print Report button
    tk.Button(
        content,
        text="Print Report",
        command=show_report_selection,
        bg=PINK_DARK,
        fg=WHITE,
        activebackground=PINK_ACTIVE,
        activeforeground=WHITE,
        font=("Arial", 10, "bold"),
        padx=20,
        pady=8,
        cursor="hand2"
    ).pack(pady=(0, 12))

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


# Keep all the modules connected to the same dashboard
if __name__ == "__main__":
    import sys
    sys.modules["dashboard"] = sys.modules["__main__"]
    start_app()
