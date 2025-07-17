import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from datetime import datetime
import os

class FoodAnxietyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Food Anxiety Data Collection")
        self.root.geometry("800x600")
        
        # Data storage
        self.data_file = "food_anxiety_data.csv"
        self.data = self.load_data()
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_data_entry_tab()
        self.create_visualization_tab()
        
    def load_data(self):
        """Load existing data or create empty DataFrame"""
        if os.path.exists(self.data_file):
            return pd.read_csv(self.data_file)
        else:
            columns = [
                'timestamp', 'food_source', 'eating_location', 'anxiety_level',
                'breathing_difficulty', 'swallowing_difficulty', 'scratchy_throat',
                'stomach_pain', 'chest_pain', 'reflux', 'food_eaten', 'concerns',
                'additional_comments', 'took_meds', 'med_types', 'meds_helped'
            ]
            return pd.DataFrame(columns=columns)
    
    def save_data(self):
        """Save data to CSV file"""
        self.data.to_csv(self.data_file, index=False)
    
    def create_data_entry_tab(self):
        """Create the data entry tab"""
        entry_frame = ttk.Frame(self.notebook)
        self.notebook.add(entry_frame, text="Data Entry")
        
        # Create scrollable frame
        canvas = tk.Canvas(entry_frame)
        scrollbar = ttk.Scrollbar(entry_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Variables for form inputs
        self.food_source = tk.StringVar(value="Home")
        self.eating_location = tk.StringVar(value="Home")
        self.anxiety_level = tk.IntVar(value=0)
        self.breathing_difficulty = tk.StringVar(value="None")
        self.swallowing_difficulty = tk.StringVar(value="None")
        self.scratchy_throat = tk.StringVar(value="None")
        self.stomach_pain = tk.StringVar(value="None")
        self.chest_pain = tk.StringVar(value="None")
        self.reflux = tk.StringVar(value="None")
        self.took_meds = tk.BooleanVar(value=False)
        self.meds_helped = tk.BooleanVar(value=False)
        
        # Create form fields
        row = 0
        
        # Food source
        ttk.Label(scrollable_frame, text="Are you eating food made at home or from somewhere else?").grid(row=row, column=0, sticky='w', pady=5)
        food_source_frame = ttk.Frame(scrollable_frame)
        food_source_frame.grid(row=row, column=1, sticky='w', pady=5)
        ttk.Radiobutton(food_source_frame, text="Home", variable=self.food_source, value="Home").pack(side='left')
        ttk.Radiobutton(food_source_frame, text="Out", variable=self.food_source, value="Out").pack(side='left')
        row += 1
        
        # Eating location
        ttk.Label(scrollable_frame, text="Are you eating at home or out?").grid(row=row, column=0, sticky='w', pady=5)
        eating_location_frame = ttk.Frame(scrollable_frame)
        eating_location_frame.grid(row=row, column=1, sticky='w', pady=5)
        ttk.Radiobutton(eating_location_frame, text="Home", variable=self.eating_location, value="Home").pack(side='left')
        ttk.Radiobutton(eating_location_frame, text="Out", variable=self.eating_location, value="Out").pack(side='left')
        row += 1
        
        # Anxiety level
        ttk.Label(scrollable_frame, text="Rank your current anxiety level (0-10):").grid(row=row, column=0, sticky='w', pady=5)
        anxiety_frame = ttk.Frame(scrollable_frame)
        anxiety_frame.grid(row=row, column=1, sticky='w', pady=5)
        ttk.Scale(anxiety_frame, from_=0, to=10, variable=self.anxiety_level, orient='horizontal').pack(side='left')
        ttk.Label(anxiety_frame, textvariable=self.anxiety_level).pack(side='left', padx=10)
        row += 1
        
        # Symptom severity questions
        severity_options = ["None", "Mild", "Moderate", "Severe"]
        
        symptoms = [
            ("Difficulty catching breath?", self.breathing_difficulty),
            ("Difficulty swallowing?", self.swallowing_difficulty),
            ("Scratchy Throat?", self.scratchy_throat),
            ("Stomach pain?", self.stomach_pain),
            ("Chest pain?", self.chest_pain),
            ("Reflux?", self.reflux)
        ]
        
        for symptom_text, symptom_var in symptoms:
            ttk.Label(scrollable_frame, text=symptom_text).grid(row=row, column=0, sticky='w', pady=5)
            ttk.Combobox(scrollable_frame, textvariable=symptom_var, values=severity_options, state="readonly").grid(row=row, column=1, sticky='w', pady=5)
            row += 1
        
        # Text fields
        ttk.Label(scrollable_frame, text="What did you eat? Where was it from?").grid(row=row, column=0, sticky='w', pady=5)
        self.food_eaten = tk.Text(scrollable_frame, height=3, width=50)
        self.food_eaten.grid(row=row, column=1, sticky='w', pady=5)
        row += 1
        
        ttk.Label(scrollable_frame, text="What are your concerns with what you are eating?").grid(row=row, column=0, sticky='w', pady=5)
        self.concerns = tk.Text(scrollable_frame, height=3, width=50)
        self.concerns.grid(row=row, column=1, sticky='w', pady=5)
        row += 1
        
        ttk.Label(scrollable_frame, text="Additional Comments:").grid(row=row, column=0, sticky='w', pady=5)
        self.additional_comments = tk.Text(scrollable_frame, height=3, width=50)
        self.additional_comments.grid(row=row, column=1, sticky='w', pady=5)
        row += 1
        
        # Medication questions
        ttk.Label(scrollable_frame, text="Did you take meds to manage symptoms?").grid(row=row, column=0, sticky='w', pady=5)
        meds_frame = ttk.Frame(scrollable_frame)
        meds_frame.grid(row=row, column=1, sticky='w', pady=5)
        ttk.Radiobutton(meds_frame, text="Yes", variable=self.took_meds, value=True).pack(side='left')
        ttk.Radiobutton(meds_frame, text="No", variable=self.took_meds, value=False).pack(side='left')
        row += 1
        
        ttk.Label(scrollable_frame, text="If so, which ones did you take?").grid(row=row, column=0, sticky='w', pady=5)
        med_types_frame = ttk.Frame(scrollable_frame)
        med_types_frame.grid(row=row, column=1, sticky='w', pady=5)
        self.allergy_med = tk.BooleanVar()
        self.anxiety_med = tk.BooleanVar()
        self.other_med = tk.BooleanVar()
        ttk.Checkbutton(med_types_frame, text="Allergy", variable=self.allergy_med).pack(side='left')
        ttk.Checkbutton(med_types_frame, text="Anxiety", variable=self.anxiety_med).pack(side='left')
        ttk.Checkbutton(med_types_frame, text="Other", variable=self.other_med).pack(side='left')
        row += 1
        
        ttk.Label(scrollable_frame, text="Did they help?").grid(row=row, column=0, sticky='w', pady=5)
        helped_frame = ttk.Frame(scrollable_frame)
        helped_frame.grid(row=row, column=1, sticky='w', pady=5)
        ttk.Radiobutton(helped_frame, text="Yes", variable=self.meds_helped, value=True).pack(side='left')
        ttk.Radiobutton(helped_frame, text="No", variable=self.meds_helped, value=False).pack(side='left')
        row += 1
        
        # Submit button
        ttk.Button(scrollable_frame, text="Submit Entry", command=self.submit_entry).grid(row=row, column=0, columnspan=2, pady=20)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def submit_entry(self):
        """Submit the current entry to the database"""
        # Get medication types
        med_types = []
        if self.allergy_med.get():
            med_types.append("Allergy")
        if self.anxiety_med.get():
            med_types.append("Anxiety")
        if self.other_med.get():
            med_types.append("Other")
        
        # Create new entry
        new_entry = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'food_source': self.food_source.get(),
            'eating_location': self.eating_location.get(),
            'anxiety_level': self.anxiety_level.get(),
            'breathing_difficulty': self.breathing_difficulty.get(),
            'swallowing_difficulty': self.swallowing_difficulty.get(),
            'scratchy_throat': self.scratchy_throat.get(),
            'stomach_pain': self.stomach_pain.get(),
            'chest_pain': self.chest_pain.get(),
            'reflux': self.reflux.get(),
            'food_eaten': self.food_eaten.get("1.0", tk.END).strip(),
            'concerns': self.concerns.get("1.0", tk.END).strip(),
            'additional_comments': self.additional_comments.get("1.0", tk.END).strip(),
            'took_meds': self.took_meds.get(),
            'med_types': ', '.join(med_types),
            'meds_helped': self.meds_helped.get()
        }
        
        # Add to dataframe
        self.data = pd.concat([self.data, pd.DataFrame([new_entry])], ignore_index=True)
        self.save_data()
        
        messagebox.showinfo("Success", "Entry submitted successfully!")
        self.clear_form()
    
    def clear_form(self):
        """Clear all form fields"""
        self.food_source.set("Home")
        self.eating_location.set("Home")
        self.anxiety_level.set(0)
        self.breathing_difficulty.set("None")
        self.swallowing_difficulty.set("None")
        self.scratchy_throat.set("None")
        self.stomach_pain.set("None")
        self.chest_pain.set("None")
        self.reflux.set("None")
        self.took_meds.set(False)
        self.meds_helped.set(False)
        self.allergy_med.set(False)
        self.anxiety_med.set(False)
        self.other_med.set(False)
        self.food_eaten.delete("1.0", tk.END)
        self.concerns.delete("1.0", tk.END)
        self.additional_comments.delete("1.0", tk.END)
    
    def create_visualization_tab(self):
        """Create the visualization tab"""
        viz_frame = ttk.Frame(self.notebook)
        self.notebook.add(viz_frame, text="Visualizations")
        
        # Control frame
        control_frame = ttk.Frame(viz_frame)
        control_frame.pack(fill='x', padx=10, pady=10)
        
        # Visualization type selector
        ttk.Label(control_frame, text="Select Visualization:").pack(side='left')
        self.viz_type = tk.StringVar(value="Anxiety Over Time")
        viz_options = ["Anxiety Over Time", "Symptom Severity", "Food Source Analysis", "Medication Effectiveness"]
        ttk.Combobox(control_frame, textvariable=self.viz_type, values=viz_options, state="readonly").pack(side='left', padx=10)
        ttk.Button(control_frame, text="Generate Plot", command=self.generate_plot).pack(side='left', padx=10)
        
        # Plot frame
        self.plot_frame = ttk.Frame(viz_frame)
        self.plot_frame.pack(fill='both', expand=True, padx=10, pady=10)
    
    def severity_to_numeric(self, severity):
        """Convert severity text to numeric value"""
        mapping = {"None": 0, "Mild": 1, "Moderate": 2, "Severe": 3}
        return mapping.get(severity, 0)
    
    def generate_plot(self):
        """Generate the selected visualization"""
        if self.data.empty:
            messagebox.showwarning("No Data", "No data available for visualization. Please enter some data first.")
            return
        
        # Clear previous plot
        for widget in self.plot_frame.winfo_children():
            widget.destroy()
        
        # Convert timestamp to datetime
        if 'timestamp' in self.data.columns:
            self.data['timestamp'] = pd.to_datetime(self.data['timestamp'])
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        viz_type = self.viz_type.get()
        
        if viz_type == "Anxiety Over Time":
            if len(self.data) > 1:
                ax.plot(self.data['timestamp'], self.data['anxiety_level'], marker='o')
                ax.set_title('Anxiety Level Over Time')
                ax.set_xlabel('Time')
                ax.set_ylabel('Anxiety Level (0-10)')
                ax.grid(True, alpha=0.3)
            else:
                ax.text(0.5, 0.5, 'Need at least 2 data points for time series', 
                       ha='center', va='center', transform=ax.transAxes)
        
        elif viz_type == "Symptom Severity":
            symptoms = ['breathing_difficulty', 'swallowing_difficulty', 'scratchy_throat', 
                       'stomach_pain', 'chest_pain', 'reflux']
            
            # Convert severity to numeric and calculate averages
            severity_data = {}
            for symptom in symptoms:
                if symptom in self.data.columns:
                    numeric_values = self.data[symptom].apply(self.severity_to_numeric)
                    severity_data[symptom.replace('_', ' ').title()] = numeric_values.mean()
            
            if severity_data:
                ax.bar(severity_data.keys(), severity_data.values())
                ax.set_title('Average Symptom Severity')
                ax.set_ylabel('Average Severity (0-3)')
                ax.tick_params(axis='x', rotation=45)
        
        elif viz_type == "Food Source Analysis":
            if 'food_source' in self.data.columns and 'anxiety_level' in self.data.columns:
                food_anxiety = self.data.groupby('food_source')['anxiety_level'].mean()
                ax.bar(food_anxiety.index, food_anxiety.values)
                ax.set_title('Average Anxiety by Food Source')
                ax.set_ylabel('Average Anxiety Level')
        
        elif viz_type == "Medication Effectiveness":
            if 'took_meds' in self.data.columns and 'meds_helped' in self.data.columns:
                med_data = self.data[self.data['took_meds'] == True]
                if not med_data.empty:
                    helped_count = med_data['meds_helped'].sum()
                    total_count = len(med_data)
                    effectiveness = helped_count / total_count * 100
                    
                    ax.bar(['Helped', 'Did Not Help'], [effectiveness, 100 - effectiveness])
                    ax.set_title('Medication Effectiveness')
                    ax.set_ylabel('Percentage')
                else:
                    ax.text(0.5, 0.5, 'No medication data available', 
                           ha='center', va='center', transform=ax.transAxes)
        
        plt.tight_layout()
        
        # Embed plot in tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = FoodAnxietyApp(root)
    root.mainloop()