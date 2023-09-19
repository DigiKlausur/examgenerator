import os
import shutil


class MakeSolution:
    def preprocess(self, resources):
        if resources["source"]:
            return resources
        exam_path = os.path.join(
            resources["dst"],
            "release",
            resources["exam_name"],
            resources["student"],
        )
        solution_path = os.path.join(
            resources["dst"],
            "solution",
            resources["exam_name"],
            f"{resources['student']}",
        )
        shutil.copytree(exam_path, solution_path)
        return resources
