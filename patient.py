import tkinter as tk
import json
import os
from tkinter import ttk, messagebox
from datetime import date
from data import PATIENT_FIELDS
from data import save_database
def show_patients(self): 
    frame = self.replace_page("Patient Management") 

    # Patient information form 
    form = ttk.LabelFrame(frame, text="Patient Information", padding=10) 

    form.pack(side="left", fill="y", padx=10) 

    fields = [ 
        ("Patient ID", "patient_id"), 
        ("Full Name", "name"), 
        ("Date of Birth", "dob"), 
        ("Phone", "phone"), 
        ("Address", "address"), 
        ("Emergency Contact", "emergency_contact"), 
        ("Diagnosis", "diagnosis") 
    ] 

    entries = {} 
    for row, (label, key) in enumerate(fields): 
     
        ttk.Label(form, text=label).grid(row=row, column=0, pady=5) 
        entry = ttk.Entry(form, width=25) 
        entry.grid(row=row, column=1, pady=5) 
        entries[key] = entry 
    # Gender selection 

    row = len(fields) 
    ttk.Label(form, text="Gender").grid(row=row, column=0, pady=5) 

    gender = ttk.Combobox( 
        form, values=["Female", "Male", "Other"], 
        state="readonly", width=22 
    ) 

    gender.grid(row=row, column=1, pady=5) 
    entries["gender"] = gender 

    # Bed selection 
    row += 1 
    ttk.Label(form, text="Bed").grid(row=row, column=0, pady=5) 

    bed_box = ttk.Combobox(form, state="readonly", width=22) 
    bed_box.grid(row=row, column=1, pady=5) 

    selected_id = [""] 

    # Search and patient list 
    result = ttk.LabelFrame(frame, text="Patient Records", padding=10) 
    result.pack(side="left", fill="both", expand=True) 

    search = ttk.Entry(result) 
    search.pack(fill="x", pady=5) 

    tree = ttk.Treeview( 
        result, 
        columns=("id", "name", "bed", "status"), 
        show="headings" 
    ) 

    tree.heading("id", text="Patient ID") 
    tree.heading("name", text="Name") 
    tree.heading("bed", text="Bed") 
    tree.heading("status", text="Status") 
    tree.pack(fill="both", expand=True) 

    # Update available bed choices 
    def update_beds(): 
        choices = ["No bed"] 

        for bed in self.beds: 

            if bed["status"] == "Available": 

                choices.append(bed["bed_id"]) 

        bed_box["values"] = choices 

        if bed_box.get() not in choices: 
            bed_box.set("No bed") 

    # Display and search patients 
    def display_patients(event=None): 
        for item in tree.get_children(): 
            tree.delete(item) 

        keyword = search.get().lower() 

        for patient in self.patients: 

            if (keyword in patient["patient_id"].lower() 
                    or keyword in patient["name"].lower()): 
                tree.insert("", "end", values=( 
                    patient["patient_id"], 
                    patient["name"], 
                    patient["bed_id"] or "-", 
                    patient["status"] 
                )) 

    # Show selected patient's details in the form 

    def view_patient(event=None): 
        selected = tree.selection() 

        if not selected: 

            return 
        
        patient_id = tree.item(selected[0], "values")[0] 

        for patient in self.patients: 
            if patient["patient_id"] == patient_id: 
                for key, widget in entries.items(): 
                     if isinstance (widget, ttk.Entry):
                        widget.delete(0, "end")
                        widget.insert(0, patient.get(key, ""))
                     else:
                        widget.set(patient.get(key, ""))


                selected_id[0] = patient_id 

                if patient["bed_id"]: 

                    bed_box.set(patient["bed_id"]) 

                else: 
                    bed_box.set("No bed") 

 

                break 

 

    # Register a new patient 
    def register_patient(): 
        patient = {} 

        for key, widget in entries.items(): 
            patient[key] = widget.get().strip() 

        patient["bed_id"] = bed_box.get() 
        if patient["bed_id"] == "No bed": 
            patient["bed_id"] = "" 

        if not patient["patient_id"] or not patient["name"]: 
            messagebox.showerror( 
                "Error", "Patient ID and name are required." 
            ) 
            return 

        for old_patient in self.patients: 
            if old_patient["patient_id"] == patient["patient_id"]: 
                messagebox.showerror( 

                    "Error", "Patient ID already exists." 
                ) 
                return 

        patient["admission_date"] = date.today().isoformat() 
        patient["status"] = ( 

            "Admitted" if patient["bed_id"] else "Registered" 
        ) 

        patient["discharge_date"] = "" 
        patient["payment_confirmed"] = "" 

        for field in PATIENT_FIELDS: 

            if field not in patient: 

                patient[field] = "" 
 
        self.patients.append(patient) 

        save_database(self.db_data) 

 
        display_patients() 
        update_beds() 

        messagebox.showinfo("Success", "Patient registered.") 

    # Update an existing patient 

    def update_patient(): 

        if not selected_id[0]: 

            messagebox.showwarning( 

                "Warning", "Select a patient from the list first." 
            ) 
            return 

        for patient in self.patients: 
            if patient["patient_id"] == selected_id[0]: 
                if patient["status"] == "Discharged": 
                    messagebox.showwarning( 

                        "Warning", "Cannot edit a discharged patient." 
                    ) 
                    return 
                
                for key, widget in entries.items(): 
                    patient[key] = widget.get().strip() 

                patient["bed_id"] = bed_box.get() 

                if patient["bed_id"] == "No bed": 

                    patient["bed_id"] = "" 

                patient["status"] = ( 

                 "Admitted" if patient["bed_id"] else "Registered" 
                ) 

                save_database(self.db_data) 
                display_patients() 
                update_beds() 

                messagebox.showinfo("Success", "Patient updated.") 
                return 

    # Buttons 
    ttk.Button( 

        form, text="Register", command=register_patient 

    ).grid(row=row + 1, column=0, pady=10) 

    ttk.Button( 
        form, text="Update", command=update_patient
    ).grid(row=row + 1, column=1, pady=10)

    # Connect search and selection 
    search.bind("<KeyRelease>", display_patients) 
    tree.bind("<<TreeviewSelect>>", view_patient) 
    update_beds() 
