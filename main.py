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

# CLASS TOPIC CONTAINER
class StudyManager:
    def __init__(self):
        self.topics: list[Topic] = []

    # Naming convention
    # NOTE: What if at some point, data have to be deleted?
    # The naming convention is not too flexible yet
    def generate_id(self) -> str:
        number = len(self.topics) + 1
        return f"MIMR-T{number:03d}"

    # Topic addition
    def add_topic(self, name: str, category: str, mastery: int, difficulty: int, last_review_date: str) -> None:
        new_id = self.generate_id()
        topic = Topic(new_id, name, category, mastery, difficulty, last_review_date)
        self.topics.append(topic)

    # Review queue generation
    def generate_queue(self) -> list[Topic]:
        queue = sorted(self.topics, key=lambda x: x.get_priority(), reverse=True)
        return queue

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
                topic = Topic(key, value['name'], value['category'], value['mastery'], value['difficulty'], value['last_review_date'])
                self.topics.append(topic)
        # NOTE: Notice the print here, must later be handled by GUI
        except FileNotFoundError:
            print("Welcome to your new Knowledge System! Starting a new database...")
            self.topics = []

# GUI LOGIC
class Application(tk.Tk):
    # Main window
    def __init__(self):
        super().__init__()
        self.title("MIMR System")
        self.geometry("600x600")

    # Container for frames
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)

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

# MAIN MENU FRAME
class MainMenu(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        ttk.Label(self, text="Main Menu", font=("Arial", 18)).pack(pady=20)

        ttk.Button(self, text="Add Topic",
                   command=lambda: controller.show_frame(AddTopic)).pack(pady=5)

        ttk.Button(self, text="Review Queue",
                   command=lambda: controller.show_frame(ReviewQueue)).pack(pady=5)

        ttk.Button(self, text="Analytics",
                   command=lambda: controller.show_frame(Analytics)).pack(pady=5)


# ADD TOPIC FRAME
class AddTopic(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

# REVIEW QUEUE FRAME
class ReviewQueue(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

# ANALYTICS FRAME
class Analytics(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

if __name__ == "__main__":
    main()