from typing import List, Union

from ..sampling import TaskSampler
from ..sampling.constraints import (
    PoolConstraint,
    TasksPerPoolConstraint,
    TasksWithScorePerPoolConstraint,
)
from .task import Task
from .taskgroup import TaskGroup


class SampledTaskGroup(TaskGroup):
    def __init__(
        self,
        tasks: List[Task],
        task_constraints: List[
            Union[TasksPerPoolConstraint, TasksWithScorePerPoolConstraint]
        ],
        pool_constraint: PoolConstraint = None,
        permute: bool = False,
    ):
        super().__init__(tasks)
        self.sampler = TaskSampler(
            tasks,
            pool_constraint=pool_constraint,
            task_constraints=task_constraints,
            permute=permute,
        )

    def get_tasks(self, seed=None, source=None):
        return self.sampler.get_tasks(seed=seed, source=source)
