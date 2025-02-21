import uuid, os, pickle, ast
from agents.model.config import EXAMPLE_DIR
from agents.model.environment_configuration import EnvironmentConfiguration


"""
when a successful attempt trace is stored, the task should also be revised to incorporate the feedback rounds, 
to specify the task if it was ill-posed initially...
"""


class TaskExample:
    def __init__(
        self,
        task: str,
        code: str,
        initial_config: EnvironmentConfiguration,
        final_config: EnvironmentConfiguration,
    ):
        self.id = uuid.uuid4()
        self.task = task
        # code should only be non-function, i.e. flat code
        self.code = code
        self.initial_config = initial_config
        self.final_config = final_config

    @property
    def save_dir(self):
        return f"{EXAMPLE_DIR}/{self.id}"

    def dump(self):
        os.makedirs(self.save_dir, exist_ok=True)
        with open(f"{self.save_dir}/code.py", "w") as file:
            file.write(f"# TASK:{self.task}\n\n{self.code}")
        with open(f"{self.save_dir}/example.pkl", "wb") as file:
            pickle.dump(self, file)

    def get_skill_headers(self):
        tree = ast.parse(self.code)
        func_defs = [node for node in tree.body if isinstance(node, ast.FunctionDef)]
        funcs = [ast.get_source_segment(self.code, func) for func in func_defs]
        return funcs

    @staticmethod
    def retrieve_task_with_id(id) -> "TaskExample":
        with open(f"{EXAMPLE_DIR}/{id}/example.pkl", "rb") as file:
            example = pickle.load(file)

        return example


