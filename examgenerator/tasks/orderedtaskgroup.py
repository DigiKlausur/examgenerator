from .taskgroup import TaskGroup


class OrderedTaskGroup(TaskGroup):
    def __init__(self, tasks):
        super().__init__(tasks)

    def get_tasks(self, seed=None, source=False):
        return self.list_tasks(seed=seed, source=source)
