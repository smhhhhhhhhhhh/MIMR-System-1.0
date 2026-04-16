"""
Mastery-Informed Memory Retention (MIMR) System
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json

# MAIN FUNCTION
def main():
    app = Application()
    app.mainloop()

# BACKEND LOGIC
class Topic:
    # Topic attributes
    def __init__(self, id: str, name: str, category: str, mastery: int, difficulty: int, last_review_date: str) -> None:
        self.id = id
        self.name = name
        self.category = category
        self.mastery = mastery
        self.difficulty = difficulty
        self.last_review_date = last_review_date

    # Days elapsed value
    def days_since_review(self) -> int:
        try:
            date_datetime: datetime = datetime.strptime(self.last_review_date, "%Y-%m-%d")
            last_review_timedelta = datetime.now() - date_datetime
            return last_review_timedelta.days
        except ValueError:
            return 0

    # Topic priority computation
    def get_priority(self) -> float:
        days_elapsed: int = max(self.days_since_review(), 1)
        priority: float = (self.difficulty*days_elapsed) / (self.mastery + 1)
        return priority

    # Threshold for when a topic is considered "finished" or no longer needed
    def is_recent(self, threshold: int = 14) -> bool:
        return self.days_since_review() <= threshold

# CLASS TOPIC CONTAINER
class StudyManager:
    def __init__(self):
        self.topics: list[Topic] = []

    # Naming convention
    def generate_id(self) -> str:
        existing_numbers: list[int] = [
            int(t.id.split("T")[1])
            for t in self.topics
            if "T" in t.id
        ]
        next_number: int = max(existing_numbers, default=0) + 1
        return f"MIMR-T{next_number:03d}"

    # Topic addition
    def add_topic(self, name: str, category: str, mastery: int, difficulty: int, last_review_date: str) -> None:
        new_id: str = self.generate_id()
        topic: Topic = Topic(new_id, name, category, mastery, difficulty, last_review_date)
        self.topics.append(topic)

    # Review queue generation
    def generate_queue(self, limit: int = 10) -> list[Topic]:
        eligible_topics: list[Topic] = [
            t for t in self.topics
            if t.is_recent(60)
        ]

        sorted_topics: list[Topic] = sorted(
            eligible_topics,
            key=lambda x: x.get_priority(),
            reverse=True
        )

        return sorted_topics[:limit]

    # Group topics by category
    def group_by_category(self) -> dict:
        groups = {}
        for t in self.topics:
            groups.setdefault(t.category, []).append(t)
        return groups

    # Get analytics information
    def get_analysis(self, threshold=50) -> dict:
        groups: dict = self.group_by_category()
        result = {}

        for category, topics in groups.items():
            avg: float = sum(t.mastery for t in topics) / len(topics)
            below: int = len([t for t in topics if t.mastery < threshold])

            result[category] = {
                "avg_mastery": round(avg, 2),
                "below_threshold": below,
            }
        return result

    # Count categories below threshold
    def count_weak_categories(self, threshold=50) -> int:
        analysis: dict = self.get_analysis()
        if not analysis:
            return 0
        return len([cat for cat, data in analysis.items()
                    if data["avg_mastery"] < threshold])

    # List categories below threshold
    def get_weak_categories(self, threshold=50) -> list:
        analysis: dict = self.get_analysis()
        if not analysis:
            return []
        return[cat for cat, data in analysis.items()
                    if data["avg_mastery"] < threshold]

    # Weakest category
    def get_weakest_category(self) -> str:
        analysis: dict = self.get_analysis()
        if not analysis:
            return ""
        return min(analysis.items(),key=lambda x:
                    x[1]["avg_mastery"])[0]

    # Mastery updating
    def update_mastery(self, topic_id: str, new_mastery: int) -> bool:
        for topic in self.topics:
            if topic.id == topic_id:
                topic.mastery = new_mastery
                topic.last_review_date = datetime.now().strftime("%Y-%m-%d")
                return True
        return False

    # JSON save
    def save_to_json(self, filename: str) -> None:
        topic_dict = {}
        for topic in self.topics:
            topic_dict[topic.id] = {
                'name': topic.name,
                'category': topic.category,
                'mastery': topic.mastery,
                'difficulty': topic.difficulty,
                'last_review_date': topic.last_review_date
            }

        with open(filename, 'w') as file:
            json.dump(topic_dict, file, indent=4)

    # JSON load
    def load_from_json(self, filename: str) -> None:
        self.topics = []
        try:
            with open(filename, 'r') as file:
                well = json.load(file)
            for key, value in well.items():
                topic: Topic = Topic(key, value['name'], value['category'], value['mastery'], value['difficulty'], value['last_review_date'])
                self.topics.append(topic)

        except FileNotFoundError:
            self.topics = []


# STYLING
class AppStyle:
    # Color palette
    BG = "#1e1e1e"
    FG = "#d4d4d4"
    ACCENT = "#3c3c3c"
    BUTTON_BG = "#2d2d2d"
    BUTTON_ACTIVE = "#4a4a4a"
    FONT = ("Consolas", 11)
    FONT_TITLE = ("Consolas", 18, "bold")

    @staticmethod
    def apply(root: tk.Tk):
        root.configure(bg=AppStyle.BG)

        style = ttk.Style(root)
        style.theme_use("clam")

        style.configure("TFrame", background=AppStyle.BG)
        style.configure("TLabel", background=AppStyle.BG, foreground=AppStyle.FG, font=AppStyle.FONT)
        style.configure("TButton",
                        background=AppStyle.BUTTON_BG,
                        foreground=AppStyle.FG,
                        font=AppStyle.FONT,
                        relief="flat",
                        padding=6)
        style.map("TButton",
                  background=[("active", AppStyle.BUTTON_ACTIVE)],
                  foreground=[("active", AppStyle.FG)])

# GUI LOGIC
class Application(tk.Tk):
    def __init__(self):
        super().__init__()

        self.manager = StudyManager()
        self.filename = "well.json"

        self.manager.load_from_json(self.filename)

        self.title("MIMR System")
        self.geometry("600x600")
        AppStyle.apply(self)

    # Container for frames
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)
        container.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)

        self.frames = {}

        for F in (MainMenu, AddTopic, ReviewQueue, Analytics):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(MainMenu)

        self.protocol("WM_DELETE_WINDOW", self.save_and_exit)

    # Frame switching
    def show_frame(self, frame):
        next_frame = self.frames[frame]
        next_frame.tkraise()

        if hasattr(next_frame, "refresh"):
            next_frame.refresh()

    # Save to json and close application
    def save_and_exit(self):
        self.manager.save_to_json(self.filename)
        self.destroy()

# MAIN MENU FRAME
class MainMenu(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        ttk.Label(self, text="Main Menu", font=("Arial", 18)).pack(anchor="center",pady=10)

        ttk.Button(self, text="Add Topic",
                   command=lambda: controller.show_frame(AddTopic)).pack(fill="both", pady=5, padx=200)
        ttk.Button(self, text="Review Queue",
                   command=lambda: controller.show_frame(ReviewQueue)).pack(fill="both", pady=5, padx=200)
        ttk.Button(self, text="Analytics",
                   command=lambda: controller.show_frame(Analytics)).pack(fill="both", pady=5, padx=200)
        ttk.Button(self, text="Save & Exit",
                   command=lambda: controller.save_and_exit()).pack(fill="both", pady=5, padx=200)


# ADD TOPIC FRAME
class AddTopic(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.entries = {}

        self.fields = [
            ("Topic Name", "e.g. Linked Lists, Algebraic Substitution"),
            ("Category", "e.g. Data Structures and Algorithms, Integral Calculus"),
            ("Mastery", "1-100"),
            ("Difficulty", "1-5")
        ]

        self.build_ui()
        self.bind("<Return>", lambda e: self.add_topic())

    # Initialize the Add Topic UI
    def build_ui(self):
        self.columnconfigure(1, weight=1)
        self.rowconfigure(len(self.fields)+1, weight=1)

        for row, (label_text, placeholder) in enumerate(self.fields):
            ttk.Label(self, text=label_text).grid(row=row, column=0, sticky="w", padx=10, pady=5)
            entry = ttk.Entry(self, foreground="grey")
            entry.insert(0, placeholder)

            entry.bind("<FocusIn>", lambda e, ph=placeholder: self.clear_placeholder(e, ph))
            entry.bind("<FocusOut>", lambda e, ph=placeholder: self.restore_placeholder(e, ph))

            entry.grid(row=row, column=1, sticky="ew", padx=10, pady=5)
            self.entries[label_text] = entry

        ttk.Button(self, text="Add Topic", command=self.add_topic).grid(row=len(self.fields),
                                                                        column=0, columnspan=2,
                                                                        pady=10)
        ttk.Button(self, text="Main Menu", command=lambda: self.controller.show_frame(MainMenu)).grid(row=len(self.fields)+2,
                                                                                                      column=0, padx=5, pady=5,
                                                                                                      columnspan=2, sticky="ew")

    # Clear placeholder if it is still there upon entry selection
    def clear_placeholder(self, event, placeholder):
        if event.widget.get() == placeholder:
            event.widget.delete(0, tk.END)
            event.widget.config(foreground="black")
    # Restore placeholder if entry is empty once out of focus
    def restore_placeholder(self, event, placeholder):
        if not event.widget.get():
            event.widget.insert(0, placeholder)
            event.widget.config(foreground="grey")

    # Add topic if entry input matches key
    def add_topic(self):
        raw = {}

        for key, entry in self.entries.items():
            raw[key] = entry.get().strip()

        if any(v == "" for v in raw.values()):
            messagebox.showwarning("Missing Fields", "Please fill in all fields.")
            return

        try:
            mastery = int(raw["Mastery"])
            difficulty = int(raw["Difficulty"])
        except ValueError:
            messagebox.showwarning("Invalid Input", "Mastery must be 1-100, and Difficulty must be 1-5.")
            return

        self.controller.manager.add_topic(
                                          raw["Topic Name"],
                                          raw["Category"],
                                          mastery,
                                          difficulty,
                                          datetime.now().strftime("%Y-%m-%d")
        )
        messagebox.showinfo("Success", f"'{raw['Topic Name']}' has been added!")
        self.reset_fields()

    # After calling add_topic, clear all entries
    def reset_fields(self):
        for (label, placeholder), entry in zip(self.fields, self.entries.values()):
            entry.delete(0, tk.END)
            entry.insert(0, placeholder)
            entry.config(foreground="grey")

# REVIEW QUEUE FRAME
class ReviewQueue(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.columnconfigure(1, weight=1)

        ttk.Label(self, justify="center", text="Review Queue", font=("Arial", 18)).grid(row=0, column=0, sticky="nsew")

        self.mastery_entry = ttk.Entry(self)
        self.mastery_entry.grid(row=1, rowspan=2, column=0)
        self.mastery_entry.bind("<Return>", lambda e: self.update_selected())
        ttk.Button(self, text="Update Mastery", command=self.update_selected).grid(row=2, column=0)

        self.listbox = tk.Listbox(self)
        self.listbox.grid(row=0, rowspan=3, column=1, padx=10, pady=10, sticky="nsew")

        ttk.Button(self, text="Main Menu",
                   command=lambda: controller.show_frame(MainMenu)).grid(row=3, column=0,
                                                                         padx=5, pady=5,
                                                                         columnspan=2, sticky="ew")

    # Clear listbox and insert queue
    def refresh(self):
        topics: list[Topic] = self.controller.manager.generate_queue()
        self.current_topics = topics
        self.listbox.delete(0, tk.END)

        if not topics:
            self.listbox.insert(tk.END, "No topics to review currently.")
            return

        for t in topics:
            display = f"{t.name} | Mastery: {t.mastery} Difficulty: {t.difficulty} | Priority: {t.get_priority():.2f}"
            self.listbox.insert(tk.END, display)

    # Update mastery of selected topic
    def update_selected(self):
        selection = self.listbox.curselection()

        if not selection:
            return

        index = selection[0]
        selected_topic = self.current_topics[index]

        try:
            new_mastery = int(self.mastery_entry.get())
        except ValueError:
            return

        self.controller.manager.update_mastery(selected_topic.id, new_mastery)
        self.controller.manager.save_to_json(self.controller.filename)
        self.refresh()

# ANALYTICS FRAME
class Analytics(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.rowconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        ttk.Label(self, text="Analytics", font=("Arial", 18)).grid(row=0, column=0, sticky="nsew")
        self.listbox = tk.Listbox(self)
        self.listbox.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        ttk.Button(self, text="Main Menu",
                   command=lambda: controller.show_frame(MainMenu)).grid(row=1, column=0,
                                                                         padx=5, pady=5,
                                                                         columnspan=2, sticky="ew")

    # Clear listbox and insert analytics
    def refresh(self):
        analysis = self.controller.manager.get_analysis()
        weak_categories = self.controller.manager.get_weak_categories()
        weakest = self.controller.manager.get_weakest_category()

        self.listbox.delete(0, tk.END)

        if not analysis:
            self.listbox.insert(tk.END, "No data available.")
            return

        for category, data in analysis.items():
            display = (
                f"{category} | Average: {data['avg_mastery']} | "
                f"Topics Below Mastery Threshold: {data['below_threshold']}"
            )
            self.listbox.insert(tk.END, display)

        self.listbox.insert(tk.END, "")

        self.listbox.insert(tk.END, "Weak Categories:")
        count = self.controller.manager.count_weak_categories()
        if weak_categories:
            for cat in weak_categories:
                self.listbox.insert(tk.END, f"- {cat}")
        else:
            self.listbox.insert(tk.END, "None, keep it up!")

        self.listbox.insert(tk.END, f"{count} total weak categories.\n")
        self.listbox.insert(tk.END, "")

        self.listbox.insert(tk.END, "Weakest Category:")
        if weakest:
            avg = analysis[weakest]['avg_mastery']
            self.listbox.insert(tk.END, f"{weakest} | Average: {avg}")
        else:
            self.listbox.insert(tk.END, "No data available.")

if __name__ == "__main__":
    main()