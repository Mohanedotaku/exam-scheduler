# 📘 Surveillance and Examination Management Application

**🗓 Date:** February 24, 2025  

## 📌 Introduction  
This project aims to develop an application for managing surveillance duties and exam scheduling in a school. The application will:  
✅ Automatically calculate teachers' surveillance workload based on their teaching hours.  
✅ Schedule exams for each class.  
✅ Allow teachers to input their availability for surveillance.  

---

## 🎯 Context and Objectives  

### 📍 Context  
The school seeks to automate surveillance and exam management to simplify planning and reduce administrative workload.  

### 🎯 Objectives  
The application should enable:  
- 📊 **Automated calculation** of teachers' surveillance workload.  
- 🗓 **Management of the exam calendar** for each class.  
- 📝 **Teachers to input their availability** for surveillance duties.  

---

## ⚙️ Functional Specifications  

### 👩‍🏫 Teacher Management  
- Each teacher has a weekly teaching workload.  
- The surveillance workload is equal to the teaching workload (e.g., **9 teaching hours = 9 surveillance hours**).  

### 🏫 Exam Management  
- The application must allow **creating an exam schedule** for each class.  
- Necessary information (**subject, class, teachers**) can be imported via an **Excel file** or entered manually.  

### 🔍 Surveillance Management  
- Teachers can **input their availability** (days and time slots).  
- The application must **consider these availabilities** when assigning surveillance duties.  

---

## 🛠 Technical Specifications  

### 💻 Development Environment  
- **Programming language:** Python 🐍  
- **Graphical interface:** Flutter or JavaScript for full-stack hybrid (Electron)  
- **Database:** SQLite or MySQL  

### 📥 Data Import  
- The application must support **importing data from an Excel file** (`.xlsx` format).  
- Required columns: **Subject | Class | Teacher**  

### 📤 Data Export  
- The application must allow exporting **exam schedules and surveillance planning** in **PDF or Excel format**.  

---

## 🚧 Constraints  
- The application must be **easy to use** for teachers and administrative staff.  
- **Data security** must be ensured and accessible **only to authorized personnel**.  

---

## ⏳ Provisional Schedule  

| Phase | Duration |
|--------|----------|
| **Design Phase** | 2 weeks |
| **Development Phase** | 2 weeks |
| **Testing Phase** | 1-2 weeks |
| **Deployment Phase** | 0.5-1 week |

---

## ✅ Conclusion  
This document defines the **main features and constraints** of the **Surveillance and Examination Management Application**. It serves as the foundation for the project's development.  

---

💡 **Feel free to contribute or suggest improvements!** 🚀  
