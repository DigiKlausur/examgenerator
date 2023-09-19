from dataclasses import dataclass


@dataclass
class PoolConstraint:
    """This class represents a constraint on how many pools should be sampled"""

    pools: int


@dataclass
class TaskConstraint:
    """This class represents a basic task constraint"""

    tasks: int


@dataclass
class TasksPerPoolConstraint(TaskConstraint):
    """This class represents a constraint on how many tasks should be sampled from each pool"""

    pass


@dataclass
class TasksConstraint(TaskConstraint):
    """This class represents a constraint on how many tasks should be sampled"""

    pass


@dataclass
class TasksWithScoreConstraint(TaskConstraint):
    """This class represents a constraint on how many tasks
    with a certain score should be sampled"""

    score: int


@dataclass
class TasksWithScorePerPoolConstraint(TaskConstraint):
    """This class represents a constraint on how many tasks
    with a certain score should be sampled from each pool"""

    score: int
