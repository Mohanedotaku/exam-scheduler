import tkinter as tk

from UI.ExamSchedulerApp import ExamSchedulerApp


def main():
    root = tk.Tk()
    ExamSchedulerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
