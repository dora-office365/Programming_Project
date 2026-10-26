import tkinter as tk
import json
import os
from tkinter import ttk, messagebox
from datetime import date
from data import save_data

#Refer to the data file
DB_FILE = "hospital_database.json" 

def load_database():
    """Reads your existing JSON database file directly."""
    if not os.path.exists(DB_FILE):
        # Safety alert in case the file name is misspelled or in the wrong folder
        messagebox.showerror("Error", f"Database file '{DB_FILE}' not found!\nMake sure it is in the same folder as this script.")
        return {"users": [], "patients": [], "beds": []}
        
    with open(DB_FILE, "r") as file:
        return json.load(file)

def save_database(data):
    """Overwrites your JSON file with your updated patient/bed statuses."""
    with open(DB_FILE, "w") as file:
        json.dump(data, file, indent=4)

#Discharge Function
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
    
        for patient in self.db_data["patients"]: 
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
                    "Success",
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


#Application Engine Class
class HospitalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hospital Management System")
        self.root.geometry("700x500")
        
        # Base container canvas
        self.container = ttk.Frame(self.root)
        self.container.pack(fill="both", expand=True)
        
        self.db_data=load_database()
        show_discharge(self)

    def replace_page(self, title):
        for widget in self.container.winfo_children():
            widget.destroy()
        
        page_frame = ttk.Frame(self.container, padding=20)
        page_frame.pack(fill="both", expand=True)
        
        ttk.Label(page_frame, text=title, font=("Arial", 16, "bold")).pack(anchor="w")
        return page_frame

if __name__ == "__main__":
    root = tk.Tk()
    app = HospitalApp(root) 
    root.mainloop()
