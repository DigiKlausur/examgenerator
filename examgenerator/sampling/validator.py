from collections import defaultdict
from typing import Dict, List

from ..tasks import Task
from .constraints import PoolConstraint, TaskConstraint


class ConstraintValidator:
    def __init__(
        self,
        tasks: List[Task],
        task_constraints: Dict[str, List[TaskConstraint]],
        pool_constraint: PoolConstraint = None,
    ):
        self.tasks = tasks
        self.task_constraints = task_constraints
        self.pool_constraint = pool_constraint

        self.pools = defaultdict(list)
        for task in self.tasks:
            self.pools[task.pool].append(task)

    @property
    def tasks_per_pool(self):
        tasks_per_pool = sum(
            [
                constraint.tasks
                for constraint in self.task_constraints.get(
                    "TasksPerPoolConstraint", []
                )
            ]
        )
        tasks_per_pool += sum(
            [
                constraint.tasks
                for constraint in self.task_constraints.get(
                    "TasksWithScorePerPoolConstraint", []
                )
            ]
        )
        return tasks_per_pool

    def validate_pool_constraint(self):
        assert self.pool_constraint is None or self.pool_constraint.pools <= len(
            self.pools
        ), (
            f"You want to sample from {self.pool_constraint.pools}"
            + " pools but only provided {len(self.pools)} pools."
        )

    def validate_number_of_task_constraints(self):
        assert (
            len(self.task_constraints.get("TasksPerPoolConstraint", [])) <= 1
        ), "You can only specify one TasksPerPoolConstraint"
        assert (
            len(self.task_constraints.get("TasksConstraint", [])) <= 1
        ), "You can only specify one TasksConstraint"

    def validate_tasks_per_pool(self):
        smallest_pool_size = min([len(tasks) for tasks in self.pools.values()])

        assert self.tasks_per_pool <= smallest_pool_size, (
            f"You want to sample at least {self.tasks_per_pool} tasks per pool"
            + "but your smallest pool only has {smallest_pool_size} tasks."
        )

    def validate_total_tasks(self):
        total_tasks = 0
        if self.pool_constraint is not None:
            total_tasks += self.tasks_per_pool * self.pool_constraint.pools
        else:
            total_tasks += self.tasks_per_pool * len(self.pools)

        total_tasks += sum(
            [
                constraint.tasks
                for constraint in self.task_constraints.get("TasksConstraint", [])
            ]
        )
        total_tasks += sum(
            [
                constraint.tasks
                for constraint in self.task_constraints.get(
                    "TasksWithScoreConstraint", []
                )
            ]
        )
        assert total_tasks <= len(self.tasks), (
            f"You want to sample a total of {total_tasks} tasks"
            + " but only provided {len(self.tasks)} tasks."
        )

    def validate_total_tasks_with_score(self):
        score = defaultdict(lambda: defaultdict(int))
        for pool, tasks in self.pools.items():
            for task in tasks:
                score[task.points][pool] += 1

        for constraint in self.task_constraints.get(
            "TasksWithScorePerPoolConstraint", []
        ):
            assert len(score[constraint.score]) == len(
                self.pools
            ), f"Not all of your pools have enough tasks with {constraint.score} points."
            assert min(score[constraint.score].values()) >= constraint.tasks, (
                f"You don't have enough tasks worth {constraint.score}"
                + " points to sample from per pool."
            )
            for pool in score[constraint.score]:
                score[constraint.score][pool] -= 1

        score_sum = {key: len(val) for key, val in score.items()}
        for constraint in self.task_constraints.get("TasksWithScoreConstraint", []):
            assert (
                constraint.tasks <= score_sum[constraint.score]
            ), f"You don't have enough tasks worth {constraint.score} points to sample from"
            score_sum[constraint.score] -= constraint.tasks

    def validate(self):
        self.validate_pool_constraint()
        self.validate_number_of_task_constraints()
        self.validate_tasks_per_pool()
        self.validate_total_tasks()
        self.validate_total_tasks_with_score()
