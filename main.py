"""
Mastery-Informed Memory Retention (MIMR) System
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime
import json

# CLASS TOPIC
class Topic:
    def __init__(self, id: str, name: str, category: str, mastery: int, difficulty: int, last_review_date: str) -> None:
        self.id = id
        self.name = name
        self.category = category
        self.mastery = mastery
        self.difficulty = difficulty
        self.last_review_date = last_review_date

    def days_since_review(self) -> int:
        try:
            date_datetime: datetime = datetime.strptime(self.last_review_date, "%Y-%m-%d")
            last_review_timedelta = datetime.now() - date_datetime
            return last_review_timedelta.days
        except ValueError:
            return 0

    def get_priority(self) -> float:
        days_elapsed: int = self.days_since_review()
        priority: float = (self.difficulty*days_elapsed) / (self.mastery + 1)
        return priority

# CLASS TOPIC CONTAINER
class StudyManager:
    def __init__(self):
        self.topics: list[Topic] = []

    def generate_id(self) -> str:
        number = len(self.topics) + 1
        return f"MIMR-T{number:03d}"

    def add_topic(self, name: str, category: str, mastery: int, difficulty: int, last_review_date: str) -> None:
        new_id = self.generate_id()
        topic = Topic(new_id, name, category, mastery, difficulty, last_review_date)
        self.topics.append(topic)

    def generate_queue(self) -> list[Topic]:
        queue = sorted(self.topics, key=lambda x: x.get_priority(), reverse=True)
        return queue

    def update_mastery(self, topic_id: str, new_mastery: int):
        for topic in self.topics:
            if topic.id == topic_id:
                topic.mastery = new_mastery
                topic.last_review_date = datetime.now().strftime("%Y-%m-%d")
                return True
        return False

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

    def load_from_json(self, filename: str) -> None:
        self.topics = []
        try:
            with open(filename, 'r') as file:
                well = json.load(file)
            for key, value in well.items():
                topic = Topic(key, value['name'], value['category'], value['mastery'], value['difficulty'], value['last_review_date'])
                self.topics.append(topic)
        except FileNotFoundError:
            print("Welcome to your new Knowledge System! Starting a new database...")
            self.topics = []

    