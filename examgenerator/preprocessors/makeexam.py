import base64
import os
import pickle

import nbformat
from jupyter_client.kernelspec import KernelSpecManager


class MakeExam:
    def obscure(self, my_dict):
        byte_str = pickle.dumps(my_dict)
        return base64.b85encode(byte_str)

    def new_notebook(self, resources):
        nb = nbformat.v4.new_notebook()
        if "kernel" in resources:
            kernelspec = (
                KernelSpecManager().get_kernel_spec(resources["kernel"]).to_dict()
            )
            nb.metadata["kernelspec"] = dict(
                name=resources["kernel"], display_name=kernelspec["display_name"]
            )
        nb.metadata["scramble_config"] = dict(
            config=self.obscure(resources["replacements"]), seed=resources["seed"]
        )
        return nb

    def preprocess(self, resources):
        exam = self.new_notebook(resources)
        for task in resources["tasks"]:
            nb = nbformat.read(task.notebook_path, as_version=nbformat.NO_CONVERT)
            exam.cells.extend(nb.cells)
        dst = os.path.join(
            resources["dst"],
            "release",
            resources["exam_name"],
            f"{resources['student']}",
            f"{resources['exam_name']}.ipynb",
        )
        if resources["source"]:
            dst = os.path.join(
                resources["dst"],
                "source",
                resources["exam_name"],
                f"{resources['exam_name']}.ipynb",
            )
        nbformat.write(exam, dst)
        return resources
