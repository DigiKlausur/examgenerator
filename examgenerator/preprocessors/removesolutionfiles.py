import os
import shutil


class RemoveSolutionFiles:
    def preprocess(self, resources):
        if resources["source"]:
            return resources
        solution_path = os.path.join(
            resources["dst"],
            "release",
            resources["exam_name"],
            resources["student"],
            "files",
            "solution",
        )
        if os.path.exists(solution_path):
            shutil.rmtree(solution_path)
        return resources
