import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

def show_discharge(self): 
    frame= self.replace_page("Discharge Management") 
    ttk.Label(
        frame,
        text="Select a patient to discharge."
    ).pack(anchor="w", pady=10) 


    # Display admitted patients 
    columns = ["ID", "Name", "Bed", "Admission Date"]
    tree = ttk.Treeview(frame, columns=columns, show="headings") 
    for col in columns: 
        tree.heading(col, text=col) 
        tree.column(col, width=150) 
    tree.pack(fill="both", expand=True) 


    # Refresh patient list 
    def refresh_table(): 
        for item in tree.get_children(): 
            tree.delete(item) 
    
        for patient in self.patients: 
            if patient["status"] == "Admitted": 
                tree.insert("", "end", values=( 
                    patient["patient_id"], 
                    patient["name"], 
                    patient["bed_id"], 
                    patient["admission_date"]
              )) 


    # Process discharge 
    def discharge_patient(): 
        selected = tree.selection() 
    
        if not selected: 
            messagebox.showwarning( 
                "Warning", "Please select a patient." 
            ) 
            return 
    
        patient_id = tree.item(selected[0], "values")[0] 
        for patient in self.patients: 
            if (patient["patient_id"] == patient_id and patient["status"] == "Admitted"): 
                payment = messagebox.askyesno( 
                    "Payment Confirmation", 
                    "Patient's payment completed?" 
                ) 

                if not payment: 
                    patient["payment_confirmed"] = "No" 
                    save_data(self.patients, self.beds) 
                    messagebox.showwarning(
                        "Discharge Restricted",
                        "Patient remains admitted." 
                    ) 
                    return 
            
                patient["payment_confirmed"] = "Yes" 
                patient["status"] = "Discharged" 
                patient["discharge_date"] = date.today().isoformat() 
                patient["bed_id"] = "" 
            
                save_data(self.patients, self.beds) 
                refresh_table() 
            
                messagebox.showinfo(  
                    "Patient discharged successfully." 
                ) 
                return 
        messagebox.showerror("Error", "Patient not found.") 


    # Buttons 
    ttk.Button( 
        frame, text="Discharge", 
        command=discharge_patient 
    ).pack(side="left", padx=5, pady=10) 

    ttk.Button( 
        frame, text="Refresh List", 
        command=refresh_table 
    ).pack(side="left", padx=5, pady=10) 
    
    refresh_table() 