from copy import deepcopy


class TaskGroup:
    def __init__(self, tasks):
        self.tasks = tasks

    def list_tasks(self, seed=None, source=False):
        tasks = []
        for task in self.tasks:
            if isinstance(task, TaskGroup):
                tasks.extend(task.get_tasks(seed=seed, source=source))
            else:
                tasks.append(task)
        return deepcopy(tasks)

    def get_tasks(self, seed=None, source=False):
        tasks = self.list_tasks(seed=seed, source=source)
        if source:
            return tasks
        return tasks
