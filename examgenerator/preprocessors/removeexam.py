import os
import shutil


class RemoveExam:
    def preprocess(self, resources):
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
        source_path = os.path.join(resources["dst"], "source", resources["exam_name"])
        if os.path.exists(exam_path):
            shutil.rmtree(exam_path)
        if os.path.exists(solution_path):
            shutil.rmtree(solution_path)
        if resources["source"] and os.path.exists(source_path):
            shutil.rmtree(source_path)
        return resources
