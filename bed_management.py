import tkinter as tk
from tkinter import ttk, messagebox

# ----------------------------------------------------------
# SAMPLE BED RECORDS
# In the integrated project, replace this list with the
# shared bed data used by the other team modules.
# ----------------------------------------------------------
beds = [
    {"bed_id": "B001", "ward": "W01", "status": "Available"},
    {"bed_id": "B002", "ward": "W01", "status": "Occupied"},
    {"bed_id": "B003", "ward": "W01", "status": "Available"},
    {"bed_id": "B004", "ward": "W02", "status": "Occupied"},
    {"bed_id": "B005", "ward": "W02", "status": "Available"},
    {"bed_id": "B006", "ward": "W02", "status": "Occupied"},
    {"bed_id": "B007", "ward": "W03", "status": "Available"},
    {"bed_id": "B008", "ward": "W03", "status": "Occupied"},
]


def validate_bed_records(records):
    """Validate required fields, value types, statuses and unique IDs."""
    seen_ids = set()

    for bed in records:
        if not isinstance(bed, dict):
            return False, "A bed record is not in the correct format."

        required = ("bed_id", "ward", "status")
        if not all(key in bed for key in required):
            return False, "A bed record is missing a required field."

        if not all(isinstance(bed[key], str) for key in required):
            return False, "Bed ID, ward and status must be text values."

        bed_id = bed["bed_id"].strip().upper()
        ward = bed["ward"].strip().upper()
        status = bed["status"].strip().title()

        if not bed_id or not ward:
            return False, "Bed ID and ward cannot be empty."

        if status not in ("Available", "Occupied"):
            return False, f"Invalid status found for bed {bed_id}."

        if bed_id in seen_ids:
            return False, f"Duplicate bed ID found: {bed_id}."

        seen_ids.add(bed_id)

    return True, ""


class BedManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CAREFLOW | Bed Management")
        self.root.geometry("1120x720")
        self.root.minsize(900, 600)
        self.root.configure(bg="#F3F6FB")

        self.filtered_records = list(beds)
        self.status_filter = tk.StringVar(value="All Statuses")
        self.search_var = tk.StringVar()
        self.ward_var = tk.StringVar(value="All Wards")

        self.setup_styles()
        self.build_layout()
        self.refresh_table(self.filtered_records)
        self.update_summary()

    def setup_styles(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(
            "Treeview",
            background="white",
            foreground="#243247",
            fieldbackground="white",
            rowheight=36,
            font=("Arial", 10),
            borderwidth=0
        )
        style.configure(
            "Treeview.Heading",
            background="#EAF0F8",
            foreground="#334155",
            font=("Arial", 10, "bold"),
            padding=(10, 12),
            relief="flat"
        )
        style.map(
            "Treeview",
            background=[("selected", "#DCEAFE")],
            foreground=[("selected", "#173B70")]
        )

    def build_layout(self):
        # Sidebar
        sidebar = tk.Frame(self.root, bg="#14243A", width=220)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(
            sidebar, text="â CAREFLOW", bg="#14243A", fg="white",
            font=("Arial", 19, "bold"), pady=28
        ).pack(fill="x")

        tk.Label(
            sidebar, text="HOSPITAL MANAGEMENT", bg="#14243A",
            fg="#A9B9CD", font=("Arial", 8, "bold")
        ).pack(pady=(0, 24))

        self.sidebar_item(sidebar, "â¦   Dashboard", False)
        self.sidebar_item(sidebar, "â£   Patient Management", False)
        self.sidebar_item(sidebar, "â¤   Bed Management", True)
        self.sidebar_item(sidebar, "â   Discharge Management", False)

        tk.Frame(sidebar, bg="#34465D", height=1).pack(
            fill="x", padx=18, pady=22
        )
        tk.Label(
            sidebar, text="BED MANAGEMENT MODULE",
            bg="#14243A", fg="#A9B9CD",
            font=("Arial", 8, "bold")
        ).pack(anchor="w", padx=20)
        tk.Label(
            sidebar, text="Search â¢ Filter â¢ Display",
            bg="#14243A", fg="white",
            font=("Arial", 10), pady=10
        ).pack(anchor="w", padx=20)

        tk.Label(
            sidebar, text="CAREFLOW v1.0\nUniversity Project",
            bg="#14243A", fg="#91A2B8",
            font=("Arial", 9), justify="left"
        ).pack(side="bottom", anchor="w", padx=20, pady=22)

        # Main content area
        content = tk.Frame(self.root, bg="#F3F6FB")
        content.pack(side="left", fill="both", expand=True)

        header = tk.Frame(content, bg="white", height=76)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header, text="Bed Management",
            bg="white", fg="#172B4D",
            font=("Arial", 21, "bold")
        ).pack(side="left", padx=28, pady=20)

        tk.Label(
            header, text="â System Ready",
            bg="white", fg="#16845B",
            font=("Arial", 10, "bold")
        ).pack(side="right", padx=28)

        body = tk.Frame(content, bg="#F3F6FB")
        body.pack(fill="both", expand=True, padx=26, pady=22)

        tk.Label(
            body, text="Bed Overview",
            bg="#F3F6FB", fg="#172B4D",
            font=("Arial", 15, "bold")
        ).pack(anchor="w")

        tk.Label(
            body,
            text="Search bed records and monitor current bed availability.",
            bg="#F3F6FB", fg="#64748B",
            font=("Arial", 10)
        ).pack(anchor="w", pady=(5, 17))

        # Summary cards
        cards = tk.Frame(body, bg="#F3F6FB")
        cards.pack(fill="x", pady=(0, 20))

        self.total_value = self.create_card(cards, "TOTAL BEDS", "0", "#315D9B")
        self.available_value = self.create_card(
            cards, "AVAILABLE BEDS", "0", "#16845B"
        )
        self.occupied_value = self.create_card(
            cards, "OCCUPIED BEDS", "0", "#C47A19"
        )
        self.rate_value = self.create_card(
            cards, "OCCUPANCY RATE", "0%", "#7C55B7"
        )

        # Search/filter panel
        tools_panel = tk.Frame(body, bg="white", padx=16, pady=16)
        tools_panel.pack(fill="x", pady=(0, 16))

        tk.Label(
            tools_panel, text="Search by bed ID",
            bg="white", fg="#334155", font=("Arial", 9, "bold")
        ).grid(row=0, column=0, sticky="w", padx=(0, 8))

        self.search_entry = ttk.Entry(
            tools_panel, textvariable=self.search_var, width=23
        )
        self.search_entry.grid(row=1, column=0, sticky="ew", padx=(0, 8), pady=(7, 0))
        self.search_entry.bind("<Return>", lambda event: self.search_bed())

        ttk.Button(
            tools_panel, text="Search", command=self.search_bed
        ).grid(row=1, column=1, padx=(0, 18), pady=(7, 0))

        tk.Label(
            tools_panel, text="Ward",
            bg="white", fg="#334155", font=("Arial", 9, "bold")
        ).grid(row=0, column=2, sticky="w", padx=(0, 8))

        self.ward_combo = ttk.Combobox(
            tools_panel, textvariable=self.ward_var,
            values=["All Wards"] + sorted({b["ward"] for b in beds}),
            state="readonly", width=13
        )
        self.ward_combo.grid(row=1, column=2, padx=(0, 18), pady=(7, 0))
        self.ward_combo.bind("<<ComboboxSelected>>", lambda event: self.apply_filters())

        tk.Label(
            tools_panel, text="Bed status",
            bg="white", fg="#334155", font=("Arial", 9, "bold")
        ).grid(row=0, column=3, sticky="w", padx=(0, 8))

        self.status_combo = ttk.Combobox(
            tools_panel, textvariable=self.status_filter,
            values=["All Statuses", "Available", "Occupied"],
            state="readonly", width=15
        )
        self.status_combo.grid(row=1, column=3, padx=(0, 18), pady=(7, 0))
        self.status_combo.bind(
            "<<ComboboxSelected>>", lambda event: self.apply_filters()
        )

        ttk.Button(
            tools_panel, text="Reset", command=self.reset_filters
        ).grid(row=1, column=4, pady=(7, 0))

        tools_panel.columnconfigure(0, weight=1)

        # Table panel
        table_panel = tk.Frame(body, bg="white", padx=16, pady=14)
        table_panel.pack(fill="both", expand=True)

        table_header = tk.Frame(table_panel, bg="white")
        table_header.pack(fill="x", pady=(0, 12))

        tk.Label(
            table_header, text="Bed Records",
            bg="white", fg="#172B4D",
            font=("Arial", 13, "bold")
        ).pack(side="left")

        self.result_label = tk.Label(
            table_header, text="0 records",
            bg="white", fg="#64748B", font=("Arial", 9)
        )
        self.result_label.pack(side="right")

        table_frame = tk.Frame(table_panel, bg="white")
        table_frame.pack(fill="both", expand=True)

        columns = ("bed_id", "ward", "status")
        self.tree = ttk.Treeview(
            table_frame, columns=columns, show="headings",
            selectmode="browse"
        )
        self.tree.heading("bed_id", text="BED ID")
        self.tree.heading("ward", text="WARD")
        self.tree.heading("status", text="STATUS")
        self.tree.column("bed_id", width=180, anchor="center")
        self.tree.column("ward", width=180, anchor="center")
        self.tree.column("status", width=220, anchor="center")

        scrollbar = ttk.Scrollbar(
            table_frame, orient="vertical", command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.tag_configure("Available", foreground="#16845B")
        self.tree.tag_configure("Occupied", foreground="#B45309")

        footer = tk.Frame(body, bg="#F3F6FB")
        footer.pack(fill="x", pady=(10, 0))
        tk.Label(
            footer, text="CAREFLOW | Bed Management",
            bg="#F3F6FB", fg="#64748B", font=("Arial", 9)
        ).pack(side="left")
        tk.Label(
            footer, text="For authorised hospital personnel",
            bg="#F3F6FB", fg="#64748B", font=("Arial", 9)
        ).pack(side="right")

    def sidebar_item(self, parent, text, active):
        bg = "#25466D" if active else "#14243A"
        fg = "white" if active else "#C4D0DE"
        item = tk.Label(
            parent, text=text, bg=bg, fg=fg,
            font=("Arial", 10, "bold" if active else "normal"),
            anchor="w", padx=20, pady=13
        )
        item.pack(fill="x", padx=10, pady=2)

    def create_card(self, parent, title, value, accent):
        card = tk.Frame(parent, bg="white", padx=16, pady=14)
        card.pack(side="left", fill="both", expand=True, padx=(0, 12))
        tk.Frame(card, bg=accent, height=4).pack(fill="x", pady=(0, 12))
        tk.Label(
            card, text=title, bg="white", fg="#64748B",
            font=("Arial", 8, "bold")
        ).pack(anchor="w")
        value_label = tk.Label(
            card, text=value, bg="white", fg="#172B4D",
            font=("Arial", 22, "bold")
        )
        value_label.pack(anchor="w", pady=(5, 0))
        return value_label

    def refresh_table(self, records):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for bed in records:
            status = bed["status"].strip().title()
            self.tree.insert(
                "", "end",
                values=(
                    bed["bed_id"].strip().upper(),
                    bed["ward"].strip().upper(),
                    status
                ),
                tags=(status,)
            )

        self.result_label.config(
            text=f"{len(records)} record{'s' if len(records) != 1 else ''}"
        )

    def update_summary(self):
        total = len(beds)
        available = sum(
            1 for bed in beds
            if bed["status"].strip().title() == "Available"
        )
        occupied = sum(
            1 for bed in beds
            if bed["status"].strip().title() == "Occupied"
        )
        occupancy = (occupied / total * 100) if total else 0

        self.total_value.config(text=str(total))
        self.available_value.config(text=str(available))
        self.occupied_value.config(text=str(occupied))
        self.rate_value.config(text=f"{occupancy:.1f}%")

    def search_bed(self):
        query = self.search_var.get().strip().upper()
        if not query:
            messagebox.showwarning(
                "Input Required", "Please enter a bed ID to search."
            )
            self.search_entry.focus_set()
            return

        matches = [
            bed for bed in beds
            if bed["bed_id"].strip().upper() == query
        ]

        if matches:
            self.ward_var.set("All Wards")
            self.status_filter.set("All Statuses")
            self.refresh_table(matches)
        else:
            self.refresh_table([])
            messagebox.showinfo(
                "No Results", f"No bed record was found for '{query}'."
            )

    def apply_filters(self):
        ward = self.ward_var.get()
        status = self.status_filter.get()
        query = self.search_var.get().strip().upper()

        matches = []
        for bed in beds:
            if ward != "All Wards" and bed["ward"].strip().upper() != ward:
                continue
            if status != "All Statuses" and bed["status"].strip().title() != status:
                continue
            if query and query not in bed["bed_id"].strip().upper():
                continue
            matches.append(bed)

        self.refresh_table(matches)

    def reset_filters(self):
        self.search_var.set("")
        self.ward_var.set("All Wards")
        self.status_filter.set("All Statuses")
        self.refresh_table(beds)


def main():
    valid, error_message = validate_bed_records(beds)
    if not valid:
        # Create a hidden root to show a friendly error dialog.
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Invalid Bed Data", error_message)
        root.destroy()
        return

    root = tk.Tk()
    BedManagementApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
