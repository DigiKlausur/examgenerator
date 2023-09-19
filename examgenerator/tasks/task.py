import glob
import os
from dataclasses import dataclass
from typing import List


@dataclass
class Task:
    """Class for keeping information on a task"""

    pool: str
    name: str
    root: str = ""
    points: int = -1

    @property
    def relpath(self):
        return os.path.join(self.pool, self.name)

    @property
    def path(self):
        return os.path.join(self.root, self.pool, self.name)

    @property
    def notebook_path(self) -> str:
        return os.path.join(self.path, f"{self.name}.ipynb")

    @property
    def notebook_exists(self) -> bool:
        return os.path.exists(self.notebook_path)

    @property
    def is_randomizable(self) -> bool:
        return os.path.exists(os.path.join(self.path, "scramble", "__init__.py"))

    @property
    def data_files(self) -> List[str]:
        data_path = os.path.join(self.path, "data")
        data_files = glob.glob(os.path.join(data_path, "*"))
        return [os.path.relpath(file, start=data_path) for file in data_files]
