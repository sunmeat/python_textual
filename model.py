from dataclasses import dataclass
from typing import List


@dataclass
class Task:
    description: str
    done: bool = False


class TaskModel:
    def __init__(self):
        self.tasks: List[Task] = []

    def add_task(self, description: str) -> bool:
        desc = description.strip()
        if not desc:
            return False
        self.tasks.append(Task(desc))
        return True

    def get_all_tasks(self) -> List[Task]:
        return self.tasks.copy()

    def mark_done(self, index: int) -> bool:
        if 0 <= index < len(self.tasks):
            self.tasks[index].done = True
            return True
        return False

    def delete_task(self, index: int) -> bool:
        if 0 <= index < len(self.tasks):
            del self.tasks[index]
            return True
        return False