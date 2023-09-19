import importlib.util
import os
import re
import shutil
import sys

import nbformat


class ScrambleTasks:
    def __init__(self):
        self.__pattern = re.compile(r"{{\s*(\w+)\s*}}")

    def __add_prefix(self, prefix, string):
        return self.__pattern.sub(r"{{{{{}_\1}}}}".format(prefix), string)

    def prefix_scramble_variables(self, nb, task):
        prefix = "_".join([task.pool, task.name])
        for cell in nb.cells:
            cell.source = self.__add_prefix(prefix, cell.source)

    def replace_scramble_variables(self, nb, task, replacements):
        for cell in nb.cells:
            for replacement_variable, value in replacements.items():
                cell.source = cell.source.replace(
                    "{{" + replacement_variable + "}}", str(value)
                )

    def load_scrambler_from_task(self, task, name="task_scrambler"):
        path = os.path.join(task.path, "scramble", "__init__.py")
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        return module

    def preprocess_task(self, task, resources):
        if not task.is_randomizable:
            return
        nb = nbformat.read(task.notebook_path, as_version=nbformat.NO_CONVERT)
        self.prefix_scramble_variables(nb, task)

        if not resources["source"]:
            scrambler = self.load_scrambler_from_task(task)
            prefix = "_".join([task.pool, task.name])
            replacements = {
                f"{prefix}_{name}": value
                for name, value in scrambler.replacement_variables(
                    resources["seed"]
                ).items()
            }

            resources["replacements"].update(replacements)
            self.replace_scramble_variables(nb, task, replacements)
            if hasattr(scrambler, "create_extra_files"):
                scrambler.create_extra_files(resources["seed"], task.path)

        nbformat.write(nb, task.notebook_path)
        shutil.rmtree(os.path.join(task.path, "scramble"))

    def preprocess(self, resources):
        for task in resources["tasks"]:
            self.preprocess_task(task, resources)

        return resources
