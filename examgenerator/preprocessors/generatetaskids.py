import nbformat
from e2xgrader.utils.nbgrader_cells import (
    get_task_info,
    get_valid_name,
    is_description,
    is_grade,
    is_solution,
)


class GenerateTaskIDs:
    def generate_ids(self, nb, name):
        task = get_task_info(nb)

        ids = []
        suffix = ord("A")

        for subtask in task["subtasks"]:
            subtask_id = "{}_{}".format(name, chr(suffix))
            ids.append(subtask_id)
            suffix += 1
            tests = 0
            headers = 0
            for idx in subtask:
                cell = nb.cells[idx]
                if is_description(cell):
                    cell.metadata.nbgrader.grade_id = "{}_Description{}".format(
                        subtask_id, headers
                    )
                    headers += 1
                elif is_solution(cell):
                    cell.metadata.nbgrader.grade_id = subtask_id
                elif is_grade(cell):
                    cell.metadata.nbgrader.grade_id = "test_{}{}".format(
                        subtask_id, tests
                    )
                    tests += 1

        if "header" in task:
            header = nb.cells[task["header"]]
            header.metadata.nbgrader.grade_id = "{}_Header".format("".join(ids))

        return nb

    def preprocess(self, resources):
        for task in resources["tasks"]:
            nb = nbformat.read(task.notebook_path, as_version=nbformat.NO_CONVERT)
            name = get_valid_name("_".join([task.pool, task.name]))
            self.generate_ids(nb, name)
            nbformat.write(nb, task.notebook_path)
        return resources
