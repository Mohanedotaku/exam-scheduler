Specifications Document
Surveillance and Examination Management Application
February 24, 2025

1. Introduction
This specifications document aims to define the functional and technical requirements of a surveillance and examination management application for a school. The application will automatically manage teachers’ surveillance workload based on their teaching hours and schedule exams for each class.

2. Context and Objectives
2.1 Context
The school wishes to automate the management of surveillance and exams to facilitate planning and reduce administrative workload.

2.2 Objectives
The application should allow:
— Automatic calculation of teachers’ surveillance workload based on their teaching hours.
— Management of the exam schedule for each class.
— Teachers to enter their availability for surveillance duties.

3. Functional Specifications
3.1 Teacher Management
— Each teacher has a weekly teaching workload.
— The surveillance workload is equal to the teaching workload (e.g., 9 teaching hours = 9 surveillance hours).

3.2 Exam Management
— The application must allow the creation of an exam schedule for each class.
— Necessary information (subject, class, teachers) can be imported via an Excel file or entered manually.

3.3 Surveillance Management
— Teachers can enter their availability for surveillance (days and time slots).
— The application must take these availabilities into account when assigning surveillance duties.

4. Technical Specifications
4.1 Development Environment
— Programming language: Python
— Graphical interface: Flutter or JavaScript for full-stack hybrid (Electron)
— Database: SQLite or MySQL

4.2 Data Import
— The application must be able to import data from an Excel file (.xlsx format).
— The data must be structured with the following columns: Subject, Class, Teacher.

4.3 Data Export
— The application must allow exporting the exam schedule and surveillance planning in PDF or Excel format.

5. Constraints
— The application must be easy to use for teachers and administrative staff.
— Data must be secure and accessible only to authorized personnel.

6. Provisional Schedule
— Design phase: 2 weeks
— Development phase: 2 weeks
— Testing phase: 1 to 2 weeks
— Deployment phase: 0.5 to 1 week

7. Conclusion
This specifications document defines the main features and constraints of the surveillance and examination management application. It will serve as a basis for project development.
