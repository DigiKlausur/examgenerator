import os
import shutil


class CopyTasks:
    def preprocess(self, resources):
        for task in resources["tasks"]:
            src = task.path
            dst = os.path.join(resources["tmp_dir"], task.relpath)
            shutil.copytree(src, dst)
            task.root = resources["tmp_dir"]
        return resources
