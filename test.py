import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from datetime import datetime
import json

# ---------------------- MODEL ----------------------
class Topic:
    def __init__(self, id, name, category, mastery, last_review_date):
        self.id = id
        self.name = name
        self.category = category
        self.mastery = mastery
        self.last_review_date = last_review_date

    def days_since_review(self):
        try:
            date_obj = datetime.strptime(self.last_review_date, "%Y-%m-%d")
            return (datetime.now() - date_obj).days
        except:
            return 0

    def get_priority(self):
        return (100 - self.mastery) + (self.days_since_review() * 2)


# ---------------------- CONTROLLER ----------------------
class StudyManager:
    def __init__(self):
        self.topics = []

    def generate_id(self):
        return f"MIMR-T{len(self.topics)+1:03d}"

    def add_topic(self, name, category, mastery, date):
        topic = Topic(self.generate_id(), name, category, mastery, date)
        self.topics.append(topic)

    def remove_topic(self, index):
        if 0 <= index < len(self.topics):
            self.topics.pop(index)

    def generate_queue(self):
        return sorted(self.topics, key=lambda t: t.get_priority(), reverse=True)

    def save(self, filename):
        data = {}
        for t in self.topics:
            data[t.id] = {
                "name": t.name,
                "category": t.category,
                "mastery": t.mastery,
                "last_review_date": t.last_review_date
            }
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)

    def load(self, filename):
        try:
            with open(filename, "r") as f:
                data = json.load(f)
            self.topics = []
            for id, val in data.items():
                self.topics.append(
                    Topic(id, val["name"], val["category"],
                          val["mastery"], val["last_review_date"])
                )
        except FileNotFoundError:
            self.topics = []


# ---------------------- VIEW (GUI) ----------------------


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("MIMR System")

        # Apply theme
        style = ttk.Style()
        style.theme_use("clam")

        self.manager = StudyManager()
        self.manager.load("data.json")

        # ---------------- FRAMES ----------------
        input_frame = ttk.Frame(root, padding=10)
        input_frame.grid(row=0, column=0, sticky="n")

        table_frame = ttk.Frame(root, padding=10)
        table_frame.grid(row=0, column=1)

        button_frame = ttk.Frame(root, padding=10)
        button_frame.grid(row=1, column=0, columnspan=2)

        # ---------------- INPUTS ----------------
        ttk.Label(input_frame, text="Name").grid(row=0, column=0, sticky="w")
        ttk.Label(input_frame, text="Category").grid(row=1, column=0, sticky="w")
        ttk.Label(input_frame, text="Mastery").grid(row=2, column=0, sticky="w")
        ttk.Label(input_frame, text="Date (YYYY-MM-DD)").grid(row=3, column=0, sticky="w")

        self.name_entry = ttk.Entry(input_frame)
        self.category_entry = ttk.Entry(input_frame)
        self.mastery_entry = ttk.Entry(input_frame)
        self.date_entry = ttk.Entry(input_frame)

        self.name_entry.grid(row=0, column=1, pady=5)
        self.category_entry.grid(row=1, column=1, pady=5)
        self.mastery_entry.grid(row=2, column=1, pady=5)
        self.date_entry.grid(row=3, column=1, pady=5)

        # ---------------- BUTTONS ----------------
        ttk.Button(button_frame, text="Add Topic", command=self.add_topic).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Remove Selected", command=self.remove_topic).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Show Priority", command=self.show_queue).grid(row=0, column=2, padx=5)
        ttk.Button(button_frame, text="Show All", command=self.refresh_table).grid(row=0, column=3, padx=5)

        # ---------------- TABLE (Treeview) ----------------
        self.tree = ttk.Treeview(
            table_frame,
            columns=("Name", "Category", "Mastery"),
            show="headings",
            height=10
        )

        self.tree.heading("Name", text="Name")
        self.tree.heading("Category", text="Category")
        self.tree.heading("Mastery", text="Mastery")

        self.tree.column("Name", width=120)
        self.tree.column("Category", width=100)
        self.tree.column("Mastery", width=80)

        self.tree.pack()

        self.refresh_table()

    # ---------------- METHODS ----------------

    def add_topic(self):
        try:
            name = self.name_entry.get()
            category = self.category_entry.get()
            mastery = int(self.mastery_entry.get())
            date = self.date_entry.get()

            if not name or not category or not date:
                raise ValueError

            self.manager.add_topic(name, category, mastery, date)
            self.manager.save("data.json")

            self.refresh_table()
            self.clear_inputs()

        except:
            messagebox.showerror("Error", "Invalid input!")

    def remove_topic(self):
        selected = self.tree.selection()
        if selected:
            index = self.tree.index(selected[0])
            self.manager.remove_topic(index)
            self.manager.save("data.json")
            self.refresh_table()

    def refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        for t in self.manager.topics:
            self.tree.insert("", "end", values=(t.name, t.category, f"{t.mastery}%"))

    def show_queue(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        queue = self.manager.generate_queue()
        for t in queue:
            self.tree.insert("", "end", values=(t.name, "Priority", t.get_priority()))

    def clear_inputs(self):
        self.name_entry.delete(0, tk.END)
        self.category_entry.delete(0, tk.END)
        self.mastery_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)


# ---------------------- MAIN ----------------------
def main():
    root = tk.Tk()
    app = App(root)
    root.mainloop()

if __name__ == "__main__":
    main()