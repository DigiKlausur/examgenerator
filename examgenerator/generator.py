import os
from tempfile import TemporaryDirectory

import nbformat
from e2xauthoring.converters import Converter
from e2xgrader.preprocessors import ClearHiddenTests, ClearSolutions
from nbgrader.preprocessors import ClearMarkScheme, ClearOutput, LockCells
from traitlets import List
from traitlets.config import Configurable
from traitlets.utils.importstring import import_item

from .preprocessors import (
    CopyFiles,
    CopyTasks,
    GenerateTaskIDs,
    MakeExam,
    MakeSolution,
    RemoveExam,
    RemoveSolutionFiles,
    ScrambleTasks,
)


class ExamGenerator(Converter):
    preprocessors = List(
        [
            RemoveExam,
            CopyTasks,
            ScrambleTasks,
            CopyFiles,
            GenerateTaskIDs,
            MakeExam,
            MakeSolution,
            RemoveSolutionFiles,
        ]
    ).tag(config=True)
    sanitizers = List(
        [ClearOutput, ClearSolutions, LockCells, ClearMarkScheme, ClearHiddenTests]
    ).tag(config=True)

    def __init__(self, dst, exam_name, config=None):
        if config is not None:
            self.config = config
        self.dst_base = dst
        self.exam_name = exam_name
        self._preprocessors = self.init_preprocessors(self.preprocessors)
        self._sanitizers = self.init_preprocessors(self.sanitizers)

    def init_preprocessor(self, preprocessor):
        if isinstance(preprocessor, type):
            return preprocessor()
        else:
            return import_item(preprocessor)()

    def init_preprocessors(self, preprocessors):
        _preprocessors = []
        for preprocessor in preprocessors:
            proc = self.init_preprocessor(preprocessor)
            if isinstance(proc, Configurable) and self.config is not None:
                proc.config = self.config
            _preprocessors.append(proc)
        return _preprocessors

    def make_exam(self, student, tasks, seed=None, source=False):
        tasks = tasks.get_tasks(seed=seed, source=source)
        os.path.join(self.dst_base, student)

        with TemporaryDirectory() as tmp:
            resources = dict(
                student=student,
                seed=seed,
                source=source,
                tmp_dir=tmp,
                tasks=tasks,
                replacements=dict(),
                dst=self.dst_base,
                exam_name=self.exam_name,
            )
            for preprocessor in self._preprocessors:
                resources = preprocessor.preprocess(resources)
            if source:
                return
            exam_path = os.path.join(
                resources["dst"],
                "release",
                resources["exam_name"],
                resources["student"],
                f"{self.exam_name}.ipynb",
            )
            nb = nbformat.read(exam_path, as_version=nbformat.NO_CONVERT)
            for preprocessor in self._sanitizers:
                nb, _ = preprocessor.preprocess(nb, dict())
            nbformat.write(nb, exam_path)
