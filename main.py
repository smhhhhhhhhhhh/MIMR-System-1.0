"""
Mastery-Informed Memory Retention (MIMR) System
"""

import tkinter as tk
from tkinter import ttk
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
        days_elapsed: int = self.days_since_review()
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
                "count": len(topics)
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
    def update_mastery(self, topic_id: str, new_mastery: int):
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
        # NOTE: Notice the print here, must later be handled by GUI
        except FileNotFoundError:
            print("Welcome to your new Knowledge System! Starting a new database...")
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

    # Frame switching
    def show_frame(self, frame):
        next_frame = self.frames[frame]
        next_frame.tkraise()

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
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=0)

# REVIEW QUEUE FRAME
class ReviewQueue(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.rowconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        ttk.Label(self, text="Review Queue", font=("Arial", 18)).grid(row=0, column=0, sticky="nsew")
        tk.Listbox(self).grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        ttk.Button(self, text="Main Menu",
                   command=lambda: controller.show_frame(MainMenu)).grid(row=1, column=0, columnspan=2, sticky="ew")

    def refresh(self):
        pass


# ANALYTICS FRAME
class Analytics(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        ttk.Label(self, text="Analytics", font=("Arial", 18)).grid(row=0, column=0, sticky="nsew")
        tk.Listbox(self).grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        ttk.Button(self, text="Main Menu",
                   command=lambda: controller.show_frame(MainMenu)).grid(row=1, column=0, columnspan=2, sticky="ew")

if __name__ == "__main__":
    main()