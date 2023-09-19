import filecmp
import os
import shutil

import nbformat


def get_import_path(file_path):
    """Get the import path of a python file"""
    if os.path.split(file_path)[-1] == "__init__.py":
        file_path = os.path.split(file_path)[0]
    else:
        file_path = os.path.splitext(file_path)[0]
    return file_path.replace(os.path.sep, ".")


class CopyFiles:
    def rename(self, task, old_name, new_name):
        if os.path.splitext(old_name)[-1] == ".py":
            old_file_name = get_import_path(old_name)
            new_file_name = get_import_path(new_name)
        else:
            old_file_name = os.path.split(old_name)[1]
            new_file_name = os.path.split(new_name)[1]

        nb = nbformat.read(task.notebook_path, as_version=nbformat.NO_CONVERT)
        for cell in nb.cells:
            cell.source = cell.source.replace(old_name, new_name)
            if old_file_name != new_file_name:
                cell.source = cell.source.replace(old_file_name, new_file_name)
        nbformat.write(nb, task.notebook_path)

    def get_files(self, task, source=False, ignored_file_extensions=[".pyc"]):
        finds = []
        subdirs = ["img", "data", "solution"]
        if source:
            subdirs = [
                d for d in subdirs if not d.startswith(".") and d not in ["scramble"]
            ]
        for subdir in subdirs:
            for root, dirs, files in os.walk(os.path.join(task, subdir)):
                dirs[:] = [d for d in dirs if d not in [".ipynb_checkpoints"]]
                for file in files:
                    if os.path.splitext(file)[-1] not in ignored_file_extensions:
                        finds.append(os.path.relpath(os.path.join(root, file), task))
        return finds

    def get_new_name(self, file, dst):
        suffix = 1
        name, extension = os.path.splitext(file)
        new_name = "{}_{}{}".format(name, suffix, extension)
        while os.path.exists(os.path.join(dst, new_name)):
            suffix += 1
            new_name = "{}_{}{}".format(name, suffix, extension)
        return new_name

    def copyfile(self, src, dst):
        """
        Copy file
        Arguments:
            src -- source file
            dst -- destination file
        Returns:
            status -- True if dst does not exists or is equal to src,
                      False if dst exists and differs from src.
                      In this case nothing is copied
        """
        if os.path.exists(dst):
            return filecmp.cmp(src, dst)
        dirs = os.path.split(dst)[0]
        os.makedirs(dirs, exist_ok=True)
        shutil.copyfile(src, dst)
        return True

    def copyfiles(self, task, dst, source=False):
        exercise_base = "files"
        src = task.path
        for file in self.get_files(src, source=source):
            src_file = os.path.join(src, file)
            dst_file = os.path.join(dst, file)
            new_name = os.path.join(exercise_base, file)
            if not self.copyfile(src_file, dst_file):
                # File with that name already exists
                renamed = self.get_new_name(file, dst)
                self.copyfile(src_file, os.path.join(dst, renamed))
                new_name = os.path.join(exercise_base, renamed)
            # Rename in notebook
            self.rename(task, file, new_name)

    def preprocess(self, resources):
        dst = os.path.join(
            resources["dst"],
            "release",
            resources["exam_name"],
            resources["student"],
            "files",
        )
        if resources["source"]:
            dst = os.path.join(
                resources["dst"], "source", resources["exam_name"], "files"
            )
        os.makedirs(dst, exist_ok=True)
        for task in resources["tasks"]:
            self.copyfiles(task, dst, resources["source"])
        return resources
