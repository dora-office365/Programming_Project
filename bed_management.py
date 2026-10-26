# Sample bed records
beds = [
    {"bed_id": "B001", "ward": "W01", "status": "Available"},
    {"bed_id": "B002", "ward": "W01", "status": "Occupied"},
    {"bed_id": "B003", "ward": "W01", "status": "Available"},
    {"bed_id": "B004", "ward": "W02", "status": "Occupied"},
    {"bed_id": "B005", "ward": "W02", "status": "Available"},
    {"bed_id": "B006", "ward": "W02", "status": "Occupied"},
    {"bed_id": "B007", "ward": "W03", "status": "Available"},
    {"bed_id": "B008", "ward": "W03", "status": "Occupied"}
]


# ==========================================================
# 1. VALIDATE BED RECORDS
# ==========================================================

def validate_bed_records():
    """Check bed records for missing fields and duplicate IDs."""

    seen_ids = set()

    for bed in beds:
        if not all(key in bed for key in ("bed_id", "ward", "status")):
            return False

        bed_id = bed["bed_id"].strip().upper()
        ward = bed["ward"].strip().upper()
        status = bed["status"].strip().title()

        if not bed_id or not ward:
            return False

        if status not in ("Available", "Occupied"):
            return False

        if bed_id in seen_ids:
            return False

        seen_ids.add(bed_id)

    return True


# ==========================================================
# 2. DISPLAY BED TABLE
# ==========================================================

def display_bed_table(records):
    """Display bed records in a formatted table."""

    if not records:
        print("\nNo matching bed records found.")
        return

    print("\n" + "=" * 55)
    print("                 BED INFORMATION")
    print("=" * 55)

    print(f"{'Bed ID':<15}{'Ward Number':<18}{'Status':<15}")
    print("-" * 55)

    for bed in records:
        print(
            f"{bed['bed_id']:<15}"
            f"{bed['ward']:<18}"
            f"{bed['status']:<15}"
        )

    print("-" * 55)


# ==========================================================
# 3. SEARCH BED BY BED ID
# ==========================================================

def search_bed_by_id():
    """Search for a specific bed using its ID."""

    print("\n========== SEARCH BED BY ID ==========")

    bed_id = input("Enter bed ID: ").strip().upper()

    if not bed_id:
        print("Error: Bed ID cannot be empty.")
        return

    for bed in beds:
        if bed["bed_id"].strip().upper() == bed_id:
            print("\nBed record found successfully!")
            display_bed_table([bed])
            return

    print(f"\nError: Bed ID '{bed_id}' does not exist.")


# ==========================================================
# 4. SEARCH BEDS BY WARD
# ==========================================================

def search_beds_by_ward():
    """Display all beds belonging to a selected ward."""

    print("\n========== SEARCH BEDS BY WARD ==========")

    ward_number = input("Enter ward number: ").strip().upper()

    if not ward_number:
        print("Error: Ward number cannot be empty.")
        return

    matching_beds = [
        bed for bed in beds
        if bed["ward"].strip().upper() == ward_number
    ]

    if matching_beds:
        print(f"\nBeds registered in Ward {ward_number}:")
        display_bed_table(matching_beds)
    else:
        print(f"\nNo beds found in Ward {ward_number}.")


# ==========================================================
# 5. FILTER BEDS BY STATUS
# ==========================================================

def filter_beds_by_status():
    """Filter beds according to availability status."""

    print("\n========== FILTER BEDS BY STATUS ==========")
    print("1. Available Beds")
    print("2. Occupied Beds")

    choice = input("Select status (1-2): ").strip()

    if choice == "1":
        selected_status = "Available"

    elif choice == "2":
        selected_status = "Occupied"

    else:
        print("Invalid selection. Please choose 1 or 2.")
        return

    matching_beds = [
        bed for bed in beds
        if bed["status"].strip().title() == selected_status
    ]

    print(f"\n{selected_status} Beds:")
    display_bed_table(matching_beds)


# ==========================================================
# 6. DISPLAY ALL BEDS AND AVAILABILITY SUMMARY
# ==========================================================

def display_all_beds():
    """Display every bed and summarise bed availability."""

    print("\n========== ALL BED RECORDS ==========")

    display_bed_table(beds)

    total_beds = len(beds)

    available_beds = sum(
        1 for bed in beds
        if bed["status"].strip().title() == "Available"
    )

    occupied_beds = sum(
        1 for bed in beds
        if bed["status"].strip().title() == "Occupied"
    )

    print("\n========== BED AVAILABILITY SUMMARY ==========")
    print(f"Total Beds          : {total_beds}")
    print(f"Available Beds      : {available_beds}")
    print(f"Occupied Beds       : {occupied_beds}")

    if total_beds > 0:
        occupancy_rate = (occupied_beds / total_beds) * 100
        print(f"Bed Occupancy Rate  : {occupancy_rate:.1f}%")

    print("=" * 48)


# ==========================================================
# 7. BED MANAGEMENT MENU
# ==========================================================

def bed_management():
    """Main menu for the Bed Management module."""

    if not validate_bed_records():
        print("Error: Bed records contain invalid or duplicate data.")
        return

    while True:
        print("\n" + "=" * 48)
        print("       CAREFLOW - BED MANAGEMENT")
        print("=" * 48)
        print("1. Search Bed by ID")
        print("2. Search Beds by Ward")
        print("3. Filter Beds by Status")
        print("4. Display All Beds")
        print("5. Return to Main Dashboard")
        print("=" * 48)

        choice = input("Enter your choice (1-5): ").strip()

        if choice == "1":
            search_bed_by_id()

        elif choice == "2":
            search_beds_by_ward()

        elif choice == "3":
            filter_beds_by_status()

        elif choice == "4":
            display_all_beds()

        elif choice == "5":
            print("Returning to the Main Dashboard...")
            break

        else:
            print("Invalid choice. Please enter a number from 1 to 5.")


# ==========================================================
# MAIN PROGRAM FOR TESTING
# ==========================================================

if __name__ == "__main__":
    bed_management()
