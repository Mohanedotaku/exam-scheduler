
import pandas as pd
import numpy as np
import random
import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mates

from matplotlib import cm
import matplotlib.pyplot as plt
from tkcalendar import DateEntry  # For date picker
import os
import threading  # For running optimization in background thread

from BusinessLogic.GeneticAlgorithm import GeneticAlgorithm


class ExamSchedulerAppNew:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Exam Scheduler")
        self.root.geometry("1280x800")
        self.root.configure(bg="#f0f0f0")

        # Set default icon if available
        try:
            if os.path.exists("icons/app_icon.ico"):
                self.root.iconbitmap("icons/app_icon.ico")
        except:
            pass

        self.teachers_data = None
        self.exams = []
        self.current_schedule = None
        self.optimization_in_progress = False

        # GA parameters with defaults
        self.ga_params = {
            'population_size': 50,
            'generations': 100,
            'mutation_rate': 0.1,
            'elite_size': 5
        }

        self.create_ui()

    def create_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Style configuration - use a more modern theme
        style = ttk.Style()
        available_themes = style.theme_names()
        if 'azure' in available_themes:
            style.theme_use('azure')
        elif 'vista' in available_themes:
            style.theme_use('vista')
        else:
            style.theme_use('clam')  # Fallback

        # Configure styles for different components
        style.configure('TButton', font=('Segoe UI', 10), padding=6)
        style.configure('TLabel', font=('Segoe UI', 11))
        style.configure('Header.TLabel', font=('Segoe UI', 16, 'bold'))
        style.configure('Title.TLabel', font=('Segoe UI', 12, 'bold'))
        style.configure('Important.TButton', font=('Segoe UI', 10, 'bold'))
        style.configure('TFrame', background='#f5f5f5')
        style.configure('TLabelframe', background='#f5f5f5')
        style.configure('TLabelframe.Label', font=('Segoe UI', 11, 'bold'))

        # Add a notebook (tabbed interface)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(10, 20))

        # Create tabs
        self.data_tab = ttk.Frame(self.notebook, padding=10)
        self.schedule_tab = ttk.Frame(self.notebook, padding=10)
        self.settings_tab = ttk.Frame(self.notebook, padding=10)
        self.help_tab = ttk.Frame(self.notebook, padding=10)

        self.notebook.add(self.data_tab, text="Data Management")
        self.notebook.add(self.schedule_tab, text="Schedule Visualization")
        self.notebook.add(self.settings_tab, text="Settings")
        self.notebook.add(self.help_tab, text="Help")

        # Create content for each tab
        self.create_data_tab()
        self.create_schedule_tab()
        self.create_settings_tab()
        self.create_help_tab()

        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready to import teachers data")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, pady=(5, 0))

    def create_data_tab(self):
        # Top section: Data import controls
        top_frame = ttk.Frame(self.data_tab)
        top_frame.pack(fill=tk.X, pady=(0, 20))

        ttk.Label(top_frame, text="Data Management", style='Header.TLabel').pack(side=tk.LEFT, padx=5)

        import_exams_btn = ttk.Button(top_frame, text="Import Exams CSV", command=self.import_exams_csv)
        import_exams_btn.pack(side=tk.RIGHT, padx=5)

        import_btn = ttk.Button(top_frame, text="Import Teachers CSV", command=self.import_csv)
        import_btn.pack(side=tk.RIGHT, padx=5)

        # Middle section: Split into two parts
        middle_frame = ttk.Frame(self.data_tab)
        middle_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Left side: Exam creation
        left_frame = ttk.LabelFrame(middle_frame, text="Add New Exam", padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Improved exam fields with better input controls
        exam_fields_frame = ttk.Frame(left_frame)
        exam_fields_frame.pack(fill=tk.X, pady=10)

        ttk.Label(exam_fields_frame, text="Exam Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.exam_name_var = tk.StringVar()
        ttk.Entry(exam_fields_frame, textvariable=self.exam_name_var, width=30).grid(row=0, column=1, sticky=tk.W,
                                                                                     pady=5)

        ttk.Label(exam_fields_frame, text="Date:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.exam_date_var = tk.StringVar()

        # Date picker widget instead of text entry
        date_frame = ttk.Frame(exam_fields_frame)
        date_frame.grid(row=1, column=1, sticky=tk.W, pady=5)

        try:
            # Use DateEntry if available
            self.date_picker = DateEntry(date_frame, width=17, background='darkblue',
                                         foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd',
                                         textvariable=self.exam_date_var)
            self.date_picker.pack(side=tk.LEFT)
        except:
            # Fallback to regular entry
            ttk.Entry(date_frame, textvariable=self.exam_date_var, width=30).pack(side=tk.LEFT)
            ttk.Label(date_frame, text=" (YYYY-MM-DD)", foreground="gray").pack(side=tk.LEFT)

        ttk.Label(exam_fields_frame, text="Start Time:").grid(row=2, column=0, sticky=tk.W, pady=5)

        # Time picker using spinboxes
        time_frame = ttk.Frame(exam_fields_frame)
        time_frame.grid(row=2, column=1, sticky=tk.W, pady=5)

        self.hour_var = tk.StringVar(value="08")
        self.minute_var = tk.StringVar(value="00")

        hour_spinner = ttk.Spinbox(time_frame, from_=0, to=23, width=3, format="%02.0f", textvariable=self.hour_var)
        hour_spinner.pack(side=tk.LEFT)

        ttk.Label(time_frame, text=":").pack(side=tk.LEFT)

        minute_spinner = ttk.Spinbox(time_frame, from_=0, to=59, width=3, format="%02.0f", textvariable=self.minute_var)
        minute_spinner.pack(side=tk.LEFT)

        # Combined time variable for compatibility
        self.exam_time_var = tk.StringVar()

        # Duration
        ttk.Label(exam_fields_frame, text="Duration (hours):").grid(row=3, column=0, sticky=tk.W, pady=5)

        duration_frame = ttk.Frame(exam_fields_frame)
        duration_frame.grid(row=3, column=1, sticky=tk.W, pady=5)

        self.exam_duration_var = tk.StringVar(value="2")
        duration_spinner = ttk.Spinbox(duration_frame, from_=1, to=8, width=3, textvariable=self.exam_duration_var)
        duration_spinner.pack(side=tk.LEFT)

        # Supervisors
        ttk.Label(exam_fields_frame, text="Supervisors Needed:").grid(row=4, column=0, sticky=tk.W, pady=5)

        supervisors_frame = ttk.Frame(exam_fields_frame)
        supervisors_frame.grid(row=4, column=1, sticky=tk.W, pady=5)

        self.supervisors_var = tk.StringVar(value="2")
        supervisors_spinner = ttk.Spinbox(supervisors_frame, from_=1, to=10, width=3, textvariable=self.supervisors_var)
        supervisors_spinner.pack(side=tk.LEFT)

        # Buttons for exam management
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(pady=10)

        add_exam_btn = ttk.Button(button_frame, text="Add Exam", command=self.add_exam, style='Important.TButton')
        add_exam_btn.pack(side=tk.LEFT, padx=5)

        edit_exam_btn = ttk.Button(button_frame, text="Edit Selected", command=self.edit_exam)
        edit_exam_btn.pack(side=tk.LEFT, padx=5)

        delete_exam_btn = ttk.Button(button_frame, text="Delete Selected", command=self.delete_exam)
        delete_exam_btn.pack(side=tk.LEFT, padx=5)

        # Exam list
        ttk.Label(left_frame, text="Scheduled Exams:", style='Title.TLabel').pack(anchor=tk.W, pady=(10, 5))

        exam_list_frame = ttk.Frame(left_frame)
        exam_list_frame.pack(fill=tk.BOTH, expand=True)

        # Enhanced treeview with ID column for easier selection
        self.exam_tree = ttk.Treeview(exam_list_frame,
                                      columns=("ID", "Name", "Date", "Time", "Duration", "Supervisors"),
                                      show="headings", height=10)
        self.exam_tree.heading("ID", text="ID")
        self.exam_tree.heading("Name", text="Name")
        self.exam_tree.heading("Date", text="Date")
        self.exam_tree.heading("Time", text="Time")
        self.exam_tree.heading("Duration", text="Duration (h)")
        self.exam_tree.heading("Supervisors", text="Supervisors")

        self.exam_tree.column("ID", width=40)
        self.exam_tree.column("Name", width=150)
        self.exam_tree.column("Date", width=100)
        self.exam_tree.column("Time", width=80)
        self.exam_tree.column("Duration", width=80)
        self.exam_tree.column("Supervisors", width=80)

        self.exam_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(exam_list_frame, orient=tk.VERTICAL, command=self.exam_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.exam_tree.configure(yscrollcommand=scrollbar.set)

        # Double-click to edit
        self.exam_tree.bind("<Double-1>", lambda event: self.edit_exam())

        # Right side: Teachers data and button controls
        right_frame = ttk.LabelFrame(middle_frame, text="Teacher Management", padding=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Show info about teachers if loaded
        self.teachers_info_text = tk.Text(right_frame, height=10, width=40, wrap=tk.WORD)
        self.teachers_info_text.pack(fill=tk.BOTH, expand=True, pady=10)
        self.teachers_info_text.insert(tk.END,
                                       "No teacher data loaded yet.\n\nPlease use the 'Import Teachers CSV' button to load teacher data.")
        self.teachers_info_text.config(state=tk.DISABLED)

        # Bottom controls
        bottom_frame = ttk.Frame(self.data_tab)
        bottom_frame.pack(fill=tk.X, pady=(10, 0))

        optimize_btn = ttk.Button(bottom_frame, text="Generate Optimal Schedule",
                                  command=self.optimize_schedule, style='Important.TButton')
        optimize_btn.pack(side=tk.LEFT, padx=5)

        export_btn = ttk.Button(bottom_frame, text="Export Schedule", command=self.export_schedule)
        export_btn.pack(side=tk.LEFT, padx=5)

        clear_btn = ttk.Button(bottom_frame, text="Clear All Data", command=self.clear_all)
        clear_btn.pack(side=tk.RIGHT, padx=5)

    def create_schedule_tab(self):
        # Top controls
        top_frame = ttk.Frame(self.schedule_tab)
        top_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(top_frame, text="Schedule Visualization", style='Header.TLabel').pack(side=tk.LEFT, padx=5)

        # Visualization options
        ttk.Label(top_frame, text="View:").pack(side=tk.RIGHT, padx=(0, 5))
        self.view_var = tk.StringVar(value="timeline")
        view_combo = ttk.Combobox(top_frame, textvariable=self.view_var, width=15,
                                  values=["Timeline", "Calendar", "Teacher Load"])
        view_combo.pack(side=tk.RIGHT, padx=5)
        view_combo.bind("<<ComboboxSelected>>", lambda e: self.update_visualization())

        refresh_btn = ttk.Button(top_frame, text="Refresh View", command=self.update_visualization)
        refresh_btn.pack(side=tk.RIGHT, padx=5)

        # Visualization frame
        viz_frame = ttk.Frame(self.schedule_tab)
        viz_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Matplotlib figure for visualization with better sizing
        self.fig = Figure(figsize=(8, 6), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=viz_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Add toolbar
        from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
        toolbar_frame = ttk.Frame(self.schedule_tab)
        toolbar_frame.pack(fill=tk.X)
        toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        toolbar.update()

        # Bottom controls
        bottom_frame = ttk.Frame(self.schedule_tab)
        bottom_frame.pack(fill=tk.X, pady=(10, 0))

        details_btn = ttk.Button(bottom_frame, text="Show Assignment Details", command=self.show_assignment_details)
        details_btn.pack(side=tk.LEFT, padx=5)

        export_viz_btn = ttk.Button(bottom_frame, text="Export Visualization", command=self.export_visualization)
        export_viz_btn.pack(side=tk.LEFT, padx=5)

    def create_settings_tab(self):
        # Main frame
        settings_frame = ttk.Frame(self.settings_tab)
        settings_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        ttk.Label(settings_frame, text="Genetic Algorithm Parameters", style='Header.TLabel').pack(anchor=tk.W,
                                                                                                   pady=(0, 20))

        # Parameters grid
        params_frame = ttk.Frame(settings_frame)
        params_frame.pack(fill=tk.X, pady=10)

        # Population size
        ttk.Label(params_frame, text="Population Size:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.population_var = tk.StringVar(value=str(self.ga_params['population_size']))
        ttk.Spinbox(params_frame, from_=10, to=200, width=5, textvariable=self.population_var).grid(row=0, column=1,
                                                                                                    sticky=tk.W, pady=5)
        ttk.Label(params_frame, text="Higher values may give better results but take longer to compute").grid(row=0,
                                                                                                              column=2,
                                                                                                              sticky=tk.W,
                                                                                                              padx=10)

        # Generations
        ttk.Label(params_frame, text="Generations:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.generations_var = tk.StringVar(value=str(self.ga_params['generations']))
        ttk.Spinbox(params_frame, from_=10, to=500, width=5, textvariable=self.generations_var).grid(row=1, column=1,
                                                                                                     sticky=tk.W,
                                                                                                     pady=5)
        ttk.Label(params_frame, text="More generations allow for better optimization but increase runtime").grid(row=1,
                                                                                                                 column=2,
                                                                                                                 sticky=tk.W,
                                                                                                                 padx=10)

        # Mutation rate
        ttk.Label(params_frame, text="Mutation Rate:").grid(row=2, column=0, sticky=tk.W, pady=5)
        mutation_frame = ttk.Frame(params_frame)
        mutation_frame.grid(row=2, column=1, sticky=tk.W, pady=5)

        self.mutation_var = tk.StringVar(value=str(self.ga_params['mutation_rate']))
        mutation_spinner = ttk.Spinbox(mutation_frame, from_=0.01, to=0.5, increment=0.01, width=5, format="%.2f",
                                       textvariable=self.mutation_var)
        mutation_spinner.pack()
        ttk.Label(params_frame, text="Controls diversity in solutions (0.01-0.5)").grid(row=2, column=2, sticky=tk.W,
                                                                                        padx=10)

        # Elite size
        ttk.Label(params_frame, text="Elite Size:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.elite_var = tk.StringVar(value=str(self.ga_params['elite_size']))
        ttk.Spinbox(params_frame, from_=1, to=20, width=5, textvariable=self.elite_var).grid(row=3, column=1,
                                                                                             sticky=tk.W, pady=5)
        ttk.Label(params_frame, text="Number of best solutions to preserve between generations").grid(row=3, column=2,
                                                                                                      sticky=tk.W,
                                                                                                      padx=10)

        # Save button
        save_frame = ttk.Frame(settings_frame)
        save_frame.pack(pady=20)

        save_btn = ttk.Button(save_frame, text="Save Settings", command=self.save_settings)
        save_btn.pack()

        # Separator
        ttk.Separator(settings_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=20)

        # Application settings
        ttk.Label(settings_frame, text="Application Settings", style='Title.TLabel').pack(anchor=tk.W, pady=(0, 10))

        app_settings_frame = ttk.Frame(settings_frame)
        app_settings_frame.pack(fill=tk.X, pady=10)

        # Theme selection
        ttk.Label(app_settings_frame, text="Theme:").grid(row=0, column=0, sticky=tk.W, pady=5)

        style = ttk.Style()
        self.theme_var = tk.StringVar(value=style.theme_use())
        theme_combo = ttk.Combobox(app_settings_frame, textvariable=self.theme_var, width=15,
                                   values=list(style.theme_names()))
        theme_combo.grid(row=0, column=1, sticky=tk.W, pady=5)
        theme_combo.bind("<<ComboboxSelected>>", lambda e: style.theme_use(self.theme_var.get()))

    def create_help_tab(self):
        # Main frame
        help_frame = ttk.Frame(self.help_tab)
        help_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        ttk.Label(help_frame, text="How to Use the Exam Scheduler", style='Header.TLabel').pack(anchor=tk.W,
                                                                                                pady=(0, 20))

        # Help text with instructions
        help_text = tk.Text(help_frame, wrap=tk.WORD, height=20, width=80)
        help_text.pack(fill=tk.BOTH, expand=True)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(help_text, orient=tk.VERTICAL, command=help_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        help_text.configure(yscrollcommand=scrollbar.set)

        help_content = """Welcome to the Advanced Exam Scheduler!

This application helps you create optimal exam supervision schedules by assigning teachers to exams using a genetic algorithm.

Step-by-step instructions:

1. Data Management Tab:
   - Import teacher data using the "Import Teachers CSV" button
   - Import existing exams or add them manually using the form
   - Review and edit exams as needed

2. Settings Tab:
   - Adjust genetic algorithm parameters if needed
   - Customize application appearance

3. Generate Schedule:
   - Once all data is in place, click "Generate Optimal Schedule" to run the optimization
   - The algorithm will assign teachers to exams based on their availability and supervision capacity

4. Visualization Tab:
   - View the schedule in different formats: Timeline, Calendar, or Teacher Load
   - Use the navigation toolbar to zoom, pan, or save the visualization

5. Export:
   - Export the complete schedule for distribution

Tips:
- Make sure your CSV files follow the expected format
- The genetic algorithm parameters can significantly affect optimization quality and time
- Higher population sizes and generation counts provide better results but take longer
- You can adjust mutation rate to control diversity in solutions

For questions and support, please contact the development team.
"""
        help_text.insert(tk.END, help_content)
        help_text.config(state=tk.DISABLED)

        # Bottom section with buttons for quick actions
        bottom_frame = ttk.Frame(help_frame)
        bottom_frame.pack(fill=tk.X, pady=(20, 0))

        data_help_btn = ttk.Button(bottom_frame, text="CSV Format Guide", command=self.show_csv_format_guide)
        data_help_btn.pack(side=tk.LEFT, padx=5)

        about_btn = ttk.Button(bottom_frame, text="About", command=self.show_about)
        about_btn.pack(side=tk.RIGHT, padx=5)

    def edit_exam(self):
        selected_item = self.exam_tree.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select an exam to edit")
            return

        # Get the exam ID from the tree
        exam_id = int(self.exam_tree.item(selected_item, "values")[0])

        # Find the exam in our data
        exam = next((e for e in self.exams if e['id'] == exam_id), None)
        if not exam:
            return

        # Set the form values for editing
        self.exam_name_var.set(exam['name'])
        self.exam_date_var.set(exam['date'].strftime("%Y-%m-%d"))

        # Set the time separately for spinners
        self.hour_var.set(f"{exam['date'].hour:02d}")
        self.minute_var.set(f"{exam['date'].minute:02d}")

        self.exam_duration_var.set(str(exam['duration']))
        self.supervisors_var.set(str(exam['supervisors_needed']))

        # Ask for confirmation
        if messagebox.askyesno("Edit Exam", "Update this exam with the form values after editing?"):
            # Delete this exam
            self.exams = [e for e in self.exams if e['id'] != exam_id]

            # Remove from treeview
            self.exam_tree.delete(selected_item[0])

            # Add the exam back with the updated values by calling add_exam
            self.add_exam()

            self.status_var.set(f"Exam updated: {exam['name']}")

    def delete_exam(self):
        selected_item = self.exam_tree.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select an exam to delete")
            return

        exam_id = int(self.exam_tree.item(selected_item, "values")[0])
        exam = next((e for e in self.exams if e['id'] == exam_id), None)

        if not exam:
            return

        if messagebox.askyesno("Delete Exam", f"Are you sure you want to delete the exam: {exam['name']}?"):
            # Remove from our data
            self.exams = [e for e in self.exams if e['id'] != exam_id]

            # Remove from treeview
            self.exam_tree.delete(selected_item[0])

            # Update status
            self.status_var.set(f"Deleted exam: {exam['name']}")

            # Update visualization
            self.update_visualization()

    def import_exams_csv(self):
        filename = filedialog.askopenfilename(
            title="Select Exams CSV file",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )

        if not filename:
            return

        try:
            # Try different encodings and delimiters
            encodings = ['utf-8', 'latin1', 'cp1252', 'iso-8859-1', 'utf-8-sig']
            delimiters = [',', ';', '\t']

            success = False

            for encoding in encodings:
                if success:
                    break

                for delimiter in delimiters:
                    try:
                        exams_data = pd.read_csv(filename, sep=delimiter, encoding=encoding)

                        # Check if the dataframe has the required columns
                        required_cols = ['name', 'date', 'time', 'duration', 'supervisors_needed']
                        if not all(col in exams_data.columns for col in required_cols):
                            continue

                        # Process the exams
                        for _, row in exams_data.iterrows():
                            try:
                                name = str(row['name']).strip()
                                date_str = str(row['date']).strip()
                                time_str = str(row['time']).strip()
                                duration = float(row['duration'])
                                supervisors_needed = int(row['supervisors_needed'])

                                # Parse date and time
                                date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
                                time_obj = datetime.datetime.strptime(time_str, "%H:%M").time()
                                datetime_obj = datetime.datetime.combine(date_obj, time_obj)

                                # Create exam object
                                exam = {
                                    'id': len(self.exams),
                                    'name': name,
                                    'date': datetime_obj,
                                    'duration': duration,
                                    'supervisors_needed': supervisors_needed,
                                    'assigned_teachers': []
                                }

                                self.exams.append(exam)

                                # Update UI
                                self.exam_tree.insert("", tk.END, values=(
                                    name,
                                    date_obj.strftime("%Y-%m-%d"),
                                    time_obj.strftime("%H:%M"),
                                    supervisors_needed
                                ))
                            except Exception as e:
                                print(f"Error processing exam row: {e}")
                                continue

                        # Update status and visualization
                        self.status_var.set(f"Imported {len(exams_data)} exams from {filename}")
                        self.update_visualization()
                        success = True
                        break

                    except Exception as e:
                        continue

            if not success:
                messagebox.showerror("Import Error",
                                     "Could not import exams from the CSV file. Please check the format.")

        except Exception as e:
            messagebox.showerror("Import Error", f"Error importing exams: {str(e)}")

    def import_csv(self):
        filename = filedialog.askopenfilename(
            title="Select Teachers CSV file",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )

        if not filename:
            return

        try:
            # Try different encodings and delimiters
            encodings = ['utf-8', 'latin1', 'cp1252', 'iso-8859-1', 'utf-8-sig']
            delimiters = [',', ';', '\t']

            success = False

            for encoding in encodings:
                if success:
                    break

                for delimiter in delimiters:
                    try:
                        self.teachers_data = pd.read_csv(filename, sep=delimiter, encoding=encoding,engine='python')

                        # Check if the dataframe has the required column
                        if 'Nom Et Prénom' in self.teachers_data.columns:
                            success = True
                            break
                    except:
                        continue

            if not success:
                messagebox.showerror("Import Error",
                                     "Could not import data from the CSV file. Please check the format.")
                return

            # Update status
            self.status_var.set(f"Imported {len(self.teachers_data)} teachers from {filename}")

            # Update the teacher info display
            if hasattr(self, 'teachers_info_text'):
                self.teachers_info_text.config(state=tk.NORMAL)
                self.teachers_info_text.delete(1.0, tk.END)

                # Create a summary of the loaded data
                total_teachers = len(self.teachers_data)
                departments = {}
                total_capacity = 0

                for _, row in self.teachers_data.iterrows():
                    # Handle NaN values safely
                    dept = row.get('Département', 'Unknown') if 'Département' in row else 'Unknown'
                    if pd.isna(dept):
                        dept = 'Unknown'

                    if dept not in departments:
                        departments[dept] = 0
                    departments[dept] += 1

                    # Safely convert capacity to int with NaN handling
                    capacity = row.get('Nombre de Séances de surveillance', 0)
                    if pd.isna(capacity):
                        capacity = 0
                    else:
                        try:
                            capacity = int(capacity)
                        except (ValueError, TypeError):
                            capacity = 0

                    total_capacity += capacity

                summary = f"Loaded {total_teachers} teachers with total supervision capacity: {total_capacity}\n\n"
                summary += "Teachers by department:\n"

                for dept, count in sorted(departments.items()):
                    summary += f"- {dept}: {count} teachers\n"

                summary += "\nFirst 10 teachers:\n"
                for i, (_, row) in enumerate(self.teachers_data.iterrows()):
                    if i >= 10:
                        break

                    name = row['Nom Et Prénom']
                    dept = row.get('Département', '') if 'Département' in row else ''
                    if pd.isna(dept):
                        dept = ''

                    # Safely handle capacity
                    capacity = row.get('Nombre de Séances de surveillance', 0)
                    if pd.isna(capacity):
                        capacity = 0
                    else:
                        try:
                            capacity = int(capacity)
                        except (ValueError, TypeError):
                            capacity = 0

                    summary += f"- {name} ({dept}): {capacity} supervisions\n"

                self.teachers_info_text.insert(tk.END, summary)
                self.teachers_info_text.config(state=tk.DISABLED)
        except Exception as e:
            messagebox.showerror("Import Error", f"Error importing data: {str(e)}")
            # Print detailed error for debugging
            import traceback
            print(f"Detailed error: {traceback.format_exc()}")

    def prepare_teachers_data(self):
        if self.teachers_data is None:
            return []

        teachers = []
        for idx, row in self.teachers_data.iterrows():
            try:
                # Handle NaN values safely
                supervision_capacity = row.get('Nombre de Séances de surveillance', 0)
                if pd.isna(supervision_capacity):
                    supervision_capacity = 0
                else:
                    supervision_capacity = int(supervision_capacity)

                department = row.get('Département', '')
                if pd.isna(department):
                    department = ''

                grade = row.get('Grade', '')
                if pd.isna(grade):
                    grade = ''

                teacher = {
                    'id': idx,
                    'name': row['Nom Et Prénom'],
                    'department': department,
                    'grade': grade,
                    'supervision_capacity': supervision_capacity
                }
                teachers.append(teacher)
            except Exception as e:
                print(f"Error processing teacher data row {idx}: {e}")
                continue

        return teachers

    def add_exam(self):
        try:
            name = self.exam_name_var.get().strip()
            date_str = self.exam_date_var.get().strip()

            # Get time from hour and minute spinners
            hour = int(self.hour_var.get())
            minute = int(self.minute_var.get())
            time_str = f"{hour:02d}:{minute:02d}"

            # Update the time_var for compatibility with other methods
            self.exam_time_var.set(time_str)

            duration_str = self.exam_duration_var.get().strip()
            supervisors_str = self.supervisors_var.get().strip()

            if not (name and date_str and time_str and duration_str and supervisors_str):
                messagebox.showwarning("Missing Information", "All fields are required")
                return

            # Parse date and time
            date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            time_obj = datetime.datetime.strptime(time_str, "%H:%M").time()
            datetime_obj = datetime.datetime.combine(date_obj, time_obj)
            duration = float(duration_str)
            supervisors_needed = int(supervisors_str)

            # Create exam object
            exam = {
                'id': len(self.exams),
                'name': name,
                'date': datetime_obj,
                'duration': duration,
                'supervisors_needed': supervisors_needed,
                'assigned_teachers': []  # Will be filled by the algorithm
            }

            self.exams.append(exam)

            # Update UI
            self.exam_tree.insert("", tk.END, values=(
                exam['id'],
                name,
                date_obj.strftime("%Y-%m-%d"),
                time_obj.strftime("%H:%M"),
                duration,
                supervisors_needed
            ))

            # Clear form
            self.exam_name_var.set("")
            self.exam_date_var.set("")
            self.hour_var.set("08")
            self.minute_var.set("00")
            self.exam_duration_var.set("2")
            self.supervisors_var.set("2")

            # Update status
            self.status_var.set(f"Added exam: {name}")

            # Update visualization
            self.update_visualization()

        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid input: {str(e)}")

    def optimize_schedule(self):
        if not self.exams:
            messagebox.showwarning("No Exams", "Please add some exams first")
            return

        if self.teachers_data is None:
            messagebox.showwarning("No Teachers", "Please import teachers data first")
            return

        # Get GA parameters from settings
        try:
            population_size = int(self.population_var.get())
            generations = int(self.generations_var.get())
            mutation_rate = float(self.mutation_var.get())
            elite_size = int(self.elite_var.get())

            self.ga_params = {
                'population_size': population_size,
                'generations': generations,
                'mutation_rate': mutation_rate,
                'elite_size': elite_size
            }
        except (ValueError, AttributeError):
            # Use defaults if settings tab not created yet or invalid values
            pass

        # Prepare teachers data
        teachers = self.prepare_teachers_data()

        # Create a progress dialog
        progress_window = tk.Toplevel(self.root)
        progress_window.title("Optimizing Schedule")
        progress_window.geometry("400x150")
        progress_window.transient(self.root)
        progress_window.grab_set()

        ttk.Label(progress_window, text="Running genetic algorithm optimization...",
                  padding=10).pack()

        # Add a progress bar
        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(progress_window, variable=progress_var, maximum=100)
        progress_bar.pack(fill=tk.X, padx=20, pady=10)

        status_label = ttk.Label(progress_window, text="Initializing...")
        status_label.pack(pady=5)

        cancel_btn = ttk.Button(progress_window, text="Cancel", command=progress_window.destroy)
        cancel_btn.pack(pady=10)

        # Status update
        self.status_var.set("Optimizing schedule...")

        # Function to run the optimization in a separate thread
        def run_optimization():
            # Run genetic algorithm with our specified parameters
            ga = GeneticAlgorithm(
                teachers,
                self.exams,
                population_size=self.ga_params['population_size'],
                generations=self.ga_params['generations'],
                mutation_rate=self.ga_params['mutation_rate'],
                elite_size=self.ga_params['elite_size']
            )

            # Store original evolve method to restore it later
            original_evolve = ga.evolve

            # Track progress through generations
            total_generations = self.ga_params['generations']
            best_solution = None

            try:
                # Create initial population
                population = ga.create_initial_population()

                for generation in range(ga.generations):
                    # Check if progress window was closed (user canceled)
                    if not progress_window.winfo_exists():
                        return

                    # Calculate fitness for population
                    fitness_scores = [ga.fitness(chrom) for chrom in population]

                    # Update progress display
                    progress = (generation / total_generations) * 100
                    progress_var.set(progress)
                    status_label.config(
                        text=f"Generation {generation}/{total_generations} - Best Fitness: {max(fitness_scores):.2f}")
                    progress_window.update()

                    # Select parents
                    parents = ga.select_parents(population, fitness_scores)

                    # Create new population
                    new_population = []

                    # Keep elite chromosomes
                    elite_indices = np.argsort(fitness_scores)[-ga.elite_size:]
                    for idx in elite_indices:
                        new_population.append(population[idx])

                    # Create offspring
                    while len(new_population) < ga.population_size:
                        parent1, parent2 = random.sample(parents, 2)
                        child = ga.crossover(parent1, parent2)
                        child = ga.mutate(child)
                        new_population.append(child)

                    population = new_population

                # Get final best solution
                fitness_scores = [ga.fitness(chrom) for chrom in population]
                best_idx = np.argmax(fitness_scores)
                best_solution = population[best_idx]

                # Apply solution to exams
                if best_solution:
                    for exam_id, assigned_teachers in best_solution.items():
                        exam = next(e for e in self.exams if e['id'] == exam_id)
                        exam['assigned_teachers'] = assigned_teachers

                    self.current_schedule = best_solution

            except Exception as e:
                messagebox.showerror("Optimization Error", f"An error occurred during optimization: {str(e)}")
                if progress_window.winfo_exists():
                    progress_window.destroy()
                return

            # Finish up on the main thread
            self.root.after(100, lambda: self.finish_optimization(progress_window))

        # Start the optimization thread
        threading.Thread(target=run_optimization, daemon=True).start()

    def finish_optimization(self, progress_window):
        # Close the progress window if still open
        if progress_window.winfo_exists():
            progress_window.destroy()

        # Update visualization
        self.update_visualization()

        # Update status
        self.status_var.set("Schedule optimization complete")

        # Show detailed assignment
        self.show_assignment_details()

        # Switch to visualization tab
        if hasattr(self, 'notebook') and hasattr(self, 'schedule_tab'):
            self.notebook.select(self.schedule_tab)

    def show_assignment_details(self):
        if not self.current_schedule:
            return

        details_window = tk.Toplevel(self.root)
        details_window.title("Assignment Details")
        details_window.geometry("900x600")

        # Create a frame for the treeview
        frame = ttk.Frame(details_window, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        # Create treeview with improved columns
        columns = ("Exam", "Date", "Time", "Teacher", "Department", "Grade", "Weekly Supervisions")
        tree = ttk.Treeview(frame, columns=columns, show="headings")

        # Configure columns with better sizing
        tree.heading("Exam", text="Exam")
        tree.heading("Date", text="Date")
        tree.heading("Time", text="Time")
        tree.heading("Teacher", text="Teacher")
        tree.heading("Department", text="Department")
        tree.heading("Grade", text="Grade")
        tree.heading("Weekly Supervisions", text="Weekly Load")

        tree.column("Exam", width=200)
        tree.column("Date", width=100)
        tree.column("Time", width=80)
        tree.column("Teacher", width=180)
        tree.column("Department", width=150)
        tree.column("Grade", width=100)
        tree.column("Weekly Supervisions", width=100)

        # Get teacher details
        teachers = self.prepare_teachers_data()
        teacher_dict = {t['id']: t for t in teachers}

        # Add data with alternating row colors
        row_tags = ("even", "odd")
        row_idx = 0

        for exam in self.exams:
            exam_date = exam['date']
            week_num = exam_date.isocalendar()[1]

            for teacher_id in exam.get('assigned_teachers', []):
                if teacher_id in teacher_dict:
                    teacher = teacher_dict[teacher_id]

                    # Count weekly supervisions for this teacher
                    weekly_count = sum(1 for e in self.exams
                                       if e['date'].isocalendar()[1] == week_num
                                       and teacher_id in e.get('assigned_teachers', []))

                    tag = row_tags[row_idx % 2]
                    tree.insert("", tk.END, values=(
                        exam['name'],
                        exam_date.strftime("%Y-%m-%d"),
                        exam_date.strftime("%H:%M"),
                        teacher['name'],
                        teacher.get('department', ''),
                        teacher.get('grade', ''),
                        f"{weekly_count}/{teacher['supervision_capacity']}"
                    ), tags=(tag,))
                    row_idx += 1

        # Configure row colors
        tree.tag_configure("even", background="#f0f0f0")
        tree.tag_configure("odd", background="white")

        # Add scrollbar
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        # Pack everything
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Add export button
        bottom_frame = ttk.Frame(details_window, padding=10)
        bottom_frame.pack(fill=tk.X)

        export_btn = ttk.Button(bottom_frame, text="Export to CSV", command=self.export_schedule)
        export_btn.pack(side=tk.LEFT, padx=5)

        close_btn = ttk.Button(bottom_frame, text="Close", command=details_window.destroy)
        close_btn.pack(side=tk.RIGHT, padx=5)

    def export_schedule(self):
        if not self.current_schedule:
            messagebox.showwarning("No Schedule", "Please generate a schedule first")
            return

        filename = filedialog.asksaveasfilename(
            title="Export Schedule",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )

        if not filename:
            return

        try:
            # Prepare data for export
            export_data = []
            teachers = self.prepare_teachers_data()
            teacher_dict = {t['id']: t for t in teachers}

            for exam in self.exams:
                exam_date = exam['date']
                for teacher_id in exam.get('assigned_teachers', []):
                    if teacher_id in teacher_dict:
                        teacher = teacher_dict[teacher_id]
                        export_data.append({
                            'Exam': exam['name'],
                            'Date': exam_date.strftime("%Y-%m-%d"),
                            'Time': exam_date.strftime("%H:%M"),
                            'Duration': exam['duration'],
                            'Teacher': teacher['name'],
                            'Department': teacher.get('department', ''),
                            'Grade': teacher.get('grade', ''),
                            'Supervision Capacity': teacher['supervision_capacity']
                        })

            # Create DataFrame and export
            df = pd.DataFrame(export_data)
            df.to_csv(filename, index=False, encoding='utf-8')

            self.status_var.set(f"Schedule exported to {filename}")
            messagebox.showinfo("Export Successful", f"Schedule has been exported to {filename}")

        except Exception as e:
            messagebox.showerror("Export Error", f"Error exporting schedule: {str(e)}")

    def clear_all(self):
        if messagebox.askyesno("Clear All", "Are you sure you want to clear all data?"):
            self.teachers_data = None
            self.exams = []
            self.current_schedule = None

            # Clear UI
            for item in self.exam_tree.get_children():
                self.exam_tree.delete(item)

            # Clear form fields
            self.exam_name_var.set("")
            self.exam_date_var.set("")
            self.hour_var.set("08")
            self.minute_var.set("00")
            self.exam_duration_var.set("2")
            self.supervisors_var.set("2")

            # Clear teacher info
            if hasattr(self, 'teachers_info_text'):
                self.teachers_info_text.config(state=tk.NORMAL)
                self.teachers_info_text.delete(1.0, tk.END)
                self.teachers_info_text.insert(tk.END,
                                               "No teacher data loaded yet.\n\nPlease use the 'Import Teachers CSV' button to load teacher data.")
                self.teachers_info_text.config(state=tk.DISABLED)

            # Clear visualization
            self.ax.clear()
            self.canvas.draw()

            self.status_var.set("All data cleared")

    def update_visualization(self):
        self.ax.clear()

        if not self.exams:
            self.canvas.draw()
            return

        # Get the current view type
        view_type = self.view_var.get().lower() if hasattr(self, 'view_var') else "timeline"

        if view_type == "timeline" or view_type == "":
            self.create_timeline_view()
        elif view_type == "calendar":
            self.create_calendar_view()
        elif view_type == "teacher load":
            self.create_teacher_load_view()
        else:
            self.create_timeline_view()  # Default

        self.canvas.draw()

    def create_timeline_view(self):
        # Create an enhanced Gantt chart of exams with better colors
        exam_names = [f"{exam['name']} ({len(exam.get('assigned_teachers', []))}/"
                      f"{exam['supervisors_needed']})" for exam in self.exams]
        start_dates = [exam['date'] for exam in self.exams]
        durations = [datetime.timedelta(hours=exam['duration']) for exam in self.exams]
        end_dates = [start + duration for start, duration in zip(start_dates, durations)]

        # Sort by date
        sorted_data = sorted(zip(exam_names, start_dates, end_dates, self.exams), key=lambda x: x[1])
        exam_names, start_dates, end_dates, sorted_exams = zip(*sorted_data)

        # Create colormap based on coverage ratio
        coverage_ratios = [len(exam.get('assigned_teachers', [])) / max(1, exam['supervisors_needed'])
                           for exam in sorted_exams]
        colors = [cm.RdYlGn(min(1.0, ratio)) for ratio in coverage_ratios]

        # Plot the chart with enhanced styling
        bars = self.ax.barh(range(len(exam_names)),
                            [(end - start).total_seconds() / 3600 for start, end in zip(start_dates, end_dates)],
                            left=[mates.date2num(start) for start in start_dates],
                            height=0.6,
                            align='center',
                            color=colors,
                            alpha=0.8,
                            edgecolor='black',
                            linewidth=0.5)

        # Add text labels showing assigned teachers count
        for i, bar in enumerate(bars):
            assigned = len(sorted_exams[i].get('assigned_teachers', []))
            needed = sorted_exams[i]['supervisors_needed']
            if assigned < needed:
                color = 'red'
            else:
                color = 'green'

            self.ax.text(bar.get_x() + bar.get_width() / 2,
                         bar.get_y() + bar.get_height() / 2,
                         f"{assigned}/{needed}",
                         ha='center',
                         va='center',
                         color='black',
                         fontweight='bold')

        # Format the plot
        self.ax.set_yticks(range(len(exam_names)))
        self.ax.set_yticklabels(exam_names)
        self.ax.xaxis.set_major_formatter(mates.DateFormatter('%Y-%m-%d %H:%M'))
        self.fig.autofmt_xdate()
        self.ax.set_xlabel('Date and Time')
        self.ax.set_title('Exam Schedule Timeline')
        self.ax.grid(True, alpha=0.3)

        # Add a legend for the coverage colors
        sm = plt.cm.ScalarMappable(cmap=cm.RdYlGn, norm=plt.Normalize(0, 1))
        sm.set_array([])
        cbar = self.fig.colorbar(sm, ax=self.ax)
        cbar.set_label('Teacher Assignment Coverage')

    def create_calendar_view(self):
        # Group exams by day and create a calendar-like view
        if not self.exams:
            return

        # Find min and max dates to determine calendar range
        dates = [exam['date'].date() for exam in self.exams]
        min_date = min(dates)
        max_date = max(dates)

        # Get all unique dates with exams
        unique_dates = sorted(set(dates))

        # Create a calendar-style plot
        self.ax.clear()

        # Set up the grid for days
        day_count = len(unique_dates)

        # If too many days, maybe show a different view or paginate
        if day_count > 14:
            # Just show first 14 days and add a note
            unique_dates = unique_dates[:14]
            self.ax.set_title(f'Exam Calendar (showing first 14 days of {day_count} total)')
        else:
            self.ax.set_title('Exam Calendar')

        day_count = len(unique_dates)

        # For each date, gather all exams
        y_positions = []
        x_positions = []
        labels = []
        colors = []

        for day_idx, date in enumerate(unique_dates):
            # Get exams on this day
            day_exams = [e for e in self.exams if e['date'].date() == date]

            # Sort by time
            day_exams.sort(key=lambda e: e['date'].time())

            for i, exam in enumerate(day_exams):
                x_positions.append(day_idx)
                # Position down the day based on time
                hour = exam['date'].hour + exam['date'].minute / 60
                y_positions.append(-hour)  # Negative so earlier times are at the top

                # Create a label with time and name
                time_str = exam['date'].strftime("%H:%M")
                name = exam['name']
                assigned = len(exam.get('assigned_teachers', []))
                needed = exam['supervisors_needed']
                labels.append(f"{time_str} - {name} ({assigned}/{needed})")

                # Color based on coverage
                coverage = assigned / max(1, needed)
                colors.append(cm.RdYlGn(min(1.0, coverage)))

        # Create a scatter plot with boxes
        self.ax.scatter(x_positions, y_positions, s=1)  # Tiny dots just to establish coordinates

        # Add text boxes for each exam
        for i in range(len(labels)):
            self.ax.text(x_positions[i], y_positions[i], labels[i],
                         ha='center', va='center',
                         bbox=dict(boxstyle='round,pad=0.5', facecolor=colors[i],
                                   alpha=0.8, edgecolor='black', linewidth=0.5))

        # Configure the plot
        self.ax.set_xticks(range(day_count))
        self.ax.set_xticklabels([d.strftime("%a %d %b") for d in unique_dates], rotation=45)

        # Set y-axis to represent hours (8am to 8pm common exam hours)
        self.ax.set_yticks([-h for h in range(8, 21)])
        self.ax.set_yticklabels([f"{h:02d}:00" for h in range(8, 21)])

        self.ax.set_ylabel('Time')
        self.ax.grid(True, alpha=0.3, linestyle='--')

        # Adjust layout for rotated labels
        self.fig.tight_layout()

    def create_teacher_load_view(self):
        if not self.exams or not hasattr(self, 'teachers_data') or self.teachers_data is None:
            self.ax.set_title("No data to display")
            return

        # Get all teachers and their assignments
        teachers = self.prepare_teachers_data()
        teacher_dict = {t['id']: t for t in teachers}

        # Count assignments per teacher
        teacher_assignments = {}
        weekly_assignments = {}

        for exam in self.exams:
            week_num = exam['date'].isocalendar()[1]

            for teacher_id in exam.get('assigned_teachers', []):
                if teacher_id not in teacher_assignments:
                    teacher_assignments[teacher_id] = 0
                    weekly_assignments[teacher_id] = {}

                teacher_assignments[teacher_id] += 1

                if week_num not in weekly_assignments[teacher_id]:
                    weekly_assignments[teacher_id][week_num] = 0

                weekly_assignments[teacher_id][week_num] += 1

        # Prepare data for plotting
        teacher_names = []
        assignment_counts = []
        capacities = []
        weekly_overloads = []

        for teacher_id, count in teacher_assignments.items():
            if teacher_id in teacher_dict:
                teacher = teacher_dict[teacher_id]
                teacher_names.append(teacher['name'][:20])  # Truncate long names
                assignment_counts.append(count)
                capacities.append(teacher['supervision_capacity'])

                # Check if any week exceeds capacity
                overloaded = any(weekly_count > teacher['supervision_capacity']
                                 for weekly_count in weekly_assignments[teacher_id].values())
                weekly_overloads.append(overloaded)

        # Sort by assignment count
        sorted_data = sorted(zip(teacher_names, assignment_counts, capacities, weekly_overloads),
                             key=lambda x: x[1], reverse=True)
        if sorted_data:
            teacher_names, assignment_counts, capacities, weekly_overloads = zip(*sorted_data)
        else:
            self.ax.set_title("No teacher assignments to display")
            return

        # Create bar chart
        x = range(len(teacher_names))

        # Assignment bars
        assignment_bars = self.ax.bar(x, assignment_counts, width=0.6, alpha=0.7, label='Assignments')

        # Capacity line
        self.ax.plot(x, capacities, 'r--', label='Weekly Capacity')

        # Highlight overloaded teachers
        overload_colors = ['red' if overloaded else 'green' for overloaded in weekly_overloads]
        for i, bar in enumerate(assignment_bars):
            bar.set_color(overload_colors[i])

        # Format plot
        self.ax.set_ylabel('Number of Supervisions')
        self.ax.set_title('Teacher Supervision Load')
        self.ax.set_xticks(x)
        self.ax.set_xticklabels(teacher_names, rotation=45, ha='right')
        self.ax.legend()

        # Add text labels above bars
        for i, bar in enumerate(assignment_bars):
            self.ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1,
                         f"{assignment_counts[i]}/{capacities[i]}",
                         ha='center', va='bottom')

        # Adjust layout
        self.fig.tight_layout()

    def export_visualization(self):
        if not self.exams:
            messagebox.showwarning("No Data", "There is no schedule to export")
            return

        filename = filedialog.asksaveasfilename(
            title="Save Visualization",
            filetypes=[
                ("PNG Image", "*.png"),
                ("PDF Document", "*.pdf"),
                ("SVG Image", "*.svg"),
                ("JPEG Image", "*.jpg"),
                ("All Files", "*.*")
            ],
            defaultextension=".png"
        )

        if not filename:
            return

        try:
            self.fig.savefig(filename, dpi=300, bbox_inches='tight')
            self.status_var.set(f"Visualization saved to {filename}")
            messagebox.showinfo("Export Successful", f"Visualization has been saved to {filename}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Error saving visualization: {str(e)}")

    def save_settings(self):
        try:
            # Update GA parameters
            self.ga_params['population_size'] = int(self.population_var.get())
            self.ga_params['generations'] = int(self.generations_var.get())
            self.ga_params['mutation_rate'] = float(self.mutation_var.get())
            self.ga_params['elite_size'] = int(self.elite_var.get())

            # Apply theme change
            style = ttk.Style()
            style.theme_use(self.theme_var.get())

            self.status_var.set("Settings updated successfully")
            messagebox.showinfo("Settings Saved", "Your settings have been saved and applied")

        except ValueError as e:
            messagebox.showerror("Invalid Input", f"Please check your settings values: {str(e)}")

    def show_csv_format_guide(self):
        guide_window = tk.Toplevel(self.root)
        guide_window.title("CSV Format Guide")
        guide_window.geometry("600x400")

        guide_frame = ttk.Frame(guide_window, padding=20)
        guide_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(guide_frame, text="CSV File Format Guide", style='Header.TLabel').pack(anchor=tk.W, pady=(0, 10))

        text = tk.Text(guide_frame, wrap=tk.WORD, height=15, width=70)
        text.pack(fill=tk.BOTH, expand=True)

        text.insert(tk.END, """Teachers CSV Format:
The teachers CSV file should contain the following columns:
- "Nom Et Prénom": Teacher's full name
- "Département": Department or faculty (optional)
- "Grade": Academic grade or rank (optional)
- "Nombre de Séances de surveillance": Maximum weekly supervision capacity

Example:
Nom Et Prénom,Département,Grade,Nombre de Séances de surveillance
John Smith,Computer Science,Professor,3
Jane Doe,Mathematics,Associate Professor,2

-----------------------------------------------------------

Exams CSV Format:
The exams CSV file should contain the following columns:
- "name": Name of the exam
- "date": Date in YYYY-MM-DD format
- "time": Time in HH:MM format
- "duration": Duration in hours (e.g., 2.5 for 2.5 hours)
- "supervisors_needed": Number of supervisors needed

Example:
name,date,time,duration,supervisors_needed
Database Fundamentals,2023-05-15,09:00,2,2
Algorithms,2023-05-16,14:00,3,3
""")

        text.config(state=tk.DISABLED)

        close_btn = ttk.Button(guide_frame, text="Close", command=guide_window.destroy)
        close_btn.pack(pady=10)

    def show_about(self):
        about_window = tk.Toplevel(self.root)
        about_window.title("About")
        about_window.geometry("400x300")

        about_frame = ttk.Frame(about_window, padding=20)
        about_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(about_frame, text="Advanced Exam Scheduler", style='Header.TLabel').pack(pady=(0, 5))
        ttk.Label(about_frame, text="Version 2.0").pack(pady=(0, 20))

        ttk.Label(about_frame, text="""This application helps educational institutions create optimal 
exam supervision schedules using genetic algorithms.

Developed as part of a project for scheduling optimization.

Copyright © 2023 - All Rights Reserved.""", justify=tk.CENTER).pack()

        close_btn = ttk.Button(about_frame, text="Close", command=about_window.destroy)
        close_btn.pack(pady=20)