import pandas as pd
import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
import io

from BusinessLogic.GeneticAlgorithm import GeneticAlgorithm


class ExamSchedulerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Exam Scheduler")
        self.root.geometry("1200x800")
        self.root.configure(bg="#f5f5f5")

        self.teachers_data = None
        self.exams = []
        self.current_schedule = None

        self.create_ui()

    def create_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Style configuration
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TButton', font=('Helvetica', 10), background='#4a7abc')
        style.configure('TLabel', font=('Helvetica', 11))
        style.configure('Header.TLabel', font=('Helvetica', 14, 'bold'))

        # Top section: Data import and basic controls
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 20))

        ttk.Label(top_frame, text="Exam Scheduler", style='Header.TLabel').pack(side=tk.LEFT, padx=5)
        # Add this after the import_btn line in the top_frame section
        import_exams_btn = ttk.Button(top_frame, text="Import Exams CSV", command=self.import_exams_csv)
        import_exams_btn.pack(side=tk.RIGHT, padx=5)
        import_btn = ttk.Button(top_frame, text="Import Teachers CSV", command=self.import_csv)
        import_btn.pack(side=tk.RIGHT, padx=5)

        # Middle section: Split into two parts
        middle_frame = ttk.Frame(main_frame)
        middle_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Left side: Exam creation
        left_frame = ttk.LabelFrame(middle_frame, text="Add New Exam", padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        exam_fields_frame = ttk.Frame(left_frame)
        exam_fields_frame.pack(fill=tk.X, pady=10)

        ttk.Label(exam_fields_frame, text="Exam Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.exam_name_var = tk.StringVar()
        ttk.Entry(exam_fields_frame, textvariable=self.exam_name_var, width=30).grid(row=0, column=1, sticky=tk.W,
                                                                                     pady=5)

        ttk.Label(exam_fields_frame, text="Date (YYYY-MM-DD):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.exam_date_var = tk.StringVar()
        ttk.Entry(exam_fields_frame, textvariable=self.exam_date_var, width=30).grid(row=1, column=1, sticky=tk.W,
                                                                                     pady=5)

        ttk.Label(exam_fields_frame, text="Start Time (HH:MM):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.exam_time_var = tk.StringVar()
        ttk.Entry(exam_fields_frame, textvariable=self.exam_time_var, width=30).grid(row=2, column=1, sticky=tk.W,
                                                                                     pady=5)

        ttk.Label(exam_fields_frame, text="Duration (hours):").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.exam_duration_var = tk.StringVar()
        ttk.Entry(exam_fields_frame, textvariable=self.exam_duration_var, width=30).grid(row=3, column=1, sticky=tk.W,
                                                                                         pady=5)

        ttk.Label(exam_fields_frame, text="Supervisors Needed:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.supervisors_var = tk.StringVar()
        ttk.Entry(exam_fields_frame, textvariable=self.supervisors_var, width=30).grid(row=4, column=1, sticky=tk.W,
                                                                                       pady=5)

        add_exam_btn = ttk.Button(left_frame, text="Add Exam", command=self.add_exam)
        add_exam_btn.pack(pady=10)

        # Exam list
        ttk.Label(left_frame, text="Scheduled Exams:").pack(anchor=tk.W, pady=(10, 5))

        exam_list_frame = ttk.Frame(left_frame)
        exam_list_frame.pack(fill=tk.BOTH, expand=True)

        self.exam_tree = ttk.Treeview(exam_list_frame, columns=("Name", "Date", "Time", "Supervisors"), show="headings",
                                      height=10)
        self.exam_tree.heading("Name", text="Name")
        self.exam_tree.heading("Date", text="Date")
        self.exam_tree.heading("Time", text="Time")
        self.exam_tree.heading("Supervisors", text="Supervisors")

        self.exam_tree.column("Name", width=150)
        self.exam_tree.column("Date", width=100)
        self.exam_tree.column("Time", width=100)
        self.exam_tree.column("Supervisors", width=80)

        self.exam_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(exam_list_frame, orient=tk.VERTICAL, command=self.exam_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.exam_tree.configure(yscrollcommand=scrollbar.set)

        # Right side: Schedule visualization and optimization
        right_frame = ttk.LabelFrame(middle_frame, text="Schedule Visualization", padding=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Matplotlib figure for visualization
        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=right_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Bottom section: Optimization and status
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.X, pady=(20, 0))

        optimize_btn = ttk.Button(bottom_frame, text="Generate Optimal Schedule", command=self.optimize_schedule)
        optimize_btn.pack(side=tk.LEFT, padx=5)

        export_btn = ttk.Button(bottom_frame, text="Export Schedule", command=self.export_schedule)
        export_btn.pack(side=tk.LEFT, padx=5)

        clear_btn = ttk.Button(bottom_frame, text="Clear All", command=self.clear_all)
        clear_btn.pack(side=tk.RIGHT, padx=5)

        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready to import teachers data")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, pady=(20, 0))

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
            # First, read the file as text to determine the actual structure
            with open(filename, 'rb') as f:
                # Try to detect the encoding
                import chardet
                raw_data = f.read()
                result = chardet.detect(raw_data)
                detected_encoding = result['encoding']

                self.status_var.set(f"Detected encoding: {detected_encoding}")

                # Try to read with the detected encoding
                try:
                    # Check for different delimiters
                    for delimiter in [',', ';', '\t']:
                        try:
                            self.teachers_data = pd.read_csv(
                                filename,
                                sep=delimiter,
                                encoding=detected_encoding,
                                engine='python'  # More flexible parsing
                            )

                            # If successful, process the data
                            if 'Nom Et Prénom' not in self.teachers_data.columns:
                                # Try with alternate column names or assume first column is name
                                if len(self.teachers_data.columns) > 0:
                                    self.teachers_data.rename(columns={self.teachers_data.columns[0]: 'Nom Et Prénom'},
                                                              inplace=True)

                            # Create other required columns if missing
                            required_cols = ['Département', 'Grade', 'Cours', 'TD', 'TP', 'coef',
                                             'Nombre de Séances de surveillance']
                            for col in required_cols:
                                if col not in self.teachers_data.columns:
                                    self.teachers_data[col] = 0

                            # Clean up and convert numeric data
                            for col in ['Cours', 'TD', 'TP', 'coef', 'Nombre de Séances de surveillance']:
                                self.teachers_data[col] = pd.to_numeric(self.teachers_data[col],
                                                                        errors='coerce').fillna(0)

                            self.status_var.set(f"Imported {len(self.teachers_data)} teachers from {filename}")
                            return
                        except:
                            continue

                    messagebox.showerror("Import Error", "Could not determine the correct delimiter for this CSV file.")
                    return
                except Exception as e:
                    messagebox.showerror("Import Error", f"Error with {detected_encoding} encoding: {str(e)}")
                    return
        except Exception as e:
            # If all else fails, try a direct approach
            try:
                # Try a simple approach with a flexible engine
                self.teachers_data = pd.DataFrame([
                    {'Nom Et Prénom': f'Enseignant {i + 1}',
                     'Département': '1-INFORMATIQUE',
                     'Grade': 'Ass / Vac',
                     'Cours': 0, 'TD': 0, 'TP': 3, 'coef': 0,
                     'Nombre de Séances de surveillance': 1}
                    for i in range(28)
                ])

                self.status_var.set("Created sample data (CSV import failed)")

                # Create a message suggesting to fix the CSV
                messagebox.showinfo(
                    "Using Sample Data",
                    "Importing the CSV failed. Using sample data instead.\n\n"
                    "To fix your CSV file, try:\n"
                    "1. Opening it in Excel\n"
                    "2. Saving as CSV (comma delimited)\n"
                    "3. Ensuring column names match expected format"
                )
                return
            except Exception as final_e:
                messagebox.showerror("Import Error", f"Final error: {str(final_e)}")
                return

    def prepare_teachers_data(self):
        if self.teachers_data is None:
            return []

        teachers = []
        for idx, row in self.teachers_data.iterrows():
            teacher = {
                'id': idx,
                'name': row['Nom Et Prénom'],
                'department': row['Département'] if 'Département' in row else '',
                'grade': row['Grade'] if 'Grade' in row else '',
                'supervision_capacity': int(
                    row['Nombre de Séances de surveillance']) if 'Nombre de Séances de surveillance' in row else 0
            }
            teachers.append(teacher)

        return teachers

    def add_exam(self):
        try:
            name = self.exam_name_var.get().strip()
            date_str = self.exam_date_var.get().strip()
            time_str = self.exam_time_var.get().strip()
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
                name,
                date_obj.strftime("%Y-%m-%d"),
                time_obj.strftime("%H:%M"),
                supervisors_needed
            ))

            # Clear form
            self.exam_name_var.set("")
            self.exam_date_var.set("")
            self.exam_time_var.set("")
            self.exam_duration_var.set("")
            self.supervisors_var.set("")

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

        # Prepare teachers data
        teachers = self.prepare_teachers_data()

        # Run genetic algorithm
        self.status_var.set("Optimizing schedule... This may take a moment.")
        self.root.update()

        ga = GeneticAlgorithm(teachers, self.exams)
        best_solution = ga.evolve()

        # Apply solution to exams
        for exam_id, assigned_teachers in best_solution.items():
            exam = next(e for e in self.exams if e['id'] == exam_id)
            exam['assigned_teachers'] = assigned_teachers

        self.current_schedule = best_solution

        # Update visualization
        self.update_visualization()

        # Update status
        self.status_var.set("Schedule optimization complete")

        # Show detailed assignment
        self.show_assignment_details()

    def update_visualization(self):
        self.ax.clear()

        if not self.exams:
            self.canvas.draw()
            return

        # Create a Gantt chart of exams
        exam_names = [f"{exam['name']} ({len(exam['assigned_teachers'])}/{exam['supervisors_needed']})" for exam in
                      self.exams]
        start_dates = [exam['date'] for exam in self.exams]
        durations = [datetime.timedelta(hours=exam['duration']) for exam in self.exams]
        end_dates = [start + duration for start, duration in zip(start_dates, durations)]

        # Sort by date
        sorted_data = sorted(zip(exam_names, start_dates, end_dates), key=lambda x: x[1])
        exam_names, start_dates, end_dates = zip(*sorted_data)

        # Plot the chart
        self.ax.barh(range(len(exam_names)),
                     [(end - start).total_seconds() / 3600 for start, end in zip(start_dates, end_dates)],
                     left=[mdates.date2num(start) for start in start_dates],
                     height=0.5,
                     align='center',
                     color='#4a7abc',
                     alpha=0.8)

        # Format the plot
        self.ax.set_yticks(range(len(exam_names)))
        self.ax.set_yticklabels(exam_names)
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
        self.fig.autofmt_xdate()
        self.ax.set_xlabel('Date and Time')
        self.ax.set_title('Exam Schedule')
        self.ax.grid(True, alpha=0.3)

        self.canvas.draw()

    def show_assignment_details(self):
        if not self.current_schedule:
            return

        details_window = tk.Toplevel(self.root)
        details_window.title("Assignment Details")
        details_window.geometry("800x600")

        # Create a frame for the treeview
        frame = ttk.Frame(details_window, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        # Create treeview
        columns = ("Exam", "Date", "Time", "Teacher", "Department", "Weekly Supervisions")
        tree = ttk.Treeview(frame, columns=columns, show="headings")

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)

        # Get teacher details
        teachers = self.prepare_teachers_data()
        teacher_dict = {t['id']: t for t in teachers}

        # Add data
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

                    tree.insert("", tk.END, values=(
                        exam['name'],
                        exam_date.strftime("%Y-%m-%d"),
                        exam_date.strftime("%H:%M"),
                        teacher['name'],
                        teacher['department'],
                        f"{weekly_count}/{teacher['supervision_capacity']}"
                    ))

        # Add scrollbar
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        # Pack everything
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Add close button
        close_btn = ttk.Button(details_window, text="Close", command=details_window.destroy)
        close_btn.pack(pady=10)

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
                            'Department': teacher['department'],
                            'Grade': teacher['grade'],
                            'Supervision Capacity': teacher['supervision_capacity']
                        })

            # Create DataFrame and export
            df = pd.DataFrame(export_data)
            df.to_csv(filename, index=False, encoding='utf-8')

            self.status_var.set(f"Schedule exported to {filename}")

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

            self.exam_name_var.set("")
            self.exam_date_var.set("")
            self.exam_time_var.set("")
            self.exam_duration_var.set("")
            self.supervisors_var.set("")

            # Clear visualization
            self.ax.clear()
            self.canvas.draw()

            self.status_var.set("All data cleared")