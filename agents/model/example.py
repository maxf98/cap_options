import uuid, os, pickle, ast
from config import EXAMPLE_DIR


class TaskExample:
    def __init__(self, task: str, code: str):
        self.id = uuid.uuid4()
        self.task = task
        self.code = code

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

    def get_non_function_code(self):
        # Parse the code into an AST
        tree = ast.parse(self.code)
        # Extract non-function top-level code
        non_function_code_nodes = [
            node
            for node in tree.body
            if not isinstance(
                node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
            )
        ]
        # Convert AST nodes back to source code
        non_function_code = "\n".join(
            ast.unparse(node) for node in non_function_code_nodes
        )

        return non_function_code

    @staticmethod
    def retrieve_task_with_id(id) -> "TaskExample":
        with open(f"{EXAMPLE_DIR}/{id}/example.pkl", "rb") as file:
            example = pickle.load(file)

        return example
