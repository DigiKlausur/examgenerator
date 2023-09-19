import random as rd
from copy import deepcopy

from .taskgroup import TaskGroup


class PermutationTaskGroup(TaskGroup):
    def __init__(self, tasks):
        super().__init__(tasks)

    def list_tasks(self, tasks, seed=None, source=False):
        extracted_tasks = []
        for task in tasks:
            if isinstance(task, TaskGroup):
                extracted_tasks.extend(task.get_tasks(seed=seed, source=source))
            else:
                extracted_tasks.append(task)
        return extracted_tasks

    def get_tasks(self, seed=None, source=False):
        random = rd.Random(seed)
        tasks = deepcopy(self.tasks)
        if not source:
            random.shuffle(tasks)
        return self.list_tasks(tasks, seed=seed, source=source)
