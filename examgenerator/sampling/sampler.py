import random as rd
from collections import defaultdict
from copy import deepcopy
from typing import Dict, List

import nbformat
from e2xgrader.utils.nbgrader_cells import get_points

from ..tasks import Task
from .constraints import PoolConstraint, TaskConstraint
from .validator import ConstraintValidator


class TaskSampler:
    """
    A class for sampling tasks from a list of tasks with constraints.

    Args:
        tasks (List[Task]): A list of tasks to sample from.
        task_constraints (List[TaskConstraint]): A list of constraints that must be satisfied
                                                 for each task.
        pool_constraint (PoolConstraint, optional): A constraint on the pools to sample from.
                                                    Defaults to None.
        permute (bool, optional): Whether to permute the list of sampled tasks. Defaults to False.
    """

    def __init__(
        self,
        tasks: List[Task],
        task_constraints: List[TaskConstraint],
        pool_constraint: PoolConstraint = None,
        permute: bool = False,
    ):
        self.random_gen = rd.Random()
        self.permute = permute
        self.tasks = tasks
        self.calculate_points()
        self.pool_constraint = pool_constraint
        self.task_constraints = self.parse_task_constraints(task_constraints)

        self.validator = ConstraintValidator(
            tasks, self.task_constraints, self.pool_constraint
        )
        self.validator.validate()

        tasks_per_pool = self.task_constraints["TasksPerPoolConstraint"]
        self.tasks_per_pool = tasks_per_pool[0].tasks if tasks_per_pool else 0

    def calculate_points(self) -> None:
        """
        Calculates the score for each task based on the points assigned to each cell
        in the task's notebook.
        """
        self.score_per_pool = defaultdict(lambda: defaultdict(list))
        for task in self.tasks:
            if task.points < 0:
                assert task.notebook_exists, f"No notebook found for task {task}"
                nb = nbformat.read(task.notebook_path, as_version=nbformat.NO_CONVERT)
                task.points = sum([get_points(cell) for cell in nb.cells])
            self.score_per_pool[task.pool][task.points].append(task)

    def parse_task_constraints(
        self, task_constraints: List[TaskConstraint]
    ) -> Dict[str, List[TaskConstraint]]:
        """
        Parses a list of task constraints and returns a dictionary of constraint type
        to constraint objects.

        Args:
            task_constraints (List[TaskConstraint]): A list of task constraints to parse.

        Returns:
            Dict[str, List[TaskConstraint]]: A dictionary of constraint type to constraint objects.
        """
        constraints = defaultdict(list)
        for constraint in task_constraints:
            constraints[type(constraint).__name__].append(constraint)
        return constraints

    def get_score_dict(
        self, pools: List[str], tasks: List[Task]
    ) -> Dict[str, Dict[str, List[Task]]]:
        """
        Returns a dictionary of task scores by pool.

        Args:
            pools (List[str]): A list of pool names to include in the score dictionary.
            tasks (List[Task]): A list of tasks to include in the score dictionary.

        Returns:
            Dict[str, Dict[str, List[Task]]]: A dictionary of task scores by pool.
        """
        scores = defaultdict(lambda: defaultdict(list))
        for task in tasks:
            if task.pool in pools:
                scores[task.points][task.pool].append(task)
        for score in scores:
            for pool in scores[score]:
                self.random_gen.shuffle(scores[score][pool])
        return scores

    def sample_pools(self, tasks: List[Task]) -> List[str]:
        """
        Sample a list of pools based on the given pool constraint, if any.
        Otherwise, return all available pools.

        Args:
            tasks (List[Task]): The list of tasks to sample pools from.

        Returns:
            List[str]: The list of pools to sample tasks from.
        """
        pools = list(set([task.pool for task in tasks]))
        if self.pool_constraint is not None:
            pools = self.random_gen.sample(pools, self.pool_constraint.pools)
        return pools

    def sample_tasks_with_score_per_pool(
        self, scores: Dict[int, Dict[int, List[Task]]], pools: List[int]
    ) -> List[Task]:
        """
        Sample a list of tasks based on the "TasksWithScorePerPool" constraints.
        For each constraint sample n_tasks with a certain score from each pool.

        Args:
            scores (Dict[int, Dict[int, List[Task]]]): A dictionary of scores for each pool.
            pools (List[int]): The list of pools to sample tasks from.

        Returns:
            List[Task]: The list of sampled tasks.
        """
        sample = []
        for constraint in self.task_constraints["TasksWithScorePerPoolConstraint"]:
            for pool in pools:
                sample.extend(scores[constraint.score][pool][-constraint.tasks :])
                del scores[constraint.score][pool][-constraint.tasks :]
        return sample

    def sample_tasks_with_score(
        self, scores: Dict[int, Dict[int, List[Task]]], pools: List[int]
    ) -> List[Task]:
        """
        Sample a list of tasks based on the "TasksWithScore" constraints.
        For each constraint sample n_tasks with a certain score from all tasks.

        Args:
            scores (Dict[int, Dict[int, List[Task]]]): A dictionary of scores for each pool.
            pools (List[int]): The list of pools to sample tasks from.

        Returns:
            List[Task]: The list of sampled tasks.
        """
        sample = []
        pool_size = {
            pool: sum([len(scores[score][pool]) for score in scores]) for pool in pools
        }
        for constraint in self.task_constraints["TasksWithScoreConstraint"]:
            candidates = [
                x
                for pool, candidate in scores[constraint.score].items()
                for x in candidate[-(pool_size[pool] - self.tasks_per_pool) :]
            ]
            new_sample = self.random_gen.sample(candidates, constraint.tasks)
            sample.extend(new_sample)
            # Remove sample
            for task in new_sample:
                scores[task.points][task.pool].remove(task)
                pool_size[task.pool] -= 1
        return sample

    def sample_tasks_without_score(
        self, scores: Dict[int, Dict[int, List[Task]]], pools: List[int]
    ) -> List[Task]:
        """
        Sample a list of based on the "TasksPerPoolConstraint" and the "TasksConstraint".
        This will sample tasks regardless of the score of a task.


        Args:
            scores (Dict[int, Dict[int, List[Task]]]): A dictionary of scores for each pool.
            pools (List[int]): The list of pools to sample tasks from.

        Returns:
            List[Task]: The list of sampled tasks.
        """
        sample = []
        pool_dict = defaultdict(list)
        for score, pools in scores.items():
            for pool, tasks in pools.items():
                pool_dict[pool].extend(tasks)

        if self.tasks_per_pool > 0:
            for pool, tasks in pool_dict.items():
                # Get the last N tasks based on the `tasks_per_pool` constraint
                sample.extend(tasks[-self.tasks_per_pool :])
                del tasks[-self.tasks_per_pool :]

        # Flatten the list of remaining tasks
        rest = [task for pool_tasks in pool_dict.values() for task in pool_tasks]

        if len(self.task_constraints["TasksConstraint"]) > 0:
            sample.extend(
                self.random_gen.sample(
                    rest, self.task_constraints["TasksConstraint"][0].tasks
                )
            )
        return sample

    def get_tasks(self, seed: int = None, source: bool = False) -> List[Task]:
        """
        Sample the tasks according to the given constraints.

        Args:
            seed (int, optional): The seed to use for the random number generator. If None,
                the current system time is used. Defaults to None.
            source (bool, optional): If True, no tasks will be sampled and all tasks will be
                returned.

        Returns:
            List[Task]: The sampled tasks
        """
        self.random_gen = rd.Random(seed)
        tasks = [deepcopy(task) for task in self.tasks]

        if source:
            return tasks

        pools = self.sample_pools(tasks)
        scores = self.get_score_dict(pools, tasks)

        sample = self.sample_tasks_with_score_per_pool(scores, pools)
        sample.extend(self.sample_tasks_with_score(scores, pools))
        sample.extend(self.sample_tasks_without_score(scores, pools))

        if self.permute:
            self.random_gen.shuffle(sample)
        return sample
